"""Authoritative 2026 eLife bat cave-exit model source-identity and runtime gate.

Downloads only explicitly pinned public MIT-licensed original GitHub blobs,
verifies Git blob identity, and inspects architecture and MAT variable SHAPES.
No original source code or .mat numeric outcomes are redistributed, executed,
or modified. Source-author exact MATLAB reproduction is NOT claimed.
"""
from __future__ import annotations
import base64,hashlib,io,json,re,urllib.request,zipfile
from pathlib import Path

OUT=Path(__file__).resolve().parent/"MAZAR_2026_AUTHENTIC_SOURCE_GATE_V1.json"
DOC=Path(__file__).resolve().parent/"MAZAR_2026_SOURCE_AUTHENTICITY_AND_BOIDS_BRIDGE_V1.md"
UPSTREAM="omermazar/Colony-Exit-Bat-Simulation"
UPSTREAM_PIN="a74fb61a8efb57ca37693893c3bd7b35fa94fa89"
BLOBS={
  "Experiments Code/CaveExit_Experiment_Confusion.m":"0fe72111bd0f421adb4d7105f7cae0bb7c422ee5",
  "BatFlightForGui.m":"4979e10b1c2c67081c45ce9a7a55a3b4e95bd317",
  "BatManueverDecision.m":"25056bcabd1cf4859d9ca452f040f4e4157f7595",
  "BatSonarDecision.m":"7890890860397defe9315d6c88aca20e9866da75",
  "DATA/DefaultParamsTable_CaveExit_FInal_PK.xlsx":"328ca8d0de52beb2cc02a15d54d8717651f3c586",
  "DATA/DefaultParamsTable_CaveExit_FInal_Rhino.xlsx":"1f7ec837f7745e459e7016b3937cb8e58df48374",
  "Swarm_200bats_New_1.mat":"c2c43de0dee059036d5a2263c1e2bf30d9a45323",
}
ARCH_FIELDS=("ConfusionObs","MaskingByConsps","MaskingByConspsObsEchoes",
             "ObsMemorySize","ObsRepeationsFlag","ObsEchoesRatioTH",
             "DistToReactConsp","DistToReactObstacle","BatDetectionRange",
             "FilterBank","NumOfSetups","CaveExit")
DEPENDENCIES={
 "absolute_Windows_drive":r"[A-Za-z]:\\",
 "interactive_source_dialog":r"\b(?:uigetfile|uigetdir|inputdlg)\s*\(",
 "matlab_table_data_type":r"\b(?:table|readtable|writetable)\s*\(",
 "matlab_polyshape":r"\bpolyshape\s*\(",
 "matlab_GUI":r"\b(?:uicontrol|guidata|figure|plot3)\s*\(",
 "source_random_stream":r"\b(?:randn|rand|randi|rng)\s*\(",
 "source_Main_BatFlightForGui":r"\bBatFlightForGui\s*\(",
 "source_ReadDefaultParamsTable":r"\bReadDefaultParamsTable\s*\(",
}
MAX_BLOB=5*1024*1024

def gitblob(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def get_exact_blob(sha):
    url=f"https://api.github.com/repos/{UPSTREAM}/git/blobs/{sha}"
    req=urllib.request.Request(url,headers={
       "User-Agent":"reproducible-bat-model-source-audit/1.0",
       "Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=45) as r:
        raw=r.read(8*1024*1024)
    doc=json.loads(raw)
    if doc.get("sha")!=sha or doc.get("encoding")!="base64":
        raise ValueError("STOP_UPSTREAM_ORIGINAL_GITHUB_BLOB_RESPONSE")
    original=base64.b64decode(doc["content"].encode(),validate=False)
    if len(original)>MAX_BLOB or gitblob(original)!=sha:
        raise ValueError("STOP_ORIGINAL_SOURCE_HASH_OR_SIZE_MISMATCH")
    return original

def summarize_matlab(src):
    text=src.decode("utf-8","replace")
    return {
      "first_function_declarations":[line.strip()[:120] for line in text.splitlines()
          if re.match(r"^\s*function(?:\s|$)",line)][:4],
      "lines":len(text.splitlines()),
      "source_architecture_token_counts":{f:len(re.findall(re.escape(f),text,re.I))
                                            for f in ARCH_FIELDS},
      "runtime_portability_flags":{f:bool(re.search(pattern,text,re.I))
                                   for f,pattern in DEPENDENCIES.items()},
      "full_matlab_original_model_executed":False
    }

def summarize_xlsx(src):
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(io.BytesIO(src)) as z:
        names=z.namelist()
        book=z.read("xl/workbook.xml") if "xl/workbook.xml" in names else b""
    if not book:raise ValueError("STOP_NOT_VALID_ORIGINAL_PARAMETER_WORKBOOK")
    root=ET.fromstring(book)
    ns={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets=[{"sheetname":s.get("name"),"sheetId":s.get("sheetId")}
            for s in root.findall(".//s:sheet",ns)]
    return {"sheets":sheets,"source_original_cell_values_opened":False}

def summarize_mat_header(src):
    try:
        from scipy.io import whosmat
        shapes=whosmat(io.BytesIO(src))
        return {"original_source_mat_type":"MAT_standard",
                "source_variable_metadata":[{"name":name,"shape":list(shape),
                  "class":kind} for name,shape,kind in shapes],
                "source_numeric_mat_variables_loaded":False}
    except Exception as e:
        return {"original_source_mat_type":"STOP_MAT_CONTENT_METADATA_UNSUPPORTED",
                "error":type(e).__name__+":"+str(e)[:130],
                "source_numeric_mat_variables_loaded":False}

def main():
    if not DOC.exists():raise ValueError("STOP_SOURCE_RESEARCH_CONTRACT_MISSING")
    result={
      "schema":1,"status":"AUTHOR_SOURCE_IDENTITY_ARCHITECTURE_ONLY",
      "source_paper_DOI":"10.7554/eLife.105571",
      "source_UPSTREAM_GitHub":f"https://github.com/{UPSTREAM}",
      "original_upstream_COMMIT":UPSTREAM_PIN,
      "upstream_license":"MIT (check original LICENSE for redistribution conditions)",
      "new_bat_measurements":False,
      "original_author_simulation_executed":False,
      "original_source_files_or_numeric_outputs_redistributed":False,
      "public_author_source":{}
    }
    for path,sha in BLOBS.items():
        item={"path":path,"expected_original_Git_blob":sha,"status":"NOT_CHECKED"}
        try:
            raw=get_exact_blob(sha)
            item.update(status="ORIGINAL_SOURCE_VERIFIED",size_bytes=len(raw),
                        independent_sha256=hashlib.sha256(raw).hexdigest())
            if path.endswith(".m"):item["MATLAB_structure"]=summarize_matlab(raw)
            elif path.endswith(".xlsx"):item["parameter_workbook_structure"]=summarize_xlsx(raw)
            elif path.endswith(".mat"):item["stored_MAT_structure"]=summarize_mat_header(raw)
        except Exception as e:
            item.update(status="STOP_SOURCE_BLOB_OR_STRUCTURE",
                        error=type(e).__name__+":"+str(e)[:160])
        result["public_author_source"][path]=item
        print("AUTHOR_SOURCE",path,item["status"],"bytes",item.get("size_bytes"),
              "sha256",item.get("independent_sha256"))
        if "MATLAB_structure" in item:
            print("MODEL_ARCHITECTURE",path,json.dumps(item["MATLAB_structure"],sort_keys=True))
        if "parameter_workbook_structure" in item:
            print("SPECIES_PARAMETER_SCHEMA",path,item["parameter_workbook_structure"])
        if "stored_MAT_structure" in item:
            print("STORED_SAMPLE_MAT_METADATA",path,item["stored_MAT_structure"])
        if "error" in item:print("STOP_REASON",path,item["error"])
    result["all_seven_original_github_blobs_verified"]=all(
          v["status"]=="ORIGINAL_SOURCE_VERIFIED" for v in result["public_author_source"].values())
    result["status"]="PASS_ALL_AUTHOR_SOURCE_BLOBS" if result["all_seven_original_github_blobs_verified"] else "STOP_INCOMPLETE_AUTHENTIC_ORIGINAL_SOURCE"
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("MODEL_SOURCE_GATE",result["status"])
    return 0

if __name__=="__main__":raise SystemExit(main())
