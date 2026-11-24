"""v34b source-only original 2026 author small file checksum and ZIP-TOC audit.

No original trajectory/figure sample, outcome values, or condition effects read.
Only original provider files exactly named, provider size+MD5 strictly checked.
"""
from __future__ import annotations
import argparse,ast,hashlib,io,json,re,zipfile
from pathlib import Path,PurePosixPath
from urllib import request,error
from urllib.parse import urlparse

from validation_fish_school_v34.original_figshare_metadata import (
    SourceStop,original_figshare_record_bytes,decode_author_record,
    PERMITTED_ORIGINAL_FILE_HOSTS,API_TEMPLATE
)

PINS={
    31378621:{"Figs.zip":(1863466,"4514391ae74d0715969159b9eda9c11a")},
    31386349:{"Model code.zip":(181872,"4e6cf4d167c6204d4f557ae456ed5ba1")},
    30539666:{
       "Model3D-VR.py":(44263,"fdb679b5bb70f654eb569b7b45a54e9c"),
       "Parameters-Input.txt":(2409,"ee85f780cd248dfda38a4438a581d8a3")
    }
}
MAX_ZIP_ENTRIES=200
MAX_DECLARED_ZIP_UNCOMPRESSED=100*1024*1024
MAX_SINGLE_SOURCE_BYTES=2*1024*1024+1024
SOURCE_PROTOCOL="docs/V34B_ORIGINAL_VR_FIGSHARE_SMALL_SOURCE_CHECKSUM_ARCHIVE_SCHEMA_FREEZE.md"
SUGGESTIVE_RE=r"(?i)(read|load|track|traj|fish|trial|experiment|session|virtual|robot|position|camera|time|[Cc][123])"


class FigshareNoExternalRedirect(request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        q=urlparse(newurl)
        if q.scheme!="https" or q.hostname not in PERMITTED_ORIGINAL_FILE_HOSTS:
            raise SourceStop("V34B_ORIGINAL_SOURCE_EXTERNAL_CDN_REDIRECT_NOT_PREAUTHORIZED")
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def exact_small_author_bytes(url,expected_size,provider_md5,opener=None):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in PERMITTED_ORIGINAL_FILE_HOSTS:
        raise SourceStop("V34B_AUTHOR_FILE_NOT_OFFICIAL_PROVIDER_URL")
    if type(expected_size)!=int or not 1<=expected_size<=MAX_SINGLE_SOURCE_BYTES:
        raise SourceStop("V34B_SOURCE_NOT_SMALL_VERIFIED_FILE")
    if not re.fullmatch(r"[0-9a-fA-F]{32}",provider_md5):
        raise SourceStop("V34B_SOURCE_MD5_NOT_FROZEN_FROM_PUBLISHER")
    if opener is None:
        opener=request.build_opener(FigshareNoExternalRedirect()).open
    req=request.Request(url,headers={"User-Agent":"boids-v34b-author-checksum-small-file-audit/1.0",
                                    "Accept":"application/octet-stream,*/*","Accept-Encoding":"identity"})
    try:
        with opener(req,timeout=40) as resp:
            final=resp.geturl() if hasattr(resp,"geturl") else url
            q=urlparse(final)
            if q.scheme!="https" or q.hostname not in PERMITTED_ORIGINAL_FILE_HOSTS:
                raise SourceStop("V34B_ORIGINAL_REDIRECT_EXTERNAL_PROVIDER_STOP")
            raw=resp.read(expected_size+1)
    except error.HTTPError as exc:
        raise SourceStop("V34B_FIGSHARE_ORIGINAL_FILE_HTTP_"+str(exc.code)) from exc
    except (error.URLError,OSError,TimeoutError) as exc:
        raise SourceStop("V34B_FIGSHARE_ORIGINAL_FILE_ACCESS_"+type(exc).__name__) from exc
    if len(raw)!=expected_size or hashlib.md5(raw).hexdigest()!=provider_md5.lower():
        raise SourceStop("V34B_ORIGINAL_AUTHOR_MD5_SIZE_MISMATCH")
    if raw[:128].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise SourceStop("V34B_ORIGINAL_BYTES_WERE_HTML_ERROR")
    return raw


def safe_zip_original_members(blob):
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            members=z.infolist()
            if not 1<=len(members)<=MAX_ZIP_ENTRIES:
                raise SourceStop("V34B_ORIGINAL_AUTHOR_ZIP_MEMBER_COUNT_STOP")
            total=0
            out=[]
            for f in members:
                name=f.filename.replace("\\","/")
                path=PurePosixPath(name)
                if (name.startswith("/") or ".." in path.parts or not name or
                    f.flag_bits & 1 or f.file_size<0 or f.compress_size<0):
                    raise SourceStop("V34B_ORIGINAL_ARCHIVE_UNSAFE_PATH_OR_ENCRYPTED")
                if f.compress_size==0 and f.file_size>0:
                    raise SourceStop("V34B_ORIGINAL_ARCHIVE_COMPRESSION_RATIO_UNSAFE")
                if f.compress_size>0 and f.file_size/f.compress_size>1000:
                    raise SourceStop("V34B_ORIGINAL_ARCHIVE_COMPRESSION_RATIO_UNSAFE")
                total+=f.file_size
                if total>MAX_DECLARED_ZIP_UNCOMPRESSED:
                    raise SourceStop("V34B_ORIGINAL_AUTHOR_ARCHIVE_TOTAL_UNCOMPRESSED_EXCESS")
                if not f.is_dir():
                    out.append({"member_filename":f.filename,
                                "declared_uncompressed_bytes":f.file_size,
                                "likely_fish_trial_OR_code_by_filename":bool(re.search(SUGGESTIVE_RE,name)),
                                "member_contents_NOT_EXTRACTED":True})
            return {"original_archive_entries":len(members),
                    "original_archive_declared_uncompressed_bytes":total,
                    "original_zip_member_listing_without_extracting_content":out,
                    "original_zip_data_members_read":False}
    except (zipfile.BadZipFile,zipfile.LargeZipFile) as ex:
        raise SourceStop("V34B_ORIGINAL_AUTHOR_FILE_NOT_VALID_ZIP") from ex


def source_code_names_only(filename,raw):
    for encoding in ("utf-8-sig","cp1252"):
        try:
            text=raw.decode(encoding)
            break
        except UnicodeError:continue
    else:
        raise SourceStop("V34B_ORIGINAL_AUTHOR_TEXT_NOT_SUPPORTED_ENCODING")
    lines=text.splitlines()
    if not 1<=len(lines)<=50000:
        raise SourceStop("V34B_ORIGINAL_AUTHOR_CODE_LINE_COUNT_STOP")
    relevant=[i+1 for i,s in enumerate(lines)
              if re.search(r"(?i)\b(C1|C2|C3|virtual|real.?fish|trial|loadtxt|read_csv|genfromtxt|time|camera)\b",s)]
    filenames=sorted(set(re.findall(r"[A-Za-z0-9_.+\-/ ]+\.(?:dat|csv|txt|py|json|mat|h5|npz)\b",text,re.I)))
    variables=sorted(set(re.findall(r"(?m)^\s*([A-Za-z_][A-Za-z_0-9]{1,90})\s*=",text)))
    # Intentionally no original source code or model coefficient VALUES.
    result={
      "original_file_header_kind":"original_author_code_or_parameter_text",
      "original_source_text_decoder":encoding,
      "original_source_line_count":len(lines),
      "line_numbers_of_possible_condition_time_session_data_loader_references_first_60":relevant[:60],
      "n_lines_with_relevant_metadata_keywords":len(relevant),
      "source_filename_literal_candidates_first_40":filenames[:40],
      "author_parameter_or_variable_name_candidates_first_40":variables[:40],
      "original_source_lines_or_coefficients_redistributed":False,
      "original_author_code_NOT_EXECUTED":True
    }
    if filename.endswith(".py"):
        try:
            tree=ast.parse(text)
            im=sorted(set(node.names[0].name for node in ast.walk(tree)
                    if isinstance(node,ast.Import) and node.names))
            result["author_imported_module_name_candidates_first_20"]=im[:20]
            result["source_original_python_code_ast_syntax_parsed_without_running"]=True
        except SyntaxError:
            result["source_original_python_code_ast_syntax_parsed_without_running"]=False
    return result


def source_run(fetchmeta=original_figshare_record_bytes,fetchsmall=exact_small_author_bytes):
    out={
      "status":"SOURCE_ACCESS_STOP",
      "frozen_small_original_source_protocol":SOURCE_PROTOCOL,
      "original_figshare_article_ids":sorted(PINS),
      "original_2026_research_trial_values_read":False,
      "original_agent_position_trajectories_read":False,
      "original_experimental_treatment_effect_fit":False,
      "original_fish_calls_not_available":True,
      "source_per_record":{}
    }
    good=0
    for article,filenames in PINS.items():
        record={"status":"SOURCE_ACCESS_STOP","original_figshare_article_id":article,
                "source_files":[]}
        try:
            meta=decode_author_record(fetchmeta(article),article)
            available={x["original_filename"]:x for x in meta["original_provider_file_manifest"]}
            if not set(filenames).issubset(available):
                raise SourceStop("V34B_ORIGINAL_AUTHOR_4_SMALL_FILES_NOT_FOUND_IN_METADATA")
            # Source-only all-original metadata validation BEFORE any 1st code content opened.
            for name,(size,md5) in filenames.items():
                f=available[name]
                if (f["original_source_file_bytes"]!=size or
                    f["original_provider_supplied_MD5"]!=md5 or
                    f["original_provider_computed_MD5"]!=md5):
                    raise SourceStop("V34B_ORIGINAL_AUTHOR_PREDECLARED_MD5_SIZE_DRIFT_"+name)
            for name,(size,md5) in filenames.items():
                f=available[name]
                original=fetchsmall(f["original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED"],
                                    size,md5)
                info={
                  "original_filename":name,"source_published_bytes":size,
                  "original_author_MD5":md5,
                  "original_author_MD5_and_bytes_authentic":True,
                  "original_recomputed_SHA256":hashlib.sha256(original).hexdigest(),
                  "source_content_is_original_author_code_or_ZIP_TOC_only":True
                }
                if name.endswith(".zip"):
                    info.update(safe_zip_original_members(original))
                else:
                    info.update(source_code_names_only(name,original))
                record["source_files"].append(info)
            record["status"]="ALL_PREDECLARED_SMALL_ORIGINAL_AUTHOR_FILE_MD5_VERIFIED"
            record["source_published_DOI"]=meta["source_published_DOI"]
            good+=1
        except (SourceStop,ValueError,UnicodeError,KeyError) as ex:
            record["source_stop_reason"]=str(ex)
        out["source_per_record"][str(article)]=record
    out["n_verified_original_author_records"]=good
    out["status"]=("ALL_THREE_ORIGINAL_AUTHOR_SMALL_SOURCE_RECORDS_VERIFIED" if good==3
                   else "PARTIAL_ORIGINAL_SOURCE_ACCESS_STOP" if good>0
                   else "SOURCE_ACCESS_STOP")
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    d=source_run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(d,sort_keys=True))

if __name__=="__main__":main()
