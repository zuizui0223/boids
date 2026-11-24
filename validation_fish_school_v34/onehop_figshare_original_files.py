"""v34d source-only 2026 original publisher checksum small files through ONE
official Figshare ndownloader -> exact previously authenticated Cloudflare R2 CDN.

No broadened redirect access, source figure/trajectory value or fish effect.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

from validation_fish_school_v34.original_figshare_metadata import SourceStop
from validation_fish_school_v34.original_small_source_files import source_run

ORIGINAL_PROVIDER="ndownloader.figshare.com"
EXACT_VENDOR_CDN="44c1cec316ec56bca76dfd65d2882b20.r2.cloudflarestorage.com"
ORIGINAL_HOST_PROOF="docs/v34_verification/FOUR_OFFICIAL_FIGSHARE_FILES_EXACT_302_CDN_HOST_ONLY_RECEIPT.json"
FROZEN_V34D="docs/V34D_EXACT_FIGSHARE_ORIGINAL_AUTHOR_CDN_ONE_HOP_MD5_FREEZE.md"
MAX_SOURCE_BYTES=2*1024*1024+1024

class VerifiedOriginalOneHopFigshare(request.HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.onehop_count=0
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        src=urlparse(req.full_url)
        dest=urlparse(newurl)
        if (self.onehop_count!=0 or code not in (301,302,303,307,308) or
            src.scheme!="https" or src.hostname!=ORIGINAL_PROVIDER or
            dest.scheme!="https" or dest.hostname!=EXACT_VENDOR_CDN):
            raise SourceStop("V34D_ORIGINAL_PROVIDER_SIGNED_CDN_ONE_HOP_GATE_STOP")
        self.onehop_count+=1
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def verified_original_figshare_small_bytes(url,size,author_md5,opener_factory=request.build_opener):
    q=urlparse(url)
    if q.scheme!="https" or q.hostname!=ORIGINAL_PROVIDER or q.query:
        raise SourceStop("V34D_SOURCE_ORIGINAL_PROVIDER_DIRECT_UNMODIFIED_URL_REQUIRED")
    if type(size)!=int or not 0<size<=MAX_SOURCE_BYTES:
        raise SourceStop("V34D_ONLY_FOUR_FROZEN_SMALL_ORIGINAL_SOURCE_FILE_BYTES")
    if not re.fullmatch(r"[a-f0-9]{32}",author_md5):
        raise SourceStop("V34D_ORIGINAL_AUTHOR_MD5_NOT_TRUSTED")
    handler=VerifiedOriginalOneHopFigshare()
    opener=opener_factory(handler)
    req=request.Request(url,headers={
        "User-Agent":"boids-v34d-Figshare-exact-official-one-hop-MD5-source-only/1.0",
        "Accept":"application/octet-stream,*/*","Accept-Encoding":"identity"},
        method="GET")
    try:
        with opener.open(req,timeout=48) as resp:
            final=resp.geturl() if hasattr(resp,"geturl") else url
            dest=urlparse(final)
            if handler.onehop_count!=1 or dest.scheme!="https" or dest.hostname!=EXACT_VENDOR_CDN:
                raise SourceStop("V34D_ORIGINAL_FIGSHARE_EXACT_ONE_CDN_HOP_NOT_OBSERVED")
            data=resp.read(size+1)
    except error.HTTPError as ex:
        raise SourceStop("V34D_ORIGINAL_FIGSHARE_HTTP_"+str(ex.code)) from ex
    except (error.URLError,OSError,TimeoutError) as ex:
        raise SourceStop("V34D_ORIGINAL_FIGSHARE_NETWORK_"+type(ex).__name__) from ex
    if len(data)!=size or hashlib.md5(data).hexdigest()!=author_md5:
        raise SourceStop("V34D_ORIGINAL_AUTHOR_MD5_OR_BYTE_COUNT_MISMATCH")
    if data[:256].lstrip().lower().startswith((b"<html",b"<!doctype",b'{"message"')):
        raise SourceStop("V34D_ORIGINAL_FILE_WAS_HTTP_OR_JSON_ERROR_ENVELOPE")
    return data


def run():
    p=Path(ORIGINAL_HOST_PROOF)
    if not p.exists():
        raise SourceStop("V34D_IMMUTABLE_ORIGINAL_PROVIDER_REDIRECT_PROOF_NOT_COMMITTED")
    proof=json.loads(p.read_text(encoding="utf8"))
    rec=proof.get("original_provider_file_probe_receipts",[])
    if (proof.get("status")!="ALL_FOUR_OFFICIAL_FIGSHARE_FILE_REDIRECT_HOSTS_VERIFIED" or
        len(rec)!=4 or any(r.get("original_location_host_ONLY_no_query_or_path")!=EXACT_VENDOR_CDN or
                       r.get("original_request_host")!=ORIGINAL_PROVIDER or
                       r.get("original_first_http_response_code")!=302 or
                       r.get("redirect_followed") is not False or
                       r.get("n_downloaded_author_file_bytes")!=0
                       for r in rec)):
        raise SourceStop("V34D_ORIGINAL_VENDOR_SIGNED_CDN_HOST_NOT_PROVEN_BY_AUTHOR")
    out=source_run(fetchsmall=verified_original_figshare_small_bytes)
    out["original_vendor_CDN_host_exactly_audited"]=EXACT_VENDOR_CDN
    out["original_vendor_CDN_host_frozen_proof_receipt"]=ORIGINAL_HOST_PROOF
    out["original_vendor_CDN_one_original_publisher_redirect_only"]=True
    out["original_figshare_signed_Location_URLs_never_logged"]=True
    out["frozen_source_protocol"]=FROZEN_V34D
    return out


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--output",type=Path,required=True)
    args=arg.parse_args()
    try:d=run()
    except (SourceStop,KeyError,ValueError,FileNotFoundError) as ex:
        d={"status":"SOURCE_ACCESS_STOP",
           "source_stop_reason":str(ex),
           "original_2026_research_trial_values_read":False,
           "original_agent_position_trajectories_read":False,
           "original_experimental_treatment_effect_fit":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(d,sort_keys=True))


if __name__=="__main__":main()
