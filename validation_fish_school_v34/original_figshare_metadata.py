"""v34: SOURCE-ONLY original 2026 virtual/robot fish experiment figshare audit.

Frozen before original biological trial files/conditions/positions downloaded.
Checks publisher-linked figshare original DATA and CODE record metadata ONLY.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SOURCE_RECORDS={
 "PRX2026_VR_FISH_REAL_VIRTUAL_DATA":31378621,
 "PRX2026_VR_FISH_REAL_VIRTUAL_CODE":31386349,
 "BIORXIV2026_CLOSED_LOOP_ROBOT_FISH_DATA":33086195,
 "PLOS2026_3D_REAL_VIRTUAL_DATA":30539666
}
PERMITTED_META_HOST="api.figshare.com"
PERMITTED_ORIGINAL_FILE_HOSTS={"figshare.com","www.figshare.com","api.figshare.com",
                               "ndownloader.figshare.com"}
MAX_METADATA_BODY=3*1024*1024
MAX_FIGSHARE_ORIGINAL_FILES=50
API_TEMPLATE="https://api.figshare.com/v2/articles/{id}"

class SourceStop(Exception):pass

def original_figshare_record_bytes(article_id,opener=urlopen):
    if type(article_id)!=int or article_id not in SOURCE_RECORDS.values():
        raise SourceStop("V34_UNREGISTERED_2026_AUTHOR_FIGSHARE_ARTICLE")
    url=API_TEMPLATE.format(id=article_id)
    p=urlparse(url)
    if p.scheme!="https" or p.hostname!=PERMITTED_META_HOST:
        raise SourceStop("V34_FIGSHARE_API_HOST_NOT_AUTHORIZED")
    req=Request(url,headers={"User-Agent":"boids-v34-original-figshare-metadata-only/1.0",
                             "Accept":"application/json","Accept-Encoding":"identity"})
    try:
        with opener(req,timeout=28) as response:
            final=response.geturl() if hasattr(response,"geturl") else url
            p2=urlparse(final)
            if p2.scheme!="https" or p2.hostname!=PERMITTED_META_HOST:
                raise SourceStop("V34_ORIGINAL_AUTHOR_FIGSHARE_META_EXTERNAL_REDIRECT")
            blob=response.read(MAX_METADATA_BODY+1)
    except HTTPError as e: raise SourceStop("V34_AUTHOR_SOURCE_HTTP_"+str(e.code)) from e
    except (URLError,OSError,TimeoutError) as e:
        raise SourceStop("V34_AUTHOR_SOURCE_NETWORK_"+type(e).__name__) from e
    if not blob or len(blob)>MAX_METADATA_BODY:
        raise SourceStop("V34_FIGSHARE_METADATA_EMPTY_OR_EXCEEDS_LIMIT")
    return blob


def decode_author_record(body,article_id):
    if body[:64].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise SourceStop("V34_FIGSHARE_AUTH_OR_ERROR_HTML")
    try:record=json.loads(body)
    except (UnicodeError,ValueError) as ex:
        raise SourceStop("V34_FIGSHARE_AUTHOR_JSON_PARSE_STOP") from ex
    if not isinstance(record,dict):
        raise SourceStop("V34_ORIGINAL_METADATA_JSON_NOT_OBJECT")
    if ("message" in record or "error" in record) and "files" not in record:
        raise SourceStop("V34_FIGSHARE_API_ERROR_ENVELOPE_NOT_ORIGINAL_RECORD")
    if record.get("id")!=article_id:
        raise SourceStop("V34_ORIGINAL_AUTHOR_FIGSHARE_ARTICLE_ID_MISMATCH")
    doi=record.get("doi","")
    if not isinstance(doi,str) or not re.fullmatch(
        rf"10\.6084/m9\.figshare\.{article_id}(?:\.v[0-9]+)?",doi,re.I):
        raise SourceStop("V34_AUTHOR_FIGSHARE_IDENTITY_DOI_MISMATCH")
    title=record.get("title")
    if not isinstance(title,str) or not title.strip() or len(title)>1000:
        raise SourceStop("V34_AUTHOR_SOURCE_RECORD_TITLE_EMPTY")
    if record.get("is_embargoed") is True:
        raise SourceStop("V34_AUTHOR_SOURCE_IS_EMBARGOED")
    raw=record.get("files")
    if not isinstance(raw,list) or not 1<=len(raw)<=MAX_FIGSHARE_ORIGINAL_FILES:
        raise SourceStop("V34_AUTHOR_SOURCE_FILE_LIST_EMPTY_OR_EXCESSIVE")
    files=[]
    names=set()
    for f in raw:
        if not isinstance(f,dict):
            raise SourceStop("V34_PUBLISHED_FILE_ENTRY_NOT_OBJECT")
        name=f.get("name")
        size=f.get("size")
        if not isinstance(name,str) or not name.strip() or len(name)>400 or name in names:
            raise SourceStop("V34_AUTHOR_SOURCE_MISSING_OR_DUPLICATE_FILENAME")
        names.add(name)
        if type(size)!=int or size<=0:
            raise SourceStop("V34_AUTHOR_FILE_BYTES_NOT_DECLARED")
        url=f.get("download_url")
        if not isinstance(url,str) or not url:
            raise SourceStop("V34_AUTHOR_FILE_MISSING_ORIGINAL_PROVIDER_DOWNLOAD_URL")
        pu=urlparse(url)
        if pu.scheme!="https" or pu.hostname not in PERMITTED_ORIGINAL_FILE_HOSTS:
            raise SourceStop("V34_AUTHOR_FILE_ORIGINAL_DOWNLOAD_URL_NOT_FIGSHARE_HOST")
        supplied=f.get("supplied_md5")
        computed=f.get("computed_md5")
        sha=f.get("sha1")
        if supplied and not re.fullmatch(r"[a-fA-F0-9]{32}",str(supplied)):
            raise SourceStop("V34_PUBLISHED_SUPPLIED_MD5_INVALID")
        if computed and not re.fullmatch(r"[a-fA-F0-9]{32}",str(computed)):
            raise SourceStop("V34_PUBLISHED_COMPUTED_MD5_INVALID")
        lower=name.lower()
        label=("POSSIBLE_ORIGINAL_TRAJECTORIES" if any(
            s in lower for s in ("track","traj","pos","kinemat","coord","experiment","trial","fish","session"))
            else "POSSIBLE_AUTHOR_CODE" if any(s in lower for s in ("code","script","matlab",".py",".r",".m", "source"))
            else "README_OR_DATA_DICTIONARY" if any(s in lower for s in ("readme","metadata","dictionary","manifest","description"))
            else "SOURCE_ROLE_NOT_CONFIRMED_FROM_FILENAME")
        files.append({
           "original_filename":name,
           "original_provider_file_id":f.get("id"),
           "original_source_file_bytes":size,
           "original_provider_supplied_MD5":supplied,
           "original_provider_computed_MD5":computed,
           "original_provider_sha1":sha,
           "original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED":url,
           "original_source_type_candidate_FILENAME_ONLY":label,
           "source_content_not_opened":True
        })
    lic=record.get("license")
    if isinstance(lic,dict):
        lic={"name":lic.get("name"),"url":lic.get("url"),"value":lic.get("value")}
    elif lic is not None and not isinstance(lic,str):
        lic=str(type(lic).__name__)
    return {
        "status":"AUTHOR_FIGSHARE_ORIGINAL_METADATA_VERIFIED",
        "original_figshare_article_id":article_id,
        "source_published_DOI":doi,
        "original_author_record_title":title.strip(),
        "original_published_at":record.get("published_date"),
        "original_created_at":record.get("created_date"),
        "original_modified_at":record.get("modified_date"),
        "original_source_record_version":record.get("version"),
        "original_figshare_record_public":record.get("is_public"),
        "original_figshare_record_license_metadata":lic,
        "n_author_source_files":len(files),
        "total_source_provider_published_file_bytes":sum(f["original_source_file_bytes"] for f in files),
        "original_provider_file_manifest":files,
        "original_file_bytes_or_fish_behavior_loaded":False,
        "biological_intervention_effect_measured":False,
        "original_subject_session_treatment_IDs_verified":False
    }


def run(fetcher=original_figshare_record_bytes):
    report={
      "status":"SOURCE_ACCESS_STOP",
      "source_protocol":"docs/V34_CONTROLLED_FISH_VIRTUAL_ROBOT_ORIGINAL_FIGSHARE_SOURCE_FREEZE.md",
      "source_explicit_article_ids":SOURCE_RECORDS,
      "original_fish_file_contents_downloaded":False,
      "original_vr_or_robot_manipulation_outcomes_computed":False,
      "original_fish_acoustic_calls_identified":False,
      "author_figshare_record_source_manifest":{}
    }
    good=0
    for family,article in SOURCE_RECORDS.items():
        d={"status":"SOURCE_ACCESS_STOP","original_figshare_article_id":article,
           "author_declared_original_metadata_URL":API_TEMPLATE.format(id=article)}
        try:
            body=fetcher(article)
            d.update(decode_author_record(body,article))
            d["original_author_metadata_response_SHA256"]=hashlib.sha256(body).hexdigest()
            d["source_metadata_bytes"]=len(body)
            good+=1
        except (SourceStop,UnicodeError,ValueError,KeyError) as exc:
            d["source_stop_reason"]=str(exc)
        report["author_figshare_record_source_manifest"][family]=d
    if good==len(SOURCE_RECORDS):
        report["status"]="ALL_FOUR_SOURCE_RECORD_METADATA_VERIFIED"
    elif good>0:
        report["status"]="PARTIAL_SOURCE_METADATA_STOP"
    return report

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--output",type=Path,required=True)
    opts=arg.parse_args()
    data=run()
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(data,sort_keys=True))

if __name__=="__main__":main()
