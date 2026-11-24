"""v31b: verify original 2021 author Zenodo CSV + R script MD5 before group-ID join.

Only source IDs and source code metadata; no animal XY or biological response.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from validation_fish_school_v31.original_author_crosswalk import (
    SourceStop,fetch_original,decode_json,index_filenames,unique_table_report,
    parse_csv_only,EIDC_DIR
)

RECORDS={
    "data":(5490572,("MacGregorIoannou_Data.csv","Readme.csv")),
    "code":(5458081,("MacGregorIoannou_Code_Final.R",))
}
LIMITS={"MacGregorIoannou_Data.csv":300_000,
        "Readme.csv":30_000,
        "MacGregorIoannou_Code_Final.R":3_000_000}


def records_api(record_id,fetcher=fetch_original):
    u=f"https://zenodo.org/api/records/{record_id}"
    body,_=fetcher(u,2*1024*1024)
    data=decode_json(body)
    if str(data.get("id",data.get("recid","")))!=str(record_id):
        raise SourceStop("AUTHOR_ZENODO_RECORD_IDENTITY_MISMATCH")
    files=data.get("files")
    if not isinstance(files,list):
        raise SourceStop("AUTHOR_ZENODO_FILES_NOT_LIST")
    return files,hashlib.sha256(body).hexdigest()


def original_file_link(filemeta):
    if not isinstance(filemeta,dict):
        raise SourceStop("ZENODO_FILE_METADATA_SCHEMA_STOP")
    links=filemeta.get("links",{})
    if not isinstance(links,dict):
        raise SourceStop("ZENODO_ORIGINAL_LINKS_SCHEMA_STOP")
    for field in ("self","download","content"):
        link=links.get(field)
        if isinstance(link,str) and link:
            p=urlparse(link)
            if p.scheme!="https" or p.hostname!="zenodo.org":
                raise SourceStop("AUTHOR_ORIGINAL_FILE_LINK_OTHER_HOST_STOP")
            if "/api/records/" not in p.path and "/api/files/" not in p.path and "/records/" not in p.path:
                raise SourceStop("AUTHOR_ORIGINAL_FILE_LINK_NOT_RECORDED_API")
            return link
    raise SourceStop("ZENODO_SOURCE_FILE_DOES_NOT_HAVE_AUTHOR_VERIFIED_DOWNLOAD_LINK")


def _meta_field(item,filename):
    if item.get("key",item.get("filename"))!=filename:
        raise SourceStop("ZENODO_ORIGINAL_FILENAME_NOT_AUTHOR_MATCH")
    ck=item.get("checksum","")
    if isinstance(ck,dict):
        ck="md5:"+str(ck.get("md5",""))
    if not isinstance(ck,str):
        raise SourceStop("ZENODO_ORIGINAL_CHECKSUM_SCHEMA_STOP")
    ck=ck.removeprefix("md5:")
    if not re.fullmatch(r"[0-9a-fA-F]{32}",ck):
        raise SourceStop("ZENODO_ORIGINAL_MD5_NOT_PRESENT")
    n=item.get("size",item.get("filesize",0))
    if not isinstance(n,int) or n<=0 or n>LIMITS[filename]:
        raise SourceStop("ZENODO_ORIGINAL_FILENAME_SIZE_NOT_IN_BOUND")
    return ck.lower(),n,original_file_link(item)


def auth_file(filemeta,filename,fetcher=fetch_original):
    md5,size,link=_meta_field(filemeta,filename)
    body,_=fetcher(link,LIMITS[filename])
    if len(body)!=size or hashlib.md5(body).hexdigest()!=md5:
        raise SourceStop("ZENODO_ORIGINAL_MD5_SIZE_MISMATCH_"+filename)
    if body[:256].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise SourceStop("AUTHOR_ORIGINAL_FILE_WAS_HTTP_ERROR_HTML")
    return body,{"original_file_name":filename,"source_size_bytes":size,
                 "author_provider_MD5_verified":True,
                 "source_SHA256":hashlib.sha256(body).hexdigest(),
                 "original_download_link_was_author_metadata":True}


def r_source_identity_signature(body):
    try:text=body.decode("utf-8-sig")
    except UnicodeError as exc:
        raise SourceStop("AUTHOR_R_SCRIPT_ENCODING_STOP") from exc
    lines=text.splitlines()
    if not 10<len(lines)<100000:
        raise SourceStop("AUTHOR_ORIGINAL_R_SCRIPT_SIZE_LINES_STOP")
    rx=re.compile(r"\b(group|shoal|school|trial|video|file|record|session|read.csv|read.table|join|merge|left_join)\b",re.I)
    anchor=re.compile(r"(group|shoal|school)",re.I)
    names=re.compile(r"[A-Za-z0-9_\-\.]+\.(?:csv|txt|r)\b",re.I)
    # NO original author R code lines exported; only counts, original source
    # author file names, and source line number indexes for later manual audit.
    selected=[i+1 for i,line in enumerate(lines) if rx.search(line)]
    combos=[i+1 for i,line in enumerate(lines)
            if anchor.search(line) and re.search(r"(?i)(trial|video|file|record|session)",line)]
    source_filenames=sorted(set(
        m.group(0) for l in lines for m in names.finditer(l)))[:30]
    return {"original_author_R_line_count":len(lines),
            "line_indices_with_source_identity_keywords_first_40":selected[:40],
            "n_lines_with_source_identity_keywords":len(selected),
            "n_lines_containing_both_group_and_trial_or_file_identity":len(combos),
            "original_R_line_indices_for_potential_group_file_join_first_20":combos[:20],
            "original_R_source_filename_literals":source_filenames,
            "original_author_R_source_lines_redistributed":False,
            "author_R_code_not_executed":True}


def run(fetcher=fetch_original):
    report={
      "status":"SOURCE_IDENTITY_NOT_ADMITTED",
      "original_2021_dataset":"MacGregor Ioannou 2021 group motion",
      "original_EIDC_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "original_author_Zenodo_record_data":5490572,
      "original_author_Zenodo_record_R_code":5458081,
      "source_frozen_before_identifiers":"docs/V31B_ZENODO_2021_ORIGINAL_AUTHOR_CODE_DATA_ID_FREEZE.md",
      "no_new_fish_movement_outcomes_fitted":True,
      "no_raw_original_animal_positions_or_aggregate_response_exported":True,
      "source_files":{},
    }
    try:
        directory,_=fetcher(EIDC_DIR,2*1024*1024)
        original_names=index_filenames(directory)
        author={}
        for key,(record_id,expected) in RECORDS.items():
            files,digest=records_api(record_id,fetcher)
            byname={f.get("key",f.get("filename")):f for f in files if isinstance(f,dict)}
            if set(byname)!=set(expected):
                raise SourceStop("ORIGINAL_ZENODO_FILENAME_EXACT_MANIFEST_STOP_"+key)
            report["source_files"][key]={
              "source_api_record_sha256":digest,
              "original_author_record_id":record_id,
              "original_files_authenticated":[]}
            for name in expected:
                body,receipt=auth_file(byname[name],name,fetcher)
                report["source_files"][key]["original_files_authenticated"].append(receipt)
                author[name]=body
        fields,rows=parse_csv_only(author["MacGregorIoannou_Data.csv"])
        report["original_author_csv_ID_structure"]=unique_table_report(fields,rows,original_names)
        readme_fields,readme_rows=parse_csv_only(author["Readme.csv"])
        report["original_readme_header_fields"]=readme_fields
        report["original_readme_n_rows"]=len(readme_rows)
        report["original_R_code_ID_signature"]=r_source_identity_signature(author["MacGregorIoannou_Code_Final.R"])
        if report["original_author_csv_ID_structure"]["complete_author_verified_trial_to_group_map"] is not None:
            report["status"]="EXPLICIT_AUTHOR_SOURCE_FILE_TO_GROUP_CROSSWALK_ADMITTED"
            mapping=report["original_author_csv_ID_structure"]["complete_author_verified_trial_to_group_map"]
            report["source_trial_ids_covered"]=len(mapping["84_file_to_group_ID"])
            report["distinct_original_author_group_ids"]=mapping["n_distinct_original_group_labels"]
        else:
            report["stop_reason"]="PUBLISHED_CSV_HAS_NO_UNAMBIGUOUS_COMPLETE_FILE_TO_GROUP_KEY"
    except (SourceStop,ValueError,UnicodeError,KeyError) as ex:
        report["stop_reason"]=str(ex)
    return report

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    out=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":main()
