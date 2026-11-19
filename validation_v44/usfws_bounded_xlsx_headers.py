#!/usr/bin/env python3
"""v44 bounded CRC-verified USFWS selected XLSX HEADER-ONLY admission.

One 65KB last-tail original HTTP 206; selectively request at most two exact
compressed original ZIP members under frozen 12 MB/member cap. NO bat pass
counts, GPS, species values, station names or recording data are interpreted.
"""
from __future__ import annotations

import argparse
import binascii
import collections
import hashlib
import io
import json
import re
import struct
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

from usfws_zip_range_directory import (
    ORIGINAL_TOTAL,TAIL_BYTES,central_location,http_range,
)
from usfws_zip_in_tail_v43a import PINNED_TAIL_SHA256

URL="https://iris.fws.gov/APPS/ServCat/DownloadFile/165800?Reference=112151"
OUT=Path("validation_v44/results/usfws_selected_original_headers_v44.json")
MAX_COMPRESSED=12_000_000
MAX_MEMBER=30_000_000
MAX_LOCAL_EXTRA=4096
MAX_LOCAL_NAME=1024
MAX_INNER_XLSX_TOTAL=40_000_000
MAX_SHARED_XML=20_000_000
MAX_HEADER_CELLS=130
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CATEGORY_WORDS=(
    "night","pass","count","species","detector","record","file","wac",
    "effort","hours","minutes","duration","site","survey","date","time",
    "station","start","end","quality","valid","total","metadata",
    "failure","missing","operation","deployment","source","year","region",
)


def full_directory_entries(data, expected):
    """Internal entries include member name and local offsets; NEVER export them."""
    pos=0
    entries=[]
    while pos<len(data):
        if pos+46>len(data):
            raise ValueError("CENTRAL_DIRECTORY_TRUNCATED")
        rec=struct.unpack_from("<I6H3I5H2I",data,pos)
        if rec[0]!=0x02014b50:
            raise ValueError("CENTRAL_DIRECTORY_BAD_SIGNATURE")
        flags,method,crc,compressed,uncompressed=rec[3],rec[4],rec[7],rec[8],rec[9]
        name_len,extra_len,comment_len,offset=rec[10],rec[11],rec[12],rec[16]
        end=pos+46+name_len+extra_len+comment_len
        if end>len(data):
            raise ValueError("CENTRAL_DIRECTORY_MEMBER_OVERFLOW")
        if 0xffffffff in (compressed,uncompressed,offset):
            raise ValueError("ZIP64_MEMBER_UNSUPPORTED")
        raw=data[pos+46:pos+46+name_len]
        decoded=raw.decode("utf-8" if flags&0x800 else "cp437")
        entries.append({
            "raw_name":raw,"name_internal":decoded,
            "flags":flags,"method":method,"crc":crc,
            "compressed":compressed,"uncompressed":uncompressed,
            "local_offset":offset,
        })
        pos=end
    if len(entries)!=expected:
        raise ValueError("CENTRAL_DIRECTORY_ENTRY_COUNT_MISMATCH")
    return entries


def choose_members(entries):
    """Immutable original source name-category selection: no person/location names."""
    nights=[e for e in entries if all(w in e["name_internal"].casefold() for w in ("night","pass","count"))]
    metas=[e for e in entries if "metadata" in e["name_internal"].casefold()]
    if len(nights)!=1 or len(metas)!=1 or nights[0] is metas[0]:
        return {"status":"SOURCE_MEMBER_SELECTION_AMBIGUOUS_STOP",
                "night_count_candidates":len(nights),
                "metadata_candidates":len(metas)},None
    chosen={"nightly_pass_counts":nights[0],"source_metadata":metas[0]}
    metrics={}
    for key,e in chosen.items():
        metrics[key]={
            "compressed_bytes":e["compressed"],
            "original_uncompressed_bytes":e["uncompressed"],
            "zip_compression_method":e["method"],
            "zip_crc32_hex":f"{e['crc']:08x}",
            "within_frozen_compressed_cap":0<e["compressed"]<=MAX_COMPRESSED,
            "within_frozen_uncompressed_cap":0<e["uncompressed"]<=MAX_MEMBER,
        }
    return {"status":"UNIQUE_SOURCE_MEMBERS_IDENTIFIED","original_member_summaries":metrics},chosen


def source_prefix(start,length,fetcher=None):
    """Server can over-answer 206 ending at EOF; accept only exact bounded prefix."""
    if length<=0 or length>MAX_COMPRESSED+MAX_LOCAL_NAME+MAX_LOCAL_EXTRA+30:
        return {"status":"BOUND_INVALID_LENGTH_STOP"},None
    if start<0 or start+length>ORIGINAL_TOTAL:
        return {"status":"BOUND_OUTSIDE_ORIGINAL_ARCHIVE_STOP"},None
    if fetcher is None:
        def fetcher(url,offset,n):
            req=urllib.request.Request(url,headers={
                "Range":f"bytes={offset}-{offset+n-1}",
                "Accept-Encoding":"identity",
                "User-Agent":"boids-v44-official-source-header-only/1.0",
            })
            with urllib.request.urlopen(req,timeout=45) as response:
                # Critical: do not read the server's overbroad range beyond
                # the exact requested subset. Read at most n+1 bytes.
                return response.status,response.headers.get("Content-Range",""),response.read(n+1)
    try:
        status,cr,blob=fetcher(URL,start,length)
    except urllib.error.HTTPError as exc:
        return {"status":"HTTP_ACCESS_STOP","http":exc.code},None
    except (urllib.error.URLError,OSError,TimeoutError) as exc:
        return {"status":"TRANSPORT_STOP","error_type":type(exc).__name__},None
    match=re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)",str(cr).strip())
    valid=(status==206 and match is not None and int(match[1])==start
           and int(match[2])>=start+length-1 and int(match[3])==ORIGINAL_TOTAL
           and len(blob)>=length)
    if not valid:
        return {"status":"SOURCE_RANGE_PREFIX_NOT_VERIFIED_STOP",
                "http":status,"Content_Range_sanitized":str(cr)[:100],
                "received_prefix_bytes_capped":len(blob)},None
    return {"status":"SOURCE_PREFIX_206_VERIFIED",
            "request_bytes":length,
            "returned_prefix_sha256":hashlib.sha256(blob[:length]).hexdigest(),
            "server_reported_overbroad_end":int(match[2])>start+length-1},blob[:length]


def unzip_original_member(compressed,entry):
    if entry["method"]==0:
        raw=compressed
    elif entry["method"]==8:
        inflator=zlib.decompressobj(-15)
        raw=inflator.decompress(compressed,MAX_MEMBER+1)
        if not inflator.eof or inflator.unused_data or inflator.unconsumed_tail:
            raise ValueError("ORIGINAL_DEFLATE_STREAM_NOT_COMPLETE")
    else:
        raise ValueError("ZIP_COMPRESSION_UNSUPPORTED")
    if len(raw)!=entry["uncompressed"] or len(raw)>MAX_MEMBER:
        raise ValueError("ORIGINAL_MEMBER_LENGTH_MISMATCH")
    if (binascii.crc32(raw)&0xffffffff)!=entry["crc"]:
        raise ValueError("ORIGINAL_MEMBER_CRC32_MISMATCH")
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("NESTED_XLSX_CONTAINER_INVALID")
    return raw


def fetch_member(entry,fetcher=None):
    # These caps are frozen before original member sizes are inspected.
    if not (0<entry["compressed"]<=MAX_COMPRESSED
            and 0<entry["uncompressed"]<=MAX_MEMBER):
        return {"status":"ORIGINAL_SELECTED_MEMBER_CAP_STOP"},None
    begin=entry["local_offset"]
    receipt,header=source_prefix(begin,30,fetcher)
    if header is None:
        return {"status":"ORIGINAL_LOCAL_HEADER_RANGE_STOP","receipt":receipt},None
    rec=struct.unpack("<IHHHHHIIIHH",header)
    sig,version,flags,method,tm,dt,crc,cs,us,name_len,extra_len=rec
    if sig!=0x04034b50 or flags&1 or method!=entry["method"] or flags!=entry["flags"]:
        return {"status":"ORIGINAL_LOCAL_HEADER_MISMATCH_STOP"},None
    if name_len>MAX_LOCAL_NAME or extra_len>MAX_LOCAL_EXTRA:
        return {"status":"ORIGINAL_LOCAL_HEADER_NAME_EXTRA_CAP_STOP"},None
    total=30+name_len+extra_len+entry["compressed"]
    full_receipt,blob=source_prefix(begin,total,fetcher)
    if blob is None:
        return {"status":"ORIGINAL_COMPRESSED_MEMBER_RANGE_STOP","receipt":full_receipt},None
    if blob[:30]!=header or blob[30:30+name_len]!=entry["raw_name"]:
        return {"status":"ORIGINAL_LOCAL_FILENAME_OR_HEADER_MISMATCH_STOP"},None
    comp=blob[30+name_len+extra_len:]
    try:
        raw=unzip_original_member(comp,entry)
    except (OSError,ValueError,zlib.error) as exc:
        return {"status":"ORIGINAL_MEMBER_INTEGRITY_STOP",
                "failure_class":type(exc).__name__},None
    return {"status":"ORIGINAL_CRC32_AND_SIZE_VERIFIED",
            "selected_original_member_compressed_bytes":entry["compressed"],
            "selected_original_member_uncompressed_bytes":len(raw),
            "selected_original_member_crc32_hex":f"{entry['crc']:08x}",
            "server_returned_overbroad_prefix":bool(full_receipt.get("server_reported_overbroad_end")),
            "full_archive_checksum_not_claimed":True},raw


def original_xlsx_headers(raw):
    """Interpret first row text only; no original animal or source-record values."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.infolist()
        if (sum(x.file_size for x in info)>MAX_INNER_XLSX_TOTAL or
            any(x.file_size>MAX_INNER_XLSX_TOTAL for x in info)):
            return {"status":"ORIGINAL_NESTED_XLSX_UNZIPPED_CAP_STOP"}
        filenames=set(z.namelist())
        if "xl/workbook.xml" not in filenames:
            return {"status":"ORIGINAL_XLSX_WORKBOOK_XML_MISSING_STOP"}
        book=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=[x.attrib.get("name","") for x in book.iter(NS+"sheet")]
        paths=sorted(p for p in filenames if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",p))
        hdr=[]
        shared_interest=set()
        for member in paths[:8]:
            label_refs=[]
            with z.open(member) as fh:
                for _,row in ET.iterparse(fh,events=("end",)):
                    if row.tag!=NS+"row":continue
                    for cell in list(row)[:MAX_HEADER_CELLS]:
                        typ=cell.attrib.get("t","")
                        v=cell.find(NS+"v")
                        if typ=="s" and v is not None:
                            try:
                                ix=int(v.text)
                                shared_interest.add(ix)
                                label_refs.append(("shared",ix))
                            except (ValueError,TypeError):
                                label_refs.append(("empty",None))
                        elif typ=="inlineStr":
                            label_refs.append(("inline","".join(t.text or "" for t in cell.iter(NS+"t"))))
                        else:
                            label_refs.append(("empty",None))
                    break
            hdr.append({"sheet_path_category":"worksheet","header_refs":label_refs})
        wanted={}
        if shared_interest and "xl/sharedStrings.xml" in filenames:
            si=z.getinfo("xl/sharedStrings.xml")
            if si.file_size>MAX_SHARED_XML:
                return {"status":"ORIGINAL_XLSX_SHARED_STRING_CAP_STOP"}
            with z.open("xl/sharedStrings.xml") as fh:
                index=0
                for _,element in ET.iterparse(fh,events=("end",)):
                    if element.tag==NS+"si":
                        if index in shared_interest:
                            wanted[index]="".join(t.text or "" for t in element.iter(NS+"t"))
                        index+=1
                        element.clear()
        results=[]
        for sheet in hdr:
            names=[(wanted.get(v,"") if typ=="shared" else (v if typ=="inline" else ""))
                   for typ,v in sheet["header_refs"]]
            key=sorted({k for name in names for k in CATEGORY_WORDS if k in name.casefold()})
            results.append({"first_row_field_n":len(names),
                            "first_row_header_keyword_categories":key,
                            "has_structural_effort_or_time_keywords":
                            any(x in key for x in ("effort","hours","minutes","duration","wac","night","date","time"))})
        return {"status":"ORIGINAL_XLSX_FIRST_ROW_HEADERS_ONLY",
                "workbook_sheet_count":len(sheets),
                "workbook_title_keyword_categories":sorted({k for s in sheets for k in CATEGORY_WORDS if k in s.casefold()}),
                "worksheet_xml_count":len(paths),
                "first_eight_sheet_header_keyword_summary":results,
                "numeric_bat_counts_or_record_values_decoded":False,
                "raw_original_sheet_or_station_names_exported":False}


def run(fetcher=None,expected_tail=PINNED_TAIL_SHA256):
    out={
        "programme":"v44_official_usfws_original_two_workbooks_header_only",
        "original_usfws_reference":112151,
        "original_download_id":165800,
        "official_total_original_bytes":ORIGINAL_TOTAL,
        "original_v42_full_source_size_cap_stop_retained":True,
        "original_v43_exact_second_range_transport_stop_retained":True,
        "original_v43a_directory_pass_retained":True,
        "complete_original_zip_sha256_verified":False,
        "numeric_bat_pass_counts_or_species_values_decoded":False,
        "original_site_member_filenames_or_locations_exported":False,
        "full_detector_effort_or_true_zero_nights_verified":False,
        "bat_activity_or_ecological_model_fitted":False,
        "member_receipts":{},
    }
    start=ORIGINAL_TOTAL-TAIL_BYTES
    receipt,tail=http_range(start,ORIGINAL_TOTAL-1,fetcher=(
        (lambda url,s,e:fetcher(url,s,e-s+1)) if fetcher is not None else None))
    out["tail_receipt"]=receipt
    if tail is None:
        out["status"]="TAIL_SOURCE_RANGE_STOP";return out
    tail_hash=hashlib.sha256(tail).hexdigest()
    out["pinned_tail_sha256_verified"]=tail_hash==expected_tail
    if tail_hash!=expected_tail:
        out["status"]="PINNED_TAIL_SOURCE_CHANGED_STOP";return out
    cd=central_location(tail)
    out["zip_central_directory_info"]=cd
    if cd["status"]!="STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED":
        out["status"]="ZIP_DIRECTORY_STRUCTURE_STOP";return out
    relative=cd["central_directory_offset"]-start
    if relative<0 or relative+cd["central_directory_size"]>len(tail)-22:
        out["status"]="DIRECTORY_OUTSIDE_EXACT_PINNED_TAIL_STOP";return out
    try:
        entries=full_directory_entries(
            tail[relative:relative+cd["central_directory_size"]],
            cd["declared_entry_count"])
    except (UnicodeDecodeError,ValueError,struct.error) as exc:
        out["status"]="ORIGINAL_CENTRAL_DIRECTORY_PARSE_STOP"
        out["error_type"]=type(exc).__name__;return out
    selection,chosen=choose_members(entries)
    out["member_selection"]=selection
    if chosen is None:
        out["status"]="ORIGINAL_MEMBER_SELECTION_STOP";return out
    for category,entry in chosen.items():
        result,bytes_=fetch_member(entry,fetcher)
        out["member_receipts"][category]=result
        if bytes_ is None:
            out["status"]="ORIGINAL_MEMBER_CAPPED_OR_INTEGRITY_STOP";return out
        try:
            schema=original_xlsx_headers(bytes_)
        except (ET.ParseError,KeyError,OSError,ValueError,zipfile.BadZipFile) as exc:
            out["member_receipts"][category]["xlsx_status"]="ORIGINAL_XLSX_FIRST_ROW_PARSE_STOP"
            out["status"]="ORIGINAL_XLSX_FIRST_ROW_PARSE_STOP";return out
        out["member_receipts"][category]["xlsx_schema"]=schema
        if schema["status"]!="ORIGINAL_XLSX_FIRST_ROW_HEADERS_ONLY":
            out["status"]="ORIGINAL_XLSX_SCHEMA_CAP_OR_MISSING_STOP";return out
    out["status"]="ORIGINAL_WORKBOOK_HEADERS_VERIFIED_SOURCE_ONLY"
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V44_USFWS_SELECTIVE_SOURCE_HEADERS="+json.dumps(result,sort_keys=True))
    assert result["numeric_bat_pass_counts_or_species_values_decoded"] is False
    assert result["full_detector_effort_or_true_zero_nights_verified"] is False
    assert result["bat_activity_or_ecological_model_fitted"] is False
