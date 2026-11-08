"""Author source reproduction eligibility, original Git and Zenodo coverage.

Reads a pinned MIT MATLAB source checkout (GitHub Actions only) and public
original-model parameter workbook cells; does NOT run source simulations or
read bat location/acoustic observations. Zenodo official API may be blocked;
denote that STOP, never guess source filenames or fabricate implementation.
"""
from __future__ import annotations
from collections import Counter
import hashlib,io,json,re,subprocess,urllib.request,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HOME=Path(__file__).resolve().parent
REPO=HOME.parent.parent
UP=REPO/"upstream"
OUT=HOME/"MAZAR_2026_CLUSTERING_SOURCE_COMPLETENESS_RESULT_V1.json"
PIN="a74fb61a8efb57ca37693893c3bd7b35fa94fa89"
MISSING_FN="BatManueverDecision_FullConfusion_ver08Aug24"
EXPERIMENT="Experiments Code/CaveExit_Experiment_Confusion.m"
CORE="BatFlightForGui.m"
WORKBOOK="DATA/DefaultParamsTable_CaveExit_FInal_withConfusion_PK.xlsx"
ZENODO_URL="https://zenodo.org/api/records/16992617"
MAX_ZENODO_ZIP=80*1024*1024
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def get(url,limit=1_000_000):
    headers={"Accept":"application/json,application/octet-stream,*/*",
             "User-Agent":"bat-scientific-source-eligibility/2026-11"}
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=60) as r:
        chunks=[];total=0
        while True:
            part=r.read(128*1024)
            if not part:break
            total+=len(part)
            if total>limit:raise ValueError("SOURCE_EXCEEDS_HARD_SIZE_CAP")
            chunks.append(part)
        return b"".join(chunks),r.status,r.headers.get("Content-Type")

def sheet_cell_value(cell,shared):
    typ=cell.get("t")
    if typ=="inlineStr":
        return "".join(x.text or "" for x in cell.findall(".//m:t",NS))
    v=cell.find("m:v",NS)
    if v is None:return None
    if typ=="s":
        n=int(v.text)
        return shared[n] if 0<=n<len(shared) else "<invalid shared string>"
    return v.text

def source_sonar_flags(source_bytes):
    with zipfile.ZipFile(io.BytesIO(source_bytes)) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(x.text or "" for x in si.findall(".//m:t",NS))
                    for si in root.findall("m:si",NS)]
        # Workbook and prior source schema agree BatSonar is sheet3, but don't
        # assume the presence of flags; explicit SOURCE STOP if absent.
        if "xl/worksheets/sheet3.xml" not in z.namelist():
            raise ValueError("STOP_ORIGINAL_BATSONAR_SHEET3_MISSING")
        root=ET.fromstring(z.read("xl/worksheets/sheet3.xml"))
        found={}
        for row in root.findall(".//m:sheetData/m:row",NS):
            values=[sheet_cell_value(c,shared) for c in row.findall("m:c",NS)]
            for field in ("ObsClusterFlag","ObsMemorySize","ObsEchoesRatioTH","ObsRepeationsFlag"):
                if any(str(v).strip()==field for v in values):
                    # Not a bat measurement: record only parameter row values
                    # containing source flag, preserving original literal cells.
                    found[field]={"row":int(row.get("r")),"row_values":values[:8]}
        return found

def original_source_gate():
    if not UP.exists():raise ValueError("PINNED_AUTHOR_SOURCE_CHECKOUT_MISSING")
    sha=subprocess.check_output(["git","-C",str(UP),"rev-parse","HEAD"],text=True).strip()
    if sha!=PIN:raise ValueError("AUTHOR_SOURCE_PIN_CHANGED")
    tracked=subprocess.check_output(["git","-C",str(UP),"ls-tree","-r","--name-only","HEAD"],text=True).splitlines()
    checks={}
    for name in (CORE,EXPERIMENT,WORKBOOK,"BatManueverDecision.m",
                 "findRepeatedClusters.m","distanceTHClustering.m","readme.txt"):
        path=UP/name
        checks[name]={"exists":path.is_file(),
                      "sha256":sha256(path.read_bytes()) if path.is_file() else None}
    source=(UP/CORE).read_text(errors="replace")
    experiment=(UP/EXPERIMENT).read_text(errors="replace")
    lines=source.splitlines()
    call_lines=[i+1 for i,l in enumerate(lines) if MISSING_FN in l and not l.lstrip().startswith("%")]
    cluster_condition_lines=[i+1 for i,l in enumerate(lines)
                             if re.search(r"^\s*if\s+AllParams\.BatSonarParams\.ObsClusterFlag\b",l)]
    fallback_lines=[i+1 for i,l in enumerate(lines)
                    if re.search(r"^\s*\[.*BatManueverDecision\s*\(",l)]
    exact_missing_paths=[p for p in tracked if p.split("/")[-1].lower()==MISSING_FN.lower()+".m"]
    exp_override={}
    for field in ("ObsMemorySize","ObsEchoesRatioTH","ObsRepeationsFlag","ObsClusterFlag"):
        pattern=rf"^\s*AllParams\.BatSonarParams\.{field}\s*=\s*([^;%]+)"
        found=re.findall(pattern,experiment,re.M)
        exp_override[field]=[x.strip() for x in found]
    xlsx_flags=source_sonar_flags((UP/WORKBOOK).read_bytes())
    readme=(UP/"readme.txt").read_text(errors="replace")
    result={
        "repo":"https://github.com/omermazar/Colony-Exit-Bat-Simulation",
        "original_commit":sha,
        "original_matlab_tree_file_count":len(tracked),
        "original_named_MATLAB_cluster_implementation_present":len(exact_missing_paths)>0,
        "original_clustering_function_exact_matches":exact_missing_paths,
        "branch_dereferences_ObsClusterFlag":len(cluster_condition_lines)>0,
        "source_lines_with_cluster_condition":cluster_condition_lines,
        "source_lines_with_missing_cluster_implementation":call_lines,
        "source_uses_existing_noncluster_fallback":len(fallback_lines)>0,
        "source_lines_with_noncluster_fallback":fallback_lines,
        "experiment_original_literal_parameter_overrides":exp_override,
        "source_MIT_workbook_param_rows":xlsx_flags,
        "original_README_describes_default_memory_5_calls":
             bool(re.search(r"default\s*=\s*5\s*calls",readme,re.I)),
        "checked_source_SHA256":checks,
        "original_author_simulation_executed":False,
    }
    if not call_lines or not cluster_condition_lines:
        result["status"]="SOURCE_BRANCH_IDENTIFIER_NOT_FOUND_STOP"
    elif not exact_missing_paths:
        result["status"]="ORIGINAL_GITHUB_CLUSTER_PATH_HAS_MISSING_FUNCTION"
    else:
        result["status"]="ORIGINAL_GITHUB_CLUSTER_FUNCTION_PRESENT"
    return result

def zenodo_source_gate():
    out={"url":ZENODO_URL,"status":"NOT_CHECKED",
         "raw_original_numerical_results_opened":False,
         "original_archive_redistributed":False,
         "source_files":[]}
    try:
        data,status,typ=get(ZENODO_URL)
        j=json.loads(data)
        out.update(http_status=status,response_SHA256=sha256(data),
                   record_id=j.get("id"),
                   publication_date=j.get("metadata",{}).get("publication_date"),
                   license=(j.get("metadata",{}).get("license") or {}).get("id")
                          if isinstance(j.get("metadata",{}).get("license"),dict) else j.get("metadata",{}).get("license"))
        sources=j.get("files") or []
        if not isinstance(sources,list):raise ValueError("SOURCE_FILE_LIST_NOT_ARRAY")
        for f in sources:
            if not isinstance(f,dict):continue
            out["source_files"].append({
                "key":f.get("key"),"size":f.get("size"),
                "checksum":f.get("checksum"),
                "url":(f.get("links") or {}).get("self") or (f.get("links") or {}).get("content")
            })
        out["metadata_status"]="OFFICIAL_ZENODO_METADATA_READ"
        candidates=[x for x in out["source_files"]
                    if (x.get("key") or "").lower().endswith((".zip",".tar.gz"))
                    and x.get("url") and isinstance(x.get("size"),int)]
        inspected=[]
        for file in candidates:
            if file["size"]>MAX_ZENODO_ZIP:
                inspected.append({"key":file["key"],"status":"STOP_ARCHIVE_OVER_80_MB","size":file["size"]})
                continue
            try:
                contents,_,_=get(file["url"],MAX_ZENODO_ZIP)
                if not zipfile.is_zipfile(io.BytesIO(contents)):
                    inspected.append({"key":file["key"],"status":"STOP_ARCHIVE_NOT_ZIP"})
                    continue
                with zipfile.ZipFile(io.BytesIO(contents)) as z:
                    names=[i.filename for i in z.infolist()]
                missing=[n for n in names if n.lower().split("/")[-1]==MISSING_FN.lower()+".m"]
                inspected.append({"key":file["key"],"status":"SOURCE_ZIP_MEMBERS_INSPECTED",
                                  "original_download_SHA256":sha256(contents),
                                  "member_count":len(names),
                                  "missing_function_found":len(missing)>0,
                                  "matching_missing_function_paths":missing,
                                  "root_directory_examples":names[:10]})
            except Exception as e:
                inspected.append({"key":file["key"],"status":"STOP_ARCHIVE_DOWNLOAD",
                                  "error":type(e).__name__+":"+str(e)[:160]})
        out["source_archive_member_inspections"]=inspected
        direct=[x for x in out["source_files"] if (x.get("key") or "").split("/")[-1].lower()==MISSING_FN.lower()+".m"]
        out["source_direct_missing_function_matches"]=direct
        out["status"]="OFFICIAL_ZENODO_FILE_METADATA_AND_ARCHIVE_GATE_COMPLETED"
    except Exception as e:
        out["status"]="STOP_OFFICIAL_ZENODO_API_ACCESS"
        out["error"]=type(e).__name__+":"+str(e)[:200]
    return out

def main():
    assert (HOME/"MAZAR_2026_CLUSTERING_SOURCE_COMPLETENESS_CONTRACT_2026_11_08.md").exists()
    z={
      "schema":1,"status":"SOURCE_ONLY_VERIFICATION",
      "original_paper_doi":"10.7554/eLife.105571",
      "source_zenodo_doi":"10.5281/zenodo.16992617",
      "no_new_bat_measurements":True,
      "source_original_animal_measurements_opened":False,
      "author_MATLAB_original_model_rerun":False,
      "author_original_source_files_redistributed":False
    }
    try:z["github_original_source"]=original_source_gate()
    except Exception as e:z["github_original_source"]={"status":"STOP_ORIGINAL_GITHUB_SOURCE_GATE",
                                  "error":type(e).__name__+":"+str(e)[:200]}
    z["zenodo_original_source"]=zenodo_source_gate()
    OUT.write_text(json.dumps(z,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("AUTHOR_GITHUB_SOURCE_GATE",json.dumps(z["github_original_source"],ensure_ascii=False,sort_keys=True))
    print("AUTHOR_ZENODO_SOURCE_GATE",json.dumps(z["zenodo_original_source"],ensure_ascii=False,sort_keys=True))
    print("NO_SOURCE_FIGURE_REPLAY_OR_NEW_BAT_DATA")
    return 0
if __name__=="__main__":raise SystemExit(main())
