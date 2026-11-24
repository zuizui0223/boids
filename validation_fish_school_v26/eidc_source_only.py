"""v26 source-only authentic EIDC 2021 stickleback 25Hz metadata audit.

No fish movement outcome, speed, trajectory, social force or call is scored.
No original numeric XY values are emitted. Index counts are NOT school IDs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SOURCE_DOI="10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077"
BASE="https://catalogue.ceh.ac.uk/datastore/eidchub/"+SOURCE_DOI.split("/")[-1]+"/"
PROBES=("01.txt","02.txt","105.txt")
INDEX_LIMIT=2*1024*1024
FILE_LIMIT=15*1024*1024
FILE_REGEX=re.compile(
    r'<a[^>]+href=["\'](?P<file>[0-9]{2,3}\.txt)["\'][^>]*>[^<]*</a>\s+'
    r'[0-9]{2}-[A-Za-z]{3}-[0-9]{4}\s+[0-9]{2}:[0-9]{2}\s+(?P<size>[0-9]+)',
    flags=re.I
)


class SourceStop(Exception):
    pass


def fetch_bound(url, cap, opener=urlopen):
    if not url.startswith(BASE) or urlparse(url).hostname!="catalogue.ceh.ac.uk":
        raise SourceStop("ORIGINAL_EIDC_HOST_STOP")
    try:
        with opener(Request(url,headers={"User-Agent":"boids-v26-fish-source-only/1.0",
                 "Accept-Encoding":"identity"}),timeout=55) as response:
            target=response.geturl() if hasattr(response,"geturl") else url
            if not target.startswith(BASE) or urlparse(target).hostname!="catalogue.ceh.ac.uk":
                raise SourceStop("EXTERNAL_REDIRECT_STOP")
            b=response.read(cap+1)
    except (HTTPError,URLError,OSError,TimeoutError) as exc:
        raise SourceStop("ORIGINAL_SOURCE_ACCESS_"+type(exc).__name__) from exc
    if len(b)>cap or not b:
        raise SourceStop("ORIGINAL_SOURCE_EMPTY_OR_OVERSIZE")
    return b


def parse_listing(blob):
    try: text=blob.decode("utf-8")
    except UnicodeError as exc: raise SourceStop("EIDC_LISTING_ENCODING_STOP") from exc
    if "Index of " not in text or "eidchub/" not in text:
        raise SourceStop("EIDC_LISTING_NOT_PUBLISHED_DIRECTORY")
    found={}
    for match in FILE_REGEX.finditer(text):
        filename,size=match.group("file"),int(match.group("size"))
        if filename in found:
            raise SourceStop("DUPLICATED_FILE_NAME_STOP")
        if size<=0 or size>FILE_LIMIT:
            raise SourceStop("SOURCE_FILE_SIZE_OUTSIDE_DECLARED_BOUNDS")
        found[filename]=size
    if len(found)<3 or len(found)>200 or not set(PROBES).issubset(found):
        raise SourceStop("EIDC_ORIGINAL_LISTING_SCHEMA_OR_PROBES_STOP")
    return found


def inspect_first_lines(blob):
    # Counts only, never source coordinate values. A published header may differ
    # from native data rows, so report both schemas without guessing columns.
    lines=blob.splitlines()
    first=[row for row in lines if row.strip()][:3]
    if len(first)!=3:
        raise SourceStop("SOURCE_FIRST_THREE_LINES_STOP")
    summary=[]
    for raw in first:
        try: s=raw.decode("utf-8-sig")
        except UnicodeError as exc:raise SourceStop("SOURCE_TEXT_ENCODING_STOP") from exc
        tokens=[x for x in re.split(r"[\s,;]+",s.strip()) if x]
        if not 2<=len(tokens)<=100:
            raise SourceStop("SOURCE_FIRST_LINE_COLUMN_LIMIT_STOP")
        numeric=0
        for token in tokens:
            try:
                float(token)
                numeric+=1
            except ValueError:
                pass
        summary.append({"tokens":len(tokens),"numeric_token_count":numeric,
                        "numeric_fraction":numeric/len(tokens),
                        "raw_line_length_bytes":len(raw),
                        "comma_count":raw.count(b","),
                        "tab_count":raw.count(b"\t"),
                        "semicolon_count":raw.count(b";")})
    if len(lines)<100:
        raise SourceStop("SOURCE_ORIGINAL_TOO_FEW_ROWS_STOP")
    return {"nonempty_source_line_count":sum(bool(line.strip()) for line in lines),
            "initial_schema_only":summary,
            "original_fish_positions_or_timestamps_exported":False,
            "8_fish_XY_mapping":"NOT_YET_VERIFIED",
            "original_school_ID":"NOT_IDENTIFIED",
            "clock_type":"NATIVE_25FPS_REFERENCED_BY_PUBLISHER_NOT_YET_VERIFIED_IN_FILE"}


def run(opener=urlopen):
    report={
      "status":"SOURCE_ACCESS_OR_SCHEMA_STOP",
      "dataset_DOI":SOURCE_DOI,
      "source_type":"original EIDC native 25fps 8-fish stickleback XY",
      "original_animals_per_shoal_in_publication":8,
      "original_study_shoals_reported":12,
      "independent_school_ID_mapping":"UNKNOWN",
      "source_time_series_redistributed":False,
      "new_third_species_effect_estimated":False,
      "fish_calls_measured":False,
    }
    try:
        index=fetch_bound(BASE,INDEX_LIMIT,opener)
        names=parse_listing(index)
        report["directory_index_sha256"]=hashlib.sha256(index).hexdigest()
        report["number_of_indexed_original_TXT_files"]=len(names)
        report["file_names_and_source_byte_counts"]=[
           {"filename":name,"source_size_bytes":size}
           for name,size in sorted(names.items(), key=lambda v:int(v[0][:-4]))]
        results=[]
        for name in PROBES:
            data=fetch_bound(BASE+name,FILE_LIMIT,opener)
            if len(data)!=names[name]:
                raise SourceStop("SOURCE_ORIGINAL_LISTED_BYTE_COUNT_MISMATCH_"+name)
            info=inspect_first_lines(data)
            results.append({"filename":name,
              "original_bytes":len(data),
              "original_content_sha256":hashlib.sha256(data).hexdigest(),**info})
        report["source_schema_probes"]=results
        report["status"]="SOURCE_STRUCTURE_ONLY_NOT_ECOLOGY_ADMITTED"
    except SourceStop as exc:
        report["stop_reason"]=str(exc)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"reason":result.get("stop_reason"),
       "directory_count":result.get("number_of_indexed_original_TXT_files"),
       "probes":result.get("source_schema_probes"),
       "school_identity":result.get("independent_school_ID_mapping")},sort_keys=True))


if __name__=="__main__":main()
