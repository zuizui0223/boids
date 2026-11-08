"""All 28 original bat3d simulation-run evaluations keyed to original authors.

No original bat field measurements, no new source training. This is
post-publication/source-analysis of Steckel 2026 existing synthetic results.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
from steckel_2026_range_code_source_gate_v1 import (
    official_outer_catalog,extract_single_member
)
from steckel_2026_original_run_metrics_v1 import (
    source_report,CONTROL_COMPARISONS
)

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"STECKEL_2026_ORIGINAL_3D_OBSERVABILITY_SOURCE_RESULT_CONTRACT_V1.md"
OUT=ROOT/"STECKEL_2026_3D_ORIGINAL_28_RUN_COMPARISON_V1.json"
RUN_SHA="42148acb514b7bb89ab77bc7815951582b32551e54da61885c81803982d30681"
INDEX_SHA="6a8a86bdca8669468ab4ec0636369d4f1bfb9bda93c105b0e01d1cf6182833e7"
ARCHIVE_DATA="source_data/run_table.json"
EXPERIMENT_INDEX="experiments.json"
METRICS=("az","el","gc","leftright_correct","updown_correct","corr")
ORIGINAL_MAIN="smooth_online_b64"
GROUP_REFERENCE={
    "main_source_vs_shuffled_motion":ORIGINAL_MAIN,
    "main_source_vs_current_only":ORIGINAL_MAIN,
    "main_source_vs_shifted_motion":ORIGINAL_MAIN,
    "main_source_vs_head_fixed":ORIGINAL_MAIN,
    "head_motion_axes":"smooth_axis_pantilt",
    "specular_vs_sparse":"smooth_sparse",
    "memory_call_counts":ORIGINAL_MAIN,
    "relearning_degrees":None,
    "original_seeds":ORIGINAL_MAIN
}

def sha(data):return hashlib.sha256(data).hexdigest()

def compose(source):
    rows=source["original_source_all_metric_rows"]
    idx={x["source_run_name"]:x for x in source["original_source_28_declared_runs"]}
    if len(rows)!=len(idx)!=28:
        raise ValueError("STOP_AUTHOR_28_RUN_COUNT")
    by={}
    for record in rows:
        name=record["matched_source_name"]
        if name is None or name not in idx or name in by:
            raise ValueError("STOP_NOT_UNIQUELY_MATCHED_AUTHOR_ORIGINAL_RUN")
        num=record["original_source_scalar_metrics"]
        missing=[k for k in ("az","el","gc","n","step") if k not in num]
        if missing:raise ValueError("STOP_ORIGINAL_SOURCE_SCORES_MISSING_REQUIRED_METRICS")
        by[name]={
          "author_experiment":idx[name]["source_experiment"],
          "author_label":idx[name]["source_description"],
          "source_run_name":name,
          "source_evaluation_n":num["n"],
          "original_train_step":num["step"],
          "author_original_scalar_metrics":{k:num.get(k) for k in METRICS},
          "not_independent_empirical_bat_record":True
        }
    if len(by)!=28:
        raise ValueError("STOP_MISSING_SOURCE_RUN_IDENTITY")
    comparisons={}
    for group,info in source["comparison_support"].items():
        reference=GROUP_REFERENCE[group]
        names=info["planned_run_names"]
        records={k:by[k] for k in names}
        refrow=records.get(reference) if reference else None
        result=[]
        for name,row in records.items():
            r=row["author_original_scalar_metrics"]
            refscore=refrow["author_original_scalar_metrics"] if refrow else None
            delta={k:(r[k]-refscore[k] if refscore and isinstance(r[k],(int,float)) and isinstance(refscore[k],(int,float))
                      else None) for k in METRICS}
            result.append({
                "source_run":name,
                "source_exp":row["author_experiment"],
                "original_n":row["source_evaluation_n"],
                "original_step":row["original_train_step"],
                "author_metrics":r,
                "difference_from_original_source_reference":delta,
                "same_n_and_training_step_as_reference":
                  bool(refrow and row["source_evaluation_n"]==refrow["source_evaluation_n"] and
                  row["original_train_step"]==refrow["original_train_step"]),
                "evaluation_same_drawn_examples_verified":False
            })
        comparisons[group]={
            "source_original_reference":reference,
            "original_runs":result,
            "original_runs_all_present":len(records)==len(names),
            "n_real_bats_in_original_metric_table":0,
            "author_source_outcomes_are_published_prior_art":True
        }
    rest={k:v for k,v in by.items() if k not in
          set.union(*[set(c["planned_run_names"]) for c in source["comparison_support"].values()])}
    return {"all_runs":by,"comparisons":comparisons,"other_original_runs":rest}

def run():
    if not CONTRACT.exists():raise ValueError("STOP_POSTOUTCOME_INTERPRETATION_CONTRACT_MISSING")
    url,size,digest,files=official_outer_catalog()
    members={x["path"]:x for x in files}
    original={}
    for path,sha_expected in ((ARCHIVE_DATA,RUN_SHA),(EXPERIMENT_INDEX,INDEX_SHA)):
        if path not in members:raise ValueError("STOP_AUTHOR_ORIGINAL_SOURCE_MEMBER_MISSING")
        raw,receipt=extract_single_member(url,members[path],2*1024*1024)
        if sha(raw)!=sha_expected:raise ValueError("STOP_AUTHOR_ORIGINAL_SOURCE_SHA_CHANGED")
        original[path]={"data":raw,"receipt":receipt}
    table=source_report(original[ARCHIVE_DATA]["data"],original[EXPERIMENT_INDEX]["data"])
    data=compose(table)
    return {
      "schema":1,"date":"2026-11-08",
      "status":"ORIGINAL_AUTHOR_28_SIMULATED_3D_MOVEMENT_RUNS_ALL_JOINED",
      "source_zenodo_doi":"10.5281/zenodo.23537553",
      "source_preprint_doi":"10.64898/2026.10.22.760884",
      "source_metrics_original_sha256":RUN_SHA,
      "source_experiment_index_original_sha256":INDEX_SHA,
      "source_28_run_metrics_source_release_integrity":{
          p:original[p]["receipt"] for p in (ARCHIVE_DATA,EXPERIMENT_INDEX)
       },
      "author_original_28_numeric_run_count":len(data["all_runs"]),
      "author_all_original_run_results":data["all_runs"],
      "author_predeclared_control_and_movement_comparisons":data["comparisons"],
      "author_remaining_original_run_results":data["other_original_runs"],
      "new_field_or_lab_bat_measurements":False,
      "authentic_original_bat3d_Python_model_executed":False,
      "individual_live_bat_3D_tracks_read":False,
      "author_original_training_accuracy_is_prior_art":True,
      "source_original_2026_Teshima_two_species_VRNN_predictive_transfer_is_prior_art":True,
      "no_original_author_raw_files_rehosted":True,
      "interpretation_limitations":[
         "Original source simulated bat-like agent, not actual individual bats. Approximately 3990 evaluation positions are not 3990 biological replicates.",
         "Original experimental pan/tilt/roll, memory, specular/room, controls and ear rotation were already in the author preprint.",
         "Even matching n and step alone does not prove same heldout examples or matched training costs; do not infer causal performance differences.",
         "Original code source identity verified separately; this script only re-reads author source figure table, not author Python model execution.",
         "Novel cross-geometry and audio-crowding ecological prediction must be implemented and locked separately."
      ]
    }

def main():
    try:d=run()
    except Exception as e:
        d={"schema":1,"status":"STOP_AUTHOR_ORIGINAL_28_RUN_COMPARISON",
           "error":type(e).__name__+":"+str(e)[:240],
           "new_field_or_lab_bat_measurements":False}
    OUT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL_BAT3D_AUTHOR_28_RUN_REANALYSIS",d["status"])
    if d["status"].startswith("STOP"):
        print("STOP_REASON",d["error"])
        return 3
    for g,comparisons in d["author_predeclared_control_and_movement_comparisons"].items():
        print("ORIGINAL_AUTHOR_EXPERIMENT_CONTRAST",g,"reference",comparisons["source_original_reference"])
        for x in comparisons["original_runs"]:
            print("ORIGINAL_AUTHOR_CONDITION",x["source_run"],
              "n",x["original_n"],"train_step",x["original_step"],
              "az",round(x["author_metrics"]["az"],4),
              "el",round(x["author_metrics"]["el"],4),
              "gc",round(x["author_metrics"]["gc"],4),
              "delta_az",None if x["difference_from_original_source_reference"]["az"] is None else round(x["difference_from_original_source_reference"]["az"],4),
              "delta_el",None if x["difference_from_original_source_reference"]["el"] is None else round(x["difference_from_original_source_reference"]["el"],4),
              "same_n_step",x["same_n_and_training_step_as_reference"])
    print("PRIOR_ART_AUDIT_28_OF_28_SOURCE_SCORES_JOINED_NO_NEW_BAT_OBSERVATION")
    return 0

if __name__=="__main__":raise SystemExit(main())
