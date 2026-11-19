#!/usr/bin/env python3
"""v42 USFWS exact original archive source-only admission, no bat outcomes."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

SOURCE="https://iris.fws.gov/APPS/ServCat/DownloadFile/165800?Reference=112151"
OUT=Path("validation_v42/results/usfws_bat_nightly_pass_source_v42.json")
MAX_ZIP=100_000_000
MAX_XLSX=12_000_000
MAX_XLSX_COUNT=20
TERMS=("night","pass","effort","recorder","detector","wac","date","species",
       "start","end","duration","survey","site","activity","hours","count")
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def word_categories(s: str):
    return sorted({k for k in TERMS if k in s.casefold()})

def xlsx_metadata(payload):
    if not zipfile.is_zipfile(io.BytesIO(payload)):return {"status":"NESTED_XLSX_INVALID"}
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        members=set(z.namelist())
        if "xl/workbook.xml" not in members:
            return {"status":"NOT_XLSX"}
        w=ET.fromstring(z.read("xl/workbook.xml"))
        sheetnames=[x.attrib.get("name","") for x in w.iter(NS+"sheet")]
        shared=[]
        if "xl/sharedStrings.xml" in members and z.getinfo("xl/sharedStrings.xml").file_size<=4_000_000:
            text=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(k.text or "" for k in si.iter(NS+"t")) for si in text.findall(NS+"si")]
        sheets=[]
        for member in sorted(x for x in members if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",x))[:5]:
            if z.getinfo(member).file_size>10_000_000:continue
            colcount=0;categorical=[]
            with z.open(member) as f:
                for _,el in ET.iterparse(f,events=("end",)):
                    if el.tag!=NS+"row":continue
                    for cell in list(el)[:100]:
                        colcount+=1
                        typ=cell.attrib.get("t","")
                        v=cell.find(NS+"v")
                        if typ=="s" and v is not None:
                            try:label=shared[int(v.text)]
                            except (ValueError,IndexError,TypeError):label=""
                        elif typ=="inlineStr":
                            label="".join(k.text or "" for k in cell.iter(NS+"t"))
                        else:
                            label="" # Numeric not read as any bat value
                        categorical.extend(word_categories(label))
                    break
            sheets.append({"first_row_column_count":colcount,
                           "header_keyword_categories":sorted(set(categorical))})
        return {"status":"XLSX_HEADERS_ONLY",
                "workbook_sheet_count":len(sheetnames),
                "worksheet_title_keyword_categories":sorted(set(
                    x for n in sheetnames for x in word_categories(n))),
                "first_five_worksheet_header_categories":sheets,
                "original_numeric_bat_pass_count_values_opened":False}

def zip_info(raw):
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        return {"status":"ORIGINAL_ZIP_INVALID_STOP"}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=[x for x in z.infolist() if not x.is_dir()]
        suffixes=Counter(Path(x.filename).suffix.lower() for x in members)
        categories=Counter(t for x in members for t in word_categories(x.filename))
        candidates=[x for x in members if Path(x.filename).suffix.lower()==".xlsx" and
                    x.file_size<=MAX_XLSX]
        summaries=[]
        for m in candidates[:MAX_XLSX_COUNT]:
            try:
                out=xlsx_metadata(z.read(m))
            except (OSError,ValueError,ET.ParseError,zipfile.BadZipFile):
                out={"status":"NESTED_XLSX_PARSE_STOP"}
            summaries.append(out)
        return {
            "status":"ORIGINAL_ZIP_CENTRAL_DIRECTORY_AND_XLSX_HEADERS_ONLY",
            "archive_entry_count":len(members),
            "total_uncompressed_bytes_in_central_directory":sum(x.file_size for x in members),
            "largest_original_member_bytes":max((x.file_size for x in members),default=0),
            "original_member_extension_counts":dict(suffixes),
            "source_filename_keyword_categories":dict(categories),
            "xlsx_member_n":sum(suffixes[k] for k in (".xlsx",)),
            "xlsx_safely_read_n":len(summaries),
            "xlsx_header_structural_previews":summaries,
            "exact_original_site_names_or_coordinates_exported":False,
            "original_numeric_bat_pass_counts_or_species_values_opened":False,
        }

def source_fetch(fetcher=None):
    if fetcher is None:
        def fetcher(url):
            req=urllib.request.Request(url,headers={
                "User-Agent":"boids-v42-official-usfws-source-audit/1.0",
                "Accept":"application/zip,application/octet-stream,*/*;q=0.2"})
            with urllib.request.urlopen(req,timeout=40) as r:
                status=r.status
                content_type=r.headers.get("Content-Type","")
                content_length=r.headers.get("Content-Length")
                buf=io.BytesIO()
                while buf.tell()<=MAX_ZIP:
                    block=r.read(1<<20)
                    if not block:break
                    buf.write(block)
                return status,content_type,content_length,buf.getvalue()
    report={"official_source_url":SOURCE,"reference_id":112151,"original_downloadfile_id":165800,
            "source_only":True,"raw_site_geolocation_exported":False,
            "bat_numerical_activity_values_opened":False,"acoustic_model_fitted":False,
            "complete_zero_night_effort_qualified":False}
    try:
        status,typ,length,raw=fetcher(SOURCE)
    except urllib.error.HTTPError as e:
        report.update({"status":"HTTP_ACCESS_STOP","http_status":e.code})
        return report
    except (urllib.error.URLError,OSError,TimeoutError) as e:
        report.update({"status":"SOURCE_TRANSPORT_STOP","error_type":type(e).__name__})
        return report
    report.update({"http_status":status,"content_type":str(typ)[:120],
                   "reported_content_length_bytes":str(length)[:30],
                   "received_bytes":len(raw)})
    leading=raw[:1024].lstrip().lower()
    if status!=200 or len(raw)>MAX_ZIP:
        report["status"]="SOURCE_HTTP_OR_SIZE_CAP_STOP";return report
    if leading.startswith((b"<html",b"<!doctype",b"{",b"[")):
        report["status"]="SOURCE_HTML_OR_JSON_STOP";return report
    report["source_sha256"]=hashlib.sha256(raw).hexdigest()
    report.update(zip_info(raw))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
    a=p.parse_args()
    result=source_fetch()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V42_USFWS_OFFICIAL_SOURCE_ONLY="+json.dumps(result,sort_keys=True))
    assert result["bat_numerical_activity_values_opened"] is False
    assert result["acoustic_model_fitted"] is False
    assert result["complete_zero_night_effort_qualified"] is False

if __name__=="__main__":
    main()
