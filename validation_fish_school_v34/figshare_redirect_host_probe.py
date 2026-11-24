"""v34c ONLY original Figshare redirect host names, no author file bytes.

No external redirect followed. Full signed Location URL is NEVER logged.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

from validation_fish_school_v34.original_figshare_metadata import (
    original_figshare_record_bytes,decode_author_record,SourceStop,
    PERMITTED_ORIGINAL_FILE_HOSTS
)
from validation_fish_school_v34.original_small_source_files import PINS

REDIRECTS={301,302,303,307,308}
ALLOWED_AUTHOR_FILE_NAMES={n for items in PINS.values() for n in items}

class FigshareStopRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, url):
        return None

def nofollow_one_request(url,method,opener=None):
    original=urlparse(url)
    if original.scheme!="https" or original.hostname not in PERMITTED_ORIGINAL_FILE_HOSTS:
        raise SourceStop("V34C_FIGSHARE_ORIGINAL_LINK_NOT_AUTHORIZED")
    if method not in ("HEAD","GET"):
        raise SourceStop("V34C_NON_SOURCE_PROBE_METHOD")
    if opener is None:
        opener=request.build_opener(FigshareStopRedirect()).open
    headers={"User-Agent":"boids-v34c-original-file-redirect-host-only/1.0",
             "Accept-Encoding":"identity"}
    if method=="GET":
        headers["Range"]="bytes=0-0"
    req=request.Request(url,headers=headers,method=method)
    try:
        with opener(req,timeout=18) as r:
            status=getattr(r,"status",200)
            location=r.headers.get("Location","") if hasattr(r,"headers") else ""
            # Intentionally ZERO bytes read, even if original provider returns HTTP 200.
    except error.HTTPError as exc:
        status=exc.code
        location=exc.headers.get("Location","")
    except (error.URLError,OSError,TimeoutError) as ex:
        raise SourceStop("V34C_ORIGINAL_PROVIDER_NETWORK_"+type(ex).__name__) from ex
    if status in REDIRECTS:
        if not location:
            raise SourceStop("V34C_ORIGINAL_PROVIDER_REDIRECT_LOCATION_EMPTY")
        loc=urlparse(location)
        if loc.scheme!="https" or not loc.hostname:
            raise SourceStop("V34C_ORIGINAL_PROVIDER_NONHTTPS_LOCATION_STOP")
        return {"status":"ORIGINAL_PROVIDER_REDIRECT_METADATA_ONLY",
                "original_request_method":method,
                "original_first_http_response_code":status,
                "redirect_scheme":"https",
                "original_location_host_ONLY_no_query_or_path":loc.hostname,
                "original_request_host":original.hostname,
                "n_downloaded_author_file_bytes":0,
                "redirect_followed":False,
                "original_signatures_or_tokens_logged":False}
    if status in (200,206):
        return {"status":"NO_REDIRECT_SOURCE_DIRECT",
                "original_request_method":method,
                "original_first_http_response_code":status,
                "original_location_host_ONLY_no_query_or_path":None,
                "original_request_host":original.hostname,
                "n_downloaded_author_file_bytes":0,
                "redirect_followed":False,
                "original_signatures_or_tokens_logged":False}
    if status in (405,501) and method=="HEAD":
        return {"status":"SOURCE_HEAD_UNSUPPORTED_RANGE_GET_PROBE_NEEDED",
                "original_request_method":method,"original_first_http_response_code":status}
    raise SourceStop("V34C_AUTHOR_PROVIDER_RETURNED_HTTP_"+str(status))


def run(probe=nofollow_one_request,fetchmeta=original_figshare_record_bytes):
    result={"status":"SOURCE_ACCESS_STOP",
      "frozen_original_source_protocol":"docs/V34C_FIGSHARE_AUTHOR_REDIRECT_HOST_SOURCE_ONLY_FREEZE.md",
      "original_provider_public_article_ids":sorted(PINS),
      "n_original_file_bytes_downloaded":0,
      "signed_external_location_urls_logged":False,
      "original_real_fish_trial_or_treatment_rows_read":False,
      "original_social_effect_calculated":False,
      "original_provider_file_probe_receipts":[]}
    success=0
    for article,files in PINS.items():
        try:
            body=fetchmeta(article)
            metadata=decode_author_record(body,article)
            lookup={x["original_filename"]:x for x in metadata["original_provider_file_manifest"]}
            if not set(files).issubset(lookup):
                raise SourceStop("V34C_PINNED_SOURCE_PROVIDER_FILES_MISSING")
            for name,(size,md5) in files.items():
                m=lookup[name]
                if m["original_source_file_bytes"]!=size or m["original_provider_supplied_MD5"]!=md5 or m["original_provider_computed_MD5"]!=md5:
                    raise SourceStop("V34C_AUTHOR_SUPPLIED_PINNED_MD5_OR_BYTES_MISMATCH")
                url=m["original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED"]
                try:
                    receipt=probe(url,"HEAD")
                    if receipt["status"]=="SOURCE_HEAD_UNSUPPORTED_RANGE_GET_PROBE_NEEDED":
                        receipt=probe(url,"GET")
                    if receipt["status"] not in ("ORIGINAL_PROVIDER_REDIRECT_METADATA_ONLY","NO_REDIRECT_SOURCE_DIRECT"):
                        raise SourceStop("V34C_UNVERIFIED_FIRST_PROVIDER_HTTP_RESPONSE")
                    receipt.update({
                     "original_figshare_article_id":article,
                     "original_file_name":name,
                     "source_expected_original_bytes":size,
                     "source_expected_original_MD5":md5,
                     "original_publisher_file_id":m["original_provider_file_id"]
                    })
                    success+=1
                except SourceStop as ex:
                    receipt={"status":"SOURCE_ACCESS_STOP","original_figshare_article_id":article,
                             "original_file_name":name,"source_stop_reason":str(ex)}
                result["original_provider_file_probe_receipts"].append(receipt)
        except (SourceStop,ValueError,KeyError) as ex:
            for name in files:
                result["original_provider_file_probe_receipts"].append({
                  "status":"SOURCE_ACCESS_STOP","original_figshare_article_id":article,
                  "original_file_name":name,"source_stop_reason":str(ex)
                })
    result["n_original_provider_files_with_verified_redirect_or_direct_metadata"]=success
    result["status"]=("ALL_FOUR_OFFICIAL_FIGSHARE_FILE_REDIRECT_HOSTS_VERIFIED" if success==4
          else "PARTIAL_ORIGINAL_PROVIDER_SOURCE_REDIRECT_METADATA_STOP" if success>0
          else "SOURCE_ACCESS_STOP")
    return result

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    a=cli.parse_args()
    d=run()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(d,sort_keys=True))

if __name__=="__main__":
    main()
