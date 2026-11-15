"""Public-supplement source admission for two INDEPENDENT bat acoustic studies.

Does not open original animal movement/audio measurements or any PDF content.
The zip package member directory is inspected, not individual member bytes.
No invented file/download URLs, no provider authentication bypass.
"""
from __future__ import annotations
from collections import Counter
import hashlib,io,json,urllib.request,urllib.error,zipfile
from pathlib import Path

OUT=Path(__file__).resolve().parent/"INDEPENDENT_BAT_FLIGHT_SOURCE_MANIFEST_2026_11_07.json"
CONTRACT=Path(__file__).resolve().parent/"INDEPENDENT_BAT_ACOUSTIC_FLIGHT_SOURCE_ADMISSION_2026_11_07.md"
SOURCE={
 "Goldshtein_2025":{
  "pmcid":"PMC12002023",
  "original_paper_doi":"10.1073/pnas.2407810122",
  "catalog_original_data_doi":"10.17632/k7pt2j84f7.1",
  "source_role":"original_onboard_acoustics_plus_group_movement_no_prey_capture"
 },
 "Gilmour_2021":{
  "pmcid":"PMC8601711",
  "original_paper_doi":"10.1242/jeb.242715",
  "catalog_original_data_doi":"10.17632/gb45nfkkk5.1",
  "source_role":"original_ultrasound_deterrent_playback_flight_trajectories_feeding_buzz"
 }
}
MAX_BYTES=80*1024*1024
PUBLIC_EXTS={".xlsx",".xls",".csv",".tsv",".mat",".rds",".rdata",".h5",".hdf5",".parquet",".json",".zip"}
HEAD={"User-Agent":"open-science-bat-independent-supplement-source-gate/1.0",
      "Accept":"application/zip,application/octet-stream,*/*"}

def get_bounded(url,limit=MAX_BYTES):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=70) as resp:
        chunks=[];n=0
        while True:
            b=resp.read(128*1024)
            if not b:break
            n+=len(b)
            if n>limit:raise ValueError("STOP_ORIGINAL_SOURCE_EXCEEDS_READ_LIMIT")
            chunks.append(b)
        return b"".join(chunks),resp.status,resp.headers.get("Content-Type")

def member_extension(name):
    name=name.lower().split("/")[-1]
    i=name.rfind(".")
    return name[i:] if i>=0 else ""

def admission_facts(src,source_id):
    url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{src['pmcid']}/supplementaryFiles"
    out={"source_id":source_id,"pmcid":src["pmcid"],
         "paper_doi":src["original_paper_doi"],
         "original_data_doi_catalog":src["catalog_original_data_doi"],
         "source_role":src["source_role"],
         "supplement_provider_url":url,"status":"NOT_CHECKED"}
    try:
        original,http,ctype=get_bounded(url)
        out.update(http_status=http,provider_content_type=ctype,
                   transport_bytes=len(original),
                   transport_zip_sha256=hashlib.sha256(original).hexdigest(),
                   returned_zip_magic=original[:4].hex())
        if not zipfile.is_zipfile(io.BytesIO(original)):
            raise ValueError("STOP_PROVIDER_RESPONSE_NOT_ZIP")
        with zipfile.ZipFile(io.BytesIO(original)) as archive:
            entries=[{"basename":x.filename.split("/")[-1],
                      "uncompressed_bytes":x.file_size,
                      "extension":member_extension(x.filename),
                      "crc32":f"{x.CRC:08x}"}
                     for x in archive.infolist() if not x.is_dir()]
        out["original_supplement_member_count"]=len(entries)
        out["original_supplement_members"]=entries[:100]
        ext=Counter(x["extension"] for x in entries)
        out["extensions_by_member_count"]=dict(ext)
        candidates=[x for x in entries if x["extension"] in PUBLIC_EXTS
                    and x["uncompressed_bytes"]>0]
        out["potential_original_machine_readable_members"]=candidates
        out["status"]=("STRUCTURE_CANDIDATE_NEEDS_FIELD_GRAIN_CHECK"
                       if candidates else "STOP_PUBLIC_SUPPLEMENT_HAS_NO_RAW_MACHINE_READABLE_DATA")
        out["original_bat_outcome_cells_opened"]=False
        out["original_supplement_member_bytes_opened"]=False
    except Exception as e:
        out.update(status="STOP_SUPPLEMENT_SOURCE_ACCESS",
                   error=f"{type(e).__name__}: {str(e)[:230]}")
    return out

def main():
    if not CONTRACT.exists():raise ValueError("Missing source pre-output eligibility contract")
    result={"schema":1,"date":"2026-11-07",
            "status":"INDEPENDENT_BAT_SOURCE_STRUCTURE_ONLY",
            "no_new_animal_measurements":True,
            "original_animal_outcome_records_opened":False,
            "original_supplements_redistributed":False,
            "does_not_confuse_supplement_ZIP_with_original_data_ZIP":True,
            "sources":{name:admission_facts(src,name) for name,src in SOURCE.items()},
            "claims":"A public PDF/video supplement is not the original trajectory/audio dataset. Published source results are prior art."
            }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for name,d in result["sources"].items():
        print("EXTERNAL_SOURCE",name,d["status"],"members",d.get("original_supplement_member_count"),
              "type",d.get("extensions_by_member_count"))
        print("SOURCE_MEMBERS",name,json.dumps(d.get("original_supplement_members"),sort_keys=True))
        if "error" in d:print("STOP_REASON",name,d["error"])
    return 0

if __name__=="__main__":raise SystemExit(main())
