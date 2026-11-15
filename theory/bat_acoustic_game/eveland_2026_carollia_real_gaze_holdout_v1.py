"""Independent source real Carollia 2026 3D flight + acoustic gaze holdout.

Original author data (DOI 10.1007/s00359-026-01818-0), Git commit pinned.
Previous paper already reported gaze anticipates turns. New secondary question:
does acoustic gaze ADD bat-heldout prediction beyond past flight kinematics?

No new bats, no Rousettus original record admitted, no source raw records
or original animal IDs rehosted, no confirmation of acoustic interference.
All choices locked in the pre-output source contract.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import hashlib,json,math,re,subprocess
import numpy as np
import h5py

ROOT=Path(__file__).resolve().parent
UP=ROOT.parent.parent/"upstream"/"eveland2026"
CONTRACT=ROOT/"EVELAND_2026_CAROLLIA_GAZE_BEYOND_KINEMATICS_PREOUTPUT_2026_11_15.md"
OUT=ROOT/"EVELAND_2026_CAROLLIA_GAZE_MOTION_HOLDOUT_V1.json"
PIN="59928a71887d521fec143080b0b187736c046a0e"
BEAM_FIT_R_MIN=.30
HORIZONS=(.10,.20,.30)
RECEIVED_QUALITY_SOURCE="Population_Analysis.m fitR>=0.30"
LAMBDA_RIDGE=.01
MIN_BATS=6
MIN_TRIALS_PER_BAT=2
MIN_VALID_CALLS_PER_BAT=20
BOOT=5000
SEED=20261115
GEOM_FEATURES=("x","y","z","sin_heading","cos_heading",
               "previous_wrapped_heading_change","recent_planar_speed")

def unwrap_source_ref(h,obj):
    """Accept one source MATLAB v7.3 scalar-struct ref per named field."""
    while isinstance(obj,h5py.Dataset) and h5py.check_dtype(ref=obj.dtype) is not None:
        refs=np.asarray(obj[()]).reshape(-1)
        if len(refs)!=1 or not isinstance(refs[0],h5py.Reference) or not refs[0]:
            raise ValueError("STOP_HDF5_NONSCALAR_SOURCE_FIELD_REFERENCE")
        obj=h[refs[0]]
    return obj

def field_group(h,root,name):
    if not isinstance(root,h5py.Group) or name not in root:
        raise ValueError("STOP_MISSING_ORIGINAL_SOURCE_STRUCT_FIELD_"+name)
    obj=unwrap_source_ref(h,root[name])
    if not isinstance(obj,h5py.Group):
        raise ValueError("STOP_ORIGINAL_SOURCE_FIELD_NOT_STRUCT_"+name)
    return obj

def numeric_field(h,group,name):
    if name not in group:
        raise ValueError("STOP_MISSING_ORIGINAL_NUMERIC_FIELD_"+name)
    obj=unwrap_source_ref(h,group[name])
    if not isinstance(obj,h5py.Dataset):
        raise ValueError("STOP_ORIGINAL_SOURCE_FIELD_NOT_NUMERIC_DATASET_"+name)
    v=np.asarray(obj[()])
    if v.dtype.kind not in "iuf":
        raise ValueError("STOP_NONNUMERIC_ORIGINAL_FIELD_"+name)
    return np.array(v,dtype=float)

def numeric_vector(h,g,key):
    a=numeric_field(h,g,key)
    if a.ndim==1:return a
    if a.ndim==2 and 1 in a.shape:return a.reshape(-1)
    raise ValueError("STOP_ORIGINAL_SOURCE_VECTOR_SHAPE_"+key)

def xyz_track(a,n):
    if a.ndim!=2:raise ValueError("STOP_SOURCE_TRACK_NOT_MATRIX")
    if a.shape==(n,3) and a.shape!=(3,n):return a
    if a.shape==(3,n) and a.shape!=(n,3):return a.T
    raise ValueError("STOP_ORIGINAL_SOURCE_TRACK_DIMENSIONS_NOT_UNIQUE")

def read_source_trial(path):
    with h5py.File(path,"r") as h:
        top=field_group(h,h,"RESULTS")
        calls=field_group(h,top,"calls")
        beam=field_group(h,top,"beam")
        track=field_group(h,top,"track")
        tcall=numeric_vector(h,calls,"tSec")
        beam_rel=numeric_vector(h,beam,"rel_deg")
        fit=numeric_vector(h,beam,"fitR")
        track_t=numeric_vector(h,track,"tSec")
        track_pos=xyz_track(numeric_field(h,track,"pos_sm"),len(track_t))
    if len(tcall)!=len(beam_rel) or len(tcall)!=len(fit):
        raise ValueError("STOP_SOURCE_CALL_BEAM_LENGTH_MISMATCH")
    if len(tcall)<2 or len(track_t)<15:
        raise ValueError("STOP_ORIGINAL_SOURCE_TOO_FEW_SAMPLES")
    if not np.all(np.isfinite(track_t)) or not np.all(np.isfinite(track_pos)):
        raise ValueError("STOP_ORIGINAL_SOURCE_TRACK_NONFINITE")
    if not np.all(np.diff(track_t)>0) or not np.all(np.diff(tcall)>0):
        raise ValueError("STOP_ORIGINAL_SOURCE_TIMESTAMPS_NOT_STRICTLY_INCREASING")
    return {"call_times":tcall,"beam_deg":beam_rel,"beam_fitR":fit,
            "track_times":track_t,"track_pos":track_pos}

def wrap_pi(x):
    return (x+np.pi)%(2*np.pi)-np.pi

def position(t,times,coords):
    if not times[0]<=t<=times[-1]:raise ValueError("SOURCE_TRIAL_TIME_EXTRAPOLATION")
    return np.array([np.interp(t,times,coords[:,k]) for k in range(3)])

def planar_heading(t,times,coords,back=.05):
    p=position(t,times,coords)
    old=position(t-back,times,coords)
    d=p[:2]-old[:2]
    if not np.all(np.isfinite(d)) or np.linalg.norm(d)<=1e-8:
        return None
    return math.atan2(float(d[1]),float(d[0]))

def trial_rows(source,horizon=.20):
    """All candidate measurements have matched original source times; past-only features."""
    if horizon not in HORIZONS:raise ValueError("STOP_NONREGISTERED_PREDICTION_HORIZON")
    tcall=source["call_times"];quality=source["beam_fitR"];gaze=source["beam_deg"]
    t=source["track_times"];xyz=source["track_pos"]
    rows=[]
    issues=Counter()
    for i,calltime in enumerate(tcall):
        if not np.isfinite(calltime) or not np.isfinite(gaze[i]) or not np.isfinite(quality[i]):
            issues["nonfinite_call_or_beam"]+=1;continue
        if quality[i]<BEAM_FIT_R_MIN:
            issues["original_author_beam_fitR_below_0p30"]+=1;continue
        if calltime-.25<t[0] or calltime+horizon>t[-1]:
            issues["history_or_future_outside_same_trial"]+=1;continue
        ht=planar_heading(calltime,t,xyz)
        hp=planar_heading(calltime-.20,t,xyz)
        hf=planar_heading(calltime+horizon,t,xyz)
        if ht is None or hp is None or hf is None:
            issues["undefined_planar_heading"]+=1;continue
        curr=position(calltime,t,xyz)
        previous=position(calltime-.05,t,xyz)
        speed=float(np.linalg.norm(curr[:2]-previous[:2])/.05)
        angular_past=float(wrap_pi(ht-hp))
        features=np.array([curr[0],curr[1],curr[2],
            math.sin(ht),math.cos(ht),angular_past,speed],dtype=float)
        y=float(wrap_pi(hf-ht))
        if not np.all(np.isfinite(features)) or not math.isfinite(y):
            issues["nonfinite_predictor_or_target"]+=1;continue
        rows.append({"G":features,"S":math.radians(float(gaze[i])),
                     "Y":y,"t":float(calltime)})
    return rows,issues

def source_cohort():
    if not CONTRACT.exists():raise ValueError("STOP_MISSING_PREOUTPUT_SOURCE_TEST_CONTRACT")
    if subprocess.check_output(["git","-C",str(UP),"rev-parse","HEAD"],text=True).strip()!=PIN:
        raise ValueError("STOP_ORIGINAL_DATA_GIT_REVISION_CHANGED")
    paths=sorted((UP/"Trial_Data_Carolia").glob("C*_traj_bat_pos_RESULTS.mat"))
    if len(paths)!=30:raise ValueError("STOP_ORIGINAL_SOURCE_30_TRIAL_FILE_SET_CHANGED")
    expected=Counter()
    for p in paths:
        label=re.match(r"^(C\d+)_",p.name)
        if not label:raise ValueError("STOP_SOURCE_ORIGINAL_BAT_NAME_UNPARSABLE")
        expected[label.group(1)]+=1
    if len(expected)!=8:raise ValueError("STOP_SOURCE_NOT_8_BIOLOGICAL_BATS")
    source_trial={}
    fail=[]
    contents=[]
    for p in paths:
        bid=re.match(r"^(C\d+)_",p.name).group(1)
        contents.append(hashlib.sha256(p.read_bytes()).hexdigest())
        try:
            source_trial[p.name]=(bid,read_source_trial(p))
        except Exception as e:
            fail.append(type(e).__name__+":"+str(e)[:100])
    return source_trial,{
       "original_source_trials_in_repository":30,
       "original_bat_ID_count":8,
       "original_trials_per_bat_sorted":sorted(expected.values()),
       "readable_numeric_source_trials":len(source_trial),
       "source_read_failure_counts_by_reason":dict(Counter(fail)),
       "source_original_MAT_SHA256_sorted_set_commitment":
          hashlib.sha256("".join(sorted(contents)).encode()).hexdigest(),
       "source_original_values_exported":False
    }

def build_dataset(cohort,horizon):
    rows=[]
    quality=Counter()
    trials_by_bat=defaultdict(set)
    calls_by_bat=Counter()
    for name,(bat,source) in cohort.items():
        values,issues=trial_rows(source,horizon)
        quality.update(issues)
        if values:trials_by_bat[bat].add(name)
        calls_by_bat[bat]+=len(values)
        for record in values:
            record["bat"]=bat;record["trial"]=name
            rows.append(record)
    eligible={b for b in trials_by_bat
              if len(trials_by_bat[b])>=MIN_TRIALS_PER_BAT
              and calls_by_bat[b]>=MIN_VALID_CALLS_PER_BAT}
    selected=[r for r in rows if r["bat"] in eligible]
    bat_counts=sorted(calls_by_bat[b] for b in eligible)
    return selected,{
       "source_bats_eligible":len(eligible),
       "original_bats_in_cohort":8,
       "source_trials_with_valid_calls":sum(len(v) for v in trials_by_bat.values()),
       "source_original_call_rows_scored":len(selected),
       "source_bat_valid_call_counts_min_max":
          [min(bat_counts),max(bat_counts)] if bat_counts else None,
       "eligible_source_trials":sum(len(trials_by_bat[b]) for b in eligible),
       "original_qc_rejection_counts":dict(quality),
       "original_animal_labels_or_trial_names_exported":False}

def weighted_ridge(train,feature):
    X=np.vstack([r["G"] if feature=="G" else
       np.r_[r["G"],r["S"] if feature=="GS" else r["shifted_sonar"]]
       for r in train])
    Y=np.asarray([r["Y"] for r in train])
    bybat=defaultdict(lambda:defaultdict(list))
    for i,row in enumerate(train):bybat[row["bat"]][row["trial"]].append(i)
    weight=np.zeros(len(train),dtype=float)
    for bat,trials in bybat.items():
        for trial,indices in trials.items():
            weight[indices]=1/(len(bybat)*len(trials)*len(indices))
    weight/=np.sum(weight)
    mu=np.average(X,axis=0,weights=weight)
    sd=np.sqrt(np.average((X-mu)**2,axis=0,weights=weight))
    sd=np.where(sd>1e-10,sd,1.)
    Z=(X-mu)/sd
    design=np.column_stack((np.ones(len(train)),Z))
    penalty=np.diag([0.]+[LAMBDA_RIDGE]*Z.shape[1])
    coefficients=np.linalg.solve(design.T@(weight[:,None]*design)+penalty,
                                 design.T@(weight*Y))
    return mu,sd,coefficients

def predict(test,params,feature):
    mu,sd,coef=params
    X=np.vstack([r["G"] if feature=="G" else
       np.r_[r["G"],r["S"] if feature=="GS" else r["shifted_sonar"]]
       for r in test])
    z=(X-mu)/sd
    return wrap_pi(np.c_[np.ones(len(z)),z]@coef)

def shift_sonar_within_trials(rows):
    bytrial=defaultdict(list)
    for k,r in enumerate(rows):bytrial[r["trial"]].append(k)
    for indices in bytrial.values():
        seq=np.asarray([rows[k]["S"] for k in indices])
        shifted=np.roll(seq,max(1,len(seq)//2))
        for k,val in zip(indices,shifted):rows[k]["shifted_sonar"]=float(val)

def bootstrap_bat_differences(values):
    rng=np.random.default_rng(SEED)
    x=np.asarray(values)
    boot=np.mean(rng.choice(x,size=(BOOT,len(x)),replace=True),axis=1)
    return np.quantile(boot,[.025,.975]).tolist()

def holdout(rows):
    bats=sorted({r["bat"] for r in rows})
    if len(bats)<MIN_BATS:
        return {"status":"SOURCE_SUPPORT_STOP_FEWER_THAN_SIX_BATS","n_bats":len(bats)}
    shift_sonar_within_trials(rows)
    per_model=defaultdict(dict)
    per_bat_counts=[]
    for heldout in bats:
        train=[r for r in rows if r["bat"]!=heldout]
        test=[r for r in rows if r["bat"]==heldout]
        if len({r["bat"] for r in train})<MIN_BATS-1:
            raise ValueError("STOP_TRAINING_FOLD_TOO_FEW_SOURCE_BATS")
        preds={
          "G0":np.zeros(len(test),dtype=float),
          "G1":predict(test,weighted_ridge(train,"G"),"G"),
          "G2":predict(test,weighted_ridge(train,"GS"),"GS"),
          "G2_shift":predict(test,weighted_ridge(train,"GShift"),"GShift")
        }
        loss={name:np.degrees(np.abs(wrap_pi(np.array([r["Y"] for r in test])-v)))
              for name,v in preds.items()}
        original_trials=defaultdict(list)
        for i,r in enumerate(test):original_trials[r["trial"]].append(i)
        per_bat_counts.append({"source_trials":len(original_trials),"source_calls":len(test)})
        for name,errors in loss.items():
            per_model[name][heldout]=float(np.mean([
                 np.mean(errors[ids]) for ids in original_trials.values()]))
    scores={name:{
       "equal_bat_mean_angular_MAE_deg":float(np.mean(list(result.values()))),
       "median_bat_angular_MAE_deg":float(np.median(list(result.values()))),
       "original_biological_bats":len(bats)
    } for name,result in per_model.items()}
    differences={}
    for key,a,b in (("gaze_minus_geometry","G2","G1"),
                    ("gaze_minus_trial_shifted_gaze","G2","G2_shift"),
                    ("geometry_minus_zero","G1","G0")):
        vals=[per_model[a][i]-per_model[b][i] for i in bats]
        differences[key]={
          "mean_bat_MAE_difference_deg":float(np.mean(vals)),
          "whole_bat_bootstrap95_deg":bootstrap_bat_differences(vals),
          "bats_improved":sum(x< -1e-10 for x in vals),
          "bats_worsened":sum(x> 1e-10 for x in vals),
          "bats_tied":sum(abs(x)<=1e-10 for x in vals)}
    return {"status":"ELIGIBLE_SOURCE_INTERNAL_WHOLE_BAT_HOLDOUT",
            "original_bat_independent_folds":len(bats),
            "original_source_trials_scored":sum(x["source_trials"] for x in per_bat_counts),
            "original_source_calls_scored":sum(x["source_calls"] for x in per_bat_counts),
            "per_bat_trials_min_max":[min(x["source_trials"] for x in per_bat_counts),
                                      max(x["source_trials"] for x in per_bat_counts)],
            "models":scores,"comparisons":differences,
            "source_bat_IDs_and_individual_predictions_exported":False}

def run():
    original,source=source_cohort()
    output={}
    for horizon in HORIZONS:
        values,qc=build_dataset(original,horizon)
        output[str(horizon)]={"horizon_seconds":horizon,
                              "quality":qc,
                              "bat_heldout":holdout(values)}
    return {
      "schema":1,"date":"2026-11-15",
      "status":"SOURCE_REAL_CAROLLIA_3D_GAZE_GEOMETRY_INCREMENTAL_HOLDOUT",
      "source_study_doi":"10.1007/s00359-026-01818-0",
      "source_upstream_commit":PIN,
      "source_original":source,
      "source_original_bat_species":"Carollia perspicillata",
      "source_matlab_v73_hdf5_read_with_numeric_outcomes":True,
      "source_rousettus_observations_used":False,
      "source_paper_gaze_turn_70pct_original_prior_art":True,
      "original_data_record_redistributed":False,
      "new_bat_measurements":False,
      "primary_horizon_seconds":.20,
      "secondary_horizon_seconds":[.10,.30],
      "original_beam_quality_min_fitR":BEAM_FIT_R_MIN,
      "ridge_nonintercept_regularization":LAMBDA_RIDGE,
      "source_geometry_only_seven_features":list(GEOM_FEATURES),
      "all_folds_independent_biological_bat_holdout":True,
      "per_trial_half_sequence_shift_control_prespecified":True,
      "results":output,
      "claim_limit":"Intra-source acoustic gaze incremental prediction over past 3D kinematics is not a causal bat navigation mechanism or a two-species independent reproduction. Original 2026 paper's anticipatory gaze result is prior art."
    }

def main():
    try:result=run()
    except Exception as e:
        result={"schema":1,"status":"STOP_AUTHOR_SOURCE_SCHEMA_OR_PREDICTION",
            "error":type(e).__name__+":"+str(e)[:240],
            "new_bat_measurements":False,
            "original_data_record_redistributed":False}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CAROLLIA_ORIGINAL_HOLDOUT_STATUS",result["status"])
    if result["status"].startswith("STOP"):
        print("STOP_REASON",result.get("error"))
        return 3
    print("ORIGINAL_SOURCE_SUPPORT",json.dumps(result["source_original"],sort_keys=True))
    for horizon,c in result["results"].items():
        print("SOURCE_HORIZON",horizon,"original_support",json.dumps(c["quality"],sort_keys=True))
        print("SOURCE_HOLDOUT",horizon,json.dumps(c["bat_heldout"],sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
