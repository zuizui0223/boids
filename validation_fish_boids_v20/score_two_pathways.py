"""v20 original source-locked 2-pathway crossed acoustic Boids experiment.

Synthetic simulator only: no observed fish calls or school motor causality.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,platform,sys,tempfile
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import scipy
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from validation_fish_boids_v15 import simulation as v15
from validation_fish_boids_v15.analysis import arrival_record
from validation_fish_boids_v19 import crossed_simulation as v19
from validation_fish_boids_v20 import two_pathway_simulation as v20

SEEDS=tuple(range(7000,7768))
N=32; START=1000; PULSE_END=1040; FINISH=4040
RANGE={"long":.65,"short":1.35}
PHYS={"compact":.65,"spread":1.35}
ARMS=tuple((p,m,c,cue) for p in PHYS for m in RANGE for c in RANGE for cue in (False,True))
BOOT_SEED=2026112260; BOOT_N=10000
FROZEN_ORIGINAL_SHA="a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb"
SOURCE_FILES=(
 "docs/V20_TWO_PATHWAY_ACOUSTIC_FEEDBACK_FREEZE.md",
 "validation_fish_boids_v15/simulation.py",
 "validation_fish_boids_v19/crossed_simulation.py",
 "validation_fish_boids_v15/analysis.py",
 "validation_fish_boids_v20/two_pathway_simulation.py",
 "validation_fish_boids_v20/score_two_pathways.py"
)

def hash_path(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_gate():
    r={p:hash_path(ROOT/p) for p in SOURCE_FILES}
    if r["validation_fish_boids_v15/simulation.py"]!=FROZEN_ORIGINAL_SHA:
        raise RuntimeError("ORIGINAL_V15_SIMULATOR_SOURCE_CHANGED")
    return r

def physical_scene(state,ratio):
    if ratio not in PHYS.values():raise ValueError("UNFROZEN_PHYSICAL_GEOMETRY")
    v=v20._copy_state(state)
    center=v.pos.mean(axis=0)
    pos=center+ratio*(v.pos-center)
    z=v20.State(pos,v.velocity,v.calling,v.completed_steps,v.rng_state)
    if not np.allclose(z.pos.mean(0),center,atol=1e-12,rtol=0):
        raise RuntimeError("PHYSICAL_SOURCE_CENTROID_CHANGED")
    if not np.array_equal(z.velocity,state.velocity) or not np.array_equal(z.calling,state.calling) or z.rng_state!=state.rng_state:
        raise RuntimeError("SCALED_SCENE_MUTATED_NON_POSITION_DATA")
    d=np.linalg.norm(v.pos[:,None]-v.pos[None,:],axis=2)
    d2=np.linalg.norm(z.pos[:,None]-z.pos[None,:],axis=2)
    if not np.allclose(d2,ratio*d,atol=1e-11,rtol=0):
        raise RuntimeError("PHYSICAL_PAIRWISE_DISTANCE_SCALE_STOP")
    return z

def acoustic_kernel(state,ratio):
    d=np.linalg.norm(state.pos[:,None]-state.pos[None,:],axis=2)
    return np.exp(-(ratio*d)/5.)*(~np.eye(N,dtype=bool))

def pre_one(seed):
    orig=v15.advance(v15.initialize(int(seed),n=N),START)
    q=float(orig["call_fraction"][-1])
    if not np.array_equal(orig["call_fraction"]*N,np.rint(orig["call_fraction"]*N)):
        raise RuntimeError("SOURCE_NOT_BINARY_32_AGENT_CALL_GRID")
    return int(seed),q,orig["final_state"] if q<.90 else None

def _assert_source_equal(a,b,kind):
    for field in ("call_fraction","hull_area","cue"):
        if not np.array_equal(a[field],b[field]):
            raise RuntimeError("EXACT_FROZEN_SOURCE_REPLAY_"+kind+"_"+field)
    for f in ("pos","velocity","calling"):
        if not np.array_equal(getattr(a["final_state"],f),getattr(b["final_state"],f)):
            raise RuntimeError("EXACT_FROZEN_FINAL_STATE_"+kind+"_"+f)
    if a["final_state"].rng_state!=b["final_state"].rng_state:
        raise RuntimeError("EXACT_FROZEN_RNG_REPLAY_"+kind)

def call_counts(a):
    x=np.asarray(a)
    if (x.shape!=(FINISH-START,) or x.dtype!=np.float64 or
        not np.isfinite(x).all() or (x<0).any() or (x>1).any()
        or not np.array_equal(x*N,np.rint(x*N))):
        raise RuntimeError("INVALID_SOURCE_CALL_COUNTS")
    return np.rint(x*N).astype(np.int64)

def decompose_cell(numerators,p):
    # All contrasts exact integer numerators; first index motor, second vocal.
    ll=numerators[p+"_long_long"]
    ls=numerators[p+"_long_short"]
    sl=numerators[p+"_short_long"]
    ss=numerators[p+"_short_short"]
    D=N*(FINISH-PULSE_END)
    result={
      "motor_given_vocal_long":(ll-sl)/D,
      "motor_given_vocal_short":(ls-ss)/D,
      "vocal_given_motor_long":(ll-ls)/D,
      "vocal_given_motor_short":(sl-ss)/D,
      "pathway_interaction":(ll-ls-sl+ss)/D,
      "both_long_minus_both_short":(ll-ss)/D,
      "shapley_motor":(ll-sl+ls-ss)/(2*D),
      "shapley_vocal":(ll-ls+sl-ss)/(2*D),
    }
    if not np.isclose(result["shapley_motor"]+result["shapley_vocal"],
                      result["both_long_minus_both_short"],rtol=0,atol=1e-15):
        raise RuntimeError("TWO_PATH_SHAPLEY_CLOSURE_FAILED")
    return result

def one_eligible(item):
    seed,q,state=item
    if state is None or q>=.9 or state.completed_steps!=START:
        raise RuntimeError("NEW_SOURCE_ELIGIBILITY_OR_TIME_CHANGED")
    physical={p:physical_scene(state,x) for p,x in PHYS.items()}
    orig_d=np.linalg.norm(state.pos[:,None]-state.pos[None,:],axis=2)
    for p,scale in PHYS.items():
        for h,hs in RANGE.items():
            want=np.exp(-(hs*orig_d)/5.)*(~np.eye(N,dtype=bool))
            got=acoustic_kernel(physical[p],hs/scale if hs!=scale else 1.)
            if not np.allclose(got,want,atol=1e-13,rtol=0):
                raise RuntimeError("INITIAL_SPLIT_PATH_HEARING_KERNEL_MISMATCH")
    trace={};area={};arrivals={};rng_ref=None
    for p,m,c,play in ARMS:
        label=f"{p}_{m}_{c}_{'pulse' if play else 'quiet'}"
        motor_ratio=RANGE[m]/PHYS[p] if RANGE[m]!=PHYS[p] else 1.
        vocal_ratio=RANGE[c]/PHYS[p] if RANGE[c]!=PHYS[p] else 1.
        v=v20.advance(physical[p],FINISH,pulse_start=START if play else None,
                     pulse_duration=40,motor_acoustic_ratio=motor_ratio,
                     calling_acoustic_ratio=vocal_ratio)
        if rng_ref is None:rng_ref=v["final_state"].rng_state
        elif v["final_state"].rng_state!=rng_ref:
            raise RuntimeError("SAME_RANDOM_STREAM_DID_NOT_SURVIVE_16_ARMS")
        if m==c:
            old=v19.State(physical[p].pos,physical[p].velocity,physical[p].calling,START,physical[p].rng_state)
            vv=v19.advance(old,FINISH,pulse_start=START if play else None,
                           pulse_duration=40,acoustic_ratio=motor_ratio)
            _assert_source_equal(v,vv,"V19_"+label)
            if RANGE[m]==PHYS[p]:
                orig=v15.State(physical[p].pos,physical[p].velocity,physical[p].calling,START,physical[p].rng_state)
                oo=v15.advance(orig,FINISH,pulse_start=START if play else None,pulse_duration=40)
                _assert_source_equal(v,oo,"V15_"+label)
        cue_target=np.zeros(FINISH-START)
        if play:cue_target[:40]=.8
        if not np.array_equal(v["cue"],cue_target):
            raise RuntimeError("CUE_SCHEDULE_CHANGED")
        counts=call_counts(v["call_fraction"])
        trace[label]=counts
        hull=np.asarray(v["hull_area"],dtype=np.float64)
        if hull.shape!=(FINISH-START,) or (hull<=0).any() or not np.isfinite(hull).all():
            raise RuntimeError("HULL_AREA_BAD")
        area[label]=hull
        arrivals[label]=arrival_record(counts[40:]/N,start_step=PULSE_END,window=200,threshold=.90,n=N)
    D=N*(FINISH-PULSE_END)
    numerator={}
    row={"seed":seed,"pre_q":q,"source_hull":float(ConvexHull(state.pos).volume),
         "source_mean_speed":float(np.linalg.norm(state.velocity,axis=1).mean())}
    for p in PHYS:
        for m in RANGE:
            for c in RANGE:
                label=f"{p}_{m}_{c}"
                quiet=label+"_quiet";play=label+"_pulse"
                num=int(trace[play][40:].sum()-trace[quiet][40:].sum())
                numerator[label]=num
                row[label+"_cue_gain"]=num/D
                row[label+"_quiet_level"]=float(trace[quiet][40:].mean()/N)
                row[label+"_cue_level"]=float(trace[play][40:].mean()/N)
                row[label+"_quiet_hull"]=float(area[quiet][40:].mean())
                row[label+"_cue_hull"]=float(area[play][40:].mean())
                row[label+"_latency_delta"]=int(arrivals[play]["restricted_latency"]-arrivals[quiet]["restricted_latency"])
                row[label+"_quiet_censored"]=bool(arrivals[quiet]["censored"])
                row[label+"_cue_censored"]=bool(arrivals[play]["censored"])
        for k,z in decompose_cell(numerator,p).items():
            row[p+"_"+k]=z
    row["physical_compact_minus_spread_given_both_long"]=(
       numerator["compact_long_long"]-numerator["spread_long_long"])/D
    output_calls=np.stack([trace[f"{p}_{m}_{c}_{'pulse' if play else 'quiet'}"]/N for p,m,c,play in ARMS],axis=0)
    output_hulls=np.stack([area[f"{p}_{m}_{c}_{'pulse' if play else 'quiet'}"] for p,m,c,play in ARMS],axis=0)
    return seed,row,output_calls,output_hulls

def boot(values):
    a=np.asarray(values,dtype=float)
    if a.ndim!=1 or len(a)<2 or not np.isfinite(a).all():return None
    rng=np.random.default_rng(BOOT_SEED)
    rep=a[rng.integers(0,len(a),size=(BOOT_N,len(a)))].mean(axis=1)
    return np.quantile(rep,[.025,.975]).tolist()

def summarize(census,records):
    if len(census)!=len(SEEDS) or sorted(census)!=list(SEEDS):
        raise RuntimeError("FROZEN_SOURCE_CENSUS_NOT_COMPLETE")
    eligible=[s for s,q in sorted(census.items()) if q<.9]
    if eligible!=sorted(row["seed"] for row in records):
        raise RuntimeError("POST_OUTCOME_SOURCE_SELECTION_INVALID")
    keys=[p+"_"+k for p in PHYS for k in
      ("motor_given_vocal_long","motor_given_vocal_short",
      "vocal_given_motor_long","vocal_given_motor_short",
      "pathway_interaction","both_long_minus_both_short",
      "shapley_motor","shapley_vocal")]
    keys += [f"{p}_{m}_{c}_cue_gain" for p in PHYS for m in RANGE for c in RANGE]
    keys += [f"{p}_{m}_{c}_{metric}" for p in PHYS for m in RANGE for c in RANGE
             for metric in ("quiet_level","cue_level","quiet_hull","cue_hull","latency_delta")]
    keys+=["physical_compact_minus_spread_given_both_long"]
    stats={}
    for key in keys:
        v=np.array([r[key] for r in records],dtype=float)
        stats[key]={"n":len(v),"mean":float(v.mean()) if len(v) else None,
            "median":float(np.median(v)) if len(v) else None,
            "ci95":boot(v),"positive":int((v>0).sum()),"negative":int((v<0).sum()),
            "zero":int((v==0).sum())}
    main=stats["compact_motor_given_vocal_long"]
    z=np.array([r["compact_motor_given_vocal_long"] for r in records],dtype=float)
    positive=z.clip(min=0)
    return {
        "status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "original_new_census_bounds":[SEEDS[0],SEEDS[-1]],
        "n_source_seeds":len(SEEDS),"n_eligible_pre_cue_low":len(eligible),
        "source_pre_cue_q":census,"eligible_seed_ids":eligible,
        "arms":[f"{p}_{m}_{c}_{'pulse' if cue else 'quiet'}" for p,m,c,cue in ARMS],
        "physical":PHYS,"motor_attenuation":RANGE,"vocal_attenuation":RANGE,
        "primary_window":[PULSE_END,FINISH],
        "support_gate":"INSUFFICIENT_LOW_SEEDS" if len(eligible)<8 else "INDEPENDENT_SYNTHETIC_SEED_HOLDOUT_COMPLETED",
        "primary":main,"contrasts":stats,
        "top3_positive_mass_share":float(np.sort(positive)[-3:].sum()/positive.sum()) if positive.sum()>0 else None,
        "bootstrap":{"n":BOOT_N,"rng":BOOT_SEED,"unit":"independent simulator seed"},
        "v19_source_replayed_for_all_equal_pathway_arms":True,
        "v15_source_replayed_for_all_native_arms":True,
        "scope":"Artificial generator parameter interventions, NOT natural mediation or observed fish audio/motor feedback."
    }

def atomic(path,content):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        tmp=Path(f.name);f.write(content)
    tmp.replace(path)

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--workers",type=int,default=2)
    args=ap.parse_args(argv)
    if not 1<=args.workers<=4:ap.error("workers 1..4 only")
    before=source_gate()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        starters=list(pool.map(pre_one,SEEDS,chunksize=3))
    if [x[0] for x in starters]!=list(SEEDS):
        raise RuntimeError("CENSUS_SEED_ORDER_CHANGED")
    census={s:q for s,q,_ in starters}
    eligible=[x for x in starters if x[2] is not None]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        scored=list(pool.map(one_eligible,eligible,chunksize=1))
    rows=sorted([x[1] for x in scored],key=lambda x:x["seed"])
    report=summarize(census,rows)
    if source_gate()!=before:raise RuntimeError("SOURCE_CHANGED_DURING_HOLDOUT_RUN")
    report["source_sha256"]=before
    report["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    byseed={x[0]:x for x in scored}
    ordered=report["eligible_seed_ids"]
    bio=io.BytesIO()
    np.savez_compressed(bio,
        all_seeds=np.asarray(SEEDS,dtype=np.int32),
        all_pre_q=np.asarray([census[s] for s in SEEDS],dtype=np.float64),
        eligible_seeds=np.asarray(ordered,dtype=np.int32),
        eligible_calls=np.stack([byseed[s][2] for s in ordered]) if ordered else np.empty((0,len(ARMS),FINISH-START)),
        eligible_hulls=np.stack([byseed[s][3] for s in ordered]) if ordered else np.empty((0,len(ARMS),FINISH-START)))
    raw=bio.getvalue()
    report["npz_sha256"]=hashlib.sha256(raw).hexdigest()
    report["npz_bytes"]=len(raw)
    args.output.mkdir(parents=True,exist_ok=True)
    atomic(args.output/"v20_raw_traces.npz",raw)
    f=io.StringIO(newline="")
    if rows:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    rawcsv=f.getvalue().encode()
    atomic(args.output/"per_seed.csv",rawcsv)
    report["csv_sha256"]=hashlib.sha256(rawcsv).hexdigest()
    atomic(args.output/"summary.json",(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n").encode())
    print(json.dumps({k:report[k] for k in ("status","n_source_seeds","n_eligible_pre_cue_low","support_gate","primary","contrasts","top3_positive_mass_share","npz_sha256")},allow_nan=False,indent=2),flush=True)

if __name__=="__main__":main()
