"""v31: retrieve ONLY original author Dryad/Zenodo source metadata and source IDs.

No fish trajectories, speed, future movement scores, results tables or
acoustic events. A 84-file→group mapping is admitted ONLY when trial ID and
group ID are explicitly in the same original source table/author script.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

EIDC_DIR="https://catalogue.ceh.ac.uk/datastore/eidchub/08305a43-79b5-432f-ad20-2ddffe0d1077/"
DRYAD_DOI="10.5061/dryad.547d7wm8p"
ZENODO_DOI="10.5281/zenodo.5458081"
URLS={
  "dryad_api":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.547d7wm8p",
  "dryad_csv":"https://datadryad.org/downloads/file_stream/936892",
  "dryad_readme":"https://datadryad.org/downloads/file_stream/936894",
  "zenodo_5490572":"https://zenodo.org/api/records/5490572",
  "zenodo_5458081":"https://zenodo.org/api/records/5458081",
  "eidc_directory":EIDC_DIR
}
CAPS={
  "dryad_api":2*1024*1024,
  "dryad_csv":70*1024,
  "dryad_readme":10*1024,
  "zenodo_5490572":2*1024*1024,
  "zenodo_5458081":2*1024*1024,
  "eidc_directory":2*1024*1024,
}
ALLOWED_HOSTS={"catalogue.ceh.ac.uk","datadryad.org","zenodo.org"}

class SourceStop(Exception):pass

def fetch_original(url,cap,opener=request.urlopen):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS:
        raise SourceStop("V31_ORIGINAL_SOURCE_HOST_NOT_AUTHORIZED")
    req=request.Request(url,headers={
        "User-Agent":"boids-v31-original-author-crosswalk-source-only/1.0",
        "Accept":"application/json,text/csv,text/plain,text/html,*/*",
        "Accept-Encoding":"identity"})
    try:
        with opener(req,timeout=32) as resp:
            final=resp.geturl() if hasattr(resp,"geturl") else url
            finalparse=urlparse(final)
            if finalparse.scheme!="https" or finalparse.hostname not in ALLOWED_HOSTS:
                raise SourceStop("V31_AUTHOR_SOURCE_EXTERNAL_REDIRECT_STOP")
            body=resp.read(cap+1)
    except error.HTTPError as exc:
        raise SourceStop("HTTP_"+str(exc.code)) from exc
    except (error.URLError,TimeoutError,OSError) as exc:
        raise SourceStop("SOURCE_TRANSPORT_"+type(exc).__name__) from exc
    if not body or len(body)>cap:
        raise SourceStop("SOURCE_EMPTY_OR_EXCEEDS_BOUND")
    return body,final

def decode_json(body):
    try: d=json.loads(body)
    except (UnicodeError,ValueError) as exc:raise SourceStop("SOURCE_NOT_VALID_JSON") from exc
    if not isinstance(d,dict):
        raise SourceStop("SOURCE_JSON_NOT_OBJECT")
    if "message" in d and "title" not in d and "metadata" not in d:
        raise SourceStop("SOURCE_API_ERROR_ENVELOPE")
    return d

def index_filenames(raw):
    try:
        text=raw.decode("utf-8")
    except UnicodeError as exc:raise SourceStop("SOURCE_DIRECTORY_ENCODING_ERROR") from exc
    if "Index of /datastore/eidchub/" not in text:
        raise SourceStop("ORIGINAL_EIDC_INDEX_NOT_VERIFIED")
    matches=re.findall(r'href=["\x27]([0-9]{2,3}\.txt)["\x27]',text)
    if len(matches)!=84 or len(set(matches))!=84:
        raise SourceStop("ORIGINAL_EIDC_84_UNIQUE_FILES_NOT_VERIFIED")
    return sorted(matches,key=lambda x:int(x[:-4]))

def _metadata_only_json(data):
    # Do not export titles/abstract text or biological values as original files.
    root=data.get("metadata",data)
    fields=data.get("files",root.get("files"))
    info={"top_level_keys":sorted(data),
          "metadata_keys":sorted(root) if isinstance(root,dict) else [],
          "field_names":[],
          "published_file_count":None,
          "published_file_names":[]}
    if isinstance(fields,dict):
        entries=fields.get("entries",{})
        if isinstance(entries,dict):
            info["published_file_names"]=sorted(entries)[:30]
            info["published_file_count"]=len(entries)
    elif isinstance(fields,list):
        info["published_file_count"]=len(fields)
        info["published_file_names"]=[str(x.get("key",x.get("filename","")))
              for x in fields if isinstance(x,dict)][:30]
    return info


def parse_csv_only(raw):
    if raw[:4].lower() in (b"<htm",b"<!do") or b"<html" in raw[:128].lower():
        raise SourceStop("DRYAD_RAW_HTTP_ERROR_HTML_NOT_CSV")
    try: text=raw.decode("utf-8-sig")
    except UnicodeError as exc:raise SourceStop("DRYAD_CSV_ENCODING_STOP") from exc
    delimiter=csv.Sniffer().sniff(text[:4096],delimiters=",;\t")
    rows=list(csv.DictReader(io.StringIO(text,newline=""),dialect=delimiter))
    if not rows or len(rows)>10000:
        raise SourceStop("DRYAD_CSV_ROWS_INCOMPATIBLE")
    fields=list(rows[0])
    if not 2<=len(fields)<=100:
        raise SourceStop("DRYAD_CSV_FIELD_COUNT_STOP")
    return fields,rows

def _file_stem(x):
    if x is None:return None
    s=str(x).strip()
    if not s:return None
    s=s.removesuffix(".txt")
    # The original source uses filenames 01.txt ... 111.txt; e.g. "01",
    # "1" and "1.0" are consistent source-id encodings, NOT group IDs.
    if re.fullmatch(r"\d+(?:\.0+)?",s):
        return int(float(s))
    return None

def unique_table_report(fields,rows,original_names):
    stems={int(n[:-4]) for n in original_names}
    result={
      "published_csv_field_names":fields,
      "n_original_csv_rows":len(rows),
      "potential_source_identity_columns":{},
      "potential_group_identity_columns":{},
      "complete_author_verified_trial_to_group_map":None,
      "source_file_to_biological_shoal": "UNVERIFIED"
    }
    source_cols=[col for col in fields if re.search(r"(?i)(video|file|record|trial|track|sample|session|id)",col)]
    group_cols=[col for col in fields if re.search(r"(?i)(group|shoal|school)",col)]
    for col in source_cols:
        seen=[_file_stem(row.get(col)) for row in rows]
        ids={x for x in seen if x is not None}
        result["potential_source_identity_columns"][col]={
          "n_unique_numeric_ids":len(ids),
          "n_explicit_original_EIDC_file_stem_matches":len(ids&stems),
          "n_original_EIDC_file_ids_not_in_column":len(stems-ids),
          "n_original_csv_ids_not_present_in_EIDC":len(ids-stems),
          "n_non_numeric_or_null_tokens":sum(x is None for x in seen)
        }
    for col in group_cols:
        vals=[(row.get(col) or "").strip() for row in rows]
        ids={x for x in vals if x}
        result["potential_group_identity_columns"][col]={
          "n_distinct_nonmissing_labels":len(ids),
          "missing_or_empty_rows":sum(not x for x in vals),
          "group_identifier_values_as_PUBLISHED_strings":sorted(ids)[:24]
        }
    # Strict evidence: every original 84 file ID appears as explicit
    # video/file/trial source ID in author table and maps to exactly one
    # author-identified group/shoal. A table with only "trial=1-12" will
    # correctly STOP rather than infer file IDs by ordinal chronology.
    matches=[]
    for source_col in source_cols:
        assoc=collections.defaultdict(set)
        matched_file_ids=set()
        for row in rows:
            source=_file_stem(row.get(source_col))
            if source not in stems:continue
            matched_file_ids.add(source)
            for group_col in group_cols:
                val=(row.get(group_col) or "").strip()
                if val:
                    assoc[(source,group_col)].add(val)
        if matched_file_ids!=stems:continue
        for group_col in group_cols:
            filemap={fid:assoc.get((fid,group_col),set()) for fid in stems}
            if any(len(v)!=1 for v in filemap.values()):continue
            groups={next(iter(v)) for v in filemap.values()}
            if not 2<=len(groups)<=12:continue
            mapping={f"{fid:02d}.txt":next(iter(filemap[fid])) for fid in sorted(stems)}
            matches.append((source_col,group_col,mapping))
    if len(matches)==1:
        a,b,mapping=matches[0]
        result["complete_author_verified_trial_to_group_map"]={
            "source_original_id_column":a,
            "original_shoal_group_id_column":b,
            "84_file_to_group_ID":mapping,
            "n_distinct_original_group_labels":len(set(mapping.values())),
            "original_files_per_group":dict(sorted(collections.Counter(mapping.values()).items())),
            "published_original_data_source":"Dryad MacGregorIoannou_Data.csv"
        }
        result["source_file_to_biological_shoal"]="EXPLICIT_ORIGINAL_AUTHOR_TABLE_JOIN"
    else:
        result["ambiguity_reason"]=("MULTIPLE_PLAUSIBLE_JOIN_COLUMNS" if len(matches)>1
             else "NO_EXPLICIT_COMPLETE_AUTHOR_TRIAL_FILE_GROUP_CROSSWALK")
    return result


def run(fetcher=fetch_original):
    report={
      "status":"SOURCE_IDENTITY_NOT_ADMITTED",
      "dataset":"MacGregor & Ioannou 2021 stickleback",
      "eidc_original_doi":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "dryad_original_doi":DRYAD_DOI,
      "zenodo_original_doi":ZENODO_DOI,
      "source_only":True,
      "new_fish_movement_forecast_scored":False,
      "original_fish_positions_or_outcome_columns_exported":False,
      "frozen_protocol":"docs/V31_STICKLEBACK_AUTHOR_GROUP_TRIAL_CROSSWALK_FREEZE.md",
      "source_access":{},
    }
    observed={}
    for key,url in URLS.items():
        entry={"url":url,"status":"SOURCE_ACCESS_STOP"}
        try:
            body,final=fetcher(url,CAPS[key])
            entry["sha256_original_response"]=hashlib.sha256(body).hexdigest()
            entry["n_source_bytes"]=len(body)
            entry["redirected_to_same_permitted_host"]=urlparse(final).hostname in ALLOWED_HOSTS
            if key=="eidc_directory":
                observed[key]=index_filenames(body)
                entry["n_original_numbered_files"]=len(observed[key])
            elif key in ("dryad_api","zenodo_5490572","zenodo_5458081"):
                data=decode_json(body)
                entry.update(_metadata_only_json(data))
            else:
                fields,rows=parse_csv_only(body)
                observed[key]=(fields,rows)
                entry["source_csv_field_names"]=fields
                entry["source_csv_n_rows"]=len(rows)
            entry["status"]="ORIGINAL_SOURCE_METADATA_VERIFIED"
        except (SourceStop,csv.Error,ValueError) as exc:
            entry["reason"]=str(exc)
        report["source_access"][key]=entry
    if "eidc_directory" in observed and "dryad_csv" in observed:
        fields,rows=observed["dryad_csv"]
        inspect=unique_table_report(fields,rows,observed["eidc_directory"])
        report["published_author_group_trial_id_structure"]=inspect
        if inspect["complete_author_verified_trial_to_group_map"] is not None:
            report["status"]="EXPLICIT_AUTHOR_SOURCE_FILE_TO_GROUP_CROSSWALK_ADMITTED"
            report["n_original_stickleback_shoals_mapped"]=inspect["complete_author_verified_trial_to_group_map"]["n_distinct_original_group_labels"]
            report["n_original_track_files_mapped"]=84
    else:
        report["stop_reason"]="PUBLISHED_SOURCE_IDENTITY_METADATA_INACCESSIBLE_OR_INCOMPLETE"
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    d=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(d,sort_keys=True))

if __name__=="__main__":main()
