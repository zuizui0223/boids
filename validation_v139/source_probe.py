"""v139: download and inspect genuine Roscoff fish soundscape supplementary data.

The original XLSX is NOT committed. The manifest contains source SHA256,
worksheet layout, column headings and first five rows only. Never infer
biological rates or interactions from incomplete/masked time bins.
"""
from __future__ import annotations
import hashlib
import io
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

SRC="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13179613/supplementaryFiles?includeInlineImage=false"
FILENAME="12862_2026_2521_MOESM2_ESM.xlsx"
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v137"))
from appendix_site_macro import read_xlsx_table_rows

def acquire():
    req=Request(SRC,headers={"User-Agent":"OpenScienceSourceAudit/1.0 (repository source validation)","Accept":"application/zip, */*"})
    with urlopen(req,timeout=45) as response:
        buf=response.read(40*1024*1024+1)
    if len(buf)>40*1024*1024 or not zipfile.is_zipfile(io.BytesIO(buf)):
        raise ValueError("Invalid or oversized source bundle")
    with zipfile.ZipFile(io.BytesIO(buf)) as z:
        hits=[n for n in z.namelist() if n.rsplit("/",1)[-1].lower()==FILENAME.lower()]
        if len(hits)!=1:
            raise ValueError("Original XLSX unavailable or ambiguous: "+str(z.namelist())[:800])
        raw=z.read(hits[0])
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Named attachment not a real XLSX")
    with zipfile.ZipFile(io.BytesIO(raw)) as sheetz:
        if "xl/workbook.xml" not in sheetz.namelist():
            raise ValueError("File isn't an original xlsx spreadsheet")
    return raw

def audit(raw):
    tables=read_xlsx_table_rows(raw)
    sheets=[]
    for name, rows in tables.items():
        for row,cells in rows.items():
            if len(cells)!=len(set(cells)):
                raise ValueError("Duplicated Excel column reference")
        first=[{"row":k,"cells":dict(list(row.items())[:60])}
               for k,row in sorted(rows.items())[:8]]
        all_columns=sorted({k for r in rows.values() for k in r},key=lambda k:(len(k),k))
        sheets.append({
           "name":name,
           "xml_row_count":len(rows),
           "min_row":min(rows) if rows else None,
           "max_row":max(rows) if rows else None,
           "excel_column_count":len(all_columns),
           "all_column_addresses":all_columns[:120],
           "first_rows":first,
        })
    return {
       "study":"Roscoff 2026 fish acoustic communities",
       "doi":"10.1186/s12862-026-02521-z",
       "pmcid":"PMC13179613",
       "original_excel_url":SRC,
       "original_archive_member":FILENAME,
       "xlsx_sha256":hashlib.sha256(raw).hexdigest(),
       "xlsx_bytes":len(raw),
       "sheets":sheets,
       "claim_limit":"source inventory only; no current empirical tide x solar effect",
    }

def main():
    raw=acquire()
    out=audit(raw)
    path=Path(__file__).parent/"original_source_sheet_audit.json"
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("V139_WORKBOOK_AUDIT_START")
    print(json.dumps(out,ensure_ascii=False))
    print("V139_WORKBOOK_AUDIT_END")

if __name__=="__main__":
    main()
