"""v42: bounded HTTP Range ZIP source probe for published 2014 Wadden coastlines.

No original bird or tidal outcome is read. Do not download the 1.43GB whole
archive. Full ZIP checksum cannot be claimed from partial Range reads.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

DRYAD_ROOT="https://datadryad.org"
DOI="doi:10.5061/dryad.wm37pvmth"
SOURCE="https://doi.org/10.5061/dryad.wm37pvmth"
ORIGINAL_ARCHIVE="all_code_and_data_files.zip"
COAST_BASENAMES=("CoastSouth_Ameland.txt","CoastSouth_Schiermonnikoog.txt")
MAX_METADATA_BYTES=2_000_000
MAX_TRANSFER_BYTES=16_000_000
MAX_MEMBER_BYTES=6_000_000
BLOCK_BYTES=512_000

class SourceStop(RuntimeError):
    pass

def get_json(url, opener=urlopen):
    if not url.startswith(DRYAD_ROOT+"/api/v2/"):
        raise SourceStop("SOURCE_STOP_NON_PROVIDER_API")
    req=Request(url,headers={"User-Agent":"Boids-v42-Original-Dryad-Source/1.0",
                             "Accept":"application/json"})
    with opener(req,timeout=25) as response:
        raw=response.read(MAX_METADATA_BYTES+1)
    if len(raw)>MAX_METADATA_BYTES:raise SourceStop("SOURCE_STOP_DRYAD_METADATA_OVERSIZE")
    result=json.loads(raw)
    if not isinstance(result,dict):raise SourceStop("SOURCE_STOP_DRYAD_API_NOT_JSON_OBJECT")
    return result

def original_archive_metadata(get=get_json):
    versions_url=DRYAD_ROOT+"/api/v2/datasets/"+quote(DOI,safe="")+"/versions"
    version_response=get(versions_url)
    versions=(version_response.get("_embedded") or {}).get("stash:versions") or version_response.get("versions") or []
    if not versions:raise SourceStop("SOURCE_STOP_DRYAD_VERSION_UNAVAILABLE")
    def order(v):
        return (int(v.get("versionNumber") or 0),int(v.get("id") or 0))
    latest=max(versions,key=order)
    version_links=latest.get("_links") or {}
    path=(version_links.get("stash:files") or {}).get("href")
    vid=int(latest.get("id") or 0)
    if vid<1:
        # Public Dryad HAL version listings may omit id while preserving links.
        candidates=[(version_links.get("self") or {}).get("href",""),path or ""]
        matches=[re.search(r"/api/v2/versions/(\\d+)(?:/files)?(?:\\?.*)?$",x)
                 for x in candidates]
        versions=[int(m.group(1)) for m in matches if m]
        if versions and len(set(versions))==1:
            vid=versions[0]
    if vid<1:raise SourceStop("SOURCE_STOP_DRYAD_VERSION_ID_UNVERIFIED")
    if not path:path=f"/api/v2/versions/{vid}/files"
    file_url=urljoin(DRYAD_ROOT,path)
    if not file_url.startswith(DRYAD_ROOT+"/api/v2/"):
        raise SourceStop("SOURCE_STOP_DRYAD_FILE_LIST_UNTRUSTED_URL")
    file_response=get(file_url)
    original=(file_response.get("_embedded") or {}).get("stash:files") or file_response.get("files") or []
    archives=[v for v in original if Path(str(v.get("path") or v.get("name") or "")).name==ORIGINAL_ARCHIVE]
    if len(archives)!=1:raise SourceStop("SOURCE_STOP_DRYAD_EXPECTED_ARCHIVE_NOT_UNIQUE")
    item=archives[0]
    file_id=int(item.get("id") or 0)
    if file_id<1:
        link=((item.get("_links") or {}).get("self") or {}).get("href","")
        m=re.search(r"/api/v2/files/(\\d+)(?:\\?.*)?$",link)
        if m:file_id=int(m.group(1))
    if file_id<1:raise SourceStop("SOURCE_STOP_DRYAD_FILE_ID_MISSING")
    size=int(item.get("size") or 0)
    if not(1_000_000_000<size<4_000_000_000):
        raise SourceStop("SOURCE_STOP_DRYAD_ORIGINAL_ARCHIVE_SIZE_UNEXPECTED")
    return {"doi":DOI,"source":SOURCE,"version_id":vid,
            "original_archive_filename":ORIGINAL_ARCHIVE,
            "original_provider_file_id":file_id,
            "original_archive_provider_size_bytes":size,
            "archive_download_url":f"{DRYAD_ROOT}/api/v2/files/{file_id}/download"}

def probe_range_size(url, opener=urlopen):
    if not url.startswith(DRYAD_ROOT+"/api/v2/files/") or not url.endswith("/download"):
        raise SourceStop("SOURCE_STOP_RANGE_NOT_ORIGINAL_PROVIDER_ENDPOINT")
    request=Request(url,headers={"Range":"bytes=0-0",
                                "Accept-Encoding":"identity",
                                "User-Agent":"Boids-v42-RangeOnly/1.0"})
    with opener(request,timeout=25) as resp:
        status=resp.status
        contentrange=resp.headers.get("Content-Range","")
        tiny=resp.read(2)
    if status!=206:
        raise SourceStop("SOURCE_STOP_RANGE_NOT_SUPPORTED")
    match=re.fullmatch(r"bytes\s+0-0/(\d+)",contentrange)
    if not match or len(tiny)!=1:
        raise SourceStop("SOURCE_STOP_RANGE_INCOMPLETE_CONTENT_RANGE")
    return int(match.group(1))

def read_range(url,start,end,total,opener=urlopen):
    if not(0<=start<=end<total and end-start+1<=BLOCK_BYTES):
        raise SourceStop("SOURCE_STOP_RANGE_BOUNDS")
    request=Request(url,headers={"Range":f"bytes={start}-{end}",
                               "Accept-Encoding":"identity",
                               "User-Agent":"Boids-v42-RangeOnly/1.0"})
    with opener(request,timeout=40) as resp:
        status=resp.status
        contentrange=resp.headers.get("Content-Range","")
        data=resp.read(end-start+2)
    expected=f"bytes {start}-{end}/{total}"
    if status!=206 or contentrange!=expected:
        raise SourceStop("SOURCE_STOP_RANGE_NOT_VERIFIABLE")
    if len(data)!=(end-start+1):
        raise SourceStop("SOURCE_STOP_RANGE_LENGTH_MISMATCH")
    return data

class BoundedRangeReader(io.RawIOBase):
    """Seekable read-only Range-backed ZIP file with hard network byte ceiling."""
    def __init__(self,url,size,range_get=read_range):
        super().__init__()
        self.url=url;self.size=int(size);self.position=0
        self.range_get=range_get
        self.fetched=0
        self.cache={}
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.position
    def seek(self,offset,whence=0):
        if whence==0:new=int(offset)
        elif whence==1:new=self.position+int(offset)
        elif whence==2:new=self.size+int(offset)
        else:raise ValueError("unsupported seek")
        if new<0:raise ValueError("negative file position")
        self.position=new
        return new
    def read(self,n=-1):
        if self.position>=self.size:return b""
        if n is None or n<0:n=self.size-self.position
        n=min(int(n),self.size-self.position)
        if n>MAX_MEMBER_BYTES+MAX_METADATA_BYTES:
            raise SourceStop("SOURCE_STOP_UNBOUNDED_ZIP_READ")
        result=bytearray()
        while n:
            block=self.position//BLOCK_BYTES
            if block not in self.cache:
                start=block*BLOCK_BYTES
                end=min(self.size-1,start+BLOCK_BYTES-1)
                data=self.range_get(self.url,start,end,self.size)
                self.fetched+=len(data)
                if self.fetched>MAX_TRANSFER_BYTES:
                    raise SourceStop("SOURCE_STOP_MAX_16MB_REMOTE_BYTES_EXCEEDED")
                if len(self.cache)>=8:self.cache.pop(next(iter(self.cache)))
                self.cache[block]=data
            off=self.position-block*BLOCK_BYTES
            part=self.cache[block][off:off+n]
            if not part:raise SourceStop("SOURCE_STOP_EMPTY_RANGE_BLOCK")
            result.extend(part)
            self.position+=len(part);n-=len(part)
        return bytes(result)

def coast_member_info(original,zip_reader):
    """Use ZIP's original per-member CRC verification. No bird GPS data here."""
    info=[]
    with zipfile.ZipFile(zip_reader,mode="r") as z:
        all_members=z.infolist()
        for name in COAST_BASENAMES:
            matches=[x for x in all_members if Path(x.filename).name.lower()==name.lower()]
            if len(matches)!=1:
                raise SourceStop("SOURCE_STOP_COASTLINE_MEMBER_NOT_UNIQUE_"+name)
            member=matches[0]
            if (member.file_size>MAX_MEMBER_BYTES or
                member.compress_size>MAX_MEMBER_BYTES):
                raise SourceStop("SOURCE_STOP_COASTLINE_MEMBER_OVERSIZE")
            # ZipFile.open checks the archive-listed CRC32 when stream ends.
            with z.open(member) as stream:
                data=stream.read(MAX_MEMBER_BYTES+1)
            if len(data)!=member.file_size:
                raise SourceStop("SOURCE_STOP_ZIP_MEMBER_LENGTH_MISMATCH")
            lines=data.decode("utf-8-sig",errors="replace").splitlines()
            numeric_rows=0
            for line in lines:
                tokens=[x for x in re.split(r"[;\s,]+",line.strip()) if x]
                if len(tokens)<2:continue
                try:
                    x,y=float(tokens[0]),float(tokens[1])
                except ValueError:continue
                if (x==x and y==y) and abs(x)<1e7 and abs(y)<1e7:
                    numeric_rows+=1
            info.append({"member":name,
                         "provider_zip_member_path":member.filename,
                         "uncompressed_bytes":member.file_size,
                         "zip_original_member_CRC32_verified":True,
                         "extracted_member_SHA256":hashlib.sha256(data).hexdigest(),
                         "text_lines":len(lines),
                         "first_two_column_numeric_lines":numeric_rows})
        count=len(all_members)
    return info,count

def inspect():
    meta=original_archive_metadata()
    url=meta.pop("archive_download_url")
    remote_size=probe_range_size(url)
    if remote_size!=meta["original_archive_provider_size_bytes"]:
        raise SourceStop("SOURCE_STOP_ORIGINAL_DRYAD_ARCHIVE_SIZE_MISMATCH")
    reader=BoundedRangeReader(url,remote_size)
    small,member_count=coast_member_info(meta,reader)
    result={"source_status":"SOURCE_ADMITTED_2014_COASTLINES_ONLY",
            "original_provider_manifest":meta,
            "original_archive_total_members":member_count,
            "original_source_coastline_members":small,
            "source_HTTP_Range_bytes_transferred":reader.fetched+1,
            "large_archive_full_checksum_verified":False,
            "source_member_crc_and_sha256_verified":True,
            "source_CRS":"EPSG:28992_RD_New",
            "original_coastline_year":2014,
            "original_GPS_join":False,
            "real_exposed_flat_or_prey_mechanism":"NOT_ESTIMATED"}
    return result

def run(output):
    try:
        result=inspect()
    except (SourceStop,Exception) as error:
        # Do not turn an HTTP source STOP into an ecological null hypothesis.
        reason=str(error).splitlines()[0][:180]
        result={"source_status":"SOURCE_STOP_NO_2014_COASTLINE_BYTES_ADMITTED",
                "source":SOURCE,
                "reason":reason,
                "original_GPS_join":False,
                "real_exposed_flat_or_prey_mechanism":"NOT_ESTIMATED"}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
