"""Source-only v182 live metadata recheck. Zero raw rasters, bird positions or tide series emitted."""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
RESULT = ROOT / "validation_v182/results/real_original_source_evidence_matrix_v182.json"
SITES = {
    "rws_morphology": {
        "url": "https://waterinfo-extra.rws.nl/monitoring/morfologie/",
        "terms": ["Vaklodingen", "20x20", "NAP"],
    },
    "rws_gauge_nap": {
        "url": "https://geo.rijkswaterstaat.nl/services/ogc/gdr/fis_vnds/ogc/features/v1/collections/waterhoogte_nap/items?f=text%2Fhtml",
        "terms": ["waterhoogte_nap", "Vlieland haven"],
    },
    "deltares_tidal_propagation": {
        "url": "https://www.deltares.nl/expertise/publicaties/analysis-of-observed-water-level-data-in-and-around-the-dutch-wadden-sea",
        "terms": ["propagation", "amplitudes", "phases"],
    },
}
TILE_COUNT = 10

def retrieve(url: str) -> tuple[bytes | None, dict]:
    provenance = {"url": url, "sha256": None, "bytes": 0, "downloaded": False, "error_kind": None}
    try:
        req = Request(url, headers={"User-Agent": "boids-v182-research-source-audit/1.0", "Accept": "*/*"})
        with urlopen(req, timeout=40) as response:
            data = response.read(2_500_001)
        if len(data) > 2_500_000:
            raise ValueError("SOURCE_RESPONSE_TOO_LARGE")
        provenance.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), downloaded=True)
        return data, provenance
    except Exception as exc:
        provenance["error_kind"] = type(exc).__name__
        return None, provenance

def verify_v174_das(manifest: dict, downloader=retrieve) -> dict:
    tiles = manifest.get("all_original_tile_source_schema_or_STOP", [])
    if len(tiles) != TILE_COUNT or len({row["tile"] for row in tiles}) != TILE_COUNT:
        raise ValueError("Expected exactly 10 unique frozen original Deltares tile sources")
    records = []
    for row in tiles:
        p = row["das"]["original_provider_provenance"]
        url = p["source_uri_requested"]
        if not (url.startswith("https://opendap.deltares.nl/") and url.endswith(".nc.das")):
            raise ValueError("Disallowed original source URL")
        data, source = downloader(url)
        valid = bool(data is not None and source["sha256"] == p["source_metadata_content_SHA256"])
        if not valid:
            records.append({"tile": row["tile"], "source": source, "frozen_das_sha256_MATCH": False,
                            "native_das_declares_NAP": None, "native_das_declares_explicit_vertical_datum": None})
            continue
        das_text = data.decode("utf-8", errors="replace")
        # Do not confuse horizontal EPSG:28992, m units or 'altitude' with vertical datum.
        has_datum_attribute = bool(re.search(r"(?i)(vertical_datum|vertical_reference|geospatial_vertical_datum)", das_text))
        has_nap = bool(re.search(r"(?i)(?<![A-Za-z])NAP(?![A-Za-z])", das_text))
        records.append({"tile": row["tile"], "source": source, "frozen_das_sha256_MATCH": True,
                        "native_das_declares_NAP": has_nap,
                        "native_das_declares_explicit_vertical_datum": has_datum_attribute})
    return {
        "n_original_tiles": len(records),
        "original_DAS_exact_SHA_rechecked": sum(x["frozen_das_sha256_MATCH"] for x in records),
        "native_DAS_explicit_NAP_count_verified": sum(x["native_das_declares_NAP"] is True for x in records),
        "native_DAS_explicit_vertical_datum_count_verified": sum(
            x["native_das_declares_explicit_vertical_datum"] is True for x in records
        ),
        "tile_source_evidence": records,
    }

def verify_official_sources(downloader=retrieve) -> dict:
    records = {}
    for key, spec in SITES.items():
        raw, source = downloader(spec["url"])
        content = raw.decode("utf-8", errors="replace") if raw else ""
        # These are SOURCE CLASS signals only, not a local GPS tide-transfer calibration.
        hits = {term: term.lower() in content.lower() for term in spec["terms"]}
        records[key] = {"source": source, "expected_primary_terms": hits,
                        "primary_source_content_verified": all(hits.values()) and source["downloaded"]}
    return records

def build_report(manifest: dict, downloader=retrieve) -> dict:
    native = verify_v174_das(manifest, downloader)
    official = verify_official_sources(downloader)
    class_source = bool(official["rws_morphology"]["primary_source_content_verified"])
    station_source = bool(official["rws_gauge_nap"]["primary_source_content_verified"])
    propagation_source = bool(official["deltares_tidal_propagation"]["primary_source_content_verified"])
    native_exact = native["original_DAS_exact_SHA_rechecked"] == TILE_COUNT
    # Even all three pages corroborated does not establish a common z datum at individual
    # native cells, a tide correction at GPS coordinates, or exact surveying day.
    return {
        "version": "v182-original-metadata-live-recheck-source-only",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observations": {
            "native_original_DAS_rechecked": native_exact,
            "official_RWS_morphology_source_seen": class_source,
            "official_RWS_station_NAP_source_seen": station_source,
            "independent_Deltares_tidal_propagation_source_seen": propagation_source,
            "native_DAS_NAP_exact_count": native["native_DAS_explicit_NAP_count_verified"],
            "native_DAS_vertical_datum_exact_count": native["native_DAS_explicit_vertical_datum_count_verified"],
        },
        "scientific_gates": {
            "datum_source_class_plausible_NOT_native_cell_calibration": class_source and station_source,
            "vertical_datum_at_original_native_z_grid_proven": False,
            "harbor_to_each_GPS_cell_tide_transfer_calibrated": False,
            "actual_field_survey_day_per_native_pixel_verified": False,
            "local_water_depth_exposure_or_foraging_mechanism_admitted": False,
        },
        "status": "STOP_LOCAL_EXPOSURE_AND_BIOLOGICAL_FIT",
        "native": native,
        "official": official,
        "disclaimer": "Source-only evidence. No raw GPS, bathymetry, gauge observations, or foraging outcomes.",
    }

def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    report = build_report(manifest)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    print("V182_LIVE_SOURCE_SCOPE=" + json.dumps({
        "observations": report["observations"],
        "scientific_gates": report["scientific_gates"],
        "status": report["status"],
    }, sort_keys=True))
    if report["native"]["original_DAS_exact_SHA_rechecked"] != 10:
        print("V182_REMOTE_METADATA_RECHECK=INCOMPLETE_OR_SHA_CHANGED; never infer PASS")

if __name__ == "__main__":
    main()
