"""Original source-authenticated 2026 bat3d Python AST/test dependency preflight.

Not a model run. Uses only code.zip exact Zenodo HTTP206 member, sha+CRC.
Does not open original 988MB package, model weights, external HRTF, trajectory
source results or original test training outcomes.
"""
from __future__ import annotations
import ast,hashlib,io,json,sys,zipfile,tomllib,importlib.util
from collections import Counter
from pathlib import Path
from steckel_2026_range_code_source_gate_v1 import official_outer_catalog,extract_single_member

ROOT=Path(__file__).resolve().parent
DOC=ROOT/"STECKEL_2026_AUTHENTIC_PYTHON_TEST_EXECUTION_PREFLIGHT_V1.md"
OUT=ROOT/"STECKEL_2026_ORIGINAL_PYTHON_TEST_DEPENDENCIES_V1.json"
SOURCE_CODE_SHA="a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8"
MAX_SOURCE=20*1024*1024

def original_codezip():
    if not DOC.exists():raise ValueError("STOP_UNCOMMITTED_SOURCE_EXECUTION_CONTRACT")
    url,fullsize,checksum,members=official_outer_catalog()
    record=[x for x in members if x["path"]=="code.zip"]
    if len(record)!=1:raise ValueError("STOP_NON_UNIQUE_AUTHOR_CODE_ZIP")
    raw,receipt=extract_single_member(url,record[0],15*1024*1024)
    if hashlib.sha256(raw).hexdigest()!=SOURCE_CODE_SHA:
        raise ValueError("STOP_SOURCE_CODE_ZIP_SHA_CHANGED")
    return raw,receipt

def parse_source(zipbytes):
    files={}
    project=None
    n_files=0
    errors=[]
    imports=Counter()
    test_names={}
    with zipfile.ZipFile(io.BytesIO(zipbytes)) as z:
        for rec in z.infolist():
            if rec.is_dir():continue
            fn=rec.filename
            if fn=="pyproject.toml":
                project=tomllib.loads(z.read(rec).decode("utf-8"))
                continue
            if not fn.endswith(".py"):continue
            if not (fn.startswith("bat3d/") or fn.startswith("tests/")):
                continue
            if rec.file_size>500000:
                errors.append({"path":fn,"error":"STOP_PYTHON_SOURCE_FILE_OVER_500KB"})
                continue
            raw=z.read(rec)
            n_files+=1
            try:
                txt=raw.decode("utf-8-sig")
                parsed=ast.parse(txt,filename=fn)
                compile(parsed,fn,"exec")
            except Exception as e:
                errors.append({"path":fn,"error":type(e).__name__+":"+str(e)[:170]})
                continue
            mods=set()
            for node in ast.walk(parsed):
                if isinstance(node,ast.Import):
                    for x in node.names:mods.add(x.name.split(".")[0])
                elif isinstance(node,ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            files[fn]={"python_bytes":len(raw),
                       "sha256":hashlib.sha256(raw).hexdigest(),
                       "top_level_imports":sorted(mods)}
            for v in mods:imports[v]+=1
            if fn.startswith("tests/"):
                test_names[fn]=[
                    node.name for node in ast.walk(parsed) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
                    and node.name.startswith("test_")][:80]
    pyproject={}
    if project:
        pyproject={
          "project_name":project.get("project",{}).get("name"),
          "requires_python":project.get("project",{}).get("requires-python"),
          "declared_project_dependencies":project.get("project",{}).get("dependencies"),
          "build_system_requirements":project.get("build-system",{}).get("requires"),
          "top_level_configuration_keys":sorted(project.keys()),
        }
    inrunner={}
    for package in sorted(set(imports)|{"torch","numpy","pytest","scipy","h5py"}):
        if package in sys.stdlib_module_names:continue
        inrunner[package]=importlib.util.find_spec(package) is not None
    return {
      "source_python_files_AST_compiled":len(files)-len(errors),
      "source_total_selected_python_files":n_files,
      "source_syntax_errors_or_parse_stops":errors,
      "author_test_modules":test_names,
      "author_original_test_function_count":sum(map(len,test_names.values())),
      "original_pyproject_declared_requirements":pyproject,
      "top_level_import_coverage":dict(imports),
      "source_job_runner_dependency_presence":inrunner,
      "source_python_file_sha256":files,
      "original_modules_were_imported_or_run":False
    }

def main():
    result={"schema":1,"date":"2026-11-08",
      "status":"NOT_STARTED","original_2026_paper_DOI":"10.64898/2026.10.22.760884",
      "original_Zenodo_DOI":"10.5281/zenodo.23537553",
      "new_bat_measurements":False,
      "original_author_training_or_tests_run":False,
      "original_source_observed_bat_audio_or_3D_trajectories_loaded":False,
      "original_model_checkpoints_opened":False,
      "original_code_files_redistributed":False}
    try:
        raw,receipt=original_codezip()
        result["original_author_code_zip_source_integrity"]=receipt
        result.update(parse_source(raw))
        result["status"]="ORIGINAL_PYTHON_CODE_AST_AND_DEPENDENCY_AUDIT_COMPLETE"
    except Exception as e:
        result["status"]="STOP_ORIGINAL_PYTHON_SOURCE_ACCESS_OR_AST"
        result["error"]=type(e).__name__+":"+str(e)[:250]
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_AUTHOR_PYTHON_SOURCE_GATE",result["status"])
    if result["status"].startswith("STOP"):
        print("SOURCE_STOP",result["error"])
        return 0
    print("AUTHENTIC_SOURCE_PYPROJECT",json.dumps(result["original_pyproject_declared_requirements"],sort_keys=True))
    print("AUTHENTIC_SOURCE_TEST_MODULES",json.dumps(result["author_test_modules"],sort_keys=True))
    print("SOURCE_PYTHON_SYNTAX_STOPS",result["source_syntax_errors_or_parse_stops"])
    print("SOURCE_DEPENDENCY_PRESENCE",json.dumps(result["source_job_runner_dependency_presence"],sort_keys=True))
    print("CODE_AST_COMPILE_ONLY_NO_ORIGINAL_MODEL_EXECUTION",result["source_python_files_AST_compiled"])
    return 0

if __name__=="__main__":raise SystemExit(main())
