"""v33 post-result field phase/rate decomposition; exploratory, not v32 confirmation.

All source original GPS/RWS, step definitions, ridge predictors and cross-year
splits are identical to v32. Only predefined feature ablations differ.
"""
from __future__ import annotations
import argparse, json, tempfile
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from source_preflight import download_and_pin
from observed_phase import real_rws_tide,gps_hourly_steps,predict,make_x

MODES=("M0","Mphase","Mrate","Mboth")
def vector(row,mode):
    x=make_x(row,0)
    if mode not in MODES:
        raise ValueError("Unregistered tide-feature ablation model")
    if mode in ("Mphase","Mboth"):
        x.extend([row["phase"],row["phase"]*row["h"]])
    if mode in ("Mrate","Mboth"):
        x.append(row["rate"])
    return x

def predict_fixed(train,test,mode):
    a=np.asarray([vector(r,mode) for r in train],dtype=float)
    b=np.asarray([vector(r,mode) for r in test],dtype=float)
    y=np.asarray([r["response"] for r in train],dtype=float)
    c=a[:,1:].mean(axis=0);sd=a[:,1:].std(axis=0)
    sd[sd<1e-9]=1
    a[:,1:]=(a[:,1:]-c)/sd
    b[:,1:]=(b[:,1:]-c)/sd
    counts=Counter(r["id"] for r in train)
    w=np.asarray([1/counts[r["id"]] for r in train])
    w*=len(train)/w.sum()
    penalty=np.eye(a.shape[1])*10
    penalty[0,0]=0.
    beta=np.linalg.solve(a.T@(a*w[:,None])+penalty,a.T@(w*y))
    return b@beta

def contrast_boot(errors_a,errors_b,test,bird_groups,week_groups,seed=20261102):
    gain_by_bird=[float(np.mean(errors_a[ix]-errors_b[ix])) for ix in bird_groups.values()]
    byweek=[]
    for idx in week_groups.values():
        bird_ix=defaultdict(list)
        for j in idx:bird_ix[test[j]["id"]].append(j)
        byweek.append(float(np.mean([np.mean(errors_a[js]-errors_b[js]) for js in bird_ix.values()])))
    rng=np.random.default_rng(seed)
    sample=rng.choice(byweek,size=(4000,len(byweek)),replace=True).mean(axis=1)
    return {"mean_equal_bird_gain":float(np.mean(gain_by_bird)),
            "positive_birds":int(sum(v>0 for v in gain_by_bird)),
            "positive_weeks":int(sum(v>0 for v in byweek)),
            "week_bootstrap_95":np.quantile(sample,[.025,.975]).tolist()}

def compare(train,test):
    if len(train)<1000 or len(test)<1000:raise ValueError("Not enough annual source steps")
    y=np.asarray([r["response"] for r in test],dtype=float)
    forecasts={m:predict_fixed(train,test,m) for m in MODES}
    # Validate no coding drift from the original v32 primary estimand.
    if not np.allclose(forecasts["M0"],predict(train,test,0),atol=1e-9,rtol=1e-9):
        raise AssertionError("M0 ablation diverged from frozen v32 predictor")
    if not np.allclose(forecasts["Mboth"],predict(train,test,1),atol=1e-9,rtol=1e-9):
        raise AssertionError("Mboth ablation diverged from frozen v32 M1")
    errors={m:(y-p)**2 for m,p in forecasts.items()}
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        bybird[r["id"]].append(i)
        byweek[r["t"].isocalendar()[:2]].append(i)
    scores={m:float(np.mean([np.mean(errors[m][ix]) for ix in bybird.values()])) for m in MODES}
    pairs={"M0_minus_Mphase":("M0","Mphase"),
           "M0_minus_Mrate":("M0","Mrate"),
           "M0_minus_Mboth":("M0","Mboth"),
           "Mrate_minus_Mboth":("Mrate","Mboth"),
           "Mphase_minus_Mboth":("Mphase","Mboth")}
    contrasts={k:contrast_boot(errors[a],errors[b],test,bybird,byweek)
               for k,(a,b) in pairs.items()}
    return {"n_train_steps":len(train),"n_test_steps":len(test),
            "test_birds":len(bybird),"test_weeks":len(byweek),
            "MSE_equal_bird":scores,"contrasts":contrasts,
            "M0_and_Mboth_replay_v32_verified":True,
            "status":"POST_RESULT_EXPLORATORY_DECOMPOSITION_NOT_CAUSAL"}

def run(out):
    data={}
    sources={}
    with tempfile.TemporaryDirectory(prefix="v33_source_") as temp:
        for year in (2009,2010,2011):
            path=Path(temp)/f"{year}.csv.gz"
            pin=download_and_pin(year,path)
            tide,gauge=real_rws_tide(year)
            sources[str(year)]={"source_gps_sha256":pin["original_sha256"],
                                "original_MD5_match":pin["provider_md5_match"],
                                "source_gauge_NAP":gauge["gauge_rows"]}
            data[year]={}
            for clock in (0,-15):
                rows,audit=gps_hourly_steps(path,tide,clock_shift_s=clock)
                data[year][clock]=rows
                sources[str(year)][f"clock_{clock}s_valid_steps"]=audit["same_bird_first_fix_hourly_step_rows"]
            path.unlink(missing_ok=True)
    results={}
    for clock in (0,-15):
        annual={y:data[y][clock] for y in (2009,2010,2011)}
        results[f"native_clock_offset_{clock}s"]={
            "train_2010_test_2011_PRIMARY_EXPLORATORY":compare(annual[2010],annual[2011]),
            "train_2009_test_2010_SECONDARY_EXPLORATORY":compare(annual[2009],annual[2010]),
        }
    report={"source":"ORIGINAL_GPS_AND_MEASURED_RWS_NAP",
            "analysis":"V33_POSTRESULT_EXPLORATORY_PHASE_RATE_ABLATION",
            "sample_source":sources,"models":results,
            "claim_boundary":"source clocks unverified, shared site; no exposure DEM, prey, local tide propagation or Boids social mechanism"}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.output),sort_keys=True))
