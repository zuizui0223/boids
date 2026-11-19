#!/usr/bin/env python3
"""v43 official USFWS original ZIP metadata-only HTTP Range (no original files)."""
import argparse,collections,hashlib,json,re,struct,urllib.request,urllib.error
from pathlib import Path

URL="https://iris.fws.gov/APPS/ServCat/DownloadFile/165800?Reference=112151"
ORIGINAL_TOTAL=495216105 # recorded from v42 official Content-Length before v43
TAIL_BYTES=65536
MAX_CD=4_000_000
RANGE_IGNORED_CAP=1_000_000
OUT=Path("validation_v43/results/usfws_official_zip_range_directory_v43.json")
KEYWORDS=("night","pass","count","metadata","effort","wac","survey","detector","recorder","list","site")

def http_range(start,end,fetcher=None):
    if fetcher is None:
        def fetcher(url,start,end):
            req=urllib.request.Request(url,headers={
                "Range":f"bytes={start}-{end}","Accept-Encoding":"identity",
                "User-Agent":"boids-v43-usfws-source-range-metadata/1.0"})
            with urllib.request.urlopen(req,timeout=28) as r:
                # If the server ignores Range, consume no more than 1 MB.
                # For 206, consume only the requested interval plus 1 byte
                # to detect a malformed oversized response.
                limit = (end-start+2) if r.status==206 else RANGE_IGNORED_CAP
                return r.status,r.headers.get("Content-Range",""),r.read(limit)
    try:
        status,cr,data=fetcher(URL,start,end)
    except urllib.error.HTTPError as e:
        return {"status":"HTTP_ACCESS_STOP","http_status":e.code},None
    except (urllib.error.URLError,OSError,TimeoutError) as e:
        return {"status":"TRANSPORT_STOP","error_type":type(e).__name__},None
    expected=f"bytes {start}-{end}/{ORIGINAL_TOTAL}"
    if status!=206 or cr.strip()!=expected or len(data)!=end-start+1:
        return {"status":"RANGE_NOT_VERIFIED_STOP",
                "http_status":status,"reported_content_range":str(cr)[:120],
                "response_bytes_capped":len(data)},None
    return {"status":"RANGE_CONFIRMED_206","http_status":206,
            "start":start,"end":end,"received_bytes":len(data),
            "range_payload_sha256":hashlib.sha256(data).hexdigest()},data

def central_location(tail):
    sig=b"PK\x05\x06"
    p=tail.rfind(sig)
    if p<0 or p+22>len(tail):return {"status":"ZIP_END_RECORD_NOT_FOUND_STOP"}
    s,disk,cd_disk,disk_n,total_n,cd_size,cd_offset,comment_len=struct.unpack_from("<IHHHHIIH",tail,p)
    if s!=0x06054b50 or p+22+comment_len!=len(tail):
        return {"status":"ZIP_END_RECORD_INVALID_STOP"}
    if disk!=0 or cd_disk!=0 or disk_n!=total_n or 0xffff in (disk_n,total_n) or 0xffffffff in (cd_size,cd_offset):
        return {"status":"ZIP64_OR_MULTIDISK_NOT_SUPPORTED_STOP"}
    if cd_size<=0 or cd_size>MAX_CD or cd_offset+cd_size>ORIGINAL_TOTAL:
        return {"status":"ZIP_DIRECTORY_SIZE_OR_OFFSET_STOP",
                "central_directory_size":cd_size,"central_directory_offset":cd_offset}
    return {"status":"STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED",
            "declared_entry_count":total_n,
            "central_directory_offset":cd_offset,
            "central_directory_size":cd_size,
            "has_zip_comment":comment_len>0}

def scan_directory(data,expected):
    # ZIP central-file header: fixed 46 bytes followed by filename, extras, comment
    p=0;n=0;extensions=collections.Counter();wordcount=collections.Counter()
    maxsize=0;file_size_sum=0;compressed_sum=0
    while p<len(data):
        if p+46>len(data):
            return {"status":"CENTRAL_DIRECTORY_TRUNCATED_STOP","parsed_entries":n}
        v=struct.unpack_from("<I6H3I5H2I",data,p)
        if v[0]!=0x02014b50:
            return {"status":"CENTRAL_DIRECTORY_BAD_SIGNATURE_STOP","parsed_entries":n}
        compressed=v[8];uncompressed=v[9]
        namelen=v[10];extra=v[11];comment=v[12]
        localoffset=v[16]
        if 0xffffffff in (compressed,uncompressed,localoffset):
            return {"status":"ZIP64_MEMBER_UNSUPPORTED_STOP","parsed_entries":n}
        end=p+46+namelen+extra+comment
        if end>len(data):return {"status":"CENTRAL_DIRECTORY_MEMBER_OVERFLOW_STOP","parsed_entries":n}
        flags=v[3]
        rawname=data[p+46:p+46+namelen]
        try:name=rawname.decode("utf-8" if flags&0x0800 else "cp437")
        except UnicodeDecodeError:name=""
        suffix=("."+name.rsplit(".",1)[-1].lower()) if "." in name.rsplit("/",1)[-1] else "(none)"
        extensions[suffix]+=1
        for key in KEYWORDS:
            if key in name.casefold():wordcount[key]+=1
        maxsize=max(maxsize,uncompressed);file_size_sum+=uncompressed;compressed_sum+=compressed
        p=end;n+=1
    if n!=expected:
        return {"status":"CENTRAL_DIRECTORY_COUNT_MISMATCH_STOP",
                "parsed_entries":n,"declared_entries":expected}
    return {"status":"CENTRAL_DIRECTORY_INDEX_VERIFIED_SOURCE_ONLY",
            "directory_entry_count":n,
            "original_member_extension_counts":dict(extensions),
            "source_filename_keyword_categories":dict(wordcount),
            "sum_original_uncompressed_member_bytes":file_size_sum,
            "sum_original_compressed_member_bytes":compressed_sum,
            "largest_member_uncompressed_bytes":maxsize,
            "no_original_site_names_or_filename_strings_exported":True,
            "no_numeric_bat_recording_or_species_values_read":True}

def run(fetcher=None):
    result={"original_USFWS_reference":112151,"original_USFWS_download_id":165800,
            "official_original_total_bytes_from_v42":ORIGINAL_TOTAL,
            "v42_whole_archive_size_cap_stop_unchanged":True,
            "range_only_source_metadata":True,"complete_source_bitstream_checksum_verified":False,
            "numeric_bat_detection_or_activity_outcome_opened":False,
            "no_nights_assumed_zero":True,"behavior_model_fitted":False,
            "qualified_complete_sampling_effort":False}
    tail_start=ORIGINAL_TOTAL-TAIL_BYTES
    t,tail=http_range(tail_start,ORIGINAL_TOTAL-1,fetcher)
    result["tail_range_receipt"]=t
    if tail is None:
        result["status"]="TAIL_RANGE_SOURCE_STOP";return result
    loc=central_location(tail)
    result["central_directory_locator"]=loc
    if loc["status"]!="STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED":
        result["status"]="ZIP_CENTRAL_LOCATION_STOP";return result
    start=loc["central_directory_offset"]
    size=loc["central_directory_size"]
    d,buf=http_range(start,start+size-1,fetcher)
    result["central_directory_range_receipt"]=d
    if buf is None:
        result["status"]="CENTRAL_DIRECTORY_RANGE_SOURCE_STOP";return result
    parsed=scan_directory(buf,loc["declared_entry_count"])
    result["central_directory_metadata"]=parsed
    result["status"]=parsed["status"]
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("V43_USFWS_ZIP_CENTRAL_DIRECTORY="+json.dumps(r,sort_keys=True))
    assert r["numeric_bat_detection_or_activity_outcome_opened"] is False
    assert r["v42_whole_archive_size_cap_stop_unchanged"] is True
    assert r["qualified_complete_sampling_effort"] is False
