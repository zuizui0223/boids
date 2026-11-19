#!/usr/bin/env python3
"""Frozen Carollia v30 bat-heldout beam-vs-kinematics prediction.

This exploratory reanalysis uses only the 30 exact SHA-pinned upstream original
MAT files and NEVER uses author-saved future-dependent relative beam headings.
The registered source-contract governs all thresholds and outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import re
import numpy as np
import h5py

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from tunnel_source_schema_audit import git_blob_sha1

SOURCE_SHA = "59928a71887d521fec143080b0b187736c046a0e"
MANIFEST = Path("docs/BAT_ACTIVE_SENSING_TUNNEL_SOURCE_INVENTORY_V1.json")
DEFAULT_OUT = Path("validation_v30/results/carollia_absolute_beam_heldout_v30.json")
FIELDS = (
    "RESULTS/calls/tSec",
    "RESULTS/calls/XYZ_raw",
    "RESULTS/beam/az_rad",
    "RESULTS/beam/fitR",
)
ALPHA = 1.0
SEED = 20261119
B = 10000


def wrap_rad(x):
    return (np.asarray(x) + np.pi) % (2 * np.pi) - np.pi


def load_trial(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with h5py.File(path, "r") as f:
        for key in FIELDS:
            if key not in f:
                raise ValueError(f"source missing pinned field {key}: {path.name}")
        t = np.asarray(f[FIELDS[0]][()], dtype=float).reshape(-1)
        xyz = np.asarray(f[FIELDS[1]][()], dtype=float)
        az = np.asarray(f[FIELDS[2]][()], dtype=float).reshape(-1)
        fit = np.asarray(f[FIELDS[3]][()], dtype=float).reshape(-1)
    if xyz.ndim != 2 or 3 not in xyz.shape:
        raise ValueError("original XYZ_raw is not a Kx3 or 3xK array")
    xyz = xyz.T if xyz.shape[0] == 3 else xyz
    if xyz.shape != (len(t), 3) or len(az) != len(t) or len(fit) != len(t):
        raise ValueError("original calls and sonar mismatch in trial " + path.name)
    return t, xyz[:, :2], az, fit


def pre_features(t, xy, az, fit, k):
    """Strictly causal predictors from indices <=k; no target array access."""
    if k < 4 or k + 1 >= len(t):
        return None
    indices = [k - 3, k - 2, k - 1, k]
    if not np.isfinite(t[indices]).all() or not np.isfinite(xy[indices]).all():
        return None
    if not np.isfinite(az[k]) or not np.isfinite(fit[k]) or fit[k] < .30:
        return None
    dt0, dt1, dt2 = np.diff(t[[k - 3, k - 2, k - 1, k]])
    if min(dt0, dt1, dt2) <= 0:
        return None
    u1 = xy[k - 1] - xy[k - 2]
    u2 = xy[k] - xy[k - 1]
    if np.linalg.norm(u1) < .05 or np.linalg.norm(u2) < .05:
        return None
    speed = float(np.linalg.norm(u2) / dt2)
    if not .1 <= speed <= 30.0:
        return None
    th1 = math.atan2(u1[1], u1[0])
    th2 = math.atan2(u2[1], u2[0])
    dpre = float(wrap_rad(th2 - th1))
    motor = [
        float(xy[k, 0]), float(xy[k, 1]), speed, float(dt2),
        math.sin(th2), math.cos(th2), dpre
    ]
    acoustic = [math.sin(float(az[k])), math.cos(float(az[k]))]
    return np.asarray(motor, dtype=float), np.asarray(acoustic, dtype=float), th2


def target_after_call(t, xy, k, th_pre):
    """The only target: future original call (k+1), never interpolated track."""
    if not np.isfinite(t[k + 1]) or t[k + 1] <= t[k]:
        return None
    if not np.isfinite(xy[k + 1]).all():
        return None
    dnext = xy[k + 1] - xy[k]
    if np.linalg.norm(dnext) < .05:
        return None
    thnext = math.atan2(dnext[1], dnext[0])
    return float(wrap_rad(thnext - th_pre))


def extract_rows(source_root: Path, manifest: dict):
    all_rows, excluded = [], Counter()
    for item in manifest["git_blobs"]:
        path = source_root / item["path"]
        if path.stat().st_size != item["size_bytes"] or git_blob_sha1(path) != item["git_blob_sha1"]:
            raise ValueError("SOURCE_HASH_OR_SIZE_MISMATCH_STOP " + item["path"])
        t, xy, az, fit = load_trial(path)
        name = Path(item["path"]).name
        m = re.match(r"(C[1-8])_\d+_(\d{8})_traj_bat_pos_RESULTS\.mat$", name)
        if m is None:
            raise ValueError("Original filename label/date not understood " + name)
        label, date = m.groups()
        for k in range(4, len(t) - 1):
            feat = pre_features(t, xy, az, fit, k)
            if feat is None:
                excluded["invalid_pre_event_quality_or_kinematics"] += 1
                continue
            y = target_after_call(t, xy, k, feat[2])
            if y is None:
                excluded["invalid_future_original_call_displacement"] += 1
                continue
            oldaz = az[k - 3]
            secondary_ok = np.isfinite(oldaz)
            all_rows.append({
                "bat": label, "date": date, "trial": name,
                "motor": feat[0], "beam": feat[1],
                "shift": np.array([math.sin(float(oldaz)), math.cos(float(oldaz))])
                    if secondary_ok else None,
                "y": y,
            })
    return all_rows, dict(excluded)


def model_fit_predict(train, test, acoustic: str | None):
    def features(rows):
        m=np.stack([r["motor"] for r in rows])
        if acoustic is not None:
            s=np.stack([r[acoustic] for r in rows])
            m=np.column_stack((m,s))
        return m
    model=Pipeline([
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=ALPHA))
    ])
    model.fit(features(train), np.asarray([r["y"] for r in train]))
    return model.predict(features(test))


def mean_mse_by_label(rows, acoustic: str | None, label_key="bat"):
    labels=sorted({r[label_key] for r in rows})
    out={}
    for label in labels:
        tr=[r for r in rows if r[label_key]!=label]
        te=[r for r in rows if r[label_key]==label]
        if not tr or not te:
            raise ValueError("empty whole-label holdout")
        pred=model_fit_predict(tr,te,acoustic)
        actual=np.asarray([r["y"] for r in te])
        err=wrap_rad(actual-pred)
        out[label]={"n":len(te),"mse_rad2":float(np.mean(err**2))}
    return out


def per_label_gain(a, b):
    return {k:float(a[k]["mse_rad2"]-b[k]["mse_rad2"]) for k in sorted(a)}


def bootstrap_label_gain(gains):
    xs=np.asarray(list(gains.values()))
    rng=np.random.default_rng(SEED)
    resampled=rng.choice(xs, size=(B,len(xs)), replace=True).mean(axis=1)
    lo,hi=np.percentile(resampled,[2.5,97.5])
    npos=int(np.sum(xs>0))
    n=len(xs)
    p=float(sum(math.comb(n,k) for k in range(npos,n+1))/2**n)
    return {
        "equal_bat_mean_gain_rad2":float(xs.mean()),
        "bat_bootstrap_95_percentile_interval_rad2":[float(lo),float(hi)],
        "positive_bat_labels":npos,"bat_labels":n,
        "one_sided_exact_sign_p":p,
        "predeclared_primary_pass": bool(xs.mean()>0 and lo>0 and p<=.05),
    }


def run(source_root: Path, manifest: dict):
    if manifest["github_ref"]!=SOURCE_SHA or len(manifest["git_blobs"])!=30:
        raise ValueError("source version/length changed")
    rows,excluded=extract_rows(source_root,manifest)
    support=Counter(r["bat"] for r in rows)
    eligible=[k for k,v in support.items() if v>=20]
    structural_gate=len(eligible)>=6 and len(rows)>=300
    result={
        "protocol":"docs/BAT_ACTIVE_SENSING_CAROLLIA_HELDOUT_CONTRACT_V30.md",
        "status":"STRUCTURAL_STOP" if not structural_gate else "EVALUATED_FROZEN_PRIMARY",
        "original_commit":SOURCE_SHA,
        "trial_files_verified_n":30,
        "candidate_future_call_events_total":len(rows),
        "eligible_bat_labels_n":len(eligible),
        "source_bat_label_events":dict(sorted(support.items())),
        "excluded_counts":excluded,
        "source_day_counts":dict(sorted(Counter(r["date"] for r in rows).items())),
        "primary_model_class":"StandardScaler(train-only) + Ridge(alpha=1.0)",
        "primary_response":"signed wrapped next original call displacement heading rad",
        "same_event_source_measurement_independence_not_established":True,
        "published_sonar_lookahead_is_prior_art":True,
        "full_q_law_not_admitted":True,
        "universal_bat_behavior_law_supported":False,
        "no_frozen_batter_or_prior_boids_results_modified":True,
    }
    if not structural_gate:
        result["stop_reason"]="Predeclared >=6 bat labels >=20 events and >=300 pooled events not met"
        return result
    m0=mean_mse_by_label(rows,None)
    m1=mean_mse_by_label(rows,"beam")
    gains=per_label_gain(m0,m1)
    primary=bootstrap_label_gain(gains)
    result["primary"]={
        "motor_model_label_scores":m0,
        "motor_plus_absolute_beam_label_scores":m1,
        "label_gains":gains,
        **primary,
    }
    shift_rows=[r for r in rows if r["shift"] is not None]
    if len(shift_rows)>=300 and len({r["bat"] for r in shift_rows})==8:
        m0s=mean_mse_by_label(shift_rows,None)
        m1s=mean_mse_by_label(shift_rows,"beam")
        old=mean_mse_by_label(shift_rows,"shift")
        result["secondary_prior_beam_shift"]={
            "matched_rows":len(shift_rows),
            "mean_current_beam_gain_vs_motor":float(np.mean(list(per_label_gain(m0s,m1s).values()))),
            "mean_old_beam_gain_vs_motor":float(np.mean(list(per_label_gain(m0s,old).values()))),
            "test_type":"exploratory negative-control; 3 earlier calls",
        }
    else:
        result["secondary_prior_beam_shift"]={"status":"STRUCTURAL_STOP"}
    days=sorted({r["date"] for r in rows})
    if len(days)==2:
        tests={}
        for day in days:
            tr=[r for r in rows if r["date"]!=day]
            te=[r for r in rows if r["date"]==day]
            p0=model_fit_predict(tr,te,None)
            p1=model_fit_predict(tr,te,"beam")
            y=np.asarray([r["y"] for r in te])
            g=float(np.mean(wrap_rad(y-p0)**2)-np.mean(wrap_rad(y-p1)**2))
            tests[day]={"n_test":len(te),"motor_mse_minus_beam_mse_rad2":g}
        result["secondary_two_day_transfer"]=tests
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path,required=True)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    with MANIFEST.open() as f:manifest=json.load(f)
    result=run(args.source_root,manifest)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    concise={k:result.get(k) for k in (
        "status","candidate_future_call_events_total","eligible_bat_labels_n","source_bat_label_events")}
    if result["status"]=="EVALUATED_FROZEN_PRIMARY":
        concise["primary"]= {k:v for k,v in result["primary"].items() if k not in (
            "motor_model_label_scores","motor_plus_absolute_beam_label_scores","label_gains")}
    print("FROZEN_V30_RESULT="+json.dumps(concise,sort_keys=True))
    print("CAUSAL_AND_UNIVERSAL_CLAIM=NOT_ESTABLISHED")


if __name__=="__main__":
    main()
