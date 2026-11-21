"""v10 source-only official Dryad fish-chorus × 70kHz scattering admission.
No fish chorus or scattering outcome values interpreted at this stage.
Auth/redirect/download failure is SOURCE_STOP, not an ecological result.
"""
from __future__ import annotations
import csv,hashlib,io,json,re
from pathlib import Path
from urllib import request,error,parse
DOI="10.5061/dryad.qz612jmx0"
BASE="https://datadryad.org/api/v2/"
ENTRY=BASE+"datasets/"+parse.quote("doi:"+DOI,safe="")
FILES=("South_T_master_dryad.csv",
       "AllEchoviewData_T01-04_50-250mexport_70kHz_Final_arrangedbydatetime.csv",
       "README.md")
CAP={"South_T_master_dryad.csv":16_000_000,
     "AllEchoviewData_T01-04_50-250mexport_70kHz_Final_arrangedbydatetime.csv":410_000_000,
     "README.md":100_000}
class SourceStop(Exception):pass
def get(url,limit=1_000_000,headers=None):
    if not url.startswith(BASE):raise SourceStop("UNAPPROVED_DRYAD_API")
    req=request.Request(url,headers={"User-Agent":"fish-chorus-v10-original-source-only/1.0",
      "Accept":"application/json,text/csv,application/octet-stream,*/*",**(headers or {})})
    try:
        with request.urlopen(req,timeout=50) as r:
            data=r.read(limit+1)
            if len(data)>limit:raise SourceStop("RESPONSE_BYTE_CAP")
            status=r.status
            heads=dict(r.headers)
    except error.HTTPError as e:raise SourceStop("HTTP_"+str(e.code)) from None
    except error.URLError as e:raise SourceStop("NETWORK_"+type(e.reason).__name__) from None
    return data,status,heads
def get_json(url):
    raw,_,_=get(url,3_000_000)
    try:return json.loads(raw)
    except (UnicodeError,ValueError):raise SourceStop("INVALID_ORIGINAL_API_JSON") from None
def embedded(d,name):
    if not isinstance(d,dict):raise SourceStop("INVALID_API_SHAPE")
    for k,v in (d.get("_embedded") or {}).items():
        if name in k.lower() and isinstance(v,list):return v
    for k in (name,name+"s"):
        if isinstance(d.get(k),list):return d[k]
    raise SourceStop("MISSING_"+name.upper()+"_LIST")
def get_num(z,kind):
    if z.get("id") is not None:return int(z["id"])
    link=(z.get("_links") or {}).get("self") or {}
    href=link.get("href","") if isinstance(link,dict) else link
    m=re.search(r"/"+kind+r"/(\d+)",href)
    if not m:raise SourceStop("MISSING_"+kind+"_ID")
    return int(m.group(1))
def filename(item):
    return str(item.get("path") or item.get("filename") or item.get("fileName")
       or item.get("name") or item.get("originalFileName") or "").split("/")[-1]
def get_all_files(version):
    first=BASE+"versions/"+str(version)+"/files"
    seen=set();files=[];visited=set();url=first
    for _ in range(20):
        if url in visited:raise SourceStop("PAGINATION_LOOP")
        visited.add(url);p=get_json(url)
        for f in embedded(p,"file"):
            v=(filename(f),get_num(f,"files"))
            if v in seen:continue
            files.append(f);seen.add(v)
        next_link=(p.get("_links") or {}).get("next") or (p.get("_links") or {}).get("stash:next")
        if not next_link:break
        href=next_link.get("href") if isinstance(next_link,dict) else next_link
        if href.startswith("/"):
            url=parse.urljoin(BASE,href)
        else:url=parse.urljoin(BASE,href)
        if not url.startswith(BASE):raise SourceStop("NONOFFICIAL_PAGINATION")
    else:raise SourceStop("TOO_MANY_PAGES")
    return files,len(visited)
def first_row(prefix):
    try:
        line=prefix.decode("utf-8-sig",errors="strict").splitlines()[0]
        return next(csv.reader([line]))
    except (UnicodeError,ValueError,csv.Error,IndexError):
        raise SourceStop("ORIGINAL_HEADER_NOT_UTF8_CSV") from None
def read_probe(item,full=False):
    name=filename(item);size=int(item.get("size") or 0)
    if not name in FILES or size<=0 or size>CAP[name]:
        raise SourceStop("ORIGINAL_EXPECTED_FILE_METADATA_STOP "+name)
    file_id=get_num(item,"files")
    url=BASE+"files/"+str(file_id)+"/download"
    if full:
        data,status,heads=get(url,CAP[name])
        if len(data)!=size:raise SourceStop("ORIGINAL_FILE_SIZE_MISMATCH "+name)
    else:
        req=request.Request(url,headers={"User-Agent":"fish-chorus-v10-source-byte-range/1.0",
                                          "Range":"bytes=0-8191"})
        try:
            with request.urlopen(req,timeout=65) as response:
                data=response.read(8192)
                status=response.status
                heads=dict(response.headers)
        except error.HTTPError as e:raise SourceStop("ORIGINAL_LARGE_CSV_HTTP_"+str(e.code)) from None
        except error.URLError as e:raise SourceStop("ORIGINAL_LARGE_CSV_NETWORK_"+type(e.reason).__name__) from None
    prefix=data[:8192]
    h=first_row(prefix) if name.endswith(".csv") else []
    record={"name":name,"source_file_id":file_id,"source_declared_bytes":size,
       "download_http":status,"first_bytes_sha256":hashlib.sha256(prefix).hexdigest(),
       "original_header_columns":h,"bytes_read":len(data),
       "full_original_source_file_verified":False}
    if full:
        digest=str(item.get("digest") or "")
        alg=str(item.get("digestType") or "").lower().replace("-","")
        if digest and alg in ("md5","sha256") and hashlib.new(alg,data).hexdigest().lower()!=digest.lower():
            raise SourceStop("ORIGINAL_PROVIDER_DIGEST_MISMATCH "+name)
        record["full_original_source_file_verified"]=True
        record["file_sha256"]=hashlib.sha256(data).hexdigest()
        record["provider_digest_checked"]=bool(digest and alg in ("md5","sha256"))
        if name=="README.md":
            record["README_first_180_chars"]=data[:180].decode("utf-8-sig",errors="replace")
    else:
        record["partial_only"]=True
        record["content_range"]=heads.get("Content-Range")
    return record
def run():
    out={"version":"v10_same_site_chorus_scat_original_predata_gate",
        "original_DOI":DOI,"used_author_download":False,
        "behavior_effect_fitted":False,"fish_species_identified":False,
        "source_files":[]}
    try:
        d=get_json(ENTRY)
        versions=embedded(get_json(ENTRY+"/versions"),"version")
        published=max(versions,key=lambda x:int(x.get("versionNumber") or x.get("id") or 0))
        version_id=get_num(published,"versions")
        f,pages=get_all_files(version_id)
        by_name={filename(z):z for z in f}
        out["original_version"]=version_id
        out["manifest_pages"]=pages
        out["manifest_count"]=len(f)
        if not set(FILES).issubset(by_name):raise SourceStop("EXPECTED_PUBLIC_FILES_MISSING")
        # Official original publication, two same-site files: acquire small
        # original fully, large 70kHz only range header in this source gate.
        for name in FILES:
            out["source_files"].append(read_probe(by_name[name],full=name!=FILES[1]))
        out["status"]="SOURCE_SMALL_FILES_VERIFIED_BIG_HEADER_PROBED"
    except (SourceStop,OSError,TypeError,ValueError) as e:
        out["status"]="SOURCE_STOP"
        out["stop_reason"]=str(e)
    return out
def main():
    res=run()
    path=Path("validation_fish_chorus_v10/results/author_dryad_source_gate.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("stop_reason"),
      "manifest_count":res.get("manifest_count"),
      "source_files":[{"name":x["name"],"columns":x["original_header_columns"],
      "bytes":x["source_declared_bytes"],"full_verified":x["full_original_source_file_verified"]}
      for x in res["source_files"]]}))
if __name__=="__main__":main()
