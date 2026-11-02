"""v36 retrospective two-site tide-phase propagation-lag sensitivity.

POST-v34 exploratory. No lag tuning and no model selection by test effects.
A positive shifted-gauge result is not an operational predictor or a causal
estimate of local tide propagation. Retains original source checks in-run.
"""
from __future__ import annotations
import argparse,json,math,tempfile
from collections import defaultdict,Counter
from datetime import timedelta
from pathlib import Path
import numpy as np
from source_preflight import download_and_pin
from observed_phase import real_rws_tide,gps_hourly_steps
from ameland_external_site import original_gps,measured_nes,ameland_original_steps
from phase_rate_ablation import predict_fixed

LAGS=(-120,-60,0,60,120)
YEARS=(2010,2011)
SITES=("schiermonnikoog","ameland")
CLOCKS=(0,-15)

def load_site_year(site,year,path,clock):
    if site=="ameland":
        raise ValueError("Ameland original site requires independent source source loader")
    raise ValueError("use collect_sources instead")

def common_phase_support(rows,tide,lags=LAGS):
    """Same movements for ALL shifted-phase calculations in one site and year.

    Return per-row phase vectors without writing original coordinates/timestamps.
    """
    admitted=[];phases=[]
    missing=0
    for row in rows:
        p=[]
        try:
            for lag in lags:
                _,phase,_=tide.at_with_phase(row["t"]+timedelta(minutes=lag))
                p.append(phase)
        except ValueError:
            missing+=1;continue
        admitted.append(row)
        phases.append(p)
    return admitted,np.array(phases,dtype=np.int8),missing

def model_lag_comparison(train,test,trainph,testph,seed=20261102):
    if not(len(train)==len(trainph) and len(test)==len(testph)):
        raise ValueError("Source rows vs tide features count mismatch")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        bybird[r["id"]].append(i)
        byweek[r["t"].isocalendar()[:2]].append(i)
    ntestbirds=len(bybird);nweeks=len(byweek)
    if len(train)<1000 or len(test)<1000 or ntestbirds<3 or nweeks<4:
        return {"status":"NOT_ADMITTED","train_steps":len(train),
                "test_steps":len(test),"n_test_birds":ntestbirds,
                "n_test_weeks":nweeks}
    y=np.asarray([r["response"] for r in test],dtype=float)
    basepred=predict_fixed(train,test,"M0")
    e0=(y-basepred)**2
    bird_mse0=[float(np.mean(e0[idx])) for idx in bybird.values()]
    base=float(np.mean(bird_mse0))
    results=[]
    rng=np.random.default_rng(seed)
    bootstrap_indices=rng.integers(0,nweeks,size=(4000,nweeks))
    for col,lag in enumerate(LAGS):
        # Normalized and fit from zero again on each *unchanged* source
        # cohort. Only the gauge phase source time moves.
        tr=[{**r,"phase":int(trainph[i,col])} for i,r in enumerate(train)]
        te=[{**r,"phase":int(testph[i,col])} for i,r in enumerate(test)]
        p=predict_fixed(tr,te,"Mphase")
        if lag==0 and not np.allclose(p,predict_fixed(train,test,"Mphase"),atol=1e-9,rtol=1e-9):
            raise AssertionError("Lag0 changed v33 frozen model on common-source rows")
        e1=(y-p)**2
        birddiff=[float(np.mean(e0[idx]-e1[idx])) for idx in bybird.values()]
        weekdiff=[]
        for ids in byweek.values():
            byw=defaultdict(list)
            for i in ids:byw[test[i]["id"]].append(i)
            weekdiff.append(float(np.mean([np.mean(e0[js]-e1[js]) for js in byw.values()])))
        boot=np.asarray(weekdiff)[bootstrap_indices].mean(axis=1)
        m1=float(np.mean([np.mean(e1[ix]) for ix in bybird.values()]))
        results.append({"gauge_phase_lag_minutes":lag,
                        "M0_equal_bird_MSE":base,
                        "Mphase_equal_bird_MSE":m1,
                        "M0_minus_Mphase_equal_bird_gain":base-m1,
                        "percent_gain":100*(base-m1)/base if base else None,
                        "positive_birds":int(sum(z>0 for z in birddiff)),
                        "positive_weeks":int(sum(z>0 for z in weekdiff)),
                        "whole_week_bootstrap_CI95":np.quantile(boot,[.025,.975]).tolist(),
                        "phase_count_test":{str(k):int(sum(testph[:,col]==k)) for k in (-1,0,1)}})
    return {"status":"EXPLORATORY_FIXED_LAG_GRID_NO_SELECTION",
            "n_train_steps":len(train),"n_test_steps":len(test),
            "n_heldout_birds":ntestbirds,"n_heldout_weeks":nweeks,
            "lag_variants":results,
            "source_common_support_across_all_lags":True}

def run(output):
    out={"analysis":"V36_POSTRESULT_TWO_ISLAND_TIDAL_PHASE_LAG_GRID",
         "source":"ORIGINAL_ZENODO_GPS_RWS_WATHTE_NAP",
         "frozen_lags_minutes":list(LAGS),
         "clock_offsets_seconds":list(CLOCKS),
         "comparison":"train_2010_test_2011_site_specific_equal_bird_M0_vs_Mphase",
         "source_receipts":{},"scenarios":{},
         "evidence":"EXPLORATORY_AFTER_V33_V34",
         "causal_intertidal_front":"NOT_ESTABLISHED"}
    with tempfile.TemporaryDirectory(prefix="boids_v36_original_") as td:
        for site in SITES:
            one_site={}
            data={0:{},-15:{}}
            audit={}
            for year in YEARS:
                path=Path(td)/f"{site}_{year}.csv.gz"
                if site=="schiermonnikoog":
                    manifest=download_and_pin(year,path)
                    tide,gauge=real_rws_tide(year)
                    stepfn=gps_hourly_steps
                else:
                    manifest=original_gps(year,path)
                    tide,gauge=measured_nes(year)
                    stepfn=ameland_original_steps
                for clock in CLOCKS:
                    origrows,sourceinfo=stepfn(path,tide,clock_shift_s=clock)
                    rows,phase,omitted=common_phase_support(origrows,tide)
                    data[clock][year]=(rows,phase)
                    audit[f"{year}_clock_{clock}s"]={"source_valid_movement_steps":len(origrows),
                                                    "common_lag_support_steps":len(rows),
                                                    "lag_support_exclusions":omitted,
                                                    "source_bird_count":sourceinfo.get("individuals_with_steps",sourceinfo.get("birds_with_steps"))}
                path.unlink(missing_ok=True)
                one_site[str(year)]={"original_provider_manifest":manifest,
                                     "original_NAP_gauge_count":gauge.get("gauge_rows",gauge.get("n_original_unique_gauge_fixes")),
                                     "original_gauge_station":gauge.get("station")}
            out["source_receipts"][site]={"original":one_site,"support":audit}
            for clock in CLOCKS:
                train,trp=data[clock][2010]
                test,tep=data[clock][2011]
                out["scenarios"][f"{site}_GPSclock_{clock}s"]=model_lag_comparison(train,test,trp,tep)
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    return out

if __name__=="__main__":
    arg=argparse.ArgumentParser();arg.add_argument("--output",required=True)
    args=arg.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
