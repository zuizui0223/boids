"""Real 2026 fruit-bat flight SONAR/3D trial archive SOURCE-SCHEMA gate.

Checks original CC0 Git commit and ORIGINAL .mat structural metadata only.
Uses scipy.io.whosmat: no loadmat, echo arrays, animal movement outcomes or
original bat IDs serialized. No new field measurements or original artifacts
redistributed. Does not call source Matlab GUI/simulator.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess
from scipy.io import whosmat
import h5py

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"EVELAND_2026_3D_GAZE_TRAJECTORY_SOURCE_GATE_2026_11_15.md"
UP=ROOT.parent.parent/"upstream"/"eveland2026"
PIN="59928a71887d521fec143080b0b187736c046a0e"
OUT=ROOT/"EVELAND_2026_ORIGINAL_3D_SONAR_MAT_SCHEMA_V1.json"
FILES=("Population_Analysis.m","Correlation_vs_lag.m","carollia_build_track_from_calls.m")
FIELDS=("R.calls.tSec","R.calls.XYZ_sm","R.track.tSec","R.track.pos_sm",
        "R.beam.rel_deg","R.beam.fitR","R.turns.peakTime_s")

def authenticate():
    if not CONTRACT.exists():raise ValueError("STOP_PREOUTPUT_SOURCE_CONTRACT_NOT_PRESENT")
    if not UP.is_dir():raise ValueError("STOP_AUTHOR_GIT_CHECKOUT_NOT_PRESENT")
    current=subprocess.check_output(["git","-C",str(UP),"rev-parse","HEAD"],text=True).strip()
    if current!=PIN:raise ValueError("STOP_AUTHENTIC_AUTHOR_SOURCE_COMMIT_CHANGED")
    paths=subprocess.check_output(["git","-C",str(UP),"ls-tree","-r","--name-only","HEAD"],text=True).splitlines()
    return current,paths

def inspect():
    commit,paths=authenticate()
    source_files=[p for p in paths if re.fullmatch(
        r"Trial_Data_Carolia/C[0-9]+_.*_traj_bat_pos_RESULTS\.mat",p)]
    if len(source_files)<8:raise ValueError("STOP_TOO_FEW_ORIGINAL_MAT_TRAILS")
    trialnames=set()
    sourceIDs=Counter()
    mat_structs=Counter()
    source_mat_sizes=[]
    source_mat_sha=[]
    failed=[]
    hdf5_struct_field_counter=Counter()
    hdf5_v73_files=0
    for p in source_files:
        sourceID=re.match(r"Trial_Data_Carolia/(C[0-9]+)_",p).group(1)
        sourceIDs[sourceID]+=1
        original=UP/p
        content=original.read_bytes()
        source_mat_sizes.append(len(content))
        source_mat_sha.append(hashlib.sha256(content).hexdigest())
        try:
            try:
                entries=whosmat(str(original))
            except NotImplementedError:
                # Original 2026 author saved Matlab v7.3 HDF5 rather than v5.
                # HDF5 keys + attributes are metadata, no original array or
                # reference values are ever loaded/dereferenced.
                with h5py.File(original,"r") as h:
                    hdf5_v73_files+=1
                    entries=[]
                    for name,obj in h.items():
                        if name.startswith("#"):continue
                        val=obj.attrs.get("MATLAB_class")
                        kind=val.decode("utf-8","replace") if isinstance(val,bytes) else str(val)
                        shape=tuple(obj.shape) if isinstance(obj,h5py.Dataset) else (1,1)
                        entries.append((name,shape,kind))
                    if "RESULTS" in h and isinstance(h["RESULTS"],h5py.Group):
                        roots=tuple(sorted(h["RESULTS"].keys()))
                        hdf5_struct_field_counter[roots]+=1
            mat_structs[tuple(sorted((str(name),tuple(shape),kind) for name,shape,kind in entries))]+=1
        except Exception as e:
            failed.append({"error":type(e).__name__+":"+str(e)[:100],
                           "type":"MAT_OR_HDF5_SCHEMA_NOT_SUPPORTED"})
        trialnames.add(p)
    code={}
    for p in FILES:
        raw=(UP/p).read_bytes()
        src=raw.decode("utf-8","replace")
        found={f:bool(re.search(re.escape(f).replace(r"\.",r"\s*\.\s*"),src)) for f in FIELDS}
        code[p]={"original_code_sha256":hashlib.sha256(raw).hexdigest(),
                 "original_lines":len(src.splitlines()),
                 "original_expected_alignment_field_present":found,
                 "original_source_code_copied":False}
    rous=[p for p in paths if re.search(r"ROUS|Rous|rousettus",p,re.I) and
           p.lower().endswith((".mat",".csv",".h5",".xlsx"))]
    srcsizes=sorted(sourceIDs.values())
    labels={"bat_trials_min":min(srcsizes),"bat_trials_median":srcsizes[len(srcsizes)//2],
            "bat_trials_max":max(srcsizes)}
    common=[{"metadata_variable_list":[{"variable":item[0],"shape":list(item[1]),"kind":item[2]}
                                    for item in key],
             "original_trial_files_with_this_schema":count}
            for key,count in mat_structs.items()]
    gate=(not failed and len(source_files)==30 and len(sourceIDs)==8 and
          all(any(field["variable"]=="RESULTS" and field["kind"]=="struct"
                  for field in group["metadata_variable_list"]) for group in common))
    return {"schema":1,
      "date":"2026-11-15",
      "source_paper_doi":"10.1007/s00359-026-01818-0",
      "original_git_repo":"https://github.com/00keveland/Tunnel_2026",
      "original_github_commit":commit,
      "source_original_repo_license":"CC0-1.0",
      "original_study_bats_Rousettus_12_Carollia_8":True,
      "status":"PASS_ORIGINAL_CAROLLIA_3D_SONAR_MAT_SCHEMA_ONLY" if gate else "STOP_ORIGINAL_MAT_SCHEMA_INCOMPLETE",
      "source_original_carollia_trial_file_count":len(source_files),
      "source_original_individual_id_count":len(sourceIDs),
      "source_original_trials_per_individual_min_median_max":labels,
      "original_carollia_MAT_matlab_struct_schemas":common,
      "source_mat_schema_failures":failed,
      "source_matlab_v73_HDF5_original_files":hdf5_v73_files,
      "source_HDF5_struct_field_root_names_only":[
          {"original_trial_files":n,"field_names":list(key)}
          for key,n in hdf5_struct_field_counter.items()],
      "original_numeric_HDF5_datasets_or_object_references_dereferenced":False,
      "source_mat_bytes_min_max":[min(source_mat_sizes),max(source_mat_sizes)],
      "source_mat_sha256_commitment_sorted_set_hash":hashlib.sha256("".join(sorted(source_mat_sha)).encode()).hexdigest(),
      "original_rousettus_public_trial_mat_or_csv_n":len(rous),
      "original_Rousettus_behavioral_values_admitted":False,
      "original_source_fields_by_script":code,
      "original_bat_calls_or_trajectory_values_opened":False,
      "original_animal_IDs_or_trial_paths_exported":False,
      "source_original_MAT_files_copied_or_redistributed":False,
      "new_animal_measurements":False,
      "original_2026_direction_prediction_prior_art":True,
      "original_2026_paper_two_species_effect_reproduced":False,
      "claim_limit":"MAT schema admission cannot demonstrate behavior or source equal-time acoustic-to-trajectory join. Follow-on requires new frozen own-bat heldout prediction contract before loading values."
    }
if __name__=="__main__":
    try:o=inspect()
    except Exception as e:o={"schema":1,"status":"STOP_GIT_ORIGINAL_SOURCE_METADATA",
                            "error":type(e).__name__+":"+str(e)[:200],
                            "new_animal_measurements":False,
                            "original_bat_calls_or_trajectory_values_opened":False,
                            "original_animal_IDs_or_trial_paths_exported":False}
    OUT.write_text(json.dumps(o,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("EVELAND_REAL_BAT_SOURCE_GATE",o["status"])
    if not o["status"].startswith("STOP"):
        print("SOURCE_CAROLLIA_TRIALS",o["source_original_carollia_trial_file_count"],
              "SOURCE_BATS",o["source_original_individual_id_count"],
              "REPEAT_COUNTS",o["source_original_trials_per_individual_min_median_max"])
        print("SOURCE_SCHEMA",json.dumps(o["original_carollia_MAT_matlab_struct_schemas"],sort_keys=True))
        print("SOURCE_MATLAB_FIELD_EXPECTATIONS",json.dumps(o["original_source_fields_by_script"],sort_keys=True))
        print("ROUSETTUS_NUMERIC_FILES_PROVIDED",o["original_rousettus_public_trial_mat_or_csv_n"])
    else:
        print("SOURCE_STRUCTURAL_STOP_FACTS",json.dumps({
            "source_trial_count":o.get("source_original_carollia_trial_file_count"),
            "source_bat_count":o.get("source_original_individual_id_count"),
            "source_MAT_schema_distribution":o.get("original_carollia_MAT_matlab_struct_schemas"),
            "source_MAT_decode_failures":o.get("source_mat_schema_failures"),
            "source_original_MATLAB_v73_count":o.get("source_matlab_v73_HDF5_original_files"),
            "source_HDF5_struct_field_names":o.get("source_HDF5_struct_field_root_names_only"),
            "source_original_Rousettus_files":o.get("original_rousettus_public_trial_mat_or_csv_n")
        },sort_keys=True))
        print("STOP_REASON",o.get("error","Not all required trial variables are available"))
