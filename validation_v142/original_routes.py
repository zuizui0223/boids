"""v142: publicly documented Dryad download routes, fail-closed original study file verification.

Tries legitimate public archive and public individual file links of PUBLISHED
Dryad datasets, no credentials or bypass. Downloads are bounded, fingerprinted,
inspected in memory; no original copyrighted spreadsheet is published in Git.
"""
from __future__ import annotations
import hashlib, io, json, os, sys, zipfile
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import quote,urljoin
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v141"))
from source_probe import DATASETS,dataset_files,link,download_file,sample_xls,sample_xlsx
BASE="https://datadryad.org"
CAP=12*1024*1024

def public_get(url):
    request=Request(url,headers={"User-Agent":"BoidsOpenDataIntegrity/1.0 research","Accept":"application/octet-stream,application/zip,*/*"})
    with urlopen(request,timeout=35) as response:
        payload=response.read(CAP+1)
        dest=response.geturl()
        head=response.headers.get("Content-Type","")
    if len(payload)>CAP:raise ValueError("Public archive exceeds 12MiB")
    return payload,dest,head

def describe(url, data, name):
    sample={"name":name,"byte_length":len(data),"SHA256":hashlib.sha256(data).hexdigest(),
            "return_url":url}
    if data[:8]==bytes.fromhex("d0cf11e0a1b11ae1") and name.endswith(".xls"):
        sample["parsed_sheets"]=sample_xls(data)
    elif zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            members=[x for x in z.namelist() if not x.endswith("/")]
            if any(x.lower().endswith(".xlsx") for x in members) and name.endswith(".xlsx"):
                sample["parsed_sheets"]=sample_xlsx(data)
            else:
                sample["zip_file_count"]=len(members)
                sample["zip_names"]=[{"name":x,"bytes":z.getinfo(x).file_size} for x in members[:75]]
                candidates=[x for x in members if x.lower().endswith((".xls",".xlsx"))]
                if candidates:
                    chosen=[]
                    for member in candidates[:5]:
                        ext=member.lower().split(".")[-1]
                        raw=z.read(member)
                        chosen.append({"name":member,"bytes":len(raw),"SHA256":hashlib.sha256(raw).hexdigest(),
                          "sheets":sample_xls(raw) if ext=="xls" else sample_xlsx(raw)})
                    sample["sample_spreadsheets"]=chosen
    elif name.endswith(".md") or name.endswith(".txt"):
        sample["original_readme_prefix"]=data[:4000].decode("utf-8","replace")
    else:
        sample["magic_hex"]=data[:24].hex()
    return sample

def file_id(f):
    href=link(f,"self") or ""
    last=href.rstrip("/").rsplit("/",1)[-1]
    return int(last) if last.isdigit() else (f.get("id") if isinstance(f.get("id"),int) else None)

def run():
    out={"version":"v142_original_public_Dryad_download_protocol_1",
        "published_dryad_files":{},"original_binary_verification_count":0,
        "ecological_tide_by_night_effect":"NOT_ESTIMATED"}
    for target, info in DATASETS.items():
        doi=info["doi"]
        entry={"DOI":doi,"attempts":[],"originals":[]}
        try:
            dataset,version,files,metadata=dataset_files(doi)
            entry["public_api_metadata"]={"version":metadata["version_id"],"file_count":len(files)}
            entry["file_link_shapes"]={}
            for name in info["target_names"]:
                if name not in files:continue
                ff=files[name]
                entry["file_link_shapes"][name]={"file_id":file_id(ff),
                    "API_links":{k:(v.get("href") if isinstance(v,dict) else str(v))
                                 for k,v in ff.get("_links",{}).items()}}
            candidates=[]
            if target=="california_sanctuaries":
                candidates.append(("dataset_public_latest_bundle",BASE+"/api/v2/datasets/"+quote("doi:"+doi,safe="")+"/download","California_bundle.zip"))
                candidates.append(("version_public_archive",BASE+"/api/v2/versions/"+str(metadata["version_id"])+"/download","California_version.zip"))
            for name in info["target_names"]:
                f=files.get(name)
                if not f:continue
                fid=file_id(f)
                href=link(f,"download")
                if href:candidates.append(("official_file_download_link_"+name,href,name))
                if fid:
                    candidates.append(("official_file_API_"+name,BASE+"/api/v2/files/"+str(fid)+"/download",name))
                    candidates.append(("official_public_landing_download_"+name,BASE+"/stash/downloads/file_stream/"+str(fid),name))
            visited=set()
            for tag,url,filename in candidates:
                if url in visited:continue
                visited.add(url)
                try:
                    raw,final,ctype=public_get(url)
                    if (len(raw)<100 or raw[:1]==b"<" and b"<html" in raw[:500].lower()):
                        raise ValueError("Non-original response or HTML rejection")
                    digest=describe(final,raw,filename)
                    entry["attempts"].append({"method":tag,"status":"ACQUIRED_ORIGINAL_VERIFIED","length":len(raw),"content_type":ctype})
                    entry["originals"].append(digest)
                    out["original_binary_verification_count"]+=1
                    # One true California full bundle is sufficient for stage one.
                    if target=="california_sanctuaries" and digest.get("zip_file_count",0)>=50:break
                    # Keep acquisition inventory compact: at most 3 authentic files/target
                    if len(entry["originals"])>=3:break
                except Exception as exc:
                    entry["attempts"].append({"method":tag,"status":"FAILED","type":type(exc).__name__,
                                               "error":str(exc)[:180]})
        except Exception as exc:
            entry["metadata_failure"]={"type":type(exc).__name__,"error":str(exc)[:250]}
        out["published_dryad_files"][target]=entry
    return out

def main():
    out=run()
    path=Path(__file__).parent/"results"/"dryad_public_route_source_diagnostic.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print("V142_DRYAD_ORIGINAL_START")
    print(json.dumps(out,ensure_ascii=False))
    print("V142_DRYAD_ORIGINAL_END")
    # fail closed: if neither source original can be acquired, don't imply success.
    if out["original_binary_verification_count"]==0:
        print("STOP_NO_AUTHORIZED_ORIGINAL_BINARY_ACCESS")
        sys.exit(2)

if __name__=="__main__":main()
