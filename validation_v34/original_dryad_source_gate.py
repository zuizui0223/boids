#!/usr/bin/env python3
"""v34: original Dryad Chrotopterus raw/processed ZIPs, structure only."""
import argparse,csv,hashlib,io,json,urllib.request,urllib.error,zipfile
from collections import Counter
from pathlib import Path

FILES={"raw_original":5036052,"processed_interpolated":5036051}
DOI="10.5061/dryad.7d7wm38c0"
SITES={"hormiguero":"Hormiguero","okolhuitz":"Okolhuitz","corriental":"Corriental"}
OUT=Path("validation_v34/results/original_dryad_source_only_v34.json")

def signature(data):
    d=data[:1024].lstrip().lower()
    if d.startswith((b"<!doctype",b"<html",b"<?xml")):return "HTML_NOT_ZIP"
    if d.startswith((b"{",b"[")):return "JSON_NOT_ZIP"
    if data[:4]==b"PK\x03\x04":return "ZIP_HEADER"
    return "OTHER_NOT_ZIP"

def acquire(fid,fetcher=None):
    if fetcher is None:
        def fetcher(url):
            req=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (reproducibility source audit)",
                "Accept":"application/zip,application/octet-stream,*/*;q=0.2"})
            with urllib.request.urlopen(req,timeout=20) as response:
                return response.status,response.headers.get("content-type",""),response.read(8000001)
    attempts=[]
    for url in (f"https://datadryad.org/downloads/file_stream/{fid}",
                f"https://datadryad.org/api/v2/files/{fid}/download"):
        try:
            status,mime,data=fetcher(url)
            typ=signature(data)
            attempts.append({"http":status,"mime":str(mime)[:80],"type":typ,"received_bytes":len(data)})
            if status==200 and len(data)<=8000000 and typ=="ZIP_HEADER" and zipfile.is_zipfile(io.BytesIO(data)):
                return {"status":"ORIGINAL_ZIP_ACQUIRED","sha256":hashlib.sha256(data).hexdigest(),
                        "bytes":len(data),"attempts":attempts,"data":data}
        except urllib.error.HTTPError as exc:attempts.append({"http":exc.code,"type":"HTTP_ACCESS_STOP"})
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            attempts.append({"http":None,"type":"TRANSPORT_STOP","exception":type(exc).__name__})
    return {"status":"ORIGINAL_ZIP_ACCESS_STOP","attempts":attempts}

def inspect_zip(data,kind):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        info=[i for i in z.infolist() if not i.is_dir()]
        if sum(i.file_size for i in info)>30000000:
            return {"status":"UNZIPPED_SIZE_CAP_STOP","members":len(info)}
        total_rows=0;csv_n=0
        sites=Counter();colnames=Counter();status=Counter()
        schema_raw=0;schema_processed=0
        ext=Counter()
        for item in info:
            ext[Path(item.filename).suffix.lower()]+=1
            if Path(item.filename).suffix.lower() not in (".csv",".tsv",".txt"):continue
            try:s=z.read(item).decode("utf-8-sig")
            except UnicodeDecodeError:s=z.read(item).decode("latin-1")
            lines=s.splitlines()
            if not lines:continue
            first=lines[0];sep=max((";",",","\t"),key=first.count)
            reader=csv.DictReader(io.StringIO(s),delimiter=sep)
            cols=reader.fieldnames or []
            if len(cols)<3:continue
            csv_n+=1;colnames.update(cols)
            site=[v for k,v in SITES.items() if k in item.filename.casefold()]
            if len(site)==1:sites[site[0]]+=1
            else:status["csv_without_one_site_token"]+=1
            schema_raw+=int({"ID","timestamp","lat","long"}.issubset(cols))
            schema_processed+=int({"sensor","timestamps","coords.x1","coords.x2"}.issubset(cols))
            # Count rows without inspecting numeric movement fields.
            count=sum(1 for _ in reader)
            total_rows+=count
        return {"status":"STRUCTURE_CHECKED","archive":kind,"members":len(info),
                "entry_extension_counts":dict(ext),"csv_file_count":csv_n,
                "source_row_count":total_rows,"original_fix_schema_csv_count":schema_raw,
                "processed_interpolation_schema_csv_count":schema_processed,
                "site_tokens_in_original_filenames":dict(sites),
                "csv_unknown_site_count":status["csv_without_one_site_token"],
                "source_column_names":sorted(colnames),
                "numeric_movement_coordinate_or_HMM_values_interpreted":False}

def run(fetcher=None):
    report={"doi":DOI,"pre_outcome_source_only":True,"source_animal_movement_outcomes_opened":False,
            "original_bat_identity_and_site_independence_verified":False,"sources":{}}
    for kind,fid in FILES.items():
        r=acquire(fid,fetcher)
        out={k:v for k,v in r.items() if k!="data"}
        out["official_dryad_file_id"]=fid
        if r["status"]=="ORIGINAL_ZIP_ACQUIRED":out.update(inspect_zip(r["data"],kind))
        report["sources"][kind]=out
    raw=report["sources"]["raw_original"];proc=report["sources"]["processed_interpolated"]
    if raw["status"]!="STRUCTURE_CHECKED" or proc["status"]!="STRUCTURE_CHECKED":
        report["admission"]="SOURCE_ACCESS_OR_STRUCTURE_STOP"
    else:
        checks={
            "original_GPS_rows_at_least_2000":raw["source_row_count"]>=2000,
            "original_fix_schema_confirmed":raw["original_fix_schema_csv_count"]>0,
            "processed_interpolation_flag_schema_confirmed":proc["processed_interpolation_schema_csv_count"]>0,
            "three_named_sites_in_original_file_names":len(raw["site_tokens_in_original_filenames"])==3,
            "at_least_20_original_CSV_tracks":raw["csv_file_count"]>=20}
        report["fixed_structural_checks"]=checks
        report["admission"]="SCHEMA_READY_NEEDS_BAT_ID_MAPPING" if all(checks.values()) else "SOURCE_SUPPORT_STOP"
    report["source_animal_movement_outcomes_opened"]=False
    report["behavior_model_fitted"]=False
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);args=p.parse_args()
    d=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V34_CHROTOPTERUS_SOURCE="+json.dumps({
        "admission":d["admission"],
        "sources":{k:{x:v.get(x) for x in ("status","bytes","sha256","source_row_count","csv_file_count","attempts")}
                   for k,v in d["sources"].items()},
        "checks":d.get("fixed_structural_checks")},sort_keys=True))
    assert d["source_animal_movement_outcomes_opened"] is False
    assert d["behavior_model_fitted"] is False
