"""v36 original PLOS 2026 real-VR fish CODE source-only AST trial schema probe.

Original provider-MD5-authenticated MODEL source files ONLY, never download
experimental DAT source values. Original code not executed. A 9-state model
is not by itself evidence of 9-column experimental DAT meanings.
"""
from __future__ import annotations
import argparse,ast,hashlib,html,json,re
from pathlib import Path

from validation_fish_school_v34.original_figshare_metadata import (
    SourceStop,original_figshare_record_bytes,decode_author_record
)
from validation_fish_school_v34.onehop_figshare_original_files import (
    verified_original_figshare_small_bytes
)

ARTICLE_ID=30539666
FROZEN_FILES={
 "Model3D-VR.py":(44263,"fdb679b5bb70f654eb569b7b45a54e9c",
                  "7eafc4b4740345204321bde3343505dd23fb965cf3d12aae09c7665d8cd6cbff"),
 "Parameters-Input.txt":(2409,"ee85f780cd248dfda38a4438a581d8a3",
                       "19fa13b917f2a29d234b163e20b40a747f5ad6118d0bf7e750a35d4110455e72")
}
EXP_DAT_FILES=("2R-TwoRealFish.dat","C1-OneReal+OneVirtual.dat",
               "C2-OneReal+OneVirtual.dat","C3-OneReal+OneVirtual.dat")
DAT_SOURCE_AUDIT="docs/v35_verification/PLOS_2026_ALL_FOUR_ORIGINAL_FIGSHARE_DAT_MD5_SOURCE_FORMAT_ONLY.json"
AST_FUNCTION_CAP=60
DATA_FILE_CAP=35

def source_text(raw):
    try:return raw.decode("utf-8-sig"),"utf-8-sig"
    except UnicodeError:
        try:return raw.decode("cp1252"),"windows-1252"
        except UnicodeError as ex:raise SourceStop("V36_AUTHOR_CODE_SOURCE_ENCODING_UNSUPPORTED") from ex

def full_call_name(func):
    if isinstance(func,ast.Name):return func.id
    if isinstance(func,ast.Attribute):
        return full_call_name(func.value)+"."+func.attr
    return "(dynamic)"

def source_python_AST_static(text):
    try:tree=ast.parse(text)
    except SyntaxError as ex:raise SourceStop("V36_ORIGINAL_AUTHOR_PYTHON_AST_NOT_VALID") from ex
    calls={}
    readcalls=[]
    writecalls=[]
    literal_files=set()
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    funcnames=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            funcnames.append(node.name)
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            for match in re.findall(r"[-A-Za-z0-9_+./ ]+\.(?:dat|csv|txt|py|mat|npz|h5)\b",
                                     node.value,re.I):
                literal_files.add(match.strip()[-160:])
        if not isinstance(node,ast.Call):continue
        call=full_call_name(node.func)
        calls[call]=calls.get(call,0)+1
        if call in ("np.loadtxt","numpy.loadtxt","np.genfromtxt","numpy.genfromtxt",
                    "pd.read_csv","pandas.read_csv","pd.read_table","np.load",
                    "numpy.load","open","Path.open","pd.read_parquet"):
            inputs=[]
            for a in node.args[:2]:
                if isinstance(a,ast.Constant) and isinstance(a.value,str):
                    inputs.append(a.value[:160])
            readcalls.append({"call":call,"source_line":node.lineno,
                              "source_literal_filename_args_ONLY":inputs,
                              "no_source_fish_data_values_inspected":True})
        if call in ("np.savetxt","numpy.savetxt","np.save","numpy.save","write",
                    "np.savez","pd.DataFrame.to_csv"):
            writecalls.append({"call":call,"source_line":node.lineno})
    # Scan only source token labels, not code excerpts or literal parameter values.
    lines=text.splitlines()
    flags={
      "literal_published_2R_C1_C2_C3_original_dat_filename_referenced":
         {name:bool(name in text) for name in EXP_DAT_FILES},
      "source_identifier_label_presence":{
         key:bool(re.search(pattern,text,re.I)) for key,pattern in {
           "trial":r"\b(trial|trial_id)\b",
           "session":r"\b(session|session_id)\b",
           "subject":r"\b(subject|fish_id|individual_id)\b",
           "real_virtual_agent":r"\b(real.?fish|virtual.?fish|real.?agent|virtual.?agent)\b",
           "source_clock":r"\b(fps|timestamp|frame.?rate|delta.?t|deltat)\b",
           "smoothing":r"\b(gaussian|smoothing|interpolation|filter)\b"
         }.items()
      },
      "original_module_direct_DAT_load_source_paths":{
          "listed_named_original_EXPERIMENTAL_DAT_in_ast_loader":False,
          "positive_original_DAT_column_number_map":"NOT_VERIFIED",
          "published_experimental_trial_session_ID_ingested":"NOT_VERIFIED"
      }
    }
    direct={name:False for name in EXP_DAT_FILES}
    for call in readcalls:
        for v in call["source_literal_filename_args_ONLY"]:
            for name in EXP_DAT_FILES:
                if name.lower() in v.lower():direct[name]=True
    flags["original_module_direct_DAT_load_source_paths"]["listed_named_original_EXPERIMENTAL_DAT_in_ast_loader"]=all(direct.values())
    return {
      "original_python_line_count":len(lines),
      "source_ast_parse":True,
      "n_original_python_function_definitions":len(funcnames),
      "original_python_function_names_first_60":funcnames[:AST_FUNCTION_CAP],
      "original_author_module_import_calls_counts_without_values":dict(sorted(calls.items())),
      "original_script_DATA_reader_call_line_numbers_first_40":readcalls[:40],
      "original_script_simulation_or_source_write_call_line_numbers_first_40":writecalls[:40],
      "original_LITERAL_filename_reference_candidates_first_35":sorted(literal_files)[:DATA_FILE_CAP],
      "source_identifier_presence_only":flags,
      "original_author_simulation_code_executed":False,
      "original_author_full_source_text_redistributed":False
    }

def source_parameter_names_only(text):
    lines=text.splitlines()
    names=[]
    for idx,line in enumerate(lines,1):
        m=re.match(r"^\s*([A-Za-z][A-Za-z0-9_./-]{1,80})\s*[:=]\s*",line)
        if m:names.append({"original_parameter_token_label":m.group(1),
                           "original_line_number":idx})
    return {
      "original_input_parameter_source_line_count":len(lines),
      "source_parameter_LHS_name_line_numbers_first_60":names[:60],
      "original_input_parameter_VALUES_redistributed":False,
      "original_parameter_text_executed":False
    }

def original_figshare_description_metadata(description):
    if not isinstance(description,str):
        return {"author_original_record_has_public_description":False}
    desc=html.unescape(re.sub(r"<[^>]*>"," ",description))
    return {
      "author_original_record_has_public_description":bool(desc.strip()),
      "original_source_description_n_chars":len(desc),
      "original_source_description_has_EXPLICIT_nine_columns_ordered":
        bool(re.search(r"(?is)(columns?[\s:]+(?:[\w\-./, ]+){3,140})",desc))
        and bool(re.search(r"(?i)(2R-TwoRealFish|C2-OneReal|C3-OneReal)",desc)),
      "original_source_description_mentions_session_id":bool(re.search(r"(?i)\b(session.?id|trial.?id|fish.?id)\b",desc)),
      "original_source_description_text_NOT_redistributed":True,
    }

def run(fetchmeta=original_figshare_record_bytes,
        fetchsmall=verified_original_figshare_small_bytes):
    report={
      "status":"ORIGINAL_AUTHOR_DAT_NINE_COLUMN_SCHEMA_NOT_ADMITTED",
      "source_original_paper_DOI":"10.1371/journal.pcbi.1014544",
      "source_original_data_figshare_article_id":ARTICLE_ID,
      "scientific_source_freeze_before_code_read":"docs/V36_PLOS_3D_ORIGINAL_CODE_DAT_SCHEMA_SESSION_SOURCE_ONLY_FREEZE.md",
      "source_original_2026_C1_C2_C3_treatment_results_read":False,
      "source_original_real_virtual_positions_or_timestamps_read":False,
      "source_original_PLOS_author_code_executed":False,
      "source_original_script_text_distributed":False,
      "source_authentication":{},
      "source_experimental_9_column_map":"NOT_VERIFIED",
      "source_original_subject_session_identity":"NOT_VERIFIED",
      "source_original_physical_sampling_clock":"NOT_VERIFIED"
    }
    try:
        original=fetchmeta(ARTICLE_ID)
        data=decode_author_record(original,ARTICLE_ID)
        # Independent original v35 protocol/source proof and source gate
        # must exist on the same branch.
        prior=json.loads(Path(DAT_SOURCE_AUDIT).read_text(encoding="utf8"))
        if prior.get("all_four_full_author_MD5_and_size_verified") is not True:
            raise SourceStop("V36_PRIOR_ALL_FOUR_ORIGINAL_DAT_NOT_AUTHENTICATED")
        if len(prior.get("original_four_condition_source_files",[]))!=4:
            raise SourceStop("V36_FOUR_EXPERIMENT_SOURCE_FILES_NOT_IN_PRIOR_MANIFEST")
        meta={x["original_filename"]:x for x in data["original_provider_file_manifest"]}
        files={}
        for name,(size,md5,sha) in FROZEN_FILES.items():
            x=meta.get(name)
            if (not x or x["original_source_file_bytes"]!=size or
                x["original_provider_supplied_MD5"]!=md5 or
                x["original_provider_computed_MD5"]!=md5):
                raise SourceStop("V36_ORIGINAL_AUTHOR_CODE_MD5_SIZE_CHANGED_"+name)
            b=fetchsmall(x["original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED"],size,md5)
            if len(b)!=size or hashlib.md5(b).hexdigest()!=md5 or hashlib.sha256(b).hexdigest()!=sha:
                raise SourceStop("V36_ORIGINAL_AUTHOR_CODE_BYTE_MD5_SHA256_MISMATCH_"+name)
            txt,dec=source_text(b)
            files[name]={"original_sha256":sha,"original_author_md5":md5,
                         "original_source_bytes":size,"text_decoder":dec,
                         "source_static_analysis":(
                           source_python_AST_static(txt) if name.endswith(".py")
                           else source_parameter_names_only(txt))}
        report["source_authentication"]={
          "original_2_small_author_source_files_MD5_SHA256_verified":True,
          "original_source_files":files,
          "original_Figshare_article_meta_SHA256":hashlib.sha256(original).hexdigest(),
          "original_author_code_Python_AST_static_ONLY":True,
          "original_author_code_NOT_executed":True
        }
        report["source_original_figshare_description_schema_only"] = original_figshare_description_metadata(
            json.loads(original).get("description"))
        astinfo=files["Model3D-VR.py"]["source_static_analysis"]
        names=astinfo["source_identifier_presence_only"][
           "original_module_direct_DAT_load_source_paths"]
        if names["listed_named_original_EXPERIMENTAL_DAT_in_ast_loader"] and (
           report["source_original_figshare_description_schema_only"][
               "original_source_description_has_EXPLICIT_nine_columns_ordered"]
           ):
            report["status"]="POTENTIAL_AUTHOR_EXPERIMENT_COLUMN_LOADER_FOUND_NEEDS_MANUAL_SCHEMA_CONFIRMATION"
        else:
            report["status"]="ORIGINAL_AUTHOR_DAT_NINE_COLUMN_SCHEMA_NOT_ADMITTED"
    except (SourceStop,OSError,UnicodeError,ValueError,KeyError,TypeError,FileNotFoundError) as e:
        report["status"]="ORIGINAL_AUTHOR_CODE_SOURCE_OR_SCHEMA_STOP"
        report["reason"]=str(e)
    return report

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,required=True)
    opts=cli.parse_args()
    r=run()
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps(r,sort_keys=True))

if __name__=="__main__":main()
