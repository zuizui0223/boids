"""PNAS Molossus 2024 original supplemental XLSX HEADER/schema inventory ONLY.

Source originally published; original cells except exact first header row are
not read. This stage has no bat attacks/capture data opening or source IDs.
Transient publisher ZIP bytes are not committed/uploaded.
"""
from __future__ import annotations
from pathlib import Path
import io,json,zipfile,xml.etree.ElementTree as ET,re,hashlib

from molossus_2024_supplement_structure_v1 import (
 download_bounded,URL,EXPECTED,MAX_XLSX
)
OUT=Path(__file__).resolve().parent/"MOLOSSUS_2024_ORIGINAL_XLSX_HEADER_SCHEMA_V1.json"
N={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def sharedstring_labels(zipfile_member):
    if "xl/sharedStrings.xml" not in zipfile_member.namelist():
        return []
    root=ET.fromstring(zipfile_member.read("xl/sharedStrings.xml"))
    # We must parse the source string-table to resolve the header's indices,
    # but only header indices are returned. Source response values NOT emitted.
    return ["".join((x.text or "") for x in child.findall(".//m:t",N))
            for child in root.findall("m:si",N)]
def first_header(zipfile_member,shared):
    sheet="xl/worksheets/sheet1.xml"
    if sheet not in zipfile_member.namelist():raise ValueError("STOP_XLSX_NO_SHEET1")
    root_open=zipfile_member.open(sheet)
    header_row=None
    for event,element in ET.iterparse(root_open,events=("end",)):
        if element.tag.endswith("}row"):
            if element.get("r")=="1":
                header_row=element
            break
    if header_row is None:raise ValueError("STOP_ORIGINAL_SHEET_NO_ROW1")
    fields=[]
    for cell in header_row.findall("m:c",N):
        address=cell.get("r")
        kind=cell.get("t")
        v=cell.find("m:v",N)
        inline=cell.find("m:is",N)
        if kind=="s" and v is not None:
            ix=int(v.text)
            label=shared[ix] if 0<=ix<len(shared) else "STOP_INVALID_SHARED_STRING_INDEX"
        elif kind=="inlineStr" and inline is not None:
            label="".join(x.text or "" for x in inline.findall(".//m:t",N))
        elif v is not None:
            label=v.text
        else:
            label=None
        fields.append({"header_address":address,"header_string":str(label)[:140],
                       "header_cell_type":kind})
    return fields
def main():
    out={"schema":1,"source_pmc":"PMC11287165",
         "source_original_pnas_doi":"10.1073/pnas.2321724121",
         "source_http_URL":URL,"source_file_basename":EXPECTED,
         "source_animal_rows_or_values_opened":False,
         "source_animal_IDs_or_timestamps_exported":False,
         "new_bat_measurements":False,
         "original_workbook_redistributed":False,
         "status":"NOT_CHECKED"}
    try:
        bundle,status,ctype=download_bounded(URL)
        z=zipfile.ZipFile(io.BytesIO(bundle))
        member=[x for x in z.infolist() if x.filename.split("/")[-1]==EXPECTED]
        if len(member)!=1:raise ValueError("STOP_ORIGINAL_WORKBOOK_MISSING_OR_DUPLICATE")
        if member[0].file_size>MAX_XLSX:raise ValueError("STOP_ORIGINAL_WORKBOOK_TOO_LARGE")
        raw=z.read(member[0])
        out["original_workbook_sha256"]=hashlib.sha256(raw).hexdigest()
        out["original_workbook_bytes"]=len(raw)
        x=zipfile.ZipFile(io.BytesIO(raw))
        shared=sharedstring_labels(x)
        out["original_XLSX_shared_string_count"]=len(shared)
        out["original_header_8cols"]=first_header(x,shared)
        out["original_headers_count"]=len(out["original_header_8cols"])
        out["source_excel_dimensions_previous_gate"]="A1:H4300"
        out["status"]="PASS_original_PNAS_XLSX_header_only"
    except Exception as exc:
        out["status"]="STOP_original_XLSX_header_or_source"
        out["error"]=type(exc).__name__+":"+str(exc)[:240]
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("SOURCE_XLSX_HEADER_GATE",out["status"])
    print("SOURCE_PIN",out.get("original_workbook_sha256"),out.get("original_workbook_bytes"))
    print("ORIGINAL_HEADERS",out.get("original_header_8cols"))
    if out.get("error"):print("SOURCE_STOP_REASON",out["error"])
    return 0
if __name__=="__main__":raise SystemExit(main())
