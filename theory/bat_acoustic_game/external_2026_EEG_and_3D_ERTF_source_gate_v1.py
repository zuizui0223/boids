"""Independent original 2026 bat EEG and 3D source archive admission.

Source metadata plus bounded HTTP Range only. Never downloads the ~1GB
Steckel ZIP; never reads original XLSX EEG values, simulated model weights,
figure source data, real bat IDs or original source's MAT HRTF values.
"""
from __future__ import annotations
import hashlib,json,struct,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlparse

OUT=Path(__file__).resolve().parent/"EXTERNAL_2026_BAT_EEG_3D_SOURCE_GATE_V1.json"
DRYAD="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.dz08kps9w"
ZENODO="https://zenodo.org/api/records/23537553"
XLSX_NAME="in_flight_bat_eeg_echolocation_combined_table.xlsx"
ZIP_NAME="2026 - Steckel - Bats Learn Echolocation.zip"
HEAD={"User-Agent":"bat-original-open-science-no-new-observations-source-gate/1.0",
      "Accept":"application/json,application/zip,application/octet-stream,*/*"}
TAIL_BYTES=131072
MAX_TAIL=262144
MAX_CENTRAL=2*1024*1024

def fetch(url,method="GET",range_header=None,maxbytes=400000):
    if not url.startswith(("https://datadryad.org/","https://zenodo.org/","https://records.zenodo.org/")):
        raise ValueError("STOP_NON_ORIGINAL_DATA_PROVIDER_HOST")
    h=HEAD.copy()
    if range_header:h["Range"]=range_header
    req=urllib.request.Request(url,headers=h,method=method)
    try:
        with urllib.request.urlopen(req,timeout=65) as r:
            headers={"http":r.status,"content_type":r.headers.get("Content-Type"),
                     "content_length":r.headers.get("Content-Length"),
                     "content_range":r.headers.get("Content-Range"),
                     "accept_ranges":r.headers.get("Accept-Ranges"),
                     "etag":r.headers.get("ETag")}
            if method=="HEAD":return headers,b""
            data=r.read(maxbytes+1)
            if len(data)>maxbytes:raise ValueError("STOP_PROVIDER_IGNORED_RANGE_OR_RESPONSE_TOO_LARGE")
            return headers,data
    except urllib.error.HTTPError as e:
        raise ValueError("STOP_ORIGINAL_HTTP_"+str(e.code)) from e

def provider_url(link):
    if isinstance(link,dict):link=link.get("href") or link.get("url")
    if not link:raise ValueError("STOP_NO_PROVIDER_LINK")
    if link.startswith("/"):return "https://datadryad.org"+link
    if not link.startswith("https://"):raise ValueError("STOP_UNVERIFIED_PROVIDER_URL")
    return link

def dryad_gate():
    out={"provider":"Dryad","doi":"10.5061/dryad.dz08kps9w",
         "original_xlsx_name":XLSX_NAME,"status":"NOT_CHECKED",
         "original_EEG_values_or_bat_IDs_opened":False}
    try:
        h,raw=fetch(DRYAD,maxbytes=300000)
        doc=json.loads(raw)
        out["original_dataset_license"]=doc.get("license")
        out["original_dataset_title"]=doc.get("title")
        links=doc.get("_links") or {}
        u=provider_url(links.get("stash:version"))
        meta=json.loads(fetch(u,maxbytes=350000)[1])
        file_url=provider_url((meta.get("_links") or {}).get("stash:files"))
        data=json.loads(fetch(file_url,maxbytes=400000)[1])
        files=(data.get("_embedded") or {}).get("stash:files") or []
        original=[x for x in files if (x.get("path") or x.get("filename") or "").split("/")[-1]==XLSX_NAME]
        out["catalog_file_count"]=len(files)
        if len(original)!=1:raise ValueError("STOP_NONUNIQUE_ORIGINAL_XLSX")
        file=original[0]
        out["original_xlsx_metadata"]={
           "file_id":file.get("id"),"size_bytes":file.get("size"),
           "provider_checksum":file.get("digest"),
           "original_data_filename":file.get("path"),
        }
        download=provider_url((file.get("_links") or {}).get("stash:download"))
        out["provider_file_access_url"]=download
        try:out["original_provider_HEAD"]=fetch(download,method="HEAD")[0]
        except Exception as e:out["original_provider_HEAD"]={"status":"STOP","error":str(e)[:150]}
        out["range_probe"]={"status":"NOT_CHECKED"}
        try:
            hr,b=fetch(download,range_header="bytes=0-4095",maxbytes=4096)
            out["range_probe"].update(hr)
            out["range_probe"]["nbytes"]=len(b)
            out["range_probe"]["zip_magic"]=b[:4].hex()
            out["range_probe"]["first_4k_sha256"]=hashlib.sha256(b).hexdigest()
            out["status"]="PASS_PUBLISHED_EEG_XLSX_FIRST_4K_ONLY" if hr["http"]==206 and b[:4]==b"PK\x03\x04" else "STOP_EEG_SOURCE_RANGE_UNAVAILABLE"
        except Exception as e:
            out["range_probe"]={"status":"STOP_EEG_SOURCE_BYTE_ACCESS","error":str(e)[:200]}
            out["status"]="STOP_EEG_SOURCE_DOWNLOAD"
    except Exception as e:
        out["status"]="STOP_DRYAD_DATASET_OR_FILE_MANIFEST_ACCESS"
        out["error"]=str(e)[:200]
    return out

def central_zip_names(blob):
    """Unpack source ZIP central directory only, not member data."""
    entries=[];i=0
    while i<len(blob):
        if blob[i:i+4]!=b"PK\x01\x02":
            raise ValueError("STOP_CENTRAL_DIRECTORY_ENTRY_BAD_MAGIC")
        if i+46>len(blob):raise ValueError("STOP_TRUNCATED_ZIP_CENTRAL")
        name_n,extra_n,comment_n=struct.unpack_from("<HHH",blob,i+28)
        crc,compressed,uncompressed=struct.unpack_from("<III",blob,i+16)
        off=struct.unpack_from("<I",blob,i+42)[0]
        nxt=i+46+name_n+extra_n+comment_n
        if nxt>len(blob):raise ValueError("STOP_BAD_CENTRAL_DIRECTORY_LENGTH")
        original=blob[i+46:i+46+name_n]
        flags=struct.unpack_from("<H",blob,i+8)[0]
        name=original.decode("utf-8" if flags&0x800 else "cp437",errors="replace")
        entries.append({"path":name,"compressed_bytes":compressed,
                        "uncompressed_bytes":uncompressed,"crc32":format(crc,"08x"),
                        "local_header_byte_offset":off})
        if len(entries)>50000:raise ValueError("STOP_TOO_MANY_ZIP_MEMBERS")
        i=nxt
    return entries

def eocd_info(tail,full_length):
    pos=tail.rfind(b"PK\x05\x06")
    if pos<0 or len(tail)-pos<22:raise ValueError("STOP_ZIP_END_OF_CENTRAL_DIRECTORY_NOT_IN_TAIL")
    _,disk,disk_dir,disk_entries,all_entries,dir_size,dir_offset,comment_n=struct.unpack_from("<IHHHHIIH",tail,pos)
    if all_entries==0xffff or dir_size==0xffffffff or dir_offset==0xffffffff:
        raise ValueError("STOP_ZIP64_SOURCE_NEEDS_SEPARATE_PARSER")
    if disk or disk_dir or disk_entries!=all_entries:raise ValueError("STOP_MULTIDISK_ZIP_NOT_SUPPORTED")
    if dir_size>MAX_CENTRAL:raise ValueError("STOP_CENTRAL_DIRECTORY_OVER_2MB")
    if dir_offset+dir_size>full_length:raise ValueError("STOP_ZIP_CENTRAL_OUTSIDE_PACKAGE")
    return {"member_count":all_entries,"directory_offset":dir_offset,
            "directory_size":dir_size,"comment_bytes":comment_n}

def zenodo_gate():
    out={"provider":"Zenodo","doi":"10.5281/zenodo.23537553",
         "original_zip_name":ZIP_NAME,"status":"NOT_CHECKED",
         "original_3D_runs_code_or_model_metrics_opened":False}
    try:
        raw=fetch(ZENODO,maxbytes=300000)[1]
        meta=json.loads(raw)
        files=meta.get("files") or []
        out["record_id"]=meta.get("id")
        out["original_license"]=(meta.get("metadata") or {}).get("license")
        out["file_catalog"]=[{"key":f.get("key"),"size":f.get("size"),"checksum":f.get("checksum")} for f in files]
        originals=[f for f in files if f.get("key")==ZIP_NAME]
        if len(originals)!=1:raise ValueError("STOP_ZENODO_ZIP_NONUNIQUE")
        one=originals[0]
        url=(one.get("links") or {}).get("self") or (one.get("links") or {}).get("content")
        if not url:raise ValueError("STOP_ZENODO_ORIGINAL_DOWNLOAD_LINK_MISSING")
        full_len=int(one.get("size"))
        out["original_provider_zip_size_bytes"]=full_len
        out["provider_data_url"]=url
        try:out["original_provider_HEAD"]=fetch(url,method="HEAD")[0]
        except Exception as e:out["original_provider_HEAD"]={"status":"STOP","error":str(e)[:180]}
        hr,tail=fetch(url,range_header=f"bytes=-{TAIL_BYTES}",maxbytes=MAX_TAIL)
        out["source_range_http"]=hr
        out["source_tail_returned_bytes"]=len(tail)
        if hr["http"]!=206:raise ValueError("STOP_ORIGINAL_ZIP_SERVER_DOES_NOT_HONOR_RANGE")
        info=eocd_info(tail,full_len)
        out["ZIP_EOCD"]=info
        start=info["directory_offset"];end=start+info["directory_size"]-1
        hdr,dir_bytes=fetch(url,range_header=f"bytes={start}-{end}",maxbytes=MAX_CENTRAL)
        if hdr["http"]!=206 or len(dir_bytes)!=info["directory_size"]:
            raise ValueError("STOP_ZIP_CENTRAL_RANGE_NOT_EXACT")
        catalog=central_zip_names(dir_bytes)
        if len(catalog)!=info["member_count"]:
            raise ValueError("STOP_ZIP_CENTRAL_MEMBER_COUNT_MISMATCH")
        out["original_zip_member_count"]=len(catalog)
        # No member BYTES are opened; only safe manifest path/size/provenance.
        out["original_zip_manifest"]=catalog[:150]
        out["original_zip_manifest_truncated"]=len(catalog)>150
        keys=("code.zip","worlds.zip","source_data/","run_table.json","experiments.json")
        out["source_expected_member_presence"]={x:any(x in row["path"] for row in catalog) for x in keys}
        out["source_published_run_folders_metadata_only"]=[
            x["path"] for x in catalog if x["path"].endswith(("run_table.json","experiments.json"))][:20]
        out["status"]="PASS_ZENODO_OUTER_ZIP_CENTRAL_DIRECTORY_METADATA_ONLY"
    except Exception as e:
        out["status"]="STOP_ZENODO_ORIGINAL_RANGE_OR_CATALOG"
        out["error"]=str(e)[:220]
    return out

def main():
    doc=Path(__file__).resolve().parent/"EXTERNAL_2026_BAT_EEG_AND_3D_ERTF_SOURCE_ADMISSION_V1.md"
    if not doc.exists():raise ValueError("Missing frozen original source research plan")
    result={
      "schema":1,"date":"2026-11-08",
      "status":"SOURCE_ONLY_NO_NEW_BAT_ANALYSIS",
      "original_bat_record_rows_read":False,
      "original_simulated_3D_run_metrics_or_model_weights_read":False,
      "no_new_bat_measurements":True,
      "no_original_source_bytes_committed":True,
      "three_species_policy_prior_art_2026_Teshima_DOI":"10.1098/rspb.2026.1463",
      "sources":{"actual_Eptesicus_neural_EEG_2026":dryad_gate(),
                 "synthetic_3D_echoacoustic_ERTF_2026":zenodo_gate()}
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    for key,v in result["sources"].items():
        print("ORIGINAL_ARCHIVE_SOURCE_GATE",key,v["status"])
        print("SOURCE_METADATA",key,json.dumps(v,ensure_ascii=False,sort_keys=True)[:18000])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
