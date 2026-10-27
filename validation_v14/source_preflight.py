#!/usr/bin/env python3
"""v14 outcome-blind public source and data-quality preflight (not model fitting).

Downloads original published records only into a temporary runner directory.
No animal rows, locations, names/identifiers, or forecasts are written to JSON.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import re
import tempfile
import zipfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ZENODO_ID = "21092705"
DRYAD_DOI = "doi:10.5061/dryad.4tmpg4fp6"
CSV_NAME = "Pigeon.Flights.Habitat.csv"
MAX_JSON_BYTES = 8_000_000
MAX_RAW_BYTES = 100_000_000
MAX_ZENODO_BYTES = 160_000_000  # Pinned 126,588,691 byte single ZIP file
USER_AGENT = "boids-v14-research-provenance/1.0 (+https://github.com/zuizui0223/boids)"
NECESSARY = ("Bird", "Loft", "Iteration", "Counter", "Latitude", "Longitude", "Time", "Date", "Layer")


def request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "application/json"
    })
    with urllib.request.urlopen(req, timeout=35) as response:
        raw = response.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("Metadata larger than declared 8MB cap")
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Metadata JSON is not an object")
    return obj


def source_error(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return "HTTP " + str(exc.code)
    return type(exc).__name__ + ": " + str(exc)[:160]


def nested_objects(root, predicate):
    """Walk dictionaries/lists; caller decides whether a record is admissible."""
    stack = [root]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            if predicate(obj):
                yield obj
            stack.extend(v for v in obj.values() if isinstance(v, (dict, list)))
        elif isinstance(obj, list):
            stack.extend(v for v in obj if isinstance(v, (dict, list)))


def public_version_ids(obj: dict) -> list[int]:
    found = set()
    for d in nested_objects(obj, lambda d: True):
        # The official API gives version endpoints at /api/v2/versions/<integer>.
        for key, value in d.items():
            if key in ("href", "url") and isinstance(value, str):
                mat = re.search(r"/api/v2/versions/(\d+)(?:[/?#]|$)", value)
                if mat:
                    found.add(int(mat.group(1)))
            if key in ("version", "versionId", "version_id") and isinstance(value, int):
                found.add(value)
    return sorted(found)


def dryad_metadata() -> tuple[dict, list[dict]]:
    doi = urllib.parse.quote(DRYAD_DOI, safe="")
    api = "https://datadryad.org/api/v2"
    dataset_url = f"{api}/datasets/{doi}"
    out: dict = {"doi": DRYAD_DOI, "dataset_api": dataset_url,
                 "dataset_status": "not_checked", "files_status": "not_checked"}
    try:
        dataset = request_json(dataset_url)
        out["dataset_status"] = "ok"
        out["title"] = dataset.get("title")
        out["storage_size_metadata"] = dataset.get("storageSize")
        out["dataset_id"] = dataset.get("id")
        out["license"] = dataset.get("license")
        out["metadata_keys"] = sorted(dataset.keys())
    except Exception as e:
        out["dataset_status"] = "failed"
        out["dataset_error"] = source_error(e)
        return out, []

    versions_url = dataset_url + "/versions"
    try:
        versions_json = request_json(versions_url)
        out["versions_status"] = "ok"
        out["version_ids_from_metadata"] = public_version_ids(dataset) + [
            x for x in public_version_ids(versions_json) if x not in public_version_ids(dataset)]
    except Exception as e:
        out["versions_status"] = "failed"
        out["versions_error"] = source_error(e)
        versions_json = {}

    # Prefer _links to most recent version given directly by API dataset.
    candidate_ids = public_version_ids(dataset)
    if not candidate_ids:
        candidate_ids = public_version_ids(versions_json)
    candidate_ids = sorted(set(candidate_ids), reverse=True)
    out["candidate_version_ids"] = candidate_ids[:30]
    if not candidate_ids:
        out["files_status"] = "no_version_id"
        return out, []
    # This is source-admission, not forecasting. Probe first two version ids to
    # expose ambiguities instead of silently mixing versions.
    files = []
    for version_id in candidate_ids[:2]:
        file_url = f"{api}/versions/{version_id}/files"
        try:
            files_json = request_json(file_url)
        except Exception as e:
            out.setdefault("file_listing_errors", []).append({
                "version_id": version_id, "reason": source_error(e)})
            continue
        out["selected_version_id"] = version_id
        out["file_listing_api"] = file_url
        out["file_listing_top_keys"] = sorted(files_json.keys())
        for rec in nested_objects(files_json,
                lambda d: any(isinstance(d.get(k), str) and
                              d[k].endswith(".csv") for k in ("path","name","fileName"))):
            name = rec.get("path") or rec.get("name") or rec.get("fileName")
            fid = rec.get("id")
            if not isinstance(fid, int):
                for maybe in (rec.get("_links"), rec.get("links")):
                    if isinstance(maybe, dict):
                        s = json.dumps(maybe)
                        m = re.search(r"/api/v2/files/(\d+)", s)
                        if m:
                            fid = int(m.group(1))
                            break
            files.append({"name": str(name), "id": fid, "size": rec.get("size"),
                         "digest": rec.get("digest"), "digestType": rec.get("digestType"),
                         "version_id": version_id})
        if files:
            break
    out["files_status"] = "ok" if files else "not_parsed_or_missing"
    out["listed_files"] = files[:30]
    return out, files


def zenodo_metadata() -> dict:
    url = f"https://zenodo.org/api/records/{ZENODO_ID}"
    out = {"record_id_requested": ZENODO_ID, "api": url, "status": "not_checked"}
    try:
        record = request_json(url)
        out["status"] = "ok"
        out["record_id"] = record.get("id")
        out["doi"] = record.get("doi")
        out["published"] = record.get("created")
        out["title"] = (record.get("metadata") or {}).get("title", None)
        out["license"] = (record.get("metadata") or {}).get("license")
        access = (record.get("access") or {})
        out["access"] = {"record": access.get("record"), "files": access.get("files")}
        file_list = record.get("files") or []
        if isinstance(file_list, dict):
            file_list = file_list.get("entries", {})
            file_list = list(file_list.values()) if isinstance(file_list, dict) else []
        out["files"] = [
            {"name": f.get("key") or f.get("filename"),
             "size": f.get("size"),
             "checksum": f.get("checksum"),
             "access": f.get("access"),
             "download_url": (f.get("links") or {}).get("content") or
                             (f.get("links") or {}).get("self")}
            for f in file_list if isinstance(f, dict)
        ]
    except Exception as e:
        out["status"] = "failed"
        out["reason"] = source_error(e)
    return out


def download_bounded(url: str, destination: Path, cap: int = MAX_RAW_BYTES) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    sha = hashlib.sha256()
    md5 = hashlib.md5()
    total = 0
    with urllib.request.urlopen(req, timeout=120) as stream:
        ct = stream.headers.get("Content-Type", "")
        size = stream.headers.get("Content-Length")
        if size and int(size) > cap:
            raise ValueError("File content length exceeds fixed cap")
        with destination.open("wb") as f:
            while True:
                piece = stream.read(1048576)
                if not piece:
                    break
                total += len(piece)
                if total > cap:
                    raise ValueError("Downloaded file exceeds fixed cap")
                f.write(piece)
                sha.update(piece)
                md5.update(piece)
        if total == 0:
            raise ValueError("Empty source file")
    return {"bytes": total, "sha256": sha.hexdigest(), "md5": md5.hexdigest(),
            "content_type": ct}


def compare_source_digest(metadata: dict, actual: dict) -> dict:
    digest = metadata.get("digest")
    dtype = str(metadata.get("digestType") or "").lower()
    if not digest:
        return {"reported": False, "match": None}
    d = str(digest).lower().strip()
    if ":" in d:
        prefix, hexval = d.split(":", 1)
        dtype = prefix.lower()
        d = hexval
    if dtype in ("sha256", "sha-256"):
        return {"reported": True, "algorithm": "sha256", "match": d == actual["sha256"]}
    if dtype == "md5":
        return {"reported": True, "algorithm": "md5", "match": d == actual["md5"]}
    return {"reported": True, "algorithm": dtype or "unknown",
            "match": None, "note": "Unrecognized digest; not verified"}


def profile_csv(path: Path) -> dict:
    """Stream profile, never return coordinates, exact IDs, or individual tracks."""
    with path.open("r", newline="", encoding="utf-8-sig", errors="strict") as f:
        rows = csv.DictReader(f)
        if rows.fieldnames is None:
            raise ValueError("No header")
        header = [x.strip() for x in rows.fieldnames]
        if len(header) != len(set(header)):
            raise ValueError("Duplicate names after header normalization")
        missing = sorted(set(NECESSARY) - set(header))
        if missing:
            return {"status": "missing_required_columns", "missing": missing,
                    "column_count": len(header), "columns": header}
        # Normalize leading/trailing spaces in header, not values.
        name_map = dict(zip(rows.fieldnames, header))
        n = 0
        missing_fields = collections.Counter()
        invalid_position = 0
        keys_seen = set()
        duplicate_keys = 0
        trials = {}
        clock_mult = collections.Counter()
        time_per_flight = collections.defaultdict(set)
        date_counts = collections.Counter()
        invalid_counter = 0
        layer_counts = collections.Counter()
        for raw in rows:
            row = {name_map.get(k,k): v for k,v in raw.items() if k is not None}
            n += 1
            if n > 3_000_000:
                raise ValueError("Refuse unbounded row count")
            for col in NECESSARY:
                if row.get(col) is None or not str(row.get(col)).strip() or row[col].strip().lower() in ("na","nan","null"):
                    missing_fields[col] += 1
            try:
                lat, lon = float(row["Latitude"]), float(row["Longitude"])
                if not (math.isfinite(lat) and math.isfinite(lon) and
                        -90 <= lat <= 90 and -180 <= lon <= 180):
                    invalid_position += 1
            except (ValueError, TypeError, KeyError):
                invalid_position += 1
            try:
                counter = int(float(row["Counter"]))
                if str(row["Counter"]).strip() not in (str(counter), str(float(counter))):
                    raise ValueError("Fractional counter")
                if counter <= 0:
                    raise ValueError("Nonpositive counter")
            except (ValueError, TypeError, OverflowError):
                invalid_counter += 1
                counter = None

            bird = row.get("Bird", "").strip()
            loft = row.get("Loft", "").strip()
            flight = row.get("Iteration", "").strip()
            day = row.get("Date", "").strip()
            key = (loft, flight, bird, day, counter)
            if key in keys_seen:
                duplicate_keys += 1
            keys_seen.add(key)
            trial = (loft, flight, bird, day)
            if trial not in trials:
                trials[trial] = [0, None, None, set()]
            info = trials[trial]
            info[0] += 1
            if counter is not None:
                info[1] = min(info[1],counter) if info[1] is not None else counter
                info[2] = max(info[2],counter) if info[2] is not None else counter
                info[3].add(counter)
            time = row.get("Time", "").strip()
            if time:
                clock_mult[(loft, flight, bird, day, time)] += 1
                time_per_flight[trial].add(time)
            date_counts[day] += 1
            layer_counts[row.get("Layer", "").strip()] += 1
        if n == 0:
            raise ValueError("Empty rows")
        bird_sessions = collections.defaultdict(set)
        gaps = []
        for (loft, flight, bird, day), (row_count, low, high, uniques) in trials.items():
            bird_sessions[(loft,bird)].add((flight,day))
            if low is not None:
                gaps.append((high-low+1)-len(uniques))
        clock_hist = collections.Counter(clock_mult.values())
        bflight = collections.Counter(len(x) for x in bird_sessions.values())
        reused = sum(1 for x in bird_sessions.values() if len(x) >= 3)
        return {
            "status": "structure_profiled_only_no_outcome_model",
            "rows": n, "column_count": len(header), "columns": header,
            "number_distinct_loft_birds": len(bird_sessions),
            "number_bird_flight_trials": len(trials),
            "birds_with_at_least_3_flights": reused,
            "bird_flight_count_histogram": dict(sorted(bflight.items())),
            "date_count": len(date_counts),
            "no_altitude": not any("alt" in s.lower() or "height" in s.lower() for s in header),
            "duplicate_composite_keys": duplicate_keys,
            "invalid_coordinates": invalid_position,
            "invalid_counters": invalid_counter,
            "estimated_within_trial_missing_counter_values": sum(max(0,x) for x in gaps),
            "missing_field_counts": dict(missing_fields),
            "time_string_multiplicity_histogram": dict(sorted(clock_hist.items())),
            "time_string_repetition_keys": sum(v for k,v in clock_hist.items() if k>1),
            "clock_synchronicity_assessed": False,
            "synchronous_social_steering_admitted": False,
            "exact_altitude_niche_admitted": False,
            "repeated_horizontal_candidate_admitted_for_next_protocol":
                reused >= 6 and invalid_position == 0 and duplicate_keys == 0 and invalid_counter == 0,
            "layer_counts": dict(sorted(layer_counts.items())),
            "notes": [
                "Flight counter may be relative to each bird's flight; it does not prove cross-bird alignment.",
                "Rounded UTC time strings cannot supply 0.2 second unique timestamps.",
                "No exact bird IDs or GPS coordinates are exported in this aggregate.",
                "Previous 3D niche / social-force wild-animal claims remain untested."
            ],
        }




def profile_zip_manifest(zip_path: Path) -> dict:
    """Structural ZIP inventory only; never parse/model animal coordinates."""
    with zipfile.ZipFile(zip_path,"r") as arc:
        members = arc.infolist()
        unsafe = [z.filename for z in members if
                  z.filename.startswith(("/", "\\")) or
                  ".." in Path(z.filename).parts]
        if unsafe:
            raise ValueError("Archive includes unsafe member paths")
        sizes = collections.Counter()
        types = collections.Counter()
        extension_sizes = collections.Counter()
        real_files = [z for z in members if not z.is_dir()]
        for z in real_files:
            ext = Path(z.filename).suffix.lower() or "none"
            types[ext] += 1
            extension_sizes[ext] += z.file_size
            sizes[str(Path(z.filename).parent).replace("/", " > ", 1)] += 1
        # No raw observation rows or image content: read only text documentation
        # by filename and strict size cap. Any schema excerpt is explanatory,
        # not an observed prediction endpoint.
        docs = []
        for member in real_files:
            name = Path(member.filename).name.lower()
            if name in ("readme.md", "data_description.md", "data_license.txt", "version.txt", "citation.txt") and member.file_size < 500_000:
                data = arc.read(member).decode("utf-8-sig", errors="replace")
                docs.append({"path": member.filename, "bytes": member.file_size,
                    "readme_excerpt": data[:25000]})
        return {"status":"zip_structural_manifest_only",
                "total_members":len(members),
                "regular_files":len(real_files),
                "total_uncompressed_bytes_reported":sum(z.file_size for z in real_files),
                "file_extensions":dict(sorted(types.items())),
                "extension_uncompressed_bytes":dict(sorted(extension_sizes.items())),
                "member_names": [z.filename for z in real_files[:250]],
                "truncated_names":len(real_files)>250,
                "readme_documents":docs,
                "observation_rows_processed":0,
                "forecast_scores_computed":0,
                "raw_files_redistributed":False}

def run(download_dryad: bool, download_zenodo: bool = False, raw_gps_qc: bool = False) -> dict:
    result = {"study":"boids-v14-independent-field-source-admission",
              "status":"DATA_PROVENANCE_AND_STRUCTURE_ONLY_NO_FORECAST",
              "zenodo": zenodo_metadata()}
    if download_zenodo:
        records = result["zenodo"].get("files", [])
        target = next((item for item in records if
                       item.get("name")=="pigeon_homing_public_trials_v1.0.0.zip"
                       and item.get("size")==126588691
                       and item.get("checksum")=="md5:5c1e9b386bff5794e177b122b1fcb244"
                       and isinstance(item.get("download_url"),str)),None)
        if target is None:
            result["zenodo_archive"]={"status":"blocked_unverified_record_metadata"}
        else:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    path=Path(tmp)/"zenodo_pigeon_raw.zip"
                    got=download_bounded(target["download_url"],path,cap=MAX_ZENODO_BYTES)
                    matched=(got["bytes"]==target["size"] and
                        got["md5"]==target["checksum"].split(":",1)[1])
                    result["zenodo_download"]={**got,"source_size_md5_matched":matched}
                    if not matched:
                        result["zenodo_archive"]={"status":"stop_checksum_mismatch"}
                    else:
                        result["zenodo_archive"]=profile_zip_manifest(path)
                        if raw_gps_qc:
                            from raw_nmea_qc import inspect_gps_archive
                            result["zenodo_raw_gps_qc"]=inspect_gps_archive(path)
            except Exception as e:
                result["zenodo_archive"]={"status":"download_or_manifest_failed",
                                           "reason":source_error(e)}
    dryad, files = dryad_metadata()
    result["dryad"] = dryad
    file_meta = next((f for f in files if
                      Path(f["name"]).name == CSV_NAME and isinstance(f["id"], int)), None)
    dryad["requested_csv_discovered"] = file_meta is not None
    if download_dryad and file_meta is not None:
        routes = (
            f"https://datadryad.org/api/v2/files/{file_meta['id']}/download",
            f"https://datadryad.org/downloads/file_stream/{file_meta['id']}",
            f"https://datadryad.org/stash/downloads/file_stream/{file_meta['id']}",
        )
        result["source_download_attempts"] = []
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/CSV_NAME
            for url in routes:
                try:
                    transfer = download_bounded(url,p)
                    result["source_download_attempts"].append({"url":url,"status":"received_bytes"})
                    result["raw_file_url"] = url
                    break
                except Exception as e:
                    result["source_download_attempts"].append(
                        {"url":url,"status":"unavailable","reason":source_error(e)})
            else:
                transfer = None
            if transfer is None:
                result["csv"] = {"status":"retrieval_or_profile_failed",
                                 "reason":"All official public download routes unavailable"}
            else:
                result["raw_file"] = transfer
                verify = compare_source_digest(file_meta,transfer)
                result["reported_digest_check"] = verify
                byte_match = transfer["bytes"] == file_meta["size"]
                result["reported_byte_count_match"] = byte_match
                if not byte_match or verify["match"] is not True:
                    result["csv"] = {"status":"stop_bytes_or_checksum_mismatch"}
                elif p.open("rb").read(4).startswith(b"PK\x03\x04"):
                    result["csv"] = {"status":"stop_zip_not_plain_csv"}
                else:
                    try:
                        result["csv"] = profile_csv(p)
                    except Exception as e:
                        result["csv"] = {"status":"structure_profile_failed",
                                         "reason":source_error(e)}
    else:
        result["csv"] = {"status": "not_downloaded_or_not_discovered"}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-dryad",action="store_true")
    parser.add_argument("--download-zenodo",action="store_true")
    parser.add_argument("--raw-gps-qc",action="store_true",
                        help="Source-only original NMEA and paired UTC observability audit")
    parser.add_argument("--out", type=Path,
          default=Path("validation_v14/results/source_preflight_v14.json"))
    args = parser.parse_args()
    if args.raw_gps_qc and not args.download_zenodo:
        parser.error("--raw-gps-qc requires --download-zenodo")
    result = run(args.download_dryad, args.download_zenodo, args.raw_gps_qc)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                   indent=2,default=str)+"\n")
    print("V14_SOURCE_GATE_NO_FORECAST")
    print("Zenodo:",json.dumps(result["zenodo"],sort_keys=True))
    print("Zenodo archive:",json.dumps(result.get("zenodo_archive",{}),sort_keys=True))
    print("Zenodo raw digest:",json.dumps(result.get("zenodo_download",{}),sort_keys=True))
    print("NMEA source observability:",json.dumps(result.get("zenodo_raw_gps_qc",{}),sort_keys=True))
    print("Dryad:",json.dumps(result["dryad"],sort_keys=True))
    print("Raw SHA256/size:",json.dumps(result.get("raw_file",{}),sort_keys=True))
    print("CSV quality:",json.dumps(result["csv"],sort_keys=True))
    print("RESULT_PATH:",args.out)


if __name__ == "__main__":
    main()
