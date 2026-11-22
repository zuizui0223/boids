"""v16 independently seeded synthetic pulse susceptibility audit.

This is a simulator-only, preregistered holdout. v15 is discovery only.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v15.analysis import arrival_record

SEEDS = tuple(range(3000, 3192))
N, CUE_START, CUE_END, HORIZON = 32, 1000, 1040, 6000
PRIMARY = (1040, 4040)
SOURCE_SHA256 = "a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb"
SOURCE_PATHS = (
    "docs/V16_PRESTATE_SUSCEPTIBILITY_FREEZE.md",
    "validation_fish_boids_v15/simulation.py",
    "validation_fish_boids_v15/analysis.py",
    "validation_fish_boids_v16/run_holdout.py",
)
RNG_BOOTSTRAP = 2026112220
BOOTSTRAP_REPS = 10000


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _sources():
    sources = {p: _sha(ROOT / p) for p in SOURCE_PATHS}
    if sources["validation_fish_boids_v15/simulation.py"] != SOURCE_SHA256:
        raise RuntimeError("FROZEN_SIMULATOR_SOURCE_CHANGED")
    return sources


def _valid_trace(trace, length):
    arr = np.asarray(trace)
    if (arr.shape != (length,) or arr.dtype != np.float64 or
            not np.isfinite(arr).all() or (arr < 0).any() or (arr > 1).any() or
            not np.array_equal(arr * N, np.rint(arr * N))):
        raise RuntimeError("INVALID_CALL_TRACE")
    return arr


def main_contrast(pulse, control, start=1040, end=4040):
    """Input arms are global update indices [1000,6000)."""
    if not (CUE_END <= start < end <= HORIZON):
        raise ValueError("main window is outside post-cue samples")
    p = _valid_trace(pulse, HORIZON-CUE_START)
    c = _valid_trace(control, HORIZON-CUE_START)
    i, j = start-CUE_START, end-CUE_START
    # Individual call totals are integral; subtract before conversion to fraction.
    return int(np.rint(p[i:j]*N).astype(np.int64).sum() -
               np.rint(c[i:j]*N).astype(np.int64).sum()) / (N*(end-start))


def run_one(seed):
    state = sim.initialize(int(seed), n=N)
    pre = sim.advance(state, CUE_START, pulse_start=None)
    pre_trace = _valid_trace(pre["call_fraction"], CUE_START)
    split = pre["final_state"]
    if split.completed_steps != CUE_START:
        raise RuntimeError("BAD_SPLIT_STEP")
    control = sim.advance(split, HORIZON, pulse_start=None)
    pulse = sim.advance(split, HORIZON, pulse_start=CUE_START, pulse_duration=40)
    if control["final_state"].rng_state != pulse["final_state"].rng_state:
        raise RuntimeError("PAIR_RNG_MISMATCH")
    ctrl = _valid_trace(control["call_fraction"], HORIZON-CUE_START)
    play = _valid_trace(pulse["call_fraction"], HORIZON-CUE_START)
    if not np.all(control["cue"] == 0.):
        raise RuntimeError("NONZERO_CONTROL_CUE")
    if not (np.all(pulse["cue"][:40] == .8) and np.all(pulse["cue"][40:] == 0.)):
        raise RuntimeError("PULSE_TIMING_ERROR")
    if not np.isin(pre["snapshot_calling"], [0., 1.]).all():
        raise RuntimeError("BAD_CALL_SNAPSHOT")
    return int(seed), pre_trace, ctrl, play


def bootstrap_group_difference(a, b, reps=BOOTSTRAP_REPS, seed=RNG_BOOTSTRAP):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("strata must be finite one-dimensional vectors")
    if not len(a) or not len(b):
        return None, None
    point = float(a.mean()-b.mean())
    if len(a) < 2 or len(b) < 2:
        return point, None
    rng = np.random.default_rng(seed)
    av = a[rng.integers(0, len(a), (reps, len(a)))].mean(axis=1)
    bv = b[rng.integers(0, len(b), (reps, len(b)))].mean(axis=1)
    return point, np.quantile(av-bv, [.025, .975]).tolist()


def _ratio(num, denom):
    v = float(denom)
    return float(num/v) if v > 0 else None


def calculate(data):
    seeds, pre, control, pulse = data
    if (seeds.shape != (len(SEEDS),) or not np.array_equal(seeds, np.array(SEEDS))
            or pre.shape != (len(SEEDS),1000)
            or control.shape != (len(SEEDS),5000)
            or pulse.shape != (len(SEEDS),5000)):
        raise RuntimeError("INCOMPLETE_HOLDOUT_OR_MALFORMED_ARRAYS")
    if not np.isfinite(pre).all() or not np.isfinite(control).all() or not np.isfinite(pulse).all():
        raise RuntimeError("NONFINITE_HOLDOUT")
    # Only last completed PRE-cue state controls enrollment.
    q = pre[:, -1]
    risk = q < .90
    effect = np.array([main_contrast(pulse[i],control[i]) for i in range(len(seeds))])
    immediate = np.array([main_contrast(pulse[i],control[i],1040,1240) for i in range(len(seeds))])
    late = np.array([main_contrast(pulse[i],control[i],5000,6000) for i in range(len(seeds))])
    control_mean = control[:, 40:3040].mean(axis=1)
    pulse_mean = pulse[:, 40:3040].mean(axis=1)
    if not np.allclose(pulse_mean-control_mean, effect, atol=1e-15, rtol=0):
        raise RuntimeError("INTEGER_CONTRAST_MISMATCH")
    headroom = 1 - control_mean
    if (headroom < 0).any():
        raise RuntimeError("HEADROOM_OUT_OF_RANGE")
    main, ci = bootstrap_group_difference(effect[risk], effect[~risk])
    positive_total = effect.clip(min=0).sum()
    rows = []
    for i,seed in enumerate(seeds):
        c = arrival_record(control[i,40:], start_step=1040, threshold=.9, window=200,n=N)
        p = arrival_record(pulse[i,40:], start_step=1040, threshold=.9, window=200,n=N)
        rows.append({
            "seed": int(seed),
            "q_pre_t1000": float(q[i]),
            "mean_pre_800_1000": float(pre[i,800:1000].mean()),
            "risk_by_frozen_rule": bool(risk[i]),
            "mean_control_primary": float(control_mean[i]),
            "mean_pulse_primary": float(pulse_mean[i]),
            "headroom_control": float(headroom[i]),
            "delta_primary": float(effect[i]),
            "delta_immediate": float(immediate[i]),
            "delta_late": float(late[i]),
            "control_event": bool(c["event_observed"]),
            "pulse_event": bool(p["event_observed"]),
            "control_confirmation": c["confirmation_step"],
            "pulse_confirmation": p["confirmation_step"],
            "control_censored": bool(c["censored"]),
            "pulse_censored": bool(p["censored"]),
            "restricted_latency_delta": int(p["restricted_latency"]-c["restricted_latency"]),
        })
    def describe(mask):
        e=effect[mask]
        h=headroom[mask]
        return {
            "n":int(mask.sum()),
            "mean_delta_primary":float(e.mean()) if len(e) else None,
            "median_delta_primary":float(np.median(e)) if len(e) else None,
            "mean_control_primary":float(control_mean[mask].mean()) if len(e) else None,
            "mean_pulse_primary":float(pulse_mean[mask].mean()) if len(e) else None,
            "sign_counts":{"positive":int((e>0).sum()),"negative":int((e<0).sum()),"zero":int((e==0).sum())},
            "responder_count_delta_gt_0p005":int((e>.005).sum()),
            "headroom_total":float(h.sum()),
            "mean_fraction_of_available_headroom_used":_ratio(e.sum(),h.sum()),
            "mean_delta_immediate":float(immediate[mask].mean()) if len(e) else None,
            "mean_delta_late":float(late[mask].mean()) if len(e) else None,
            "mean_restricted_latency_delta":float(np.mean([rows[i]["restricted_latency_delta"] for i in range(len(seeds)) if mask[i]])) if len(e) else None,
            "control_censored":int(sum(rows[i]["control_censored"] for i in range(len(seeds)) if mask[i])),
            "pulse_censored":int(sum(rows[i]["pulse_censored"] for i in range(len(seeds)) if mask[i])),
        }
    return rows, {
        "status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "model":"identical to frozen v15 synthetic simulator",
        "discovery_seeds":"2000..2095, excluded from confirmation",
        "holdout_seeds":[int(seeds[0]),int(seeds[-1])],
        "n":len(seeds),
        "risk_cutoff_on_pre_cue_single_step":.90,
        "primary_window_global_updates":[1040,4040],
        "primary_risk_minus_high":main,
        "primary_bootstrap_95":ci,
        "primary_interpretation_status":(
            "INCONCLUSIVE_RISK_STRATUM_TOO_SMALL" if risk.sum()<2 or (~risk).sum()<2
            else ("DIRECTION_SUPPORTED_DESCRIPTIVELY" if ci and ci[0]>0 else "NOT_DIRECTIONALLY_RESOLVED")
        ),
        "cohorts":{"risk":describe(risk),"already_high":describe(~risk),"all":describe(np.ones(len(seeds),dtype=bool))},
        "positive_effect_mass_share_in_risk":_ratio(effect[risk].clip(min=0).sum(),positive_total),
        "largest_primary_positive_seeds":[int(seeds[i]) for i in np.argsort(-effect)[:5]],
        "bootstrap":{"replicates":BOOTSTRAP_REPS,"seed":RNG_BOOTSTRAP,"unit":"independent synthetic seed; stratified retrospective resampling within frozen pre-cue groups"},
        "claim_limit":"Replicates only within one artificial model; 0..1 measurement ceiling and timing confound interpretation."
    }


def _atomic_bytes(path, payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temp=Path(f.name)
        f.write(payload)
    temp.replace(path)


def save_records(path, rows):
    import io
    buffer=io.StringIO(newline="")
    writer=csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    _atomic_bytes(path,buffer.getvalue().encode("utf-8"))


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--workers",type=int,default=2)
    args=parser.parse_args(argv)
    if not 1<=args.workers<=4:
        parser.error("workers must be 1..4")
    sha_before=_sources()
    arrays={name:np.empty(shape,dtype=np.float64) for name,shape in {
        "pre_call_fraction":(len(SEEDS),1000),
        "control_call_fraction":(len(SEEDS),5000),
        "pulse_call_fraction":(len(SEEDS),5000)
    }.items()}
    seen=set()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run_one, seed):seed for seed in SEEDS}
        for future in as_completed(futures):
            seed,pre,c,p=future.result()
            if seed in seen or seed not in SEEDS:
                raise RuntimeError("UNEXPECTED_OR_DUPLICATE_SEED")
            seen.add(seed)
            i=seed-SEEDS[0]
            arrays["pre_call_fraction"][i]=pre
            arrays["control_call_fraction"][i]=c
            arrays["pulse_call_fraction"][i]=p
            if len(seen)%16==0:
                print("completed %d/%d prespecified holdout seeds" % (len(seen),len(SEEDS)),flush=True)
    if seen != set(SEEDS):
        raise RuntimeError("MISSING_HOLDOUT_SEED")
    data=(np.array(SEEDS),arrays["pre_call_fraction"],arrays["control_call_fraction"],arrays["pulse_call_fraction"])
    rows,report=calculate(data)
    sha_after=_sources()
    if sha_after!=sha_before:
        raise RuntimeError("SOURCE_CHANGED_DURING_HOLDOUT")
    args.output.mkdir(parents=True,exist_ok=True)
    # Save in a single deterministic numpy archive, then hash exactly its bytes.
    import io
    buffer=io.BytesIO()
    np.savez_compressed(buffer,seeds=data[0],**arrays)
    raw=buffer.getvalue()
    _atomic_bytes(args.output/"holdout_traces.npz",raw)
    save_records(args.output/"per_seed.csv",rows)
    report["source_sha256"]=sha_before
    report["runtime"]={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    report["raw_traces_sha256"]=hashlib.sha256(raw).hexdigest()
    report["raw_traces_bytes"]=len(raw)
    report["per_seed_csv_sha256"]=_sha(args.output/"per_seed.csv")
    _atomic_bytes(args.output/"holdout_result.json",(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps(report,indent=2,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
