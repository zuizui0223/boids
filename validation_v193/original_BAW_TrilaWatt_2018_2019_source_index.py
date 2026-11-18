"""v193 authentic BAW TrilaWatt source file index + HEAD ONLY.

Find original 2018/2019 Dutch-region (nl) tide files from a live official
directory listing. Never invent paths, never GET a .nc payload, never claim
native z/waterlevel datum, tide at GPS, real survey-day, or ecology here.
"""
from __future__ import annotations
import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

SOURCE_DOI="https://doi.org/10.48437/7ca5ef-2e1287"
SOURCE_PAPER="https://doi.org/10.1038/s41597-025-06211-1"
OFFICIAL_ROOT="https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Hydrodynamik/"
OFFICIAL_HOST="dl.datenrepository.baw.de"
MAX_HTML_BYTES=800_000
MAX_INDEX_PAGES=25
MAX_DIR_DEPTH=2
YEARS=(2018,2019)
OUT=Path(__file__).resolve().parent/"results/authentic_BAW_TrilaWatt_Dutch_tides_2018_2019_source_v193.json"

class IndexLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!="a":return
        href=dict(attrs).get("href")
        if isinstance(href,str):self.links.append(href)

def approved_original_url(url):
    x=urllib.parse.urlsplit(url)
    return (x.scheme=="https" and x.hostname==OFFICIAL_HOST
            and x.port is None and x.query=="" and x.fragment==""
            and x.path.startswith(urllib.parse.urlsplit(OFFICIAL_ROOT).path)
            and "/../" not in urllib.parse.unquote(x.path)
            and "/./" not in urllib.parse.unquote(x.path))

def original_links(html:bytes,parent:str) -> list[str]:
    parser=IndexLinks()
    parser.feed(html.decode("utf-8",errors="replace"))
    result=[]
    for raw in parser.links:
        url=urllib.parse.urljoin(parent,raw)
        if approved_original_url(url) and url not in result:
            result.append(url)
    return result

def original_index_GET(url):
    if not approved_original_url(url):raise ValueError("NONOFFICIAL_BAW_HOST_OR_PATH")
    req=urllib.request.Request(url,headers={
        "User-Agent":"boids-v193-BAW-TrilaWatt-original-source-only/1.0",
        "Accept":"text/html"},method="GET")
    with urllib.request.urlopen(req,timeout=35) as response:
        content_type=response.headers.get("Content-Type","").lower()
        data=response.read(MAX_HTML_BYTES+1)
        status=response.status
    if len(data)>MAX_HTML_BYTES:raise ValueError("ORIGINAL_BAW_INDEX_TOO_LARGE")
    if status!=200 or ("html" not in content_type and not data.lstrip().startswith(b"<")):
        raise ValueError("ORIGINAL_BAW_INDEX_NOT_HTML")
    return data,{"url":url,"http_status":status,
                 "response_bytes":len(data),
                 "original_directory_HTML_SHA256":hashlib.sha256(data).hexdigest(),
                 "Content-Type":content_type}

def original_filename_year_candidate(url,year):
    if not approved_original_url(url):return False
    basename=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/",1)[-1]).lower()
    if not basename.endswith(".nc"):return False
    return (re.search(r"(^|[_-])tides([_.-]|$)",basename) is not None
        and re.search(r"(^|[_-])"+str(year)+r"([_.-]|$)",basename) is not None
        and re.search(r"(^|[_-])nl([_.-]|$)",basename) is not None)

def discover_original_files(fetch=original_index_GET):
    queue=deque([(OFFICIAL_ROOT,0)])
    seen_dirs=set()
    file_urls=[]
    receipts=[]
    errors=[]
    while queue and len(seen_dirs)<MAX_INDEX_PAGES:
        url,depth=queue.popleft()
        if url in seen_dirs:continue
        seen_dirs.add(url)
        try:
            payload,record=fetch(url)
            receipts.append(record)
            links=original_links(payload,url)
            for link in links:
                if link.endswith("/") and depth<MAX_DIR_DEPTH and link not in seen_dirs:
                    queue.append((link,depth+1))
                elif link.lower().endswith(".nc") and link not in file_urls:
                    file_urls.append(link)
        except Exception as exc:
            errors.append({"requested":url,"error_type":type(exc).__name__,
                           "error_summary":str(exc)[:180]})
    return {"directory_receipts":receipts,
            "directory_errors":errors,
            "total_original_netCDF_links_discovered":len(file_urls),
            "2018_candidates":[u for u in file_urls if original_filename_year_candidate(u,2018)],
            "2019_candidates":[u for u in file_urls if original_filename_year_candidate(u,2019)],
            "index_root_reachable":any(r.get("url")==OFFICIAL_ROOT for r in receipts),
            "any_browse_limit_truncated":bool(queue),
            "all_candidate_files_from_actual_source_href_not_generated":True}

def official_native_HEAD(url):
    if not approved_original_url(url) or not url.lower().endswith(".nc"):
        raise ValueError("NONOFFICIAL_OR_NON_NETCDF_BAW_FILE")
    req=urllib.request.Request(url,headers={
        "User-Agent":"boids-v193-BAW-TrilaWatt-original-HEAD-only/1.0"},method="HEAD")
    with urllib.request.urlopen(req,timeout=40) as response:
        header=response.headers
        status=response.status
        final=response.geturl()
    if not approved_original_url(final):raise ValueError("ORIGINAL_FILE_REDIRECT_OUTSIDE_BAW")
    content_length=header.get("Content-Length")
    try:filesize=int(content_length) if content_length else None
    except ValueError:filesize=None
    return {"source_href_unmodified":url,"http_status":status,
            "final_approved_original_source_url":final,
            "Content-Length":filesize,
            "ETag":header.get("ETag"),
            "Last-Modified":header.get("Last-Modified"),
            "Accept-Ranges":header.get("Accept-Ranges"),
            "no_model_binary_payload_downloaded":True}

def source_gate(discovered,head_responses):
    candidate={str(year):discovered.get(f"{year}_candidates",[]) for year in YEARS}
    count={y:len(c) for y,c in candidate.items()}
    head_ok=all(len(candidate[str(y)])==1
        and head_responses.get(str(y),{}).get("http_status")==200
        and head_responses[str(y)].get("final_approved_original_source_url")
        and head_responses[str(y)].get("Content-Length") is not None
        and head_responses[str(y)]["Content-Length"]>1000
        for y in YEARS)
    return {"official_directory_root_original_HTML_confirmed":discovered.get("index_root_reachable") is True,
        "exactly_one_original_Dutch_tides_file_per_year":all(v==1 for v in count.values()),
        "original_2018_and_2019_HEAD_metadata_verified":bool(head_ok),
        "native_netCDF_dimensions_time_bbox_and_units_verified":False,
        "local_model_h_at_bird_GPS_source_admitted":False,
        "native_model_vertical_datum_offset_to_RWS_NAP_verified":False,
        "original_20m_DEM_z_survey_day_and_datum_verified":False,
        "2019_as_real_time_forecast_available_in_2018":False,
        "file_candidate_counts":count,
        "downloaded_any_full_annual_NC_binary":False}

def run(out=OUT):
    evidence={"version":"v193-original-BAW-TrilaWatt-2018-2019-Dutch-tides-native-source-preflight",
        "original_publisher_DOI":SOURCE_DOI,
        "original_scientific_publication":SOURCE_PAPER,
        "official_download_catalogue_root_candidate_not_assumed_reachable":OFFICIAL_ROOT,
        "original_paper_2015_to_2022_model_output_not_source_verified_native":True,
        "stated_grid_from_publication":"approx 500m/20min; nl subset; 2018/19; native requires further checks",
        "original_source_only":True,"status":"SOURCE_STOP"}
    discovery=discover_original_files()
    evidence["original_directory_browse"]=discovery
    heads={}
    for year in YEARS:
        items=discovery[f"{year}_candidates"]
        if len(items)!=1:
            heads[str(year)]={"source_status":"SOURCE_STOP_MISSING_OR_AMBIGUOUS_ORIGINAL_YEAR_FILE"}
            continue
        try:heads[str(year)]=official_native_HEAD(items[0])
        except Exception as exc:
            heads[str(year)]={"source_status":"SOURCE_STOP_ORIGINAL_NATIVE_HEAD",
                              "error_type":type(exc).__name__,
                              "error_summary":str(exc)[:180]}
    evidence["original_native_file_HEAD_only"]=heads
    gates=source_gate(discovery,heads)
    evidence["scientific_admission_gates"]=gates
    if gates["official_directory_root_original_HTML_confirmed"] and gates["original_2018_and_2019_HEAD_metadata_verified"]:
        evidence["status"]="SOURCE_DUTCH_2018_2019_MODEL_FILES_HEAD_CONFIRMED_NETCDF_DATA_NOT_ADMITTED"
    else:
        evidence["status"]="SOURCE_STOP_ORIGINAL_BAW_2018_2019_MODEL_NATIVE_FILE_EXISTENCE"
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(evidence,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V193_TRILAWATT_SOURCE_SCOPE="+json.dumps({
        "status":evidence["status"],
        "gates":gates,
        "source_file_names_discovered":{str(y):discovery[f"{y}_candidates"] for y in YEARS},
        "native_HEAD_years":heads,
        "source_directory_errors":discovery["directory_errors"],
        "no_GPS_tide_or_biology_scored":True
    },sort_keys=True),flush=True)
    return evidence

if __name__=="__main__":run()
