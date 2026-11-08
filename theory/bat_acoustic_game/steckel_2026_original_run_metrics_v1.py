"""Read original author-supplied 2026 bat3d run_table.json, all rows, no cherry picks.

All material fetched via official Zenodo HTTP206 range from the 988MB ZIP.
Code, HRTF, model weights, training sound data and full ZIP not redistributed.
Author's original simulated-run metrics are PRIOR ART, not measured bats.
"""
from __future__ import annotations
from pathlib import Path
import json,math
from steckel_2026_range_code_source_gate_v1 import (
 official_outer_catalog,extract_single_member
)

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"STECKEL_2026_3D_ORIGINAL_METRIC_TABLE_PREOUTPUT_V1.md"
OUT=ROOT/"STECKEL_2026_3D_AUTHOR_RUN_METRIC_RESULT_V1.json"
ADMITTED=("experiments.json","source_data/run_table.json")
CAP={"experiments.json":100000,"source_data/run_table.json":2*1024*1024}
EXPERIMENTS=tuple("E"+str(i) for i in range(1,10))+tuple("C"+str(i) for i in range(1,6))
CONTROL_COMPARISONS={
  "main_source_vs_shuffled_motion":["smooth_online_b64","smooth_ctrl_shuffle"],
  "main_source_vs_current_only":["smooth_online_b64","smooth_ctrl_nomotion"],
  "main_source_vs_shifted_motion":["smooth_online_b64","smooth_ctrl_shift2"],
  "main_source_vs_head_fixed":["smooth_online_b64","smooth_ctrl_fixedhead"],
  "head_motion_axes":["smooth_axis_pan","smooth_axis_pantilt","smooth_axis_panroll"],
  "specular_vs_sparse":["smooth_sparse","smooth_room"],
  "memory_call_counts":["smooth_online_b1","smooth_online_b4","smooth_online_b16","smooth_online_b64","smooth_online_b256","smooth_online_b512"],
  "relearning_degrees":["smooth_relearn_rot5","smooth_relearn_rot10","smooth_relearn_rot20"],
  "original_seeds":["smooth_online_b64","smooth_online_b64_s1","smooth_online_b64_s2"]
}

def source_rows(data):
    """Return dict-row records without selecting result-dependent fields."""
    if isinstance(data,list):
        if all(isinstance(x,dict) for x in data):return data,"list"
        raise ValueError("STOP_ORIGINAL_RUN_TABLE_LIST_NOT_DICT_RECORDS")
    if isinstance(data,dict):
        for k,v in data.items():
            if isinstance(v,list) and v and all(isinstance(x,dict) for x in v):
                return v,"object."+k
        if all(isinstance(v,dict) for v in data.values()):
            return [{"original_key":k,**v} for k,v in data.items()],"object_keys"
    raise ValueError("STOP_ORIGINAL_RUN_TABLE_SCHEMA_NOT_KNOWN")

def numerics(d,prefix="",limitdepth=2):
    """Extract all scalar numerics, not only positive expected results."""
    result={}
    for key,val in d.items():
        name=prefix+str(key)
        if isinstance(val,bool):continue
        if isinstance(val,(int,float)):
            if math.isfinite(float(val)):
                result[name]=val
            else:result[name]=None
        elif isinstance(val,dict) and limitdepth>0:
            result.update(numerics(val,name+".",limitdepth-1))
    return result

def labels(row):
    return {k:str(row[k])[:160] for k in
      ("name","run","run_dir","run_path","experiment","id","experiment_id","checkpoint","eval_split")
      if k in row and isinstance(row[k],(str,int))}

def analyze_index(data):
    if not isinstance(data,list) or len(data)!=28:
        raise ValueError("STOP_ORIGINAL_EXPERIMENT_ID_MAP_NOT_28")
    rows=[]
    for d in data:
        if not isinstance(d,dict):raise ValueError("STOP_INVALID_SOURCE_EXP_RECORD")
        e=d.get("experiment");name=d.get("name");run=d.get("run")
        if e not in EXPERIMENTS or not isinstance(name,str) or not isinstance(run,str):
            raise ValueError("STOP_SOURCE_EXP_ID_NAME_RUN_NOT_JOINABLE")
        rows.append({"source_experiment":e,"source_run_name":name,
                    "source_run_directory":run,
                    "source_description":str(d.get("description",""))[:200]})
    if len({x["source_run_name"] for x in rows})!=len(rows):
        raise ValueError("STOP_DUPLICATE_ORIGINAL_RUN_NAMES")
    return rows

def source_report(rawtable,rawindex):
    experiments=analyze_index(json.loads(rawindex))
    datum=json.loads(rawtable)
    rows,location=source_rows(datum)
    metric_columns=sorted(set(key for d in rows for key in numerics(d)))
    fields=sorted(set(key for d in rows for key in d))
    out={"schema":1,
      "status":"PUBLISHED_AUTHOR_3D_SIM_RUN_METRICS_SOURCE_REANALYSIS",
      "index_count":len(experiments),"table_count":len(rows),
      "original_source_table_top_type":type(datum).__name__,
      "original_source_table_grain_path":location,
      "original_source_run_row_fields":fields,
      "original_source_numeric_metric_fields":metric_columns,
      "original_metrical_runs_have_common_metric_columns":None,
      "original_source_28_declared_runs":experiments,
      "original_source_all_metric_rows":[],
      "comparison_support":{},
      "strict_claim":"Published simulated model metrics only, no measured animal 3D learning or novelty."
    }
    model_by_name={s["source_run_name"]:s for s in experiments}
    found=set()
    for d in rows:
        lab=labels(d)
        run=(lab.get("name") or lab.get("run_name") or lab.get("run") or lab.get("original_key"))
        # When source table uses run path or name, exact basename match. If it
        # doesn't, retain original row but do NOT invent source identity.
        matched=None
        if run in model_by_name:matched=run
        else:
            for field in ("name","run","run_dir","original_key"):
                value=d.get(field)
                if not isinstance(value,str):continue
                for name,x in model_by_name.items():
                    if value==name or value==x["source_run_directory"] or value.rstrip("/").split("/")[-1]==x["source_run_directory"].split("/")[-1]:
                        matched=name
                        break
                if matched:break
        if matched:found.add(matched)
        out["original_source_all_metric_rows"].append({
             "source_original_row_identity":lab,
             "matched_source_name":matched,
             "original_source_scalar_metrics":numerics(d),
             "original_non_numeric_field_names":sorted(k for k in d if k not in numerics(d))
        })
    out["original_source_matched_unique_runs"]=len(found)
    out["source_original_run_names_missing_from_metrics"]=sorted(set(model_by_name)-found)
    out["original_metrical_runs_have_common_metric_columns"]=sorted(set.intersection(
       *(set(r["original_source_scalar_metrics"]) for r in out["original_source_all_metric_rows"]))) if rows else []
    for comp,names in CONTROL_COMPARISONS.items():
        matched=[r for r in out["original_source_all_metric_rows"]
                 if r["matched_source_name"] in names]
        names_observed=set(r["matched_source_name"] for r in matched)
        common=set.intersection(*(set(r["original_source_scalar_metrics"]) for r in matched)) if matched else set()
        out["comparison_support"][comp]={
           "planned_run_names":names,
           "matched_source_rows":len(matched),
           "matched_unique_run_names":sorted(names_observed),
           "unavailable_runs":sorted(set(names)-names_observed),
           "shared_numeric_metric_columns":sorted(common),
           "numbers_are_author_published_prior_art":True,
           "common_evaluation_subset_verified":False
        }
    return out

def main():
    result={"schema":1,"date":"2026-11-08",
      "status":"STOP_SOURCE_GATE_UNFINISHED",
      "source_doi":"10.5281/zenodo.23537553",
      "source_preprint_DOI":"10.64898/2026.10.22.760884",
      "new_animal_measurements":False,
      "original_author_model_executed":False,
      "source_original_raw_files_rehosted":False,
      "original_model_weights_3D_echo_samples_HRTF_opened":False,
      "source_integrity":{}}
    try:
        if not CONTRACT.exists():raise ValueError("STOP_MISSING_FROZEN_METRIC_PREOUTPUT")
        url,size,checksum,dir=official_outer_catalog()
        catalog={x["path"]:x for x in dir}
        if not all(p in catalog for p in ADMITTED):
            raise ValueError("STOP_NO_AUTHOR_ORIGINAL_EXP_RUN_TABLE")
        source={}
        for path in ADMITTED:
            raw,receipt=extract_single_member(url,catalog[path],CAP[path])
            result["source_integrity"][path]=receipt
            source[path]=raw
            print("AUTHOR_SOURCE_METRIC_INPUT_SHA",path,receipt["member_sha256"],receipt["original_uncompressed_bytes"])
        report=source_report(source["source_data/run_table.json"],source["experiments.json"])
        result.update(report)
        result["status"]="PASS_SOURCE_ORIGINAL_RUN_TABLE_ALL_METRICS_NO_TUNING"
    except Exception as e:
        result["status"]="STOP_SOURCE_3D_PUBLISHED_TABLE_ACCESS_OR_GRAIN"
        result["error"]=type(e).__name__+":"+str(e)[:250]
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("STECKEL_BAT3D_TABLE_STATUS",result["status"])
    if result["status"].startswith("STOP"):
        print("STOP_REASON",result.get("error"))
    else:
        print("TABLE_SCHEMA",json.dumps({k:result[k] for k in
              ("table_count","original_source_table_grain_path","original_source_numeric_metric_fields",
               "original_source_matched_unique_runs","source_original_run_names_missing_from_metrics")},sort_keys=True))
        for key,r in result["comparison_support"].items():
            print("SOURCE_PLANNED_COMPARISON_COVERAGE",key,json.dumps(r,sort_keys=True))
        for item in result["original_source_all_metric_rows"]:
            print("ORIGINAL_AUTHOR_SIMULATED_RUN",item["matched_source_name"],
                  json.dumps(item["original_source_scalar_metrics"],sort_keys=True)[:3500])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
