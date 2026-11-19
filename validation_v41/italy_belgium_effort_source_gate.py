#!/usr/bin/env python3
"""v41 original Italy/Belgium bat acoustic file/time/effort source-only gate.

Read original location/date/time/file identifiers, NEVER numeric bat activity,
species effects, insect counts, forest values, coordinates or raw site names
into output. Missing recording windows must not be called zero detections.
"""
import argparse,csv,hashlib,io,json,statistics,urllib.parse,urllib.request,urllib.error
from collections import Counter,defaultdict
from pathlib import Path

FILES={
"italy":("21808015","Databats_Cansiglio.csv","76b954fd896ad182aa5a9b97516b6535"),
"belgium_activity":("20137204","Obs.AudioMoths-bats_activity.csv","d0588f30bf4ed86a168c5438373e6019"),
"belgium_metadata":("20137204","metadata_loc.csv","9672cb0e7dec4d0811540458375229b1"),
}
SCHEMA={
"italy":("SITE","DATE","TIME-12","FILES","TREATMENT"),
"belgium_activity":("Loc","Date","Time","Filename","Filepath","Group"),
"belgium_metadata":("Loc","Datum_audio"),
}
OUT=Path("validation_v41/results/italy_belgium_audio_effort_v41.json")

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"boids-original-audio-effort-audit/1.0"})
    with urllib.request.urlopen(req,timeout=35) as r:
        return r.status,r.headers.get("Content-Type",""),r.read(10000001)

def get(study,fn=fetch):
    rec,name,md5=FILES[study]
    url=f"https://zenodo.org/records/{rec}/files/{urllib.parse.quote(name)}?download=1"
    try:
        status,mime,data=fn(url)
    except urllib.error.HTTPError as e:return {"status":"HTTP_ACCESS_STOP","http":e.code},None
    except (urllib.error.URLError,OSError,TimeoutError) as e:
        return {"status":"TRANSPORT_STOP","error":type(e).__name__},None
    receipt={"file":name,"zenodo_record":rec,"http":status,"mime":str(mime)[:100],
             "bytes":len(data),"published_md5":md5}
    if status!=200 or len(data)>10000000 or data.lstrip().lower().startswith((b"<html",b"<!doctype",b"{")):
        receipt["status"]="INVALID_ORIGINAL_DATA_STOP";return receipt,None
    receipt["computed_md5"]=hashlib.md5(data).hexdigest()
    receipt["computed_sha256"]=hashlib.sha256(data).hexdigest()
    if receipt["computed_md5"]!=md5:
        receipt["status"]="SOURCE_MD5_MISMATCH_STOP";return receipt,None
    try: text=data.decode("utf-8-sig")
    except UnicodeDecodeError:text=data.decode("latin-1")
    delim=max((";",",","\t"),key=text.splitlines()[0].count)
    reader=csv.DictReader(io.StringIO(text),delimiter=delim)
    cols=[x.strip() for x in reader.fieldnames or []]
    receipt["original_headers"]=cols
    missing=set(SCHEMA[study])-set(cols)
    if missing:
        receipt["status"]="SOURCE_SCHEMA_STOP"
        receipt["missing_structural_fields"]=sorted(missing)
        return receipt,None
    # Read ONLY structural site/date/recording metadata.
    rows=[{k:str(r.get(k) or "").strip() for k in SCHEMA[study]} for r in reader]
    receipt["status"]="PUBLISHED_ORIGINAL_MD5_AND_SCHEMA_VERIFIED"
    return receipt,rows

def aggregate(count):
    n=list(count.values())
    return {"distinct_keys":len(n),
            "min_records":min(n) if n else 0,
            "median_records":float(statistics.median(n)) if n else 0,
            "max_records":max(n) if n else 0}

def source_units(rows,study):
    site,date,time,file,mode=(("SITE","DATE","TIME-12","FILES","TREATMENT") if study=="italy"
                                else ("Loc","Date","Time","Filename","Group"))
    s={r[site] for r in rows if r[site]}
    d={r[date] for r in rows if r[date]}
    m={r[mode] for r in rows if r[mode]}
    sd=Counter((r[site],r[date]) for r in rows if r[site] and r[date])
    sdt=Counter((r[site],r[date],r[time]) for r in rows if r[site] and r[date] and r[time])
    sdf=Counter((r[site],r[date],r[file]) for r in rows if r[site] and r[date] and r[file])
    times=defaultdict(set)
    for r in rows:
        if r[site] and r[date] and r[time]:times[(r[site],r[date])].add(r[time])
    return {"source_detection_or_activity_rows":len(rows),
            "distinct_site_tokens":len(s),"distinct_date_tokens":len(d),
            "distinct_context_tokens":len(m),
            "site_date":aggregate(sd),"site_date_time":aggregate(sdt),
            "site_date_file":aggregate(sdf),
            "site_dates_with_multiple_recorded_time_tokens":sum(len(x)>=2 for x in times.values()),
            "rows_with_nonempty_recording_file_token":sum(bool(r[file]) for r in rows),
            "full_scheduled_zero_detection_windows_independently_verified":False,
            "numeric_bat_acoustic_or_prey_values_accessed":False}

def audit(fn=fetch):
    receipts={};source={}
    for k in FILES:
        rec,rows=get(k,fn)
        receipts[k]=rec
        if rows is None:
            return {"status":"SOURCE_ACCESS_OR_SCHEMA_STOP","source_receipts":receipts,
                    "bat_response_values_opened":False,"zero_detection_windows_inferred":False,
                    "cross_country_model_fitted":False}
        source[k]=rows
    a=source_units(source["italy"],"italy")
    b=source_units(source["belgium_activity"],"belgium")
    available={r["Loc"] for r in source["belgium_metadata"] if r["Loc"]}
    observed={r["Loc"] for r in source["belgium_activity"] if r["Loc"]}
    return {"status":"EFFORT_DENOMINATOR_NOT_VERIFIED_STOP",
            "source_receipts":receipts,
            "italy_source_structure":a,
            "belgium_source_structure":b,
            "belgium_site_match":{
                "source_plot_metadata_rows":len(source["belgium_metadata"]),
                "distinct_metadata_site_labels":len(available),
                "distinct_activity_site_labels":len(observed),
                "activity_site_labels_in_metadata":len(available&observed),
                "activity_site_labels_missing_from_metadata":len(observed-available),
                "source_site_names_or_coordinates_exported":False},
            "stop_reason":"Event/recording-token rows do not by themselves establish all scheduled no-detection windows and valid recording effort",
            "bat_response_values_opened":False,"zero_detection_windows_inferred":False,
            "cross_country_model_fitted":False,
            "original_v39_primary_positive_gate":"NOT_SUPPORTED",
            "v40_regional_covariate_support_diagnostic_only":True}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);arg=p.parse_args()
    d=audit();arg.out.parent.mkdir(parents=True,exist_ok=True)
    arg.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("V41_ITALY_BELGIUM_EFFORT="+json.dumps(d,sort_keys=True))
    assert not d["bat_response_values_opened"] and not d["zero_detection_windows_inferred"]
    assert not d["cross_country_model_fitted"]
