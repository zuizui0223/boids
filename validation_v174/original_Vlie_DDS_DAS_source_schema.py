"""v174: real original OPeNDAP DDS/DAS schema of ten SOURCE-verified Vlieland tiles.

v173 proved 10 of 165 actual original bathymetry tiles overlap the fixed
coarse Vlieland RD New search box, and ALL ten have catalog timeCoverage
that spans 2016. This does NOT mean any actual 2016 surveyed height
exists at a tagged bird's foraging position.

Here only open the true provider's native OPeNDAP DDS/DAS schema to prove
whether altitude, source/time and NAP vertical CRS metadata are AVAILABLE.
Never download z grids or bird GPS, never claim valid 2016 survey pixels
before inspecting the original time coordinates and source masks.
"""
from __future__ import annotations
import argparse,hashlib,json,re,time,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json"
OUT=ROOT/"validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
EXPECTED_INDEX_SHA="b4364e1d18ea3098ccef8fcbd9a9f3506e98264748c0fe9ce80697a9cb9a2193"
N_TILE=10
SUFFIXES=(".dds",".das")
MAX_RESPONSE=900_000
MAX_WORKERS=3
SOURCE_TIMEOUT=32
KEYWORDS=("altitude","time","isource","source","x","y","NAP","EPSG",
          "geospatial_vertical_datum","crs","units","projection",
          "time_coverage","fillvalue")

def request_original_schema(uri):
    req=urllib.request.Request(uri,headers={
        "User-Agent":"BoidsOriginalSourceAudit/1.0 Rijkswaterstaat-Deltares (noncommercial)",
        "Accept":"text/plain,application/octet-stream,*/*"
    })
    with urllib.request.urlopen(req,timeout=SOURCE_TIMEOUT) as f:
        raw=f.read(MAX_RESPONSE+1)
        resolved=f.geturl()
        content_type=f.headers.get("Content-Type","")
    if not 100<len(raw)<=MAX_RESPONSE:
        raise ValueError("Empty/oversize original OPeNDAP source metadata")
    text=raw.decode("utf-8","replace")
    if uri.endswith(".dds"):
        if not re.search(r"^\s*Dataset\s*\{",text,re.I):
            raise ValueError("Server returned non-DDS content")
    elif uri.endswith(".das"):
        if not re.search(r"^\s*Attributes\s*\{",text,re.I):
            raise ValueError("Server returned non-DAS content")
    return text,{
        "source_uri_requested":uri,
        "source_uri_resolved":resolved,
        "source_metadata_content_SHA256":hashlib.sha256(raw).hexdigest(),
        "source_response_bytes":len(raw),
        "source_content_type":content_type,
    }

def source_inspect_dds(txt):
    # Native OPeNDAP DAP2 DDS declares source variables and dimensions.
    decl=re.findall(
        r"(?mi)^\s*(?:Byte|Int16|UInt16|Int32|UInt32|Int64|UInt64|Float32|Float64|String)\s+([A-Za-z_]\w*)\s*(\[[^\n;]{1,300}\])?\s*;",
        txt
    )
    names=sorted(set(n for n,d in decl))
    # These are provider-declared time-grid dimensions only, NOT valid
    # bird-time historical elevation samples.
    time_dims=re.findall(r"(?i)\[\s*time\s*=\s*(\d+)\s*\]",txt)
    return {
        "source_declared_primitive_names":names,
        "source_primitive_declaration_n":len(decl),
        "native_time_dimension_lengths":sorted(set(int(x) for x in time_dims)),
        "source_DDS_has_real_altitude_variable":"altitude" in names,
        "source_DDS_has_real_time_variable":"time" in names,
        "source_DDS_has_real_isource_variable":"isource" in names,
        "no_elevation_values_loaded_from_provider":True,
    }

def source_inspect_das(txt):
    hits={k:len(re.findall(re.escape(k),txt,re.I)) for k in KEYWORDS}
    # Original metadata fragments only, capped to prevent re-publishing
    # large provider metadata. No actual grid values or bird observations.
    relevant=[]
    for line in txt.splitlines():
        if any(re.search(r"\b"+re.escape(k)+r"\b",line,re.I)
               for k in ("NAP","EPSG","vertical_datum","time_coverage","units","source")):
            if len(relevant)>=35:break
            relevant.append(line.strip()[:180])
    return {
        "source_DAS_metadata_keyword_line_hits":hits,
        "source_DAS_limited_public_original_metadata_lines":relevant,
        "original_pixel_survey_year":"NOT_VERIFIED_BY_DAS_ONLY",
        "elevation_vertical_NAP_datum":"NOT_VERIFIED_BY_DAS_ONLY",
    }

def per_tile(source):
    url=source["source_original_native_tile_url"]
    if not url.startswith("http://opendap.deltares.nl/") and not url.startswith("https://opendap.deltares.nl/"):
        raise AssertionError("Untrusted tile URL not in original domain")
    official=url.replace("http://","https://",1)
    record={
        "tile":source["source_tile_basename"],
        "original_catalog_xy_bbox_m":source["original_projected_xy_RD_NAP_search_bbox_m"],
        "original_catalog_time_coverage":[source["original_catalog_timeCoverage_start"],source["original_catalog_timeCoverage_end"]],
        "source_catalog_2016_in_TIME_RANGE_ONLY":source["calendar_year_in_tile_timeCoverage_RANGE_only"]["2016"],
    }
    for suffix in SUFFIXES:
        k=suffix[1:]
        try:
            txt,meta=request_original_schema(official+suffix)
            audit=source_inspect_dds(txt) if k=="dds" else source_inspect_das(txt)
            record[k]={"status":"AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA",
                       "original_provider_provenance":meta,
                       "original_source_schema":audit}
        except Exception as e:
            record[k]={"status":"SOURCE_STOP_OPENDAP_NOT_READABLE",
                       "error_class":type(e).__name__,
                       "error_excerpt":str(e)[:240]}
    if record["dds"]["status"]=="AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA" and record["das"]["status"]=="AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA":
        record["survey_source_admission"]="SCHEMA_AVAILABLE_BUT_NO_VALID_2016_Z_YET"
    else:
        record["survey_source_admission"]="SOURCE_STOP_SOURCE_SCHEMA_NOT_COMPLETE"
    return record

def run():
    previous=json.loads(PRIOR.read_text())
    if (previous["genuine_original_deltares_catalog_sha256"]!=EXPECTED_INDEX_SHA or
        previous["n_original_tiles_whose_xy_bbox_intersects_coarse_Vlieland_box"]!=N_TILE):
        raise AssertionError("Original v173 actual ten-tile geography source changed")
    tiles=previous["all_original_intersecting_native_tile_source_metadata"]
    if len(tiles)!=N_TILE or len({t["source_tile_basename"] for t in tiles})!=N_TILE:
        raise AssertionError("Original source has not exactly ten unique Vlieland candidates")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future={pool.submit(per_tile,x):x["source_tile_basename"] for x in tiles}
        rows=[f.result() for f in as_completed(future)]
    rows.sort(key=lambda x:x["tile"])
    count=sum(x["survey_source_admission"]=="SCHEMA_AVAILABLE_BUT_NO_VALID_2016_Z_YET" for x in rows)
    return {
        "version":"v174_real_ten_Vlieland_historical_OPeNDAP_DDS_DAS_schema_1",
        "source_v173_original_catalog_index_SHA":EXPECTED_INDEX_SHA,
        "n_real_original_candidate_tiles":N_TILE,
        "original_tiles_with_both_authentic_DDS_DAS_schemas":count,
        "all_original_tile_source_schema_or_STOP":rows,
        "actual_2016_survey_pixel_by_bird_GPS":"NOT_ESTIMATED",
        "RWS_harbor_height_vs_local_Vlieland_elevation_datum":"NOT_VERIFIED",
        "no_original_remote_bathymetry_rasters_or_bird_GPS_published":True,
        "no_tide_by_solar_causal_or_social_Boids_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    a=p.parse_args()
    r=run();OUT.parent.mkdir(parents=True,exist_ok=True)
    if a.check:
        if not OUT.exists():raise AssertionError("No frozen original v174 source schema receipt")
        old=json.loads(OUT.read_text())
        if old!=r:raise AssertionError("Original provider OPeNDAP DDS/DAS source schema/digests changed")
        print("V174_REAL_TEN_VLIE_ORIGINAL_TILE_DDS_DAS_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V174_TILE_SOURCE_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V174_TILE_SOURCE_END")
    print("V174_TILE_SOURCE_SUMMARY="+json.dumps({
        "n_total":r["n_real_original_candidate_tiles"],
        "n_both_source_schemas":r["original_tiles_with_both_authentic_DDS_DAS_schemas"],
        "tiles":[{
            "tile":x["tile"],"dds":x["dds"]["status"],
            "das":x["das"]["status"],
            "survey_status":x["survey_source_admission"],
            "native_dims":x["dds"].get("original_source_schema",{}).get("native_time_dimension_lengths"),
            "original_vars":x["dds"].get("original_source_schema",{}).get("source_declared_primitive_names")
        } for x in r["all_original_tile_source_schema_or_STOP"]]
    },sort_keys=True))
if __name__=="__main__":
    main()
