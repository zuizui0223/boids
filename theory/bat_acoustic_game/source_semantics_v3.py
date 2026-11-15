"""Source-SEMANTICS preflight: inspect published original file structure only.

No published source code is executed or redistributed. No response/outcome
values are used. Records structural SHA, signatures, schemas and STOPs.
This may locate reproducible endpoint definitions, but is not replication.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from source_gate_v2 import ARCHIVE_URL, FIGSHARE_API, get_bytes

OUT=Path(__file__).resolve().parent/"source_semantics_v3_receipt.json"
EXPECTED_2020_SHA="913dc06b606cecaeb33558de3ab97f8eca618eda302bd1cb720c2b11fc74baff"
PUBLISHER_MFILES={
    "BatSonarDecision.m",
    "Interfernce2DetectedPreys.m",
    "IsPhantomEchoesDetectected.m",
    "IsPreyDetected.m",
    "IsPreyMissDetected.m",
    "FilterBank_detector.m",
    "CalculateSonarEquation.m",
}
PUBLISHER_RFILES={
    "TF_all_ver2Sim_KH_v3.R",
    "JAR_behaviour_timecoursePlot_v3.R",
    "ReadMe.txt",
    "Data_jamming.csv",
    "TFallSim_IPIlowTF_20.csv",
    "TFallSim_IPIhighTF_20.csv"
}

def audit_elife():
    result={"sha256_expected":EXPECTED_2020_SHA,"status":"NOT_CHECKED","files":[]}
    try:
        a,_=get_bytes(ARCHIVE_URL)
        sha=hashlib.sha256(a).hexdigest()
        result["sha256_actual"]=sha
        if sha!=EXPECTED_2020_SHA:
            result["status"]="STOP_PUBLISHER_BYTES_CHANGED"
            return result
        if not shutil.which("7z"):
            result["status"]="STOP_ARCHIVE_READER_MISSING"
            return result
        archive=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"source_v3_tmp.rar"
        try:
            archive.write_bytes(a)
            for file in sorted(PUBLISHER_MFILES):
                p="Bat Simulation _eLife_270620/"+file
                x=subprocess.run(["7z","e","-so",str(archive),p],
                                 capture_output=True,timeout=25)
                if x.returncode !=0 or not x.stdout:
                    result["files"].append({"name":file,"status":"STOP_EXTRACT",
                                             "stderr":x.stderr.decode(errors="replace")[-200:]})
                    continue
                src=x.stdout.decode(errors="replace")
                fun=[q.strip()[:180] for q in src.splitlines()
                     if re.match(r"^\s*function\b",q)][:5]
                tokens={key:bool(re.search(pattern,src,re.I)) for key,pattern in {
                    "mentions_true_prey":r"prey|target",
                    "mentions_phantom_false":r"phantom|false|missdetec",
                    "mentions_sonar_frequency":r"freq|sonar|pulse",
                    "mentions_masking":r"jam|interferen|mask",
                    "mentions_detected":r"detect",
                }.items()}
                result["files"].append({"name":file,"status":"LISTED_TEXT_ONLY",
                    "sha256":hashlib.sha256(x.stdout).hexdigest(),
                    "bytes":len(x.stdout),"lines":len(src.splitlines()),
                    "function_headers":fun,"lexical_indicators":tokens})
        finally:
            if archive.exists(): archive.unlink()
        result["status"]="STRUCTURE_AUDITED"
    except Exception as e:
        result["status"]="STOP_EXTERNAL_SOURCE_OR_INSPECTION"
        result["error"]=type(e).__name__+":"+str(e)[:180]
    return result

def audit_figshare():
    result={"status":"NOT_CHECKED","files":[]}
    try:
        data,_=get_bytes(FIGSHARE_API,2*1024*1024)
        item=json.loads(data)
        files=item.get("files",[])
        for f in files:
            name=f.get("name","")
            if name not in PUBLISHER_RFILES:
                continue
            url=f.get("download_url")
            if not url:
                result["files"].append({"name":name,"status":"STOP_NO_DOWNLOAD_LINK","id":f.get("id")})
                continue
            try:
                b,_=get_bytes(url,3*1024*1024)
                info={"name":name,"id":f.get("id"),"bytes":len(b),
                      "sha256":hashlib.sha256(b).hexdigest(),"status":"INSPECTED_SCHEMA_ONLY"}
                txt=b.decode("utf-8",errors="replace")
                if name.lower().endswith(".csv"):
                    rows=csv.reader(io.StringIO(txt))
                    info["columns"]=next(rows,[])
                    info["data_rows"]=sum(1 for row in rows if row)
                elif name.lower().endswith(".r"):
                    info["lines"]=len(txt.splitlines())
                    info["R_function_count"]=len(re.findall(r"<-\s*function\s*\(",txt))
                    info["uses_csv_reader"]=bool(re.search(r"read[._]csv|read[.]table|readr::",txt))
                    info["uses_model_fitting"]=bool(re.search(r"\b(lm|glm|lmer|aov|nls)\s*\(",txt))
                else:
                    info["lines"]=len(txt.splitlines())
                    # Just record first 2 TITLE labels if any, never publisher prose.
                    info["has_file_list"]=bool(re.search(r"\.csv|\.R\b",txt))
                result["files"].append(info)
            except Exception as e:
                result["files"].append({"name":name,"id":f.get("id"),
                      "status":"STOP_FILE_ACCESS","error":type(e).__name__+":"+str(e)[:160]})
        result["status"]="SCHEMAS_INSPECTED" if result["files"] else "STOP_NO_MATCHED_FILES"
    except Exception as e:
        result["status"]="STOP_FIGSHARE_API"
        result["error"]=type(e).__name__+":"+str(e)[:160]
    return result

def main():
    result={"schema":3,"status":"SOURCE_ONLY_NOT_REPRODUCED",
            "opened_biological_response_values":False,
            "original_archive_redistributed":False,
            "elife":audit_elife(),"figshare":audit_figshare()}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for k in ("elife","figshare"):
        print(k,result[k]["status"])
        for f in result[k]["files"]:
            print("  ",f["name"],f["status"],
                  "rows",f.get("data_rows","NA"),
                  "columns",f.get("columns","NA"),
                  "function_headers",f.get("function_headers","NA"))
    print("SOURCE_SEMANTICS_JSON",str(OUT))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
