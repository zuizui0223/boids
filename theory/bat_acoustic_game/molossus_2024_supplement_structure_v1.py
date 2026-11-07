"""Source-only structural inventory of PNAS bat-capture appendix XLSX.

Fetches original public Europe PMC supplementary bundle. No worksheet cell
values, original bat IDs, five-second windows, calls or capture outcomes read.
No original publisher bytes are written to GitHub or uploaded as artifacts.
"""
from __future__ import annotations
import hashlib,io,json,urllib.request,zipfile,xml.etree.ElementTree as ET
from pathlib import Path

OUT=Path(__file__).resolve().parent/"MOLOSSUS_2024_SUPPLEMENT_SOURCE_STRUCTURE_V1.json"
URL="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11287165/supplementaryFiles"
EXPECTED="pnas.2321724121.sd01.xlsx"
MAX_BUNDLE=100*1024*1024
MAX_XLSX=15*1024*1024
N={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
HEAD={"User-Agent":"original-licensed-bat-pnas-source-structure-inventory/1.0",
      "Accept":"application/zip"}

def download_bounded(url):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=100) as r:
        chunks=[];size=0
        while True:
            t=r.read(128*1024)
            if not t:break
            size+=len(t)
            if size>MAX_BUNDLE:raise ValueError("STOP_PUBLISHER_PACKAGE_OVER_100MB")
            chunks.append(t)
        return b"".join(chunks),r.status,r.headers.get("Content-Type")

def package_scan(bundle):
    z=zipfile.ZipFile(io.BytesIO(bundle))
    members=[{"name":x.filename,"original_uncompressed_bytes":x.file_size,
              "compressed_bytes":x.compress_size,"crc32":format(x.CRC,"08x")}
             for x in z.infolist()]
    target=[x for x in z.infolist()
            if x.filename.split("/")[-1]==EXPECTED and not x.is_dir()]
    result={"n_original_package_members":len(members),
            "original_package_members":members[:100],
            "matching_original_xlsx_member_count":len(target)}
    if len(target)!=1:
        result["status"]="STOP_NO_UNIQUE_SUPPLEMENT_DATASET_S01"
        return result
    f=target[0]
    if f.file_size>MAX_XLSX:
        result["status"]="STOP_SOURCE_WORKBOOK_TOO_LARGE"
        return result
    xlsx=z.read(f)
    result["original_XLSX_member_sha256"]=hashlib.sha256(xlsx).hexdigest()
    result["original_XLSX_member_bytes"]=len(xlsx)
    if not xlsx.startswith(b"PK\x03\x04"):
        result["status"]="STOP_SUPPLEMENT_MEMBER_NOT_OOXML_ZIP"
        return result
    fz=zipfile.ZipFile(io.BytesIO(xlsx))
    names=fz.namelist()
    result["workbook_zip_members_count"]=len(names)
    result["has_workbook_xml"]="xl/workbook.xml" in names
    result["has_shared_strings_xml"]="xl/sharedStrings.xml" in names
    result["worksheet_xml_paths"]=[
        x for x in names if x.startswith("xl/worksheets/sheet") and x.endswith(".xml")]
    result["workbook_sheets_metadata"]=[]
    if "xl/workbook.xml" in names:
        root=ET.fromstring(fz.read("xl/workbook.xml"))
        for element in root.findall(".//s:sheet",N):
            result["workbook_sheets_metadata"].append({
               "sheet_name":element.get("name"),
               "sheet_id":element.get("sheetId"),
            })
    result["worksheet_dimensions_no_cells"]=[]
    for path in result["worksheet_xml_paths"][:20]:
        # Important: do NOT parse or inspect original source row cell values.
        # XML byte parsing of the sheet would load source cell strings; instead
        # scan only its first 1200 bytes for the "<dimension ref=...>" tag.
        with fz.open(path) as ff:
            header=ff.read(1200)
        import re
        m=re.search(br"<(?:\w+:)?dimension\s+ref=[\"']([^\"']+)[\"']",header)
        result["worksheet_dimensions_no_cells"].append({
           "sheet_xml_path":path,"dimension":m.group(1).decode("ascii","ignore") if m else None})
    result["status"]="PASS_ORIGINAL_PNAS_DATASET_S01_WORKBOOK_STRUCTURE_ONLY"
    return result

def main():
    out={"schema":1,"date":"2026-11-05","source_paper_doi":"10.1073/pnas.2321724121",
         "source_archive_pmcid":"PMC11287165","original_supplement_source_url":URL,
         "status":"NOT_CHECKED","original_bat_response_cells_opened":False,
         "original_bat_IDs_or_timestamps_opened":False,
         "original_workbook_or_package_redistributed":False,
         "new_animal_measurements":False}
    try:
        bundle,status,ctype=download_bounded(URL)
        out.update(original_package_http_status=status,
            original_package_content_type=ctype,
            original_package_bytes=len(bundle),
            original_package_sha256=hashlib.sha256(bundle).hexdigest())
        out.update(package_scan(bundle))
    except Exception as e:
        out.update(status="STOP_PROVIDER_ARCHIVE_OR_WORKBOOK_STRUCTURE",
                   error=type(e).__name__+":"+str(e)[:220])
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_MOLOSSUS_BAT_SOURCE_STRUCTURE",out["status"])
    print("ORIGINAL_PUBLISHER_ZIP",out.get("original_package_bytes"),
          out.get("original_package_sha256"),out.get("original_package_content_type"))
    print("ARCHIVE_MEMBERS",out.get("original_package_members"))
    print("SOURCE_DATASET_S01",out.get("matching_original_xlsx_member_count"),
          out.get("original_XLSX_member_bytes"),out.get("original_XLSX_member_sha256"))
    print("SHEETS",out.get("workbook_sheets_metadata"),
          "DIMENSIONS",out.get("worksheet_dimensions_no_cells"))
    if out.get("error"):print("STOP_REASON",out["error"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
