"""v19 new-seed crossed original school geometry × acoustic attenuation.

All results synthetic only. Physical initial scene (scale 0.65/1.35) is crossed
with acoustic distance attenuation (independent scale 0.65/1.35). The acoustic
scale controls BOTH audio-motor steering and hearing-induced calling, while
the physical positions control all Reynolds-like steering, walls and vectors.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,platform,sys,tempfile
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import scipy
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from validation_fish_boids_v15 import simulation as orig
from validation_fish_boids_v15.analysis import arrival_record
from validation_fish_boids_v19 import crossed_simulation as cross

SEEDS=tuple(range(6000,6768))
N=32
SOURCE_STOP=1000
CUE_END=1040
END=4040
SCALES={"compact":.65,"spread":1.35}
ARMS=tuple((x,y,cue) for x in SCALES for y in SCALES for cue in (False,True))
BOOT_SEED=2026112249
BOOT_REPS=10000
BASE_SIM_SHA="a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb"
FILES=("docs/V19_CROSSED_ACOUSTIC_MOTOR_GEOMETRY_FREEZE.md",
       "validation_fish_boids_v15/simulation.py",
       "validation_fish_boids_v19/crossed_simulation.py",
       "validation_fish_boids_v19/score_crossed.py")

def hash_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_hashes():
    a={p:hash_file(ROOT/p) for p in FILES}
    if a["validation_fish_boids_v15/simulation.py"]!=BASE_SIM_SHA:
        raise RuntimeError("V15_SIM_SOURCE_CHANGED")
    return a

def scene(state,physical_scale):
    if physical_scale not in SCALES.values():
        raise ValueError("UNFROZEN_PHYSICAL_SCALE")
    q=cross._copy_state(state)
    center=q.pos.mean(0)
    xyz=center+physical_scale*(q.pos-center)
    new=cross.State(xyz,q.velocity,q.calling,q.completed_steps,q.rng_state)
    if not np.allclose(xyz.mean(0),center,atol=1e-12,rtol=0):
        raise RuntimeError("CENTROID_CHANGED")
    if not np.array_equal(new.velocity,state.velocity) or not np.array_equal(new.calling,state.calling) or new.rng_state!=state.rng_state:
        raise RuntimeError("NON_POSITION_STATE_CHANGED")
    d=np.linalg.norm(state.pos[:,None,:]-state.pos[None,:,:],axis=2)
    nd=np.linalg.norm(new.pos[:,None,:]-new.pos[None,:,:],axis=2)
    if not np.allclose(nd,physical_scale*d,rtol=0,atol=1e-11):
        raise RuntimeError("DISTANCE_SCALE_FAILURE")
    return new

def acoustic_weights(state,mult):
    if state.pos.shape!=(N,2) or mult<=0:
        raise ValueError("BAD_SCENE_OR_KERNEL")
    d=np.linalg.norm(state.pos[:,None,:]-state.pos[None,:,:],axis=2)
    return np.exp(-(d*mult)/5.)*(~np.eye(N,dtype=bool))

def pre_one(seed):
    out=cross.advance(cross.initialize(seed,N),SOURCE_STOP)
    pre=out["call_fraction"]
    if not np.array_equal(pre*N,np.rint(pre*N)):
        raise RuntimeError("BAD_32_FISH_BINARY_SOURCE")
    q=float(pre[-1])
    return seed,q,out["final_state"] if q<.9 else None

def callcounts(a):
    x=np.asarray(a)
    if x.shape!=(END-SOURCE_STOP,) or x.dtype!=np.float64 or not np.isfinite(x).all() or (x<0).any() or (x>1).any() or not np.array_equal(x*N,np.rint(x*N)):
        raise RuntimeError("INVALID_CALL_FRACTIONS")
    return np.rint(x*N).astype(np.int64)
def gain(count_pulse,count_quiet):
    return int(count_pulse[CUE_END-SOURCE_STOP:].sum()-count_quiet[CUE_END-SOURCE_STOP:].sum())

def verify_original(state,result,pulse):
    oracle_state=orig.State(state.pos,state.velocity,state.calling,state.completed_steps,state.rng_state)
    oracle=orig.advance(oracle_state,END,pulse_start=SOURCE_STOP if pulse else None,pulse_duration=40)
    for field in ("call_fraction","hull_area","cue"):
        if not np.array_equal(oracle[field],result[field]):
            raise RuntimeError("ORIGINAL_V15_EXACT_DIAGONAL_REPLAY_FAILED_"+field)
    for field in ("pos","velocity","calling"):
        if not np.array_equal(getattr(oracle["final_state"],field),
                              getattr(result["final_state"],field)):
            raise RuntimeError("ORIGINAL_V15_FINAL_STATE_REPLAY_FAILED")
    if oracle["final_state"].rng_state!=result["final_state"].rng_state:
        raise RuntimeError("ORIGINAL_V15_RANDOM_STATE_REPLAY_FAILED")

def score_one(item):
    seed,q,state=item
    if state is None or q>=.9:
        raise RuntimeError("UNSUPPORTED_OR_UNENROLLED_SOURCE")
    actual={p:scene(state,s) for p,s in SCALES.items()}
    initial=np.linalg.norm(state.pos[:,None,:]-state.pos[None,:,:],axis=2)
    for p,sp in SCALES.items():
        for h,sh in SCALES.items():
            ratio=sh/sp
            if h==p:ratio=1.
            expected=np.exp(-(sh*initial)/5.)*(~np.eye(N,dtype=bool))
            if not np.allclose(acoustic_weights(actual[p],ratio),expected,rtol=0,atol=1e-13):
                raise RuntimeError("INITIAL_SENSORY_WEIGHT_CHANGED_WITH_PHYSICAL_SCALE")
    traces={};hulls={};arrivals={};first_rng=None
    for p,h,cue in ARMS:
        label=f"{p}_{h}_{'pulse' if cue else 'quiet'}"
        ratio=SCALES[h]/SCALES[p]
        if h==p:ratio=1.
        result=cross.advance(actual[p],END,pulse_start=SOURCE_STOP if cue else None,
                             pulse_duration=40,acoustic_ratio=ratio)
        if h==p:verify_original(actual[p],result,cue)
        end_state=result["final_state"].rng_state
        if first_rng is None:first_rng=end_state
        elif end_state!=first_rng:raise RuntimeError("PAIRED_RANDOM_STREAMS_NOT_IDENTICAL")
        counts=callcounts(result["call_fraction"])
        times=result["cue"]
        expected=np.zeros(END-SOURCE_STOP)
        if cue:expected[:40]=.8
        if not np.array_equal(times,expected):
            raise RuntimeError("INCORRECT_PULSE_TIMING")
        traces[label]=counts
        harea=np.asarray(result["hull_area"],dtype=np.float64)
        if not np.isfinite(harea).all() or (harea<=0).any():
            raise RuntimeError("BAD_ORIGINAL_HULL_AREA")
        hulls[label]=harea
        arrivals[label]=arrival_record(counts[40:]/N,start_step=CUE_END,window=200,threshold=.9,n=N)
    numer={}
    for p,h in ((p,h) for p in SCALES for h in SCALES):
        label=f"{p}_{h}"
        numer[label]=gain(traces[label+"_pulse"],traces[label+"_quiet"])
    cc=numer["compact_compact"]
    cs=numer["compact_spread"]
    sc=numer["spread_compact"]
    ss=numer["spread_spread"]
    denominator=N*(END-CUE_END)
    row={
        "seed":int(seed),"q_pre_cue":q,
        "main_physical_effect_same_compact_hearing":(cc-sc)/denominator,
        "physical_effect_same_spread_hearing":(cs-ss)/denominator,
        "auditory_effect_at_compact_physical":(cc-cs)/denominator,
        "auditory_effect_at_spread_physical":(sc-ss)/denominator,
        "physical_by_auditory_interaction":(cc-sc-cs+ss)/denominator,
        "source_hull_area":float(ConvexHull(state.pos).volume),
    }
    for p,h in ((p,h) for p in SCALES for h in SCALES):
        label=f"{p}_{h}"
        row[label+"_pulse_gain"]=numer[label]/denominator
        row[label+"_control_calls"]=float(traces[label+"_quiet"][40:].mean()/N)
        row[label+"_pulse_calls"]=float(traces[label+"_pulse"][40:].mean()/N)
        row[label+"_latency_difference"]=int(arrivals[label+"_pulse"]["restricted_latency"]-arrivals[label+"_quiet"]["restricted_latency"])
        row[label+"_control_censored"]=bool(arrivals[label+"_quiet"]["censored"])
        row[label+"_pulse_censored"]=bool(arrivals[label+"_pulse"]["censored"])
        row[label+"_control_hull_area"]=float(hulls[label+"_quiet"][40:].mean())
        row[label+"_pulse_hull_area"]=float(hulls[label+"_pulse"][40:].mean())
    return seed,row,np.stack([traces[f"{p}_{h}_{'pulse' if cue else 'quiet'}"]/N for p,h,cue in ARMS]),np.stack([hulls[f"{p}_{h}_{'pulse' if cue else 'quiet'}"] for p,h,cue in ARMS])

def bootstrap(values):
    values=np.asarray(values,float)
    if values.ndim!=1 or len(values)<2 or not np.isfinite(values).all():return None
    rng=np.random.default_rng(BOOT_SEED)
    samples=values[rng.integers(0,len(values),(BOOT_REPS,len(values)))].mean(axis=1)
    return np.quantile(samples,[.025,.975]).tolist()

def report(census,rows):
    if len(census)!=len(SEEDS) or sorted(census)!=list(SEEDS):
        raise RuntimeError("CENSUS_NOT_COMPLETE")
    eligible=[seed for seed,v in sorted(census.items()) if v<.9]
    if eligible!=sorted(row["seed"] for row in rows):
        raise RuntimeError("ELIGIBILITY_CHANGED_AFTER_OUTCOMES")
    fields=["main_physical_effect_same_compact_hearing","physical_effect_same_spread_hearing",
        "auditory_effect_at_compact_physical","auditory_effect_at_spread_physical",
        "physical_by_auditory_interaction"]+[
        f"{p}_{h}_{k}" for p in SCALES for h in SCALES for k in
        ("pulse_gain","control_calls","pulse_calls","latency_difference")
    ]
    summaries={}
    for name in fields:
        x=np.array([r[name] for r in rows],float)
        summaries[name]={"n":int(len(x)),
            "mean":float(x.mean()) if len(x) else None,
            "median":float(np.median(x)) if len(x) else None,
            "ci95":bootstrap(x),
            "positive":int((x>0).sum()),"negative":int((x<0).sum()),"zero":int((x==0).sum())}
    main=np.array([x[fields[0]] for x in rows])
    pos=main.clip(min=0)
    return {
        "status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "seed_census":[SEEDS[0],SEEDS[-1]],"n_census":len(SEEDS),"n_low_pre_cue":len(eligible),
        "eligible_seed_ids":eligible,"pre_cue_q_by_seed":census,
        "arms":[f"{p}_{h}_{'pulse' if cue else 'quiet'}" for p,h,cue in ARMS],
        "physical_scale":SCALES,"acoustic_initial_attenuation_scale":SCALES,
        "postpulse_window":[CUE_END,END],"source_diagonal_exact_replay":True,
        "support_gate":"LOW_ELIGIBLE_N_STOP" if len(eligible)<8 else "EVALUATED_INDEPENDENT_SYNTHETIC_HOLDOUT",
        "primary":summaries[fields[0]],"metrics":summaries,
        "top3_fraction_positive_primary":float(np.sort(pos)[-3:].sum()/pos.sum()) if pos.sum()>0 else None,
        "bootstrap":{"unit":"independent simulator seed","replicates":BOOT_REPS,"seed":BOOT_SEED},
        "interpretation_limit":"Acoustic scale changes motor and call hearing; physical state changes wall/separation/topology; sound weights matched only at initial checkpoint, not throughout divergent trajectories."
    }

def atomic(path,data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        tmp=Path(f.name);f.write(data)
    tmp.replace(path)

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--workers",type=int,default=2)
    args=parser.parse_args(argv)
    if not 1<=args.workers<=4:parser.error("workers must be 1..4")
    before=source_hashes()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pre=list(pool.map(pre_one,SEEDS,chunksize=3))
    if [s for s,*_ in pre]!=list(SEEDS):
        raise RuntimeError("ORIGINAL_CENSUS_SEED_ORDER_STOP")
    census={s:q for s,q,_ in pre}
    selected=[z for z in pre if z[2] is not None]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        all_results=list(pool.map(score_one,selected,chunksize=1))
    rows=sorted([x[1] for x in all_results],key=lambda x:x["seed"])
    obj=report(census,rows)
    if before!=source_hashes():raise RuntimeError("SOURCE_HASH_DRIFT")
    obj["source_sha256"]=before
    obj["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    outputs={x[0]:x for x in all_results}
    bio=io.BytesIO()
    ordered=obj["eligible_seed_ids"]
    np.savez_compressed(bio,all_seeds=np.array(SEEDS,dtype=np.int32),
        all_source_q=np.array([census[s] for s in SEEDS]),
        low_seeds=np.array(ordered,dtype=np.int32),
        low_call_traces=np.stack([outputs[s][2] for s in ordered]) if ordered else np.empty((0,8,3040)),
        low_area_traces=np.stack([outputs[s][3] for s in ordered]) if ordered else np.empty((0,8,3040)))
    data=bio.getvalue()
    obj["npz_sha256"]=hashlib.sha256(data).hexdigest()
    obj["npz_bytes"]=len(data)
    args.output.mkdir(parents=True,exist_ok=True)
    atomic(args.output/"crossed_traces.npz",data)
    buff=io.StringIO(newline="")
    if rows:
        writer=csv.DictWriter(buff,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    cs=buff.getvalue().encode()
    atomic(args.output/"per_seed.csv",cs)
    obj["csv_sha256"]=hashlib.sha256(cs).hexdigest()
    atomic(args.output/"summary.json",(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n").encode())
    print(json.dumps({k:obj[k] for k in ("status","n_census","n_low_pre_cue","support_gate","primary","metrics","top3_fraction_positive_primary","npz_sha256")},indent=2,allow_nan=False),flush=True)

if __name__=="__main__":main()
