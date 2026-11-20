"""v6 source-only check of genuine Mouy XAV original fish audio-video localization tables.
Sources: published OSF q8dz4, six individually inventoried result CSV identities.
NO original sound coordinates or event times written to results/repository.
"""
from __future__ import annotations
import csv, hashlib, io, json, re
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

SOURCE="https://osf.io/q8dz4"
FILE_IDS={
 "6335fcfa31d65303352de2bc":"large OGD",
 "6335fd860db48e0365e127a5":"mini",
 "6335fdb30db48e0364e11e09":"mobile A",
 "6335fdd331d65303352de44a":"mobile B",
 "6335fdf4ec7f3f0332f61087":"mobile C",
 "6335fd3aec7f3f0337f5f9a4":"large HI"
}
MAX_CSV=60_000
class SourceStop(Exception):pass

def json_get(url):
    if not url.startswith("https://api.osf.io/v2/files/"):
        raise SourceStop("INVALID_OSF_API_ENDPOINT")
    try:
        req=request.Request(url,headers={"Accept":"application/json",
             "User-Agent":"boids-acoustic-joint-source-gate/1.0"})
        with request.urlopen(req,timeout=35) as response:
            b=response.read(600_001)
        if len(b)>600_000:raise SourceStop("LARGE_METADATA_JSON")
        return json.loads(b)
    except error.HTTPError as e:raise SourceStop("OSF_METADATA_HTTP_"+str(e.code)) from None
    except error.URLError as e:raise SourceStop("OSF_METADATA_NETWORK_"+type(e.reason).__name__) from None
def download(url):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in ("osf.io","files.osf.io"):
        raise SourceStop("OSF_SOURCE_DOWNLOAD_URL_STOP")
    try:
        req=request.Request(url,headers={"User-Agent":"boids-acoustic-joint-source-gate/1.0"})
        with request.urlopen(req,timeout=45) as response:
            b=response.read(MAX_CSV+1)
        if len(b)>MAX_CSV:raise SourceStop("ORIGINAL_CSV_CAP_STOP")
        return b
    except error.HTTPError as e:raise SourceStop("OSF_CSV_HTTP_"+str(e.code)) from None
    except error.URLError as e:raise SourceStop("OSF_CSV_NETWORK_"+type(e.reason).__name__) from None

def source_structure(data):
    try:
        text=data.decode("utf-8-sig")
        rows=list(csv.reader(io.StringIO(text)))
    except (UnicodeError,csv.Error):
        raise SourceStop("ORIGINAL_CSV_FORMAT_STOP") from None
    if not rows or len(rows[0])<2:raise SourceStop("ORIGINAL_CSV_EMPTY_OR_NARROW")
    columns=[str(x).strip() for x in rows[0]]
    coltext="|".join(columns).lower()
    # Source gate only: a localization event label is NOT a tracked fish identity.
    has_time=bool(re.search(r"time|date|timestamp|utc",coltext))
    has_xy=bool(re.search(r"(^|\\W)(x|x_pos|position_x|easting)(\\W|$)",coltext)
                and re.search(r"(^|\\W)(y|y_pos|position_y|northing)(\\W|$)",coltext))
    has_individual=bool(re.search(r"fish_id|individual_id|animal_id|track_id|fish_track",coltext))
    return {"n_csv_rows_excluding_header":len(rows)-1,"columns":columns,
            "has_time_column_name":has_time,
            "has_xy_column_names":has_xy,
            "has_explicit_individual_track_identifier_column":has_individual,
            "joint_fish_movement_from_this_csv":"NOT_ADMITTED" if not(has_time and has_xy and has_individual) else "SCHEMA_ONLY_POTENTIALLY_ADMISSIBLE"}

def check_one(fid,name):
    doc=json_get(f"https://api.osf.io/v2/files/{fid}/")
    item=doc.get("data",{})
    a=item.get("attributes",{}) or {}
    file_name=a.get("name")
    size=a.get("size")
    link=item.get("links",{}).get("download")
    if not file_name or str(file_name)!="localization_results.csv":
        raise SourceStop("EXPECTED_PUBLISHED_LOCALIZATION_CSV_MISSING")
    if size is None or int(size)<=0 or int(size)>MAX_CSV:
        raise SourceStop("PUBLISHED_OSF_FILE_SIZE_STOP")
    if not link:raise SourceStop("OSF_DOWNLOAD_LINK_MISSING")
    b=download(link)
    if len(b)!=int(size):raise SourceStop("OSF_SOURCE_BYTES_MISMATCH")
    hashes=(a.get("extra") or {}).get("hashes") or {}
    if isinstance(hashes,dict):
        for algorithm in ("md5","sha256"):
            original=hashes.get(algorithm)
            if original and hashlib.new(algorithm,b).hexdigest()!=str(original).lower():
                raise SourceStop("OSF_ORIGINAL_HASH_MISMATCH")
    parsed=source_structure(b)
    return {"osf_file_id":fid,"array_label":name,"original_nbytes":len(b),
            "original_sha256":hashlib.sha256(b).hexdigest(),
            "publisher_hash_check":"MATCHED_IF_PUBLISHED",
            **parsed}

def run():
    out={"version":"v6_osf_genuine_six_localization_csv_source_support",
         "source":SOURCE,"original_acoustic_event_values_published_in_result":False,
         "fish_positions_published_in_result":False,"records":[]}
    for fid,name in FILE_IDS.items():
        try:out["records"].append(check_one(fid,name))
        except (SourceStop,ValueError,KeyError) as e:
            out["records"].append({"osf_file_id":fid,"array_label":name,
                                   "status":"SOURCE_STOP","reason":str(e)})
    success=sum("n_csv_rows_excluding_header" in r for r in out["records"])
    track=sum(r.get("joint_fish_movement_from_this_csv")=="SCHEMA_ONLY_POTENTIALLY_ADMISSIBLE"
              for r in out["records"])
    out.update({"source_csv_success":success,
                "source_csv_stop":len(FILE_IDS)-success,
                "column_only_potential_joint_tracks":track,
                "scientific_status":"SOURCE_CATALOG_ONLY_NO_SIMULTANEOUS_FISH_SCHOOL_PROOF"})
    return out
def main():
    out=run()
    p=Path("validation_fish_audio_v6/results/xav_localization_csv_schema.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"source_csv_success":out["source_csv_success"],
                      "source_csv_stop":out["source_csv_stop"],
                      "column_only_potential_joint_tracks":out["column_only_potential_joint_tracks"],
                      "columns_by_array":[{"array":x["array_label"],"cols":x.get("columns"),
                         "stop":x.get("reason")} for x in out["records"]],
                      "status":out["scientific_status"]}))
if __name__=="__main__":main()
