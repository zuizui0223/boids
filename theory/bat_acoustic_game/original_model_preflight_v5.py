"""v5 publisher-original model preflight: source file and figure-data shapes only.

No new bat field or lab measurements; never executes untrusted MATLAB or R.
No full third-party code or raw source data gets committed.
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

OUT=Path(__file__).resolve().parent/"original_model_preflight_v5.json"
ELIFE_DATA={
 "fig2_corr":"https://cdn.elifesciences.org/articles/55539/elife-55539-fig2-data1-v2.txt",
 "fig2_filter":"https://cdn.elifesciences.org/articles/55539/elife-55539-fig2-data2-v2.txt",
 "fig3_main":"https://cdn.elifesciences.org/articles/55539/elife-55539-fig3-data1-v2.txt",
 "fig4_main":"https://cdn.elifesciences.org/articles/55539/elife-55539-fig4-data1-v2.txt",
}
MATLAB_PICK=("BatSonarDecision.m","IsPreyDetected.m","IsPreyMissDetected.m",
             "IsPhantomEchoesDetectected.m","Interfernce2DetectedPreys.m",
             "FilterBank_detector.m","CreateSimDefaultParams.m","Batflight.m",
             "BatMovemet.m","AnalyzeCrossInterfernce.m","HuntingSequencesAnalysis.m",
             "BatManueverDecision.m","Pulses2Flight.m","BuildSonogram.m")
FIGSHARE_PICK=("TF_all_ver2Sim_KH_v3.R","ReadMe.txt","timecoursePlot.R")
RAR_SHA="913dc06b606cecaeb33558de3ab97f8eca618eda302bd1cb720c2b11fc74baff"

def get_figs():
    result={}
    for name,url in ELIFE_DATA.items():
        item={"source":url,"status":"NOT_ATTEMPTED"}
        try:
            b,_=get_bytes(url,limit=5*1024*1024)
            s=b.decode("utf-8-sig",errors="replace")
            lines=s.splitlines()
            nonblank=[(i+1,l) for i,l in enumerate(lines) if l.strip()]
            item.update(status="OBTAINED",bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
                        rows=len(lines),
                        # The published tables are small model summaries, not individual bats.
                        first_lines=[{"line":n,"text":l[:240]} for n,l in nonblank[:8]],
                        delimiter_counts={d:lines[0].count(d) if lines else 0 for d in (",","\\t",";")})
        except Exception as e:
            item.update(status="STOP_SOURCE",error=type(e).__name__+":"+str(e)[:180])
        result[name]=item
    return result

def matlab_metadata():
    result={"status":"NOT_ATTEMPTED","files":[]}
    try:
        raw,_=get_bytes(ARCHIVE_URL)
        digest=hashlib.sha256(raw).hexdigest()
        result["sha256"]=digest
        if digest!=RAR_SHA:
            result["status"]="STOP_SOURCE_CHANGED";return result
        if not shutil.which("7z"):
            result["status"]="STOP_NO_7Z";return result
        archive=Path(os.getenv("RUNNER_TEMP","/tmp"))/"bat_original_v5.rar"
        try:
            archive.write_bytes(raw)
            for name in MATLAB_PICK:
                fp="Bat Simulation _eLife_270620/"+name
                q=subprocess.run(["7z","e","-so",str(archive),fp],timeout=40,
                                 capture_output=True)
                item={"name":name,"status":"NOT_EXTRACTED"}
                if q.returncode or not q.stdout:
                    item["status"]="STOP_FILE_MISSING";result["files"].append(item);continue
                s=q.stdout.decode("utf-8",errors="replace")
                # Count implementation structure and diagnostic lines; no file content released.
                funs=[line.strip()[:150] for line in s.splitlines() if re.match(r"\s*function\b",line)][:15]
                is_rand=bool(re.search(r"\brand\b|\brandn\b|\brandi\b",s))
                references=[x for x in MATLAB_PICK if x!=name and re.search(r"\b"+re.escape(x[:-2])+r"\s*\(",s)]
                item.update(status="FOUND",bytes=len(q.stdout),sha256=hashlib.sha256(q.stdout).hexdigest(),
                            lines=len(s.splitlines()),functions=funs,
                            calls_selected=references,
                            uses_random=is_rand,contains_matlab_toolbox_gui=bool(re.search(r"\bguidata\b|\bfigure\b|\bwaitbar\b",s)),
                            lines_with_name_jar=sum(bool(re.search(r"\bJAR\b|FreqShift",x,re.I)) for x in s.splitlines()),
                            lines_with_name_false_alarm=sum(bool(re.search(r"Phantom|FalseAlarm|MissDetec",x,re.I)) for x in s.splitlines()))
                # print limited, targeted original function logic for PRIVATE researcher diagnostic
                if name in ("IsPreyMissDetected.m","IsPhantomEchoesDetectected.m","IsPreyDetected.m","BatSonarDecision.m","FilterBank_detector.m","CreateSimDefaultParams.m"):
                    print("MATLAB_SOURCE_SELECTED:",name)
                    for i,l in enumerate(s.splitlines(),1):
                        if re.search(r"\bfunction\b|Rand|prob|detect|phantom|jamming|JAR|carrierfreq|FreqShift|pulse|Mask",l,re.I) and not l.lstrip().startswith("%"):
                            print("  ",i,l.strip()[:190])
                            if i>400: break
                result["files"].append(item)
        finally:
            archive.unlink(missing_ok=True)
        result["status"]="SOURCE_FUNCTION_AUDIT_DONE"
    except Exception as e:
        result.update(status="STOP_SOURCE",error=type(e).__name__+":"+str(e)[:200])
    return result

def figshare_source():
    res={"status":"NOT_ATTEMPTED","files":[]}
    try:
        meta,_=get_bytes(FIGSHARE_API,2*1024*1024)
        j=json.loads(meta)
        for file in j.get("files",[]):
            if file.get("name") not in FIGSHARE_PICK:continue
            item={"name":file.get("name"),"id":file.get("id"),"status":"NOT_ACCESSED"}
            try:
                raw,_=get_bytes(file["download_url"],limit=2*1024*1024)
                txt=raw.decode("utf-8-sig",errors="replace")
                item.update(status="FOUND",bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                            lines=len(txt.splitlines()),
                            code_functions=sum("function(" in l or "function (" in l for l in txt.splitlines()))
                if item["name"].endswith(".R"):
                    lines=[(i+1,l.strip()) for i,l in enumerate(txt.splitlines()) if l.strip() and not l.lstrip().startswith("#")]
                    # Read-only code diagnostic output; short and ephemeral.
                    print("R_SOURCE_LINENUM:",item["name"])
                    for n,l in lines[:125]:print("  ",n,l[:210])
                else:
                    print("README_SOURCE:",item["name"],txt[:1400].replace("\n"," || "))
            except Exception as e:
                item.update(status="STOP_FILE",error=type(e).__name__+":"+str(e)[:120])
            res["files"].append(item)
        res["status"]="SOURCE_SCRIPTS_AUDITED"
    except Exception as e:
        res.update(status="STOP_FIGSHARE",error=type(e).__name__+":"+str(e)[:200])
    return res

def main():
    out={"schema":5,"science_status":"ORIGINAL_MODEL_STRUCTURAL_AUDIT_ONLY",
         "original_model_numerically_reproduced":False,
         "new_bat_measurements":False,"source_data_redistributed":False,
         "elife_figure_data":get_figs(),"original_matlab":matlab_metadata(),"figshare_R":figshare_source()}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    for key,v in out["elife_figure_data"].items():
        print("ELIFE_DATA",key,v["status"],"bytes",v.get("bytes"),"sha",v.get("sha256"))
        if v.get("first_lines"):print("ELIFE_FIRST",key,json.dumps(v["first_lines"]))
    print("MATLAB_STATUS",out["original_matlab"]["status"],"num_files",len(out["original_matlab"]["files"]))
    print("FIGSHARE_R_STATUS",out["figshare_R"]["status"])
    print("ORIGINAL_MODEL_AUDIT_JSON",str(OUT))
    return 0

if __name__=="__main__":raise SystemExit(main())
