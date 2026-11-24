"""v17 acoustic-feedback *motor* mechanism, independent simulator-seed experiment.

SYNTHETIC_ONLY_NOT_FIELD_RESULT. Frozen source and prereg in
docs/V17_ACOUSTIC_MOTOR_FEEDBACK_FREEZE.md. No biological inference.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import hashlib
import io
import json
import platform
from pathlib import Path
import sys
import tempfile

import numpy as np
import scipy
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v15.analysis import arrival_record

SEEDS=tuple(range(4000,4384))
N=32
SPLIT=1000
PULSE_END=1040
FINAL=4040
WINDOW=(1040,4040)
CUE_INTENSITY=.8
LOW_CUTOFF=.90
BOOTSTRAP_SEED=2026112231
BOOTSTRAP_REPS=10000
SOURCE_SIM_SHA="a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb"
SOURCE_FILES=(
 "docs/V17_ACOUSTIC_MOTOR_FEEDBACK_FREEZE.md",
 "validation_fish_boids_v15/simulation.py",
 "validation_fish_boids_v15/analysis.py",
 "validation_fish_boids_v17/motor_feedback.py",
)
ARM_SPECS=(
 ("motor5_hear3_none",5.,3.,False),
 ("motor5_hear3_pulse",5.,3.,True),
 ("motor0_hear3_none",0.,3.,False),
 ("motor0_hear3_pulse",0.,3.,True),
 ("motor5_hear0_none",5.,0.,False),
 ("motor5_hear0_pulse",5.,0.,True),
)

def _checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_hashes():
    found={path:_checksum(ROOT/path) for path in SOURCE_FILES}
    if found["validation_fish_boids_v15/simulation.py"]!=SOURCE_SIM_SHA:
        raise RuntimeError("FROZEN_SOURCE_MODEL_SHA_CHANGED")
    return found

def _counts(values,expected_length):
    arr=np.asarray(values)
    if (arr.shape!=(expected_length,) or arr.dtype!=np.float64 or
        not np.isfinite(arr).all() or (arr<0).any() or (arr>1).any() or
        not np.array_equal(arr*N,np.rint(arr*N))):
        raise ValueError("UNVERIFIED_BINARY_CALL_COUNTS")
    return np.rint(arr*N).astype(np.int64)

def fixed_window_call_delta(a,b):
    ca=_counts(a,FINAL-SPLIT)
    cb=_counts(b,FINAL-SPLIT)
    start,end=WINDOW[0]-SPLIT,WINDOW[1]-SPLIT
    numer=int(ca[start:end].sum()-cb[start:end].sum())
    return numer, numer/(N*(end-start))

def motor_interaction(arms):
    for name,_,_,_ in ARM_SPECS:
        if name not in arms:raise ValueError("MISSING_FROZEN_ARM")
    n5,e5=fixed_window_call_delta(arms["motor5_hear3_pulse"],arms["motor5_hear3_none"])
    n0,e0=fixed_window_call_delta(arms["motor0_hear3_pulse"],arms["motor0_hear3_none"])
    n00,e00=fixed_window_call_delta(arms["motor5_hear0_pulse"],arms["motor5_hear0_none"])
    if n00!=0:raise RuntimeError("HEARING_OFF_STRUCTURAL_NEGATIVE_CONTROL_FAILED")
    difference=n5-n0
    return {"motor5_hear3_pulse_delta":e5,
            "motor0_hear3_pulse_delta":e0,
            "motor5_hear0_pulse_delta":e00,
            "primary_motor_feedback_interaction":difference/(N*(WINDOW[1]-WINDOW[0])),
            "numerator_motor5":n5,"numerator_motor0":n0,
            "numerator_primary":difference}

def pre_one(seed):
    state=sim.initialize(int(seed),n=N)
    pre=sim.advance(state,SPLIT)
    if pre["final_state"].completed_steps != SPLIT:
        raise RuntimeError("INVALID_PRE_SPLIT")
    count=_counts(pre["call_fraction"],SPLIT)
    # Pre-cue eligibility depends only on the last observed natural state.
    q=float(count[-1]/N)
    chosen=q<LOW_CUTOFF
    checkpoint=pre["final_state"] if chosen else None
    return int(seed), q, float(np.mean(pre["call_fraction"][800:1000])), pre["call_fraction"],checkpoint

def _split_diagnostics(state):
    pos,vel,call=state.pos,state.velocity,state.calling
    dist=np.linalg.norm(pos[:,None,:]-pos[None,:,:],axis=2)
    audio=np.exp(-dist/5.)*(~np.eye(len(pos),dtype=bool))
    perceived=(audio@call)/(len(pos)/4.)
    return {"split_mean_perceived_call_input":float(perceived.mean()),
            "split_hull_area":float(ConvexHull(pos).volume),
            "split_mean_speed":float(np.linalg.norm(vel,axis=1).mean())}

def one_eligible(item):
    seed,q,premean,_,state=item
    if state is None or q>=LOW_CUTOFF:
        raise RuntimeError("INELIGIBLE_SEED_SCHEDULED")
    if state.completed_steps!=SPLIT:
        raise RuntimeError("WRONG_STATE_TIME")
    traces={};areas={};arrivals={}
    end_rng_state=None
    for name,motor,heard,pulse in ARM_SPECS:
        result=sim.advance(state,FINAL,pulse_start=SPLIT if pulse else None,
                           pulse_duration=PULSE_END-SPLIT,
                           audio_weight=motor,heard_weight=heard)
        if end_rng_state is None:
            end_rng_state=result["final_state"].rng_state
        elif result["final_state"].rng_state!=end_rng_state:
            raise RuntimeError("SAME_SEED_ARMS_HAVE_DIFFERENT_RNG_STREAMS")
        traces[name]=_counts(result["call_fraction"],FINAL-SPLIT)/N
        areas[name]=np.asarray(result["hull_area"],dtype=np.float64)
        if not np.isfinite(areas[name]).all() or (areas[name]<=0).any():
            raise RuntimeError("BAD_SCHOOL_AREA")
        cue=result["cue"]
        if not (np.all(cue[:40]==(.8 if pulse else 0.)) and np.all(cue[40:]==0.)):
            raise RuntimeError("INCORRECT_CUE_WINDOW")
        arrivals[name]=arrival_record(traces[name][40:],start_step=PULSE_END,
                                      threshold=.90,window=200,n=N)
    effects=motor_interaction(traces)
    def area_delta(prefix):
        return float(areas[prefix+"_pulse"][40:].mean()-areas[prefix+"_none"][40:].mean())
    response={
        "seed":seed,"prestate_call_fraction":q,"prestate_mean_800_1000":premean,
        **_split_diagnostics(state),**effects,
        "m5_no_cue_mean_calls":float(traces["motor5_hear3_none"][40:].mean()),
        "m0_no_cue_mean_calls":float(traces["motor0_hear3_none"][40:].mean()),
        "area_delta_motor5":area_delta("motor5_hear3"),
        "area_delta_motor0":area_delta("motor0_hear3"),
        "pulse_on_early_motor5_delta":float(
            traces["motor5_hear3_pulse"][:40].mean()-traces["motor5_hear3_none"][:40].mean()),
        "latency_difference_motor5":int(arrivals["motor5_hear3_pulse"]["restricted_latency"]
                                        -arrivals["motor5_hear3_none"]["restricted_latency"]),
        "latency_difference_motor0":int(arrivals["motor0_hear3_pulse"]["restricted_latency"]
                                        -arrivals["motor0_hear3_none"]["restricted_latency"]),
        "m5_control_censored":bool(arrivals["motor5_hear3_none"]["censored"]),
        "m5_pulse_censored":bool(arrivals["motor5_hear3_pulse"]["censored"]),
    }
    times=np.stack([traces[name] for name,*_ in ARM_SPECS],axis=0)
    hulls=np.stack([areas[name] for name,*_ in ARM_SPECS],axis=0)
    return seed,response,times,hulls

def _bootstrap(values):
    x=np.asarray(values,float)
    if x.ndim!=1 or not len(x) or not np.isfinite(x).all():
        raise ValueError("NO_VALID_SIMULATOR_SEEDS")
    if len(x)<2:
        return None
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    sel=rng.integers(0,len(x),size=(BOOTSTRAP_REPS,len(x)))
    return np.quantile(x[sel].mean(axis=1),[.025,.975]).tolist()

def summarize(census,records):
    if len(census)!=len(SEEDS) or sorted(census)!=list(SEEDS):
        raise RuntimeError("INCOMPLETE_SEED_CENSUS")
    low=[seed for seed,q in sorted(census.items()) if q<LOW_CUTOFF]
    if low != sorted(r["seed"] for r in records):
        raise RuntimeError("INCOMPLETE_ELIGIBLE_SEEDS")
    diag={}
    for key in ("primary_motor_feedback_interaction","motor5_hear3_pulse_delta",
                "motor0_hear3_pulse_delta","motor5_hear0_pulse_delta",
                "area_delta_motor5","area_delta_motor0",
                "pulse_on_early_motor5_delta","latency_difference_motor5",
                "latency_difference_motor0"):
        vals=np.array([row[key] for row in records],float)
        diag[key]={"n":len(vals),"mean":float(vals.mean()) if len(vals) else None,
                   "median":float(np.median(vals)) if len(vals) else None,
                   "bootstrap_95":_bootstrap(vals) if len(vals) else None,
                   "positive":int((vals>0).sum()),"negative":int((vals<0).sum()),
                   "zero":int((vals==0).sum())}
    return {
        "status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "original_model":"unchanged v15 32-agent acoustic boids",
        "protocol":"docs/V17_ACOUSTIC_MOTOR_FEEDBACK_FREEZE.md",
        "census_seed_bounds":[SEEDS[0],SEEDS[-1]],"n_census":len(SEEDS),
        "n_eligible_low_prestate":len(low),"pre_cue_low_eligibility_fraction":len(low)/len(SEEDS),
        "eligible_seed_ids":low,"seed_q_pre_cue":census,
        "primary_interpretation_gate":"SUPPORT_STOP_INSUFFICIENT_LOW_SEEDS" if len(low)<5 else "ELIGIBLE_FOR_DESCRIPTIVE_HOLDOUT",
        "primary":{"estimand":"(pulse - none)|motor5,heard3 minus (pulse - none)|motor0,heard3",
                    "window":[1040,4040],
                    **diag["primary_motor_feedback_interaction"]},
        "secondary":diag,
        "model_specific_negative_control":"post-pulse hearing=0 yields exact same call traces in cue and no-cue with shared RNG",
        "uncertainty_unit":"independent random seeds from same simulator",
        "bootstrap":{"n":BOOTSTRAP_REPS,"seed":BOOTSTRAP_SEED},
        "limitations":"not random fish experiment; not natural mediation; motor cutoff changes baseline geometry; possible near-ceiling calling",
    }

def _atomic(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        f.write(payload)
        tmp=Path(f.name)
    tmp.replace(path)

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--workers",type=int,default=2)
    a=p.parse_args(argv)
    if not 1<=a.workers<=4:
        p.error("workers 1..4 only")
    source_before=source_hashes()
    sources=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for item in pool.map(pre_one,SEEDS,chunksize=4):
            sources.append(item)
    if [item[0] for item in sources]!=list(SEEDS):
        raise RuntimeError("SEED_SCHEDULING_CHANGED")
    census={seed:q for seed,q,_,_,_ in sources}
    select=[item for item in sources if item[4] is not None]
    records=[];time_out={};area_out={}
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for seed,row,traces,areas in pool.map(one_eligible,select,chunksize=1):
            records.append(row);time_out[seed]=traces;area_out[seed]=areas
    records=sorted(records,key=lambda x:x["seed"])
    result=summarize(census,records)
    source_after=source_hashes()
    if source_before!=source_after:
        raise RuntimeError("SOURCE_CHANGED_DURING_EVALUATION")
    result["source_sha256"]=source_before
    result["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    output=a.output;output.mkdir(parents=True,exist_ok=True)
    archive=io.BytesIO()
    ordered=result["eligible_seed_ids"]
    np.savez_compressed(archive,
        census_seeds=np.array(SEEDS,dtype=np.int32),
        census_q=np.array([census[s] for s in SEEDS],dtype=np.float64),
        enrolled_seeds=np.array(ordered,dtype=np.int32),
        enrolled_pulse_traces=np.stack([time_out[s] for s in ordered]) if ordered else np.empty((0,len(ARM_SPECS),FINAL-SPLIT)),
        enrolled_hull_traces=np.stack([area_out[s] for s in ordered]) if ordered else np.empty((0,len(ARM_SPECS),FINAL-SPLIT)))
    raw=archive.getvalue()
    _atomic(output/"v17_traces.npz",raw)
    result["raw_npz_sha256"]=hashlib.sha256(raw).hexdigest()
    result["raw_npz_bytes"]=len(raw)
    rowsio=io.StringIO(newline="")
    if records:
        wr=csv.DictWriter(rowsio,fieldnames=list(records[0]))
        wr.writeheader();wr.writerows(records)
    _atomic(output/"eligible_per_seed.csv",rowsio.getvalue().encode())
    result["per_seed_csv_sha256"]=hashlib.sha256(rowsio.getvalue().encode()).hexdigest()
    _atomic(output/"summary.json",(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode())
    print(json.dumps({k:result[k] for k in ("status","n_census","n_eligible_low_prestate",
           "primary_interpretation_gate","primary","secondary","raw_npz_sha256")},
         ensure_ascii=False,indent=2),flush=True)

if __name__=="__main__":main()
