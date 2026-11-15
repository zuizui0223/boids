"""Original PNAS bat prey-capture XLSX source metadata / byte preflight only.

No workbook cells, bat records or 5-second real-bat outcomes are read.
Do NOT equate original PNAS supplementary Dataset S01 and Mendeley table
before identical original source headers/content are verified.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,urllib.request,urllib.error,ssl
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent/"MOLOSSUS_2024_PNAS_CAPTURE_SOURCE_GATE_V1.json"
URLS={
 "PMC_article_supplement":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/bin/pnas.2321724121.sd01.xlsx",
 "NCBI_www_supplement":"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11287165/bin/pnas.2321724121.sd01.xlsx",
 "PMC_article_instance":"https://pmc.ncbi.nlm.nih.gov/articles/instance/11287165/bin/pnas.2321724121.sd01.xlsx",
 "EuropePMC_supplement":"https://europepmc.org/articles/PMC11287165/bin/pnas.2321724121.sd01.xlsx",
 "PMC_OA_API":"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC11287165",
 "EuropePMC_fullTextXML":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11287165/fullTextXML",
 "EuropePMC_supplementaryFiles":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11287165/supplementaryFiles",
 "PNAS_original_file":"https://www.pnas.org/doi/suppl/10.1073/pnas.2321724121/suppl_file/pnas.2321724121.sd01.xlsx"
}
HEAD={"User-Agent":"open-science-bat-source-preflight/1.0 (original-supplement-authority)",
      "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/zip,text/xml,application/xml,*/*"}
MAX_READ=4096
def open_first(url,method="GET"):
    req=urllib.request.Request(url,headers=HEAD,method=method)
    with urllib.request.urlopen(req,timeout=36) as response:
        meta={
          "http":response.status,
          "returned_url":response.url,
          "content_type":response.headers.get("Content-Type"),
          "length_header":response.headers.get("Content-Length"),
          "content_range":response.headers.get("Content-Range"),
          "accept_ranges":response.headers.get("Accept-Ranges")}
        if method=="HEAD":return meta,None
        raw=response.read(MAX_READ)
        meta["probe_bytes"]=len(raw)
        meta["probe_sha256"]=hashlib.sha256(raw).hexdigest()
        meta["magic_hex"]=raw[:8].hex()
        meta["xlsx_zip_magic"]=raw.startswith(b"PK\x03\x04")
        meta["html_landing_page_not_xlsx"]=raw.lstrip().lower().startswith((b"<!doctype html",b"<html"))
        if raw.startswith(b"<?xml") or raw.lstrip().startswith(b"<"):
            meta["xml_or_html_header_probe"]=True
        return meta,raw
def main():
    res={"schema":1,"doi":"10.1073/pnas.2321724121",
      "publication":"Krivoruchko et al. 2024 PNAS, published foraging-tradeoff",
      "pmcid":"PMC11287165",
      "data_citation_original_Mendeley":"10.17632/h7krh54zxc.1",
      "new_animal_measurements":False,
      "source_workbook_cells_opened":False,
      "source_bat_ids_raw_outcomes_opened":False,
      "no_original_source_bytes_rehosted":True,
      "source_manifest_status":"NOT_CHECKED","endpoints":{}}
    for name,url in URLS.items():
        v={"original_source_url":url,"status":"NOT_CHECKED"}
        try:
            header,_=open_first(url,method="HEAD")
            v["head"]=header
        except Exception as e:
            v["head_error"]=type(e).__name__+":"+str(e)[:180]
        try:
            response,head=open_first(url)
            v["get"]=response
            v["status"]=("ACCESSIBLE_PUBLISHER_SUPPLEMENT_ZIP_HEADER" if response["xlsx_zip_magic"] and "application/zip" in (response["content_type"] or "").lower()
                 else "ACCESSIBLE_UNVERIFIED_ZIP_HEADER" if response["xlsx_zip_magic"]
                 else "ACCESSIBLE_METADATA_OR_NON_XLSX")
        except Exception as e:
            v["status"]="SOURCE_ACCESS_STOP"
            v["error"]=type(e).__name__+":"+str(e)[:180]
        res["endpoints"][name]=v
        print("PNAS_ORIGINAL_SOURCE_PROBE",name,v["status"],v.get("get"),v.get("error"))
    admitted=[k for k,v in res["endpoints"].items()
              if v["status"]=="ACCESSIBLE_PUBLISHER_SUPPLEMENT_ZIP_HEADER"]
    res["source_manifest_status"]=("PASS_PROVIDER_SUPPLEMENT_ZIP_HEADER_ONLY" if admitted
                                   else "STOP_NO_AUTHORIZED_PNAS_XLSX_SOURCE")
    res["accessible_xlsx_endpoint_ids"]=admitted
    OUT.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("PNAS_MOLOSSUS_SOURCE_GATE",res["source_manifest_status"],admitted)
    return 0
if __name__=="__main__":
    raise SystemExit(main())
