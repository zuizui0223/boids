"""v141 source-actual public multi-coast fish chorus data gateway.

Fetch only original Dryad API dataset/version/file endpoints; never infer file
content from metadata. Small sample originals are SHA-256-fingerprinted and
structure-inventoried. Preserve missingness and recording effort separately.
Original binary spreadsheet/music/audio is NOT committed.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, sys, zipfile
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parent
BASE="https://datadryad.org"
DATASETS={
 "california_sanctuaries": {
  "doi":"10.5061/dryad.q2bvq83sw",
  "target_names":["CI01_01_fish.xls","MB05_01_fish.xlsx","README.md"],
  "purpose":"Site deployment metadata and all-day detection intervals, not physical tide"
 },
 "japan_kashima":{
  "doi":"10.5061/dryad.zkh1893qn",
  "target_names":["q25_autoChorusDetect4.zip","ReadMe_for_data.txt","file_names2.csv"],
  "purpose":"Chorus-only acoustic segment vs independent tide/daylight data access"
 }
}
MAX_MB=3 * 1024 * 1024
HEADERS={"User-Agent":"Boids-OriginalDataIntegrity/1.0 (academic research; public Dryad API)",
         "Accept":"application/json, application/octet-stream, */*"}

def fetch(url, cap=MAX_MB):
    req=Request(url,headers=HEADERS)
    with urlopen(req,timeout=35) as response:
        chunks=[];seen=0
        while True:
            part=response.read(min(1024*1024,cap-seen+1))
            if not part:break
            seen+=len(part)
            if seen>cap:raise ValueError("Download cap exceeded")
            chunks.append(part)
        return b"".join(chunks)

def get_json(url):
    raw=fetch(url,cap=5*1024*1024)
    x=json.loads(raw)
    if not isinstance(x,dict):
        raise ValueError("Expected JSON Dryad REST object")
    return x

def embedded(obj,kind):
    emb=obj.get("_embedded",{})
    if not isinstance(emb,dict):raise ValueError("Unexpected REST _embedded")
    for k,v in emb.items():
        if kind in k.lower() and isinstance(v,list):
            return v
    for k,v in obj.items():
        if kind in k.lower() and isinstance(v,list):
            return v
    raise ValueError("No listed Dryad "+kind+" records; keys="+str(list(obj))[:300])

def link(obj,token):
    links=obj.get("_links",{})
    for name,val in links.items():
        if token in name.lower():
            if isinstance(val,dict) and val.get("href"):
                return urljoin(BASE,val["href"])
    return None

def dataset_files(doi):
    uri=BASE+"/api/v2/datasets/"+quote("doi:"+doi,safe="")
    dataset=get_json(uri)
    version_uri=link(dataset,"versions") or uri+"/versions"
    versions=get_json(version_uri)
    rows=embedded(versions,"versions")
    if not rows:raise ValueError("No public dataset version")
    rows=sorted(rows,key=lambda r:(int(r.get("versionNumber") or 0),int(r.get("id") or 0)))
    version=rows[-1]
    version_self=link(version,"self") or ""
    path_tail=version_self.rsplit("/versions/",1)[-1].split("?",1)[0].strip("/")
    vid=version.get("id") or (int(path_tail) if path_tail.isdigit() else None)
    if not vid:raise ValueError("No original Dryad version ID or usable self-link; keys="+str(list(version)))
    file_uri=link(version,"files") or BASE+"/api/v2/versions/"+str(vid)+"/files"
    allfiles=[]
    while file_uri:
        page=get_json(file_uri)
        allfiles.extend(embedded(page,"files"))
        nxt=link(page,"next")
        if nxt==file_uri:raise ValueError("Looping Dryad page")
        file_uri=nxt
    dedup={}
    for x in allfiles:
        nm=x.get("path") or x.get("name") or x.get("filename")
        if nm:
            dedup[nm.split("/")[-1]]=x
    return dataset,version,dedup,{"dataset_url":uri,"version_id":vid,"n_dataset_versions":len(rows)}

def download_file(file):
    url=link(file,"download")
    if not url:
        fid=file.get("id")
        if not fid:raise ValueError("Missing Dryad file download link and file ID")
        url=BASE+"/api/v2/files/"+str(fid)+"/download"
    return fetch(url),url

def content_excerpt(raw):
    if b"\x00" in raw[:500]:return None
    return raw[:2000].decode("utf-8","replace")[:1600]

def sample_xls(raw):
    if not raw.startswith(bytes.fromhex("d0cf11e0a1b11ae1")):
        raise ValueError("Old Excel .xls source magic missing")
    import xlrd
    wb=xlrd.open_workbook(file_contents=raw,on_demand=True)
    out=[]
    for sh in wb.sheets():
        head=[]
        for i in range(min(5,sh.nrows)):
            head.append({
             "row_index_zero_based":i,
             "values":[
               {"value":str(sh.cell_value(i,j))[:110], "cell_type":sh.cell(i,j).ctype}
               for j in range(min(sh.ncols,12))]
            })
        out.append({"name":sh.name,"nrows":sh.nrows,"ncols":sh.ncols,
                    "first_rows":head})
    return out

def sample_xlsx(raw):
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("New .xlsx not zip container")
    import sys
    sys.path.insert(0,str(ROOT.parent/"validation_v137"))
    from appendix_site_macro import read_xlsx_table_rows
    d=read_xlsx_table_rows(raw)
    out=[]
    for name,rows in d.items():
        first=[{"row":k,"cells":dict(list(v.items())[:18])} for k,v in sorted(rows.items())[:5]]
        out.append({"name":name,"xml_rows":len(rows),"sample_rows":first})
    return out

def sample_zip(raw):
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Original zip doesn't match declared format")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=z.infolist()
        listing=[{"filename":i.filename,"bytes_uncompressed":i.file_size,
                  "bytes_compressed":i.compress_size} for i in members]
        return {"n_members":len(members),"members_head":listing[:35],
                "all_members_bytes":sum(i.file_size for i in members),
                "member_names_sha256":hashlib.sha256("\n".join(
                    sorted(x.filename for x in members)).encode()).hexdigest()}

def analyze():
    report={
        "version":"v141_dryad_original_acquisition_1",
        "frozen_date":"2026-11-15",
        "method":"actual Dryad REST metadata and bounded original bytes; SHA256",
        "source_citations":{
            "california":"https://doi.org/10.5061/dryad.q2bvq83sw",
            "kashima":"https://doi.org/10.5061/dryad.zkh1893qn",
        },
        "datasets":{},
        "physical_tide_by_solar_effect":"NOT_ESTIMATED",
        "global_pooled_tidal_interaction":"NOT_ESTIMATED",
    }
    for key,request in DATASETS.items():
        doi=request["doi"]
        try:
            md,ver,files,ids=dataset_files(doi)
            item={
              "doi":doi,
              "title":md.get("title"),
              "version_number":ver.get("versionNumber"),
              "files_total":len(files),
              "file_ext_counts":{},
              "all_original_paths_and_sizes":[{"name":nm,"bytes":x.get("size")}
                                                for nm,x in sorted(files.items())],
              "api_provenance":ids,
              "originals":[],
              "effort_join_status":"NOT_ESTIMATED",
              "tide_join_status":"NOT_ESTIMATED"}
            for nm in files:
                ext=nm.rsplit(".",1)[-1].lower() if "." in nm else "none"
                item["file_ext_counts"][ext]=item["file_ext_counts"].get(ext,0)+1
            for name in request["target_names"]:
                if name not in files:
                    item["originals"].append({"file":name,"status":"NOT_LISTED_IN_LATEST_API_VERSION"})
                    continue
                f=files[name]
                try:
                    raw,url=download_file(f)
                    info={"file":name,"status":"DOWNLOADED_AND_FINGERPRINTED",
                          "size_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                          "original_dryad_download_url":url}
                    if name.lower().endswith(".xls"):
                        info["sheets"]=sample_xls(raw)
                    elif name.lower().endswith(".xlsx"):
                        info["sheets"]=sample_xlsx(raw)
                    elif name.lower().endswith(".zip"):
                        info["zip"]=sample_zip(raw)
                    else:
                        info["original_text_prefix"]=content_excerpt(raw)
                except Exception as e:
                    info={"file":name,"status":"DOWNLOAD_OR_FORMAT_FAILED",
                          "error_type":type(e).__name__,"error":str(e)[:270]}
                item["originals"].append(info)
            report["datasets"][key]=item
        except Exception as e:
            report["datasets"][key]={
                "doi":doi,"status":"REST_ACQUISITION_FAILURE",
                "error_type":type(e).__name__,"error":str(e)[:600]}
    return report

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--out",default=str(ROOT/"results"/"original_dryad_two_datasets.json"))
    cli.add_argument("--allow-metadata-only",action="store_true",help="Science gate: verify metadata but mark original downloads blocked")
    cli.add_argument("--check",action="store_true",help="Fail when public source filelist or original access status changes")
    args=cli.parse_args()
    res=analyze()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        frozen=json.loads(out.read_text())
        for key in DATASETS:
            new=res["datasets"][key]
            old=frozen["datasets"][key]
            if (new.get("files_total")!=old.get("files_total")
                    or new.get("all_original_paths_and_sizes")!=old.get("all_original_paths_and_sizes")
                    or new.get("version_number")!=old.get("version_number")):
                raise AssertionError("Dryad source filelist or dataset version changed for "+key)
            statuses=[(x["file"],x.get("status"),x.get("error_type")) for x in new.get("originals",[])]
            old_statuses=[(x["file"],x.get("status"),x.get("error_type")) for x in old.get("originals",[])]
            if statuses!=old_statuses:
                raise AssertionError("Dryad original file-access status changed for "+key+"; assess anew")
    else:
        out.write_text(json.dumps(res,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V141_SOURCE_AUDIT_START")
    print(json.dumps(res,ensure_ascii=False))
    print("V141_SOURCE_AUDIT_END")
    if not all(d.get("files_total",0)>0 for d in res["datasets"].values()):
        sys.exit(2)
    california=res["datasets"]["california_sanctuaries"]
    kashima=res["datasets"]["japan_kashima"]
    if california["files_total"]!=61 or kashima["files_total"]!=40:
        raise AssertionError("Original public Dryad file-list counts have changed; rescreen")
    ca_sites=set(n[:4] for n in (e["name"] for e in california["all_original_paths_and_sizes"])
                 if n.endswith((".xls",".xlsx")))
    if ca_sites!={"CI01","CI02","CI03","CI04","CI05","CH01","MB01","MB02","MB05"}:
        raise AssertionError("Expected 9 original California recorder-site codes")
    originals=[x for d in res["datasets"].values() for x in d["originals"]]
    verified=sum(x.get("status")=="DOWNLOADED_AND_FINGERPRINTED" for x in originals)
    if verified==0 and not args.allow_metadata_only:
        # An unauthorized REST file download is not original dataset accession.
        sys.exit(3)
    if verified==0 and args.allow_metadata_only:
        print("V141_METADATA_ONLY_PASS__NO_RAW_EFFECT__DRYAD_FILE_DOWNLOAD_BLOCKED")

if __name__=="__main__":
    main()
