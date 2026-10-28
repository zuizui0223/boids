#!/usr/bin/env python3
"""Original published PLOS Biology 2019 S3 pairing-table source probe.

Downloads only publisher/PMC supplementary XLSX (no GPS/weather),
SHA256-pins exact source and inspects identifier-bearing text with OOXML
stdlib; numeric body measurements are masked. NO movement scores.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

SOURCE_DOI = "10.1371/journal.pbio.3000299.s008"
PAPER_DOI = "10.1371/journal.pbio.3000299"
BINARY_CANDIDATES = (
    "https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3000299.s008&type=supplementary",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC6581236/bin/pbio.3000299.s008.xlsx",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6581236/bin/pbio.3000299.s008.xlsx",
)
MAX_BYTES = 5_000_000
NS = {"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ID = re.compile(r"\b[BS]\d{2}\b", re.I)


def acquire_supplement(path: Path) -> dict:
    attempts=[]
    for url in BINARY_CANDIDATES:
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 boids-v17-original-s3-table/1.0",
                "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*"
            })
            with urllib.request.urlopen(req,timeout=45) as response:
                claimed=response.headers.get("Content-Length")
                if claimed and int(claimed)>MAX_BYTES:
                    raise ValueError("Supplement larger than fixed safety cap")
                b=response.read(MAX_BYTES+1)
                content_type=response.headers.get("Content-Type","")
            if len(b)>MAX_BYTES or len(b)<100:
                raise ValueError("Invalid supplementary byte size")
            if not b.startswith(b"PK\x03\x04"):
                raise ValueError("Response is not an XLSX ZIP")
            path.write_bytes(b)
            with zipfile.ZipFile(path) as archive:
                names=archive.namelist()
                if "xl/workbook.xml" not in names or not any(
                        name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
                        for name in names):
                    raise ValueError("ZIP lacks OOXML workbook and worksheet")
            return {
                "status":"PUBLISHED_SUPPLEMENT_BYTES_VERIFIED",
                "source_doi":SOURCE_DOI,
                "url":url,
                "bytes":len(b),
                "sha256":hashlib.sha256(b).hexdigest(),
                "content_type":content_type,
                "attempts_before_success":attempts
            }
        except Exception as e:
            attempts.append({"url":url, "status":"UNAVAILABLE",
                             "reason":type(e).__name__+": "+str(e)[:160]})
    return {"status":"SUPPLEMENT_NOT_RETRIEVABLE",
            "source_doi":SOURCE_DOI,"attempts":attempts}


def read_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    tree=ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS))
            for si in tree.findall("m:si",NS)]


def col_name(reference: str) -> str:
    match=re.match(r"([A-Z]+)",reference)
    return match.group(1) if match else ""


def cell_value(cell:ET.Element,strings:list[str]) -> str:
    t=cell.attrib.get("t","")
    val=cell.find("m:v",NS)
    inline=cell.find("m:is",NS)
    if t=="s" and val is not None:
        try:
            return strings[int(val.text or "-1")]
        except (ValueError,IndexError):
            return ""
    if t=="inlineStr" and inline is not None:
        return "".join(x.text or "" for x in inline.findall(".//m:t",NS))
    if t in ("str","e") and val is not None:
        return val.text or ""
    if val is not None:
        return val.text or ""
    return ""


def mask_text(raw: str) -> str:
    txt=" ".join(str(raw).strip().split())
    if not txt:
        return ""
    if len(txt)>100:
        return "<text too long>"
    if re.fullmatch(r"[-+0-9.,% ]+",txt):
        return "<numeric body trait masked>"
    return txt


def parse_workbook(path:Path) -> dict:
    with zipfile.ZipFile(path) as arc:
        names=arc.namelist()
        if len(names)!=len(set(names)):
            raise ValueError("Duplicate OOXML member")
        if len(names)>500 or sum(z.file_size for z in arc.infolist())>15_000_000:
            raise ValueError("Oversized/decompression-bomb XLSX")
        strings=read_strings(arc)
        sheets=sorted(x for x in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",x))
        report=[]
        all_ids=set()
        for source in sheets:
            tree=ET.fromstring(arc.read(source))
            preview=[]
            row_count=0
            candidate_id_count=0
            for row in tree.findall(".//m:sheetData/m:row",NS):
                row_count+=1
                number=int(row.attrib.get("r",row_count))
                cells={}
                ids=[]
                for c in row.findall("m:c",NS):
                    col=col_name(c.attrib.get("r",""))
                    if not col: continue
                    text=mask_text(cell_value(c,strings))
                    if text:
                        cells[col]=text
                        matches=ID.findall(text)
                        ids += [x.upper() for x in matches]
                        all_ids.update(x.upper() for x in matches)
                candidate_id_count+=len(ids)
                if number<=35:
                    preview.append({"row":number,
                                    "text_only_cells":cells,
                                    "bird_ID_tokens":sorted(set(ids))})
            report.append({
                "sheet_source":source,
                "rows":row_count,
                "preview_first_35_rows_numeric_body_traits_masked":preview,
                "all_bird_id_tokens_in_sheet":candidate_id_count,
            })
        return {"status":"ORIGINAL_S3_TEXT_PREVIEW_ONLY_NO_GRAPH_YET",
                "workbook_sheets":len(sheets),
                "worksheet_reports":report,
                "distinct_bird_identifiers_from_s3":sorted(all_ids),
                "telemetry_rows_processed":0,
                "flight_turns_scored":0,
                "weather_or_GPS_data_read":False}


def run()->dict:
    with TemporaryDirectory() as temp:
        path=Path(temp)/"published_s3.xlsx"
        obtained=acquire_supplement(path)
        result={"study":"v17-original-2019-S3-pair-ledger-provenance",
                "source_paper_doi":PAPER_DOI,
                "source_table_doi":SOURCE_DOI,
                "download":obtained,
                "result_status":obtained["status"],
                "no_animal_trajectory_outcomes_read":True}
        if obtained["status"]=="PUBLISHED_SUPPLEMENT_BYTES_VERIFIED":
            result["spreadsheet_structure"]=parse_workbook(path)
        return result


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
                   default=Path("validation_v17/results/published_S3_pairing_source_v17.json"))
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                                 indent=2,allow_nan=False)+"\n")
    print("V17_B_S3_PROVENANCE",json.dumps(result["download"],sort_keys=True))
    if "spreadsheet_structure" in result:
        print("V17_B_S3_SOURCE_TEXT",json.dumps(result["spreadsheet_structure"],
                                              ensure_ascii=False,sort_keys=True))
    print("V17_B_NO_GPS_OR_WIND_OUTCOME_ANALYSIS")


if __name__=="__main__":
    main()
