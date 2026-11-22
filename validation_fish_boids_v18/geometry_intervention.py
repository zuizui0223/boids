"""v18: original independent held-out synthetic 3-scale school geometry × sound cue.

Everything here is a model intervention, NOT a fish field result.
Frozen protocol: docs/V18_GEOMETRY_INTERVENTION_FREEZE.md.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np
import scipy
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v15.analysis import arrival_record

SEEDS=tuple(range(5000,5768))
N,SPLIT,PULSE_END,FINAL=32,1000,1040,4040
PRIMARY=(1040,4040)
LOW_CUTOFF=.90
SCALES={"compact":.65,"native":1.,"spread":1.35}
MOTORS={"on":5.,"off":0.}
HEARD_WEIGHT=3.
SEED_BOOT=2026112242
N_BOOT=10000
SIMULATOR_SHA256="a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb"
SOURCES=(
 "docs/V18_GEOMETRY_INTERVENTION_FREEZE.md",
 "validation_fish_boids_v15/simulation.py",
 "validation_fish_boids_v15/analysis.py",
 "validation_fish_boids_v18/geometry_intervention.py",
)
ARMS=tuple(
 (f"{geometry}_motor_on_{'pulse' if pulse else 'quiet'}",geometry,"on",pulse)
 for geometry in SCALES for pulse in (False,True)
)+tuple(
 (f"{geometry}_motor_off_{'pulse' if pulse else 'quiet'}",geometry,"off",pulse)
 for geometry in ("compact","spread") for pulse in (False,True)
)
assert len(ARMS)==10

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def original_sources():
    result={p:_sha(ROOT/p) for p in SOURCES}
    if result["validation_fish_boids_v15/simulation.py"]!=SIMULATOR_SHA256:
        raise RuntimeError("FROZEN_32_FISH_MODEL_CHANGED")
    return result

def _counts_fraction(x,length):
    a=np.asarray(x)
    if (a.shape!=(length,) or a.dtype!=np.float64
        or not np.isfinite(a).all() or (a<0).any() or (a>1).any()
        or not np.array_equal(a*N,np.rint(a*N))):
        raise ValueError("ORIGINAL_CALL_BINARY_GRID_STOP")
    return np.rint(a*N).astype(np.int64)

def scale_geometry(state,scale):
    """Act only on X coordinates; physical position/centroid unchanged in mean."""
    if scale not in SCALES.values():
        raise ValueError("UNFROZEN_POSITION_SCALE")
    src=sim._copy_state(state)
    center=src.pos.mean(axis=0)
    pos=src.pos.copy() if scale==1. else center+scale*(src.pos-center)
    result=sim.State(pos,src.velocity,src.calling,src.completed_steps,src.rng_state)
    if not np.allclose(result.pos.mean(axis=0),center,rtol=0,atol=1e-12):
        raise RuntimeError("CENTROID_DRIFT_ON_SCALE")
    if not np.array_equal(result.velocity,src.velocity) or not np.array_equal(result.calling,src.calling):
        raise RuntimeError("NON_POSITION_COMPONENT_MUTATED")
    if result.rng_state!=src.rng_state:raise RuntimeError("RNG_MUTATED_ON_POSITION_SCALE")
    dm=np.linalg.norm(src.pos[:,None]-src.pos[None,:],axis=-1)
    dp=np.linalg.norm(result.pos[:,None]-result.pos[None,:],axis=-1)
    if not np.allclose(dp,scale*dm,rtol=0,atol=1e-11):
        raise RuntimeError("PAIRWISE_DISTANCES_DID_NOT_SCALE")
    h0=float(ConvexHull(src.pos).volume);h1=float(ConvexHull(result.pos).volume)
    if not np.isclose(h1,scale*scale*h0,rtol=1e-10,atol=1e-9):
        raise RuntimeError("HULL_SCALING_FAILED")
    if scale==1. and not np.array_equal(result.pos,src.pos):
        raise RuntimeError("NATIVE_POSITION_NOT_IDENTICAL")
    return result

def pre_one(seed):
    state=sim.initialize(int(seed),n=N)
    pre=sim.advance(state,SPLIT)
    if pre["final_state"].completed_steps!=SPLIT:
        raise RuntimeError("BAD_SOURCE_CHECKPOINT_TIME")
    calls=_counts_fraction(pre["call_fraction"],SPLIT)
    q=float(calls[-1]/N)
    return int(seed),q,pre["call_fraction"],pre["final_state"] if q<LOW_CUTOFF else None

def perceived(state):
    dist=np.linalg.norm(state.pos[:,None,:]-state.pos[None,:,:],axis=2)
    h=np.exp(-dist/5.)*(~np.eye(N,dtype=bool))
    return float(((h@state.calling)/(N/4)).mean())

def average_pulse_delta(a,b):
    """Integer call-count differences to preserve exact zero."""
    ca=_counts_fraction(a,FINAL-SPLIT)
    cb=_counts_fraction(b,FINAL-SPLIT)
    numerator=int(ca[(PULSE_END-SPLIT):].sum()-cb[(PULSE_END-SPLIT):].sum())
    return numerator, numerator/(N*(FINAL-PULSE_END))

def one_eligible(item):
    seed,q,pre,state=item
    if q>=LOW_CUTOFF or state is None:
        raise RuntimeError("INVALID_ELIGIBLE_ITEM")
    if state.completed_steps!=SPLIT:raise RuntimeError("STATE_TIME_CHANGED")
    scaled={name:scale_geometry(state,s) for name,s in SCALES.items()}
    start_hull={name:float(ConvexHull(z.pos).volume) for name,z in scaled.items()}
    start_hear={name:perceived(z) for name,z in scaled.items()}
    if not start_hear["compact"]+1e-14>=start_hear["native"]>=start_hear["spread"]-1e-14:
        raise RuntimeError("MONOTONIC_ACOUSTIC_ATTENUATION_FAILED")
    traces={};hulls={};arrivals={};common_rng=None
    for name,g,m,pulse in ARMS:
        r=sim.advance(scaled[g],FINAL,pulse_start=SPLIT if pulse else None,
                      pulse_duration=PULSE_END-SPLIT,
                      audio_weight=MOTORS[m],heard_weight=HEARD_WEIGHT)
        if common_rng is None:common_rng=r["final_state"].rng_state
        elif r["final_state"].rng_state!=common_rng:raise RuntimeError("RANDOM_STREAMS_DIVERGED")
        traces[name]=_counts_fraction(r["call_fraction"],FINAL-SPLIT)/N
        hulls[name]=np.asarray(r["hull_area"],float)
        if not np.isfinite(hulls[name]).all() or (hulls[name]<=0).any():
            raise RuntimeError("NONFINITE_GEOMETRY_RESULT")
        expected=np.zeros(FINAL-SPLIT)
        if pulse:expected[:PULSE_END-SPLIT]=.8
        if not np.array_equal(r["cue"],expected):
            raise RuntimeError("CUE_TIMES_CHANGED")
        arrivals[name]=arrival_record(traces[name][PULSE_END-SPLIT:],
                 start_step=PULSE_END,window=200,threshold=.90,n=N)
    # Motor-off with the same geometry makes cue and no-cue movement identical.
    for g in ("compact","spread"):
        if not np.array_equal(hulls[f"{g}_motor_off_pulse"],hulls[f"{g}_motor_off_quiet"]):
            raise RuntimeError("MOTOR_OFF_GEOMETRY_STRUCTURAL_CONTROL_FAILED")
    gains={}
    for g in SCALES:
        _,gain=average_pulse_delta(traces[f"{g}_motor_on_pulse"],
                                   traces[f"{g}_motor_on_quiet"])
        gains[f"{g}_motor_on"]=gain
    for g in ("compact","spread"):
        _,gain=average_pulse_delta(traces[f"{g}_motor_off_pulse"],
                                   traces[f"{g}_motor_off_quiet"])
        gains[f"{g}_motor_off"]=gain
    # integer-count differences before conversion
    num=lambda name: int(_counts_fraction(traces[name],FINAL-SPLIT)[40:].sum())
    diff=(num("compact_motor_on_pulse")-num("compact_motor_on_quiet")
         -num("spread_motor_on_pulse")+num("spread_motor_on_quiet"))
    diff0=(num("compact_motor_off_pulse")-num("compact_motor_off_quiet")
         -num("spread_motor_off_pulse")+num("spread_motor_off_quiet"))
    den=N*(FINAL-PULSE_END)
    main=diff/den
    if not np.isclose(main,gains["compact_motor_on"]-gains["spread_motor_on"],rtol=0,atol=1e-15):
        raise RuntimeError("GEOMETRY_FACTORIAL_NUMERIC_MISMATCH")
    row={
        "seed":seed,"pre_cue_call_fraction":q,
        "pre_cue_mean_800_1000":float(np.mean(pre[800:1000])),
        **{f"source_hull_{k}":v for k,v in start_hull.items()},
        **{f"source_hearing_{k}":v for k,v in start_hear.items()},
        **{f"gain_{k}":v for k,v in gains.items()},
        "primary_compact_minus_spread":main,
        "motor0_geometry_cue_interaction":diff0/den,
        "three_way_motor5_minus_motor0":(diff-diff0)/den,
        "postcue_no_cue_call_compact":float(traces["compact_motor_on_quiet"][40:].mean()),
        "postcue_no_cue_call_spread":float(traces["spread_motor_on_quiet"][40:].mean()),
        "primary_area_contrast_compact":float(hulls["compact_motor_on_pulse"][40:].mean()-hulls["compact_motor_on_quiet"][40:].mean()),
        "primary_area_contrast_spread":float(hulls["spread_motor_on_pulse"][40:].mean()-hulls["spread_motor_on_quiet"][40:].mean()),
        "restricted_confirmation_diff_compact":int(arrivals["compact_motor_on_pulse"]["restricted_latency"]-arrivals["compact_motor_on_quiet"]["restricted_latency"]),
        "restricted_confirmation_diff_spread":int(arrivals["spread_motor_on_pulse"]["restricted_latency"]-arrivals["spread_motor_on_quiet"]["restricted_latency"]),
        "censored_compact_quiet":bool(arrivals["compact_motor_on_quiet"]["censored"]),
        "censored_compact_pulse":bool(arrivals["compact_motor_on_pulse"]["censored"]),
        "censored_spread_quiet":bool(arrivals["spread_motor_on_quiet"]["censored"]),
        "censored_spread_pulse":bool(arrivals["spread_motor_on_pulse"]["censored"]),
    }
    tr=np.stack([traces[name] for name,*_ in ARMS])
    ar=np.stack([hulls[name] for name,*_ in ARMS])
    return seed,row,tr,ar

def _bootstrap(a):
    a=np.asarray(a,float)
    if a.ndim!=1 or not np.isfinite(a).all() or len(a)<2:return None
    rng=np.random.default_rng(SEED_BOOT)
    draws=a[rng.integers(0,len(a),size=(N_BOOT,len(a)))].mean(axis=1)
    return np.quantile(draws,[.025,.975]).tolist()

def aggregate(census,rows):
    if sorted(census)!=list(SEEDS) or len(census)!=len(SEEDS):
        raise RuntimeError("INCOMPLETE_PRE_CUE_SEED_CENSUS")
    eligible=[s for s,q in sorted(census.items()) if q<LOW_CUTOFF]
    if eligible!=sorted(r["seed"] for r in rows):
        raise RuntimeError("INCOMPLETE_NEW_LOW_SEEDS")
    cols=("primary_compact_minus_spread","gain_compact_motor_on","gain_native_motor_on",
          "gain_spread_motor_on","gain_compact_motor_off","gain_spread_motor_off",
          "motor0_geometry_cue_interaction","three_way_motor5_minus_motor0",
          "primary_area_contrast_compact","primary_area_contrast_spread",
          "restricted_confirmation_diff_compact","restricted_confirmation_diff_spread")
    summaries={}
    for name in cols:
        values=np.array([r[name] for r in rows],float)
        summaries[name]={
            "n":len(values),"mean":float(np.mean(values)) if len(values) else None,
            "median":float(np.median(values)) if len(values) else None,
            "bootstrap_95":_bootstrap(values),
            "signs":{"positive":int((values>0).sum()),"negative":int((values<0).sum()),"zero":int((values==0).sum())}
        }
    primary=np.array([r["primary_compact_minus_spread"] for r in rows])
    positive=primary.clip(min=0)
    return {
        "status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "source_census_size":len(SEEDS),
        "eligible_pre_cue_low":len(eligible),
        "pre_cue_eligibility_fraction":len(eligible)/len(SEEDS),
        "eligible_ids":eligible,
        "pre_cue_q_by_seed":census,
        "arms":[name for name,*_ in ARMS],
        "positional_scales":SCALES,
        "endpoint_updates":list(PRIMARY),
        "primary_gate":"STOP_INSUFFICIENT_ELIGIBLE_SEEDS" if len(rows)<8 else "EVALUATED_INDEPENDENT_SAME_MODEL_HOLDOUT",
        "summary":summaries,
        "top3_positive_mass_share":float(np.sort(positive)[-3:].sum()/positive.sum()) if positive.sum()>0 else None,
        "bootstrap":{"method":"whole simulator seed, unadjusted percentile","seed":SEED_BOOT,"n":N_BOOT},
        "scientific_ceiling":"local geometry perturbation changes wall forcing and distances; only simulator parameter-intervention effect, not observed fish social communication"
    }

def _atomic(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as handle:
        tmp=Path(handle.name);handle.write(payload)
    tmp.replace(path)

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--workers",type=int,default=2)
    args=p.parse_args(argv)
    if not 1<=args.workers<=4:p.error("workers 1..4")
    hashes_before=original_sources()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        items=list(pool.map(pre_one,SEEDS,chunksize=3))
    if [i[0] for i in items]!=list(SEEDS):raise RuntimeError("SEED_ORDER_DRIFT")
    census={s:q for s,q,pre,state in items}
    eligible=[i for i in items if i[3] is not None]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        output=list(pool.map(one_eligible,eligible,chunksize=1))
    rows=sorted([x[1] for x in output],key=lambda r:r["seed"])
    result=aggregate(census,rows)
    if original_sources()!=hashes_before:raise RuntimeError("FROZEN_INPUT_CHANGED_DURING_EXECUTION")
    result["source_sha256"]=hashes_before
    result["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    archive=io.BytesIO()
    np.savez_compressed(archive,
       all_seeds=np.array(SEEDS,dtype=np.int32),
       all_prestim_call=np.array([census[s] for s in SEEDS]),
       eligible_seeds=np.array(result["eligible_ids"],dtype=np.int32),
       eligible_call_arms=np.stack([x[2] for x in output]) if output else np.empty((0,10,FINAL-SPLIT)),
       eligible_area_arms=np.stack([x[3] for x in output]) if output else np.empty((0,10,FINAL-SPLIT)))
    raw=archive.getvalue()
    result["raw_npz_sha256"]=hashlib.sha256(raw).hexdigest()
    result["raw_npz_bytes"]=len(raw)
    args.output.mkdir(parents=True,exist_ok=True)
    _atomic(args.output/"v18_traces.npz",raw)
    mem=io.StringIO(newline="")
    if rows:
        writer=csv.DictWriter(mem,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    csvtext=mem.getvalue().encode()
    result["per_seed_csv_sha256"]=hashlib.sha256(csvtext).hexdigest()
    _atomic(args.output/"per_seed.csv",csvtext)
    _atomic(args.output/"summary.json",(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n").encode())
    print(json.dumps({k:result[k] for k in ("status","source_census_size","eligible_pre_cue_low",
                 "primary_gate","summary","top3_positive_mass_share","raw_npz_sha256")},indent=2,allow_nan=False),flush=True)

if __name__=="__main__":main()
