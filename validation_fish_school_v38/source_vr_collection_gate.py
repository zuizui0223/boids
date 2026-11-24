"""v38 original author 2026 fish VR six-speed + 3D tracking METADATA only.

No file bytes, no fish trajectory, no original experimental outcomes or real-vs-
virtual trial identification. Only exact publisher-linked Figshare REST IDs.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

ARTICLES={
 "PLOS_ONE_2026_ORIGINAL_VR_PLATFORM_DATA":29097605,
 "PLOS_ONE_2026_3D_TRACKING_CODE":30188836,
 "PLOS_ONE_2026_VR_TRAJECTORY_SIMULATOR_CODE":30188842,
 "PLOS_ONE_2026_VR_RENDERER_CODE":30188845,
 "PLOS_ONE_2026_CAMERA_CALIBRATION_CODE":30188839
}
COLLECTION=8485282
HOST="api.figshare.com"
MAX_BYTES=3*1024*1024
MAX_FILES=60
MAX_ARTICLES=50

class SourceStop(Exception):pass

def author_json(url,opener=request.urlopen):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname!=HOST or not p.path.startswith("/v2/"):
        raise SourceStop("V38_NON_ORIGINAL_AUTHOR_API_HOST")
    req=request.Request(url,headers={"Accept":"application/json","Accept-Encoding":"identity",
                     "User-Agent":"Boids-v38-exact-original-fish-VR-source-metadata-only"})
    try:
        with opener(req,timeout=35) as response:
            final=response.geturl()
            fp=urlparse(final)
            if fp.scheme!="https" or fp.hostname!=HOST:
                raise SourceStop("V38_PUBLISHED_ORIGINAL_API_REDIRECT_EXTERNAL")
            b=response.read(MAX_BYTES+1)
    except error.HTTPError as ex:
        raise SourceStop("V38_PUBLISHED_ORIGINAL_API_HTTP_"+str(ex.code)) from ex
    except (error.URLError,TimeoutError,OSError) as ex:
        raise SourceStop("V38_PUBLISHED_ORIGINAL_API_TRANSPORT_"+type(ex).__name__) from ex
    if not b or len(b)>MAX_BYTES:
        raise SourceStop("V38_PUBLISHED_API_RESPONSE_EMPTY_OR_OVERSIZE")
    return b


def decode_json_bytes(b):
    if b[:100].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise SourceStop("V38_ORIGINAL_API_RETURNED_HTML_LOGIN")
    try:x=json.loads(b)
    except (UnicodeError,ValueError) as ex:raise SourceStop("V38_ORIGINAL_API_RESPONSE_NOT_JSON") from ex
    if isinstance(x,dict) and any(q in x for q in ("error","message")) and not "title" in x:
        raise SourceStop("V38_ORIGINAL_FIGSHARE_API_ERROR_ENVELOPE")
    return x


def author_article_manifest(x,article):
    if not isinstance(x,dict) or x.get("id")!=article:
        raise SourceStop("V38_AUTHOR_ARTICLE_PUBLIC_SOURCE_ID_MISMATCH")
    doi=x.get("doi","")
    if not isinstance(doi,str) or not re.fullmatch(
           rf"10\.6084/m9\.figshare\.{article}(?:\.v[0-9]+)?",doi,re.I):
        raise SourceStop("V38_AUTHOR_ORIGINAL_DATA_DOI_ID_MISMATCH")
    if x.get("is_embargoed") is True or x.get("is_public") is False:
        raise SourceStop("V38_ORIGINAL_SOURCE_PRIVATE_OR_EMBARGOED")
    title=x.get("title")
    if not isinstance(title,str) or not title.strip():raise SourceStop("V38_AUTHOR_ARTICLE_TITLE_MISSING")
    files=x.get("files")
    if not isinstance(files,list) or not 1<=len(files)<=MAX_FILES:
        raise SourceStop("V38_AUTHOR_FILE_LIST_MISSING_OR_LARGE")
    names=set();receipts=[]
    for f in files:
        if not isinstance(f,dict):raise SourceStop("V38_ORIGINAL_FILE_ROW_NOT_OBJECT")
        name=f.get("name")
        size=f.get("size")
        if not isinstance(name,str) or not name.strip() or len(name)>512 or name in names:
            raise SourceStop("V38_ORIGINAL_AUTHOR_FILE_NAME_NOT_UNIQUE")
        names.add(name)
        if type(size)!=int or size<=0:raise SourceStop("V38_ORIGINAL_AUTHOR_FILE_SIZE_MISSING")
        url=f.get("download_url")
        if not isinstance(url,str) or urlparse(url).scheme!="https" or not urlparse(url).hostname:
            raise SourceStop("V38_ORIGINAL_AUTHOR_NO_PUBLISHED_DOWNLOAD_SOURCE")
        supplied=f.get("supplied_md5")
        calculated=f.get("computed_md5")
        for value in (supplied,calculated):
            if value is not None and not re.fullmatch(r"[0-9a-fA-F]{32}",str(value)):
                raise SourceStop("V38_PUBLISHED_MD5_SCHEMA_INVALID")
        low=name.lower()
        role=("PUBLISHED_VIDEO_OR_MOVIE_NOT_ORIGINAL_TRACKING_ROWS" if low.endswith((".mov",".mp4",".avi",".mkv"))
              else "PUBLISHED_PDF_SUPPLEMENT_NOT_INDIVIDUAL_FISH_DATA" if low.endswith(".pdf")
              else "POTENTIAL_SOURCE_DICTIONARY" if re.search(r"(readme|manifest|metadata|dictionary)",low)
              else "POTENTIAL_AUTHOR_EXPERIMENT_TRIAL_SESSION" if re.search(r"(trial|session|fish|record|experiment|track|traj|real|vr)",low)
              else "POTENTIAL_AUTHOR_CODE" if low.endswith((".py",".r",".c",".h",".m",".ipynb")) or re.search(r"(code|script)",low)
              else "UNCLASSIFIED_FILENAME_ONLY")
        receipts.append({"source_name":name,"original_Figshare_file_id":f.get("id"),
                         "provider_original_byte_size":size,
                         "source_publisher_MD5_supplied":supplied,
                         "source_publisher_MD5_computed":calculated,
                         "official_original_download_source_HOST_ONLY":urlparse(url).hostname,
                         "potential_role_FROM_FILENAME_ONLY":role,
                         "original_fish_data_file_content_read":False})
    return {
        "status":"ORIGINAL_PUBLISHER_FIGSHARE_ARTICLE_METADATA_VERIFIED",
        "original_article_id":article,
        "original_record_title":title[:500],
        "original_published_doi":doi,
        "published_date":x.get("published_date"),
        "modified_date":x.get("modified_date"),
        "n_original_published_files":len(receipts),
        "total_published_original_file_bytes":sum(f["provider_original_byte_size"] for f in receipts),
        "original_provider_filename_MD5_size_manifest":receipts,
        "original_animals_sessions_and_trails_NOT_verified":True,
    }


def author_collection_manifest(meta,items):
    if not isinstance(meta,dict) or meta.get("id")!=COLLECTION:
        raise SourceStop("V38_SIX_SPEED_COLLECTION_IDENTITY_STOP")
    doi=meta.get("doi","")
    if not isinstance(doi,str) or not re.fullmatch(
           rf"10\.6084/m9\.figshare\.c\.{COLLECTION}(?:\.v[0-9]+)?",doi,re.I):
        raise SourceStop("V38_ORIGINAL_ROYAL_COLLECTION_DOI_MISMATCH")
    if meta.get("is_public") is False:
        raise SourceStop("V38_FIGSHARE_COLLECTION_NOT_PUBLIC")
    if not isinstance(items,list) or not 1<=len(items)<=MAX_ARTICLES:
        raise SourceStop("V38_FIGSHARE_SOURCE_COLLECTION_EMPTY_OR_MORE_THAN_50")
    ids=set();out=[]
    for x in items:
        if not isinstance(x,dict) or type(x.get("id"))!=int or x.get("id")<1:
            raise SourceStop("V38_AUTHOR_ORIGINAL_COLLECTION_MEMBER_ID_INVALID")
        n=x["id"]
        if n in ids:raise SourceStop("V38_AUTHOR_COLLECTION_MEMBER_DUPLICATE")
        ids.add(n)
        title=x.get("title")
        if not isinstance(title,str) or not title.strip():
            raise SourceStop("V38_COLLECTION_MEMBER_AUTHOR_TITLE_MISSING")
        out.append({"original_member_article_ID":n,"original_member_article_TITLE":title[:500],
                    "original_member_doi":x.get("doi"),
                    "original_member_published_date":x.get("published_date"),
                    "original_member_FILES_AND_FISH_RESULTS_NOT_ACCESSED":True})
    return {
      "status":"ORIGINAL_PUBLISHER_FIGSHARE_COLLECTION_AND_MEMBER_IDS_VERIFIED",
      "original_collection_id":COLLECTION,
      "original_collection_doi":doi,
      "original_collection_title":str(meta.get("title",""))[:500],
      "original_collection_member_count":len(out),
      "original_member_article_IDs":[v["original_member_article_ID"] for v in out],
      "original_collection_member_article_METADATA_ONLY":out,
      "collection_member_full_original_file_manifests_NOT_ACCESSED":True
    }


def run(fetch=author_json):
    report={"status":"SOURCE_METADATA_STOP",
       "source_version_freeze":"docs/V38_ORIGINAL_VR_SIX_SPEED_COLLECTION_SOURCE_METADATA_FREEZE.md",
       "source_original_research":"Sanchez 2026 PLOS ONE VR fish platform; Reynaud 2026 Proc R Soc B six-speed open-loop",
       "source_original_article_request_IDs":ARTICLES,
       "source_original_collection_request_ID":COLLECTION,
       "original_source_file_bytes_read":False,
       "original_fish_trial_values_or_real_virtual_coordinates_read":False,
       "new_original_speed_effect_computed":False,
       "real_vs_virtual_and_trial_IDs_verified":False,
       "source_article_receipts":{}}
    n=0
    for label,id in ARTICLES.items():
        u=f"https://api.figshare.com/v2/articles/{id}"
        v={"status":"SOURCE_METADATA_STOP","article_id":id}
        try:
            b=fetch(u)
            v.update(author_article_manifest(decode_json_bytes(b),id))
            v["original_author_API_response_SHA256"]=hashlib.sha256(b).hexdigest()
            n+=1
        except (SourceStop,KeyError,ValueError) as ex:
            v["source_stop_reason"]=str(ex)
        report["source_article_receipts"][label]=v
    try:
        u=f"https://api.figshare.com/v2/collections/{COLLECTION}"
        u2=f"https://api.figshare.com/v2/collections/{COLLECTION}/articles?page_size=50"
        m=fetch(u)
        b=fetch(u2)
        report["source_published_six_speed_collection"]=author_collection_manifest(
           decode_json_bytes(m),decode_json_bytes(b))
        report["source_published_six_speed_collection"]["original_collection_API_SHA256"]=hashlib.sha256(m).hexdigest()
        report["source_published_six_speed_collection"]["original_member_article_list_API_SHA256"]=hashlib.sha256(b).hexdigest()
        n+=1
    except (SourceStop,KeyError,ValueError) as ex:
        report["source_published_six_speed_collection"]={"status":"SOURCE_METADATA_STOP",
                                                          "source_stop_reason":str(ex)}
    report["n_of_six_original_metadata_targets_verified"]=n
    report["status"]=("ALL_SIX_ORIGINAL_VR_PUBLISHED_SOURCE_RECORDS_VERIFIED" if n==6
         else "PARTIAL_VR_SOURCE_METADATA_VERIFIED" if n>0 else "SOURCE_METADATA_STOP")
    return report


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
