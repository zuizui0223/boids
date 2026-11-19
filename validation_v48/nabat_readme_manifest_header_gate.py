#!/usr/bin/env python3
"""v48 USGS 2026 NABat official README + bounded original CSV manifest HEADERS ONLY."""
import argparse,csv,hashlib,io,json,re,urllib.error,urllib.parse,urllib.request
from collections import Counter
from pathlib import Path

from nabat_usgs_item_source_gate import ITEM_ID,DOI,URLS

OUT=Path("validation_v48/results/nabat_readme_manifest_source_v48.json")
CAP_ITEM=1_000_000
CAP_README=1_000_000
CAP_HEADER=16384
ALLOWED_HOSTS={"www.sciencebase.gov","sciencebase.usgs.gov","www.sciencebase.usgs.gov","www.usgs.gov"}
WORDS=("effort","detector","survey","site","start","end","recording","acoustic",
       "label","taxonomy","metadata","overlap","privacy","quality","validation",
       "species","project","manual","date","time","status","duration","hours")


def read_public(url,cap,method_range=None):
    headers={"Accept":"text/plain,text/csv,application/json,application/octet-stream,*/*;q=0.5",
             "User-Agent":"boids-v48-nabat-official-source-schema/1.0"}
    if method_range is not None:
        headers["Range"]=f"bytes=0-{method_range-1}"
        headers["Accept-Encoding"]="identity"
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=28) as r:
        return r.status,r.headers.get("Content-Type",""),r.headers.get("Content-Range",""),r.read(cap+1),r.geturl()


def source_uri(f):
    u=f.get("downloadUri") or f.get("url") or f.get("downloadUrl")
    if not isinstance(u,str) or not u.startswith("https://"):
        return None
    parsed=urllib.parse.urlparse(u)
    return u if parsed.hostname in ALLOWED_HOSTS else None


def source_field_names(header):
    try:
        data=header.decode("utf-8-sig")
    except UnicodeDecodeError:
        data=header.decode("latin-1")
    if "\n" not in data:return {"status":"CSV_FIRST_ROW_INCOMPLETE_STOP"}
    first=data.splitlines()[0]
    delim=max((",", ";", "\t"),key=first.count)
    cols=[c.strip() for c in next(csv.reader([first],delimiter=delim))]
    if len(cols)<2:return {"status":"CSV_HEADER_TOO_SHORT_STOP"}
    labels=[]
    for name in cols[:180]:
        if len(name)>90 or not re.fullmatch(r"[A-Za-z0-9_ .()/%:-]+",name):
            labels.append("SANITIZED_OR_UNUSUAL");continue
        labels.append(name)
    topics=Counter(w for c in cols for w in WORDS if w in c.casefold())
    return {"status":"SOURCE_FIRST_LINE_HEADERS_ONLY",
            "header_field_count":len(cols),
            "sanitized_generic_field_names":labels,
            "semantic_field_category_counts":dict(topics),
            "original_record_values_opened":False}


def audit(reader=read_public):
    report={
        "programme":"v48_USGS_NABat_original_README_and_CSV_manifest_source",
        "official_doi":DOI,"sciencebase_item_id":ITEM_ID,
        "previous_v46_USFWS_negative_primary_unchanged":True,
        "USFWS_2010_2018_record_overlap_unresolved":True,
        "true_zero_detector_nights_or_effort_denominators_verified":False,
        "animal_audio_or_numeric_species_values_read":False,
        "bat_behavior_prediction_fitted":False,
    }
    item=None
    for url in URLS:
        try:
            status,ctype,cr,raw,final=reader(url,CAP_ITEM)
            if status!=200 or len(raw)>CAP_ITEM:
                continue
            d=json.loads(raw)
            if isinstance(d,dict) and str(d.get("id"))==ITEM_ID:
                item=d;break
        except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError,
                ValueError,json.JSONDecodeError):
            continue
    if item is None:
        report["status"]="OFFICIAL_ITEM_JSON_SOURCE_ACCESS_STOP";return report
    candidates=[x for x in item.get("files",[]) if isinstance(x,dict)]
    readmes=[x for x in candidates if str(x.get("name","")).lower().endswith("readme.md")]
    manifests=[x for x in candidates if str(x.get("name","")).lower().endswith(".csv")
               and "manifest" in str(x.get("name","")).lower()]
    report["source_candidate_counts"]={"readme":len(readmes),"CSV_manifest":len(manifests),
                                       "original_files":len(candidates)}
    if len(readmes)!=1 or not 1<=len(manifests)<=2:
        report["status"]="SOURCE_README_OR_MANIFEST_SELECTION_STOP";return report
    chosen=[("readme",readmes[0])]+[(f"manifest_{i+1}",x) for i,x in enumerate(manifests)]
    reports={}
    for key,entry in chosen:
        original_name=str(entry.get("name",""))
        size=entry.get("size")
        if size is None:size=entry.get("sizeInBytes")
        try:size=int(size)
        except (ValueError,TypeError):size=None
        url=source_uri(entry)
        ret={"source_category":key,"declared_provider_file_size":size,
             "provider_downloadURL_origin_permitted":bool(url)}
        if not url:
            ret["status"]="PUBLISHED_URL_OUTSIDE_OFFICIAL_SOURCE_STOP"
            reports[key]=ret;continue
        if key=="readme" and (size is None or size>CAP_README):
            ret["status"]="READ_ME_PROVIDER_SIZE_CAP_STOP";reports[key]=ret;continue
        n=None if key=="readme" else min(size or CAP_HEADER,CAP_HEADER)
        cap=CAP_README if key=="readme" else n
        try:
            status,ctype,cr,body,final=reader(url,cap,method_range=n)
            ret.update({"http":status,"reported_content_type":str(ctype)[:80],
                        "received_bytes_capped":len(body)})
            if key=="readme":
                valid=(status==200 and len(body)<=CAP_README)
                if not valid:
                    ret["status"]="README_ACCESS_OR_SIZE_STOP"
                else:
                    try:text=body.decode("utf-8-sig")
                    except UnicodeDecodeError:text=body.decode("latin-1")
                    lower=text.casefold()
                    ret["source_readme_sha256"]=hashlib.sha256(body).hexdigest()
                    ret["source_readme_line_count"]=len(text.splitlines())
                    ret["documentation_category_presence"]={w:(w in lower) for w in WORDS}
                    ret["status"]="README_DOCUMENTATION_CATEGORIES_ONLY"
            else:
                m=re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)",str(cr).strip())
                if not(status==206 and m and int(m[1])==0 and
                       int(m[2])>=n-1 and len(body)>=n and
                       (size is None or int(m[3])==size)):
                    ret["status"]="MANIFEST_RANGE_UNVERIFIED_STOP"
                else:
                    prefix=body[:n]
                    ret["original_source_header_prefix_sha256"]=hashlib.sha256(prefix).hexdigest()
                    ret["manifest_header"]=source_field_names(prefix)
                    ret["status"]=ret["manifest_header"]["status"]
        except urllib.error.HTTPError as e:
            ret.update({"status":"SOURCE_HTTP_ACCESS_STOP","http":e.code})
        except (urllib.error.URLError,OSError,TimeoutError) as e:
            ret.update({"status":"SOURCE_TRANSPORT_STOP","error_type":type(e).__name__})
        reports[key]=ret
    report["source_file_schema_receipts"]=reports
    report["status"]=(
        "README_AND_MANIFEST_HEADERS_SOURCE_ONLY"
        if all(x["status"] in ("README_DOCUMENTATION_CATEGORIES_ONLY","SOURCE_FIRST_LINE_HEADERS_ONLY")
               for x in reports.values())
        else "README_OR_MANIFEST_SOURCE_FILE_ACCESS_STOP")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    result=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V48_NABAT_README_MANIFEST_HEADER_ONLY="+json.dumps(result,sort_keys=True))
    assert result["animal_audio_or_numeric_species_values_read"] is False
    assert result["true_zero_detector_nights_or_effort_denominators_verified"] is False
    assert result["bat_behavior_prediction_fitted"] is False
