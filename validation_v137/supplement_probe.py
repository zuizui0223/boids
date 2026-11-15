"""Read the actual Raposa et al. 2026 Appendix S1 xlsx if publicly retrievable.

Run in GitHub Actions, where network access is available. No source data are
published back to the repository; record only SHA256, workbook structure and a
small sample of column headings for independent audit.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET
import zipfile

PMCID = "PMC12805223"
DOI = "10.1002/ece3.72872"
TARGET_NAME = "ECE3-16-e72872-s003.xlsx"
SOURCES = (
    "https://pmc.ncbi.nlm.nih.gov/articles/instance/12805223/bin/" + TARGET_NAME,
    "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12805223/supplementaryFiles?includeInlineImage=false",
    "https://onlinelibrary.wiley.com/doi/supinfo/10.1002/ece3.72872",
)
N = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
     "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
     "p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def bounded_get(url, max_bytes=85 * 1024 * 1024):
    req = Request(url, headers={"User-Agent": "ResearchSourceAudit/1.0 (scientific, no automated scraping)", "Accept": "application/zip, application/octet-stream, */*"})
    with urlopen(req, timeout=25) as resp:
        content = bytearray()
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            content += chunk
            if len(content) > max_bytes:
                raise ValueError("source is larger than safe download cap")
        return bytes(content)


def get_supplement():
    attempts = []
    for url in SOURCES:
        try:
            raw = bounded_get(url)
            if not zipfile.is_zipfile(io.BytesIO(raw)):
                raise ValueError("not a zip/xlsx container")
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                names = z.namelist()
                if "xl/workbook.xml" in names:
                    xlsx = raw
                    container = "direct_xlsx"
                else:
                    matches = [n for n in names if n.lower().endswith(".xlsx") and
                               (TARGET_NAME.lower() in n.lower() or "appendixs1" in n.lower())]
                    if len(matches) != 1:
                        raise ValueError("supplement ZIP did not contain a unique appendix S1 xlsx")
                    xlsx = z.read(matches[0])
                    container = "supplement_bundle:" + matches[0]
            attempts.append({"url": url, "status": "acquired"})
            return xlsx, url, container, attempts
        except (URLError, HTTPError, TimeoutError, ValueError, zipfile.BadZipFile) as exc:
            attempts.append({"url": url, "status": "failed", "error": type(exc).__name__,
                             "detail": str(exc)[:160]})
    return None, None, None, attempts


def excel_values(xlsx):
    with zipfile.ZipFile(io.BytesIO(xlsx)) as z:
        manifest = set(z.namelist())
        if "xl/workbook.xml" not in manifest:
            raise ValueError("Not an Excel xlsx workbook")
        strings = []
        if "xl/sharedStrings.xml" in manifest:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("x:si", N):
                strings.append("".join(el.text or "" for el in si.iter("{"+N["x"]+"}t")))
        links = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        mapping = {}
        for rel in links:
            target = rel.attrib["Target"].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            mapping[rel.attrib["Id"]] = target
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        output = []
        for s in wb.findall("x:sheets/x:sheet", N):
            rid = s.attrib["{"+N["r"]+"}id"]
            filename = mapping[rid]
            if filename not in manifest:
                raise ValueError("Declared sheet missing: " + filename)
            root = ET.fromstring(z.read(filename))
            rows = root.findall(".//x:sheetData/x:row", N)
            sample = []
            for row in rows[:8]:
                vals = {}
                for cell in row.findall("x:c", N):
                    loc = re.match(r"^([A-Z]+)", cell.attrib.get("r", ""))
                    col = loc.group(1) if loc else "?"
                    value = cell.find("x:v", N)
                    cell_t = cell.attrib.get("t", "")
                    if cell_t == "inlineStr":
                        text = "".join(t.text or "" for t in cell.findall(".//x:is/x:t", N))
                    else:
                        text = "" if value is None else str(value.text or "")
                        if cell_t == "s" and text:
                            text = strings[int(text)]
                    if text.strip():
                        vals[col] = text.replace("\n", " ")[:90]
                sample.append({"row": int(row.attrib.get("r", "0")), "sample_cells": dict(list(vals.items())[:24])})
            headings = " ".join(" ".join(r["sample_cells"].values()) for r in sample[:6]).lower()
            flags = {key:bool(re.search(pat,headings)) for key,pat in {
                "has_flood_term":r"flood|inundat|潮|tide",
                "has_dry_term":r"dry|non.flood",
                "has_diel_term":r"day|night|diel|dawn|dusk",
                "has_explicit_effort_term":r"effort|hour|deploy|operat|duration|start|end",
                "has_station_term":r"station|camera",
                "has_timestamp_term":r"datetime|timestamp|date.?time"
            }.items()}
            output.append({"sheet":s.attrib["name"], "xml_rows_including_headers":len(rows),
                           "excel_dimension":(root.find("x:dimension",N).attrib.get("ref")
                                              if root.find("x:dimension",N) is not None else None),
                           "sample_first_8_rows":sample,"heading_search_flags":flags})
        return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output", default="validation_v137/probe_run.json")
    args=p.parse_args()
    data,url,container,attempts=get_supplement()
    result={"original_doi":DOI,"pmcid":PMCID,"appendix":"S1",
            "source_acquisition_attempts":attempts,
            "downloaded_original":data is not None,"original_url":url,
            "supplement_container":container}
    if data is not None:
        result["xlsx_sha256"]=hashlib.sha256(data).hexdigest()
        result["xlsx_bytes"]=len(data)
        try:
            result["sheets"]=excel_values(data)
        except Exception as exc:
            result["parse_error"]=type(exc).__name__+":"+str(exc)[:180]
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("SOURCE_PROBE_JSON_START")
    print(json.dumps(result,ensure_ascii=False))
    print("SOURCE_PROBE_JSON_END")
    # Fail closed: no verified original means no 'successful acquisition'.
    if data is None or "sheets" not in result:
        sys.exit(2)

if __name__ == "__main__":
    main()
