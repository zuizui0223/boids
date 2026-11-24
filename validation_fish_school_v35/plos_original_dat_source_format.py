"""v35 original PLOS 2026 3D fish VR DAT streaming provider MD5/source header gate.

Fully authenticates original 2R/C1/C2/C3 author bytes from Figshare;
first 32KiB ONLY format inspection; no original trajectory rows exported,
no future-speed effect modeled and no original VR causal inference.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib import request,error
from urllib.parse import urlparse

from validation_fish_school_v34.original_figshare_metadata import (
    SourceStop, original_figshare_record_bytes, decode_author_record)
from validation_fish_school_v34.onehop_figshare_original_files import (
    VerifiedOriginalOneHopFigshare,EXACT_VENDOR_CDN,ORIGINAL_PROVIDER)

ARTICLE=30539666
ORIGINAL={
 "2R-TwoRealFish.dat":(34978800,"9221dd5d230b3db62143037b68dcd263"),
 "C1-OneReal+OneVirtual.dat":(37289920,"1404f74726278aacddc0361abcd556c3"),
 "C2-OneReal+OneVirtual.dat":(65786880,"9b727ba4bf64aa3aa1142d584a65cf2a"),
 "C3-OneReal+OneVirtual.dat":(56295005,"6b3afe13c9e1be33d19fbd24be3997a8")
}
PROTOCOL="docs/V35_PLOS_2026_ORIGINAL_FOUR_CONDITION_DAT_MD5_CLOCK_SESSION_SCHEMA_FREEZE.md"
MAX_SOURCE_BYTES=70000000
PREFIX=32768
CHUNK=1024*1024


def original_bytes_checksum_only(url,size,expected_md5,opener_factory=request.build_opener):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname!=ORIGINAL_PROVIDER or p.query:
        raise SourceStop("V35_ORIGINAL_FIGSHARE_NDOWNLOADER_HOST_ONLY")
    if type(size)!=int or not 0<size<=MAX_SOURCE_BYTES or not re.fullmatch(r"[0-9a-f]{32}",expected_md5):
        raise SourceStop("V35_AUTHOR_PUBLISHED_SIZE_OR_MD5_INVALID")
    handler=VerifiedOriginalOneHopFigshare()
    opener=opener_factory(handler)
    req=request.Request(url,headers={"Accept-Encoding":"identity",
         "User-Agent":"boids-v35-PLOS-original-fish-source-bytes-MD5-SCHEMA-ONLY/1.0"},
         method="GET")
    total=0;prefix=bytearray();nlines=0;md5=hashlib.md5();sha256=hashlib.sha256()
    try:
        with opener.open(req,timeout=90) as r:
            final=urlparse(r.geturl() if hasattr(r,"geturl") else url)
            if handler.onehop_count!=1 or final.scheme!="https" or final.hostname!=EXACT_VENDOR_CDN:
                raise SourceStop("V35_FIGSHARE_ONE_AUTHORIZED_SOURCE_CDN_HOP_NOT_PROVEN")
            while True:
                chunk=r.read(CHUNK)
                if not chunk:break
                total+=len(chunk)
                if total>size or total>MAX_SOURCE_BYTES:
                    raise SourceStop("V35_ORIGINAL_FISH_FILE_PROVIDER_BYTES_OVERRUN")
                md5.update(chunk);sha256.update(chunk);nlines+=chunk.count(b"\n")
                if len(prefix)<PREFIX:
                    prefix.extend(chunk[:PREFIX-len(prefix)])
    except error.HTTPError as ex:
        raise SourceStop("V35_ORIGINAL_PROVIDER_HTTP_"+str(ex.code)) from ex
    except (error.URLError,OSError,TimeoutError) as ex:
        raise SourceStop("V35_ORIGINAL_PROVIDER_ACCESS_"+type(ex).__name__) from ex
    if total!=size or md5.hexdigest()!=expected_md5:
        raise SourceStop("V35_ORIGINAL_AUTHOR_SUPPLIED_MD5_SIZE_CHECK_FAILED")
    if bytes(prefix[:128]).lstrip().lower().startswith((b"<html",b"<!doctype",b'{"error"',b'{"message"')):
        raise SourceStop("V35_ORIGINAL_FIGSHARE_ERROR_ENVELOPE_BYTES")
    return {
      "authenticated_original_author_bytes_count":total,
      "authenticated_original_author_MD5":md5.hexdigest(),
      "computed_original_source_SHA256":sha256.hexdigest(),
      "n_original_source_newline_bytes":nlines,
      "original_source_first_32KiB_bytes_ONLY":bytes(prefix)
    }


def safe_source_format(prefix):
    if not prefix:return {"format_status":"ORIGINAL_SOURCE_PREFIX_EMPTY_STOP"}
    binary_nul=prefix.count(b"\x00")
    low=sum((b<9 or 14<=b<=31 or b>=128) for b in prefix)
    if binary_nul>0 or low/len(prefix)>.15:
        return {"original_source_format":"BINARY_OR_NONPLAIN_TEXT",
            "first_source_prefix_bytes_examined":len(prefix),
            "n_source_null_bytes_in_prefix":binary_nul,
            "first_original_source_rows_or_values_exported":False,
            "source_explicit_subject_session_real_virtual_identity":"NOT_ADMITTED"}
    try:
        raw=prefix.decode("utf-8")
        encoding="utf-8"
    except UnicodeError:
        raw=prefix.decode("cp1252")
        encoding="windows-1252"
    full=raw.split("\n")[:-1] # ignore truncated final source line
    lines=full[:12]
    original_lines=[]
    for line in lines:
        text=line.strip()
        if not text:
            original_lines.append({"is_empty_original_line":True,"n_source_tokens":0,
                                   "n_numeric_source_tokens":0})
            continue
        # tab, comma and ordinary whitespace delimiters. Report counts only.
        tokens=[tok for tok in re.split(r"[,;\s]+",text) if tok]
        num=0
        for tok in tokens:
            try:float(tok);num+=1
            except ValueError: pass
        original_lines.append({"is_empty_original_line":False,
              "n_source_tokens":len(tokens),
              "n_numeric_source_tokens":num,
              "n_nonnumeric_source_tokens":len(tokens)-num})
    if not lines:
        return {"original_source_format":"ASCII_WITH_NO_COMPLETE_HEADER_LINES",
                "first_source_prefix_bytes_examined":len(prefix),
                "original_source_first_rows_values_exported":False,
                "source_explicit_subject_session_real_virtual_identity":"NOT_ADMITTED"}
    first=re.split(r"[,;\s]+",lines[0].strip())
    first=[tok for tok in first if tok]
    n_numeric=original_lines[0].get("n_numeric_source_tokens",0)
    nonnumeric_header=bool(first and n_numeric==0 and not lines[0].lstrip().startswith("#"))
    if nonnumeric_header:
        fields=[t for t in first[:25] if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9./-]{0,60}",t)]
    else:fields=[]
    f=" ".join(fields).lower()
    gate={
      "original_session_id_column_named_explicitly":bool(re.search(r"\b(session|subject|trial|run)[_a-z0-9]*\b",f)),
      "original_real_virtual_agent_column_named_explicitly":("real" in f and "virtual" in f),
      "original_native_sampling_clock_column_named_explicitly":bool(re.search(r"\b(time|frame|timestamp|fps|sample)[_a-z0-9]*\b",f))
    }
    return {
      "original_source_format":"ASCII_OR_UTF8_TEXT",
      "original_source_text_encoding":encoding,
      "first_source_prefix_bytes_examined":len(prefix),
      "first_source_header_is_pure_nonnumeric_tokens":nonnumeric_header,
      "original_source_first_12_complete_line_TOKEN_COUNTS_ONLY":original_lines,
      "original_header_nonnumeric_COLUMN_NAMES_only_max25":fields,
      "original_numeric_X_Y_Z_time_or_treatment_values_exported":False,
      "source_explicit_subject_session_real_virtual_identity":"NOT_ADMITTED" if not all(gate.values()) else "POTENTIAL_HEADER_NAMES_ONLY_NEEDS_AUTHOR_DOCUMENTATION",
      "source_identification_HEADER_ONLY_NOT_FULL_SESSION_ID":gate
    }


def run(name,reader=original_bytes_checksum_only,fetchmeta=original_figshare_record_bytes):
    if name not in ORIGINAL:raise SourceStop("V35_UNREGISTERED_FISH_CONDITION_SOURCE_FILENAME")
    size,md5=ORIGINAL[name]
    info={
      "status":"SOURCE_ACCESS_STOP",
      "original_source_paper_DOI":"10.1371/journal.pcbi.1014544",
      "original_provider_Figshare_article_id":ARTICLE,
      "original_source_file_name":name,
      "provider_expected_original_bytes":size,
      "provider_expected_original_MD5":md5,
      "frozen_before_original_large_file_bytes":PROTOCOL,
      "real_VR_fish_intervention_outcome_computed":False,
      "original_animal_coordinate_values_or_times_exported":False,
      "original_source_data_file_redistributed":False,
      "independent_fish_session_and_trial_IDs_verified":False
    }
    try:
        meta=decode_author_record(fetchmeta(ARTICLE),ARTICLE)
        if len(meta["original_provider_file_manifest"])!=6:
            raise SourceStop("V35_ORIGINAL_PLOS_PUBLISHED_SIX_FILE_MANIFEST_CHANGED")
        byname={f["original_filename"]:f for f in meta["original_provider_file_manifest"]}
        f=byname.get(name)
        if not f or f["original_source_file_bytes"]!=size or f["original_provider_supplied_MD5"]!=md5 or f["original_provider_computed_MD5"]!=md5:
            raise SourceStop("V35_ORIGINAL_PUBLISHED_DAT_METADATA_DRIFT")
        verified=reader(f["original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED"],size,md5)
        if (verified["authenticated_original_author_bytes_count"]!=size or
            verified["authenticated_original_author_MD5"]!=md5 or
            not re.fullmatch(r"[0-9a-f]{64}",verified["computed_original_source_SHA256"])):
            raise SourceStop("V35_ORIGINAL_AUTHOR_BYTES_NOT_AUTHENTIC")
        data=verified.pop("original_source_first_32KiB_bytes_ONLY")
        info.update(verified)
        info.update(safe_source_format(data))
        info["original_provider_SHA256_created_after_original_MD5_pass"]=True
        info["status"]="ORIGINAL_AUTHOR_DAT_BYTES_MD5_VERIFIED_SOURCE_FORMAT_ONLY"
    except (SourceStop,KeyError,ValueError,UnicodeError) as exc:
        info["source_stop_reason"]=str(exc)
    return info


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-file",required=True,choices=tuple(ORIGINAL))
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    d=run(args.source_file)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in d.items() if k!="original_source_first_12_complete_line_TOKEN_COUNTS_ONLY"},sort_keys=True))
    if d["status"]!="ORIGINAL_AUTHOR_DAT_BYTES_MD5_VERIFIED_SOURCE_FORMAT_ONLY":
        raise SystemExit(1)

if __name__=="__main__":main()
