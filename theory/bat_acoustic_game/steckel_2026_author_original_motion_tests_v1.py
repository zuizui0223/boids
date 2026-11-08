"""Run unchanged 16 original-author 2026 bat3d Python tests on original code ZIP.

Execution is in a temporary GitHub runner directory only. The author PyTorch
training program, 3D model checkpoints, HRTF, E1-E9 numerical simulations and
actual bat recordings are not run/read or rehosted.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,io,json,os,subprocess,sys,tempfile,zipfile,importlib.metadata
from steckel_2026_range_code_source_gate_v1 import official_outer_catalog,extract_single_member

ROOT=Path(__file__).resolve().parent
DOC=ROOT/"STECKEL_2026_AUTHOR_PYTHON_GEOMETRY_TESTS_EXECUTION_V1.md"
OUT=ROOT/"STECKEL_2026_ORIGINAL_MOTION_WARP_AXIS_TEST_RESULT_V1.json"
SOURCE_SHA="a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8"
TESTS=("tests/test_3d_flow_ode.py","tests/test_3d_warp.py","tests/test_3d_axis_sym.py")
EXPECTED_TESTS=(3,7,6)

def auth_code():
    if not DOC.exists():raise ValueError("STOP_MISSING_ORIGINAL_MODEL_TEST_CONTRACT")
    url,length,digest,entries=official_outer_catalog()
    found=[x for x in entries if x["path"]=="code.zip"]
    if len(found)!=1:raise ValueError("STOP_ORIGINAL_CODE_SOURCE_NOT_UNIQUE")
    source,receipt=extract_single_member(url,found[0],15*1024*1024)
    if hashlib.sha256(source).hexdigest()!=SOURCE_SHA:
        raise ValueError("STOP_ORIGINAL_CODE_SHA_CHANGED")
    return source,receipt

def selected_original_sources(original,tempdir):
    temp=Path(tempdir).resolve()
    count=0
    files=[]
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        names=set(z.namelist())
        for name in TESTS:
            if name not in names:raise ValueError("STOP_ORIGINAL_AUTHOR_TEST_MISSING_"+name)
        for member in z.infolist():
            if member.is_dir():continue
            name=member.filename
            if not (name=="pyproject.toml" or
                    ((name.startswith("bat3d/") or name.startswith("tests/"))
                      and name.endswith(".py"))):
                continue
            dest=(temp/name).resolve()
            if temp not in dest.parents:
                raise ValueError("STOP_AUTHOR_ZIP_PATH_ESCAPE")
            if member.file_size>500000:
                raise ValueError("STOP_OVERLARGE_AUTHOR_PYTHON_SOURCE_"+name)
            dest.parent.mkdir(parents=True,exist_ok=True)
            raw=z.read(member)
            dest.write_bytes(raw)
            files.append({"path":name,"bytes":len(raw),
                          "sha256":hashlib.sha256(raw).hexdigest()})
            count+=1
    return files

def run():
    original,receipt=auth_code()
    packages={}
    for p in ("torch","numpy","scipy","matplotlib","pytest"):
        try:packages[p]=importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:packages[p]=None
    if any(packages[p] is None for p in packages):
        return {"schema":1,"status":"STOP_ORIGINAL_TEST_CPU_DEPENDENCIES_MISSING",
                "source_code_receipt":receipt,
                "package_versions":packages,"source_test_executed":False}
    with tempfile.TemporaryDirectory(prefix="original_2026_bat3d_") as dirname:
        files=selected_original_sources(original,dirname)
        cmd=[sys.executable,"-m","pytest","-q","--disable-warnings",
             "--tb=short",*TESTS]
        result=subprocess.run(cmd,cwd=dirname,text=True,stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,timeout=300,
                              env={**os.environ,"CUDA_VISIBLE_DEVICES":"",
                                   "PYTHONPATH":dirname},
                              check=False)
        out=result.stdout
    return {"schema":1,
            "status":"ORIGINAL_AUTHOR_GEOMETRY_TESTS_PASSED" if result.returncode==0
                else "STOP_AUTHOR_ORIGINAL_GEOMETRY_TESTS_FAILED",
            "source_code_receipt":receipt,"package_versions":packages,
            "original_author_test_paths":list(TESTS),
            "expected_author_test_count":sum(EXPECTED_TESTS),
            "source_python_files_extracted_temporarily":len(files),
            "source_python_file_metadata":files,
            "original_source_pytest_exit_code":result.returncode,
            "source_test_executed":True,
            "source_test_output_tail":out[-6500:]}

def main():
    result={"schema":1,"status":"NOT_STARTED",
            "original_source_model_DOI":"10.64898/2026.10.22.760884",
            "original_Zenodo_doi":"10.5281/zenodo.23537553",
            "original_source_code_SHA256":SOURCE_SHA,
            "new_animal_measurements":False,
            "original_trained_model_execution":False,
            "original_publication_figures_reproduced":False,
            "source_original_HRTF_or_echo_observations_loaded":False,
            "source_author_code_rehosted":False,
            "original_simulated_source_model_tests_only":True}
    try:result.update(run())
    except Exception as e:
        result["status"]="STOP_AUTHOR_PYTHON_RUNTIME_OR_ZENODO_ACCESS"
        result["runtime_error"]=type(e).__name__+":"+str(e)[:300]
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("AUTHENTIC_AUTHOR_TEST_STATUS",result["status"])
    print("ORIGINAL_CPU_DEPENDENCIES",result.get("package_versions"))
    print("ORIGINAL_TEST_RESULTS",result.get("source_test_output_tail","NONE")[-5500:])
    if "runtime_error" in result:print("SOURCE_RUNTIME_STOP",result["runtime_error"])
    return 0

if __name__=="__main__":raise SystemExit(main())
