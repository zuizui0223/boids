"""v39 original-source two-island year-ago tidal-phase negative control.

Post-v32/34 result diagnostic, with pre-frozen v39 source cohorts and contrasts.
Real contemporaneous h(t) unchanged. Negative control source phase(t-365 days)
comes from a *different original measured calendar year at the same gauge*.
Results are associations, not demonstrated intertidal-front causes.
"""
from __future__ import annotations
import argparse,json,tempfile
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
import numpy as np

from source_preflight import download_and_pin
from observed_phase import real_rws_tide,gps_hourly_steps
from ameland_external_site import original_gps,measured_nes,ameland_original_steps
from phase_rate_ablation import predict_fixed

TIDE_PLACEBO_DAYS=365
CLOCKS=(0,-15)
SITES=("schiermonnikoog","ameland")
YEARS=(2010,2011)

def previous_year_phase_join(rows,year_ago_tide):
    """All real original GPS steps kept only where real year-ago phase exists."""
    out=[];ghost_phases=[];omitted=0
    for r in rows:
        try:
            _, p, _=year_ago_tide.at_with_phase(r["t"]-timedelta(days=TIDE_PLACEBO_DAYS))
        except ValueError:
            omitted+=1;continue
        out.append(r)
        ghost_phases.append(int(p))
    return out,ghost_phases,omitted

def percentile_interval(items, n_draws, seed):
    a=np.asarray(items,dtype=float)
    if not len(a):return [None,None]
    random=np.random.default_rng(seed)
    idx=random.integers(0,len(a),size=(n_draws,len(a)))
    return np.quantile(a[idx].mean(axis=1),[.025,.975]).tolist()

def comparison(train,test,placebo_train,placebo_test,seed=20261102,
               bird_draws=10000,week_draws=4000):
    """Week and bird resampling use their own **matching** point estimands."""
    if not(len(train)==len(placebo_train) and len(test)==len(placebo_test)):
        raise ValueError("Source rows and placebos not aligned")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        bybird[r["id"]].append(i)
        byweek[r["t"].isocalendar()[:2]].append(i)
    if len(train)<1000 or len(test)<1000 or len(bybird)<3 or len(byweek)<4:
        return {"admission":"NOT_ADMITTED_INSUFFICIENT_EXTERNAL_SOURCE",
                "train_steps":len(train),"test_steps":len(test),
                "test_birds":len(bybird),"test_weeks":len(byweek)}
    # Use precisely the frozen v33 Mphase representation and ridge.
    ghost_training=[{**r,"phase":int(p)} for r,p in zip(train,placebo_train)]
    ghost_test=[{**r,"phase":int(p)} for r,p in zip(test,placebo_test)]
    y=np.asarray([r["response"] for r in test],dtype=float)
    e0=(y-predict_fixed(train,test,"M0"))**2
    er=(y-predict_fixed(train,test,"Mphase"))**2
    ep=(y-predict_fixed(ghost_training,ghost_test,"Mphase"))**2
    perbird={name:float(np.mean([np.mean(errors[idx]) for idx in bybird.values()]))
             for name,errors in (("M0",e0),("Mactual",er),("Myear_ago",ep))}
    out={"admission":"OBSERVED_POSTRESULT_HISTORICAL_PLACEBO",
         "n_training_source_steps":len(train),"n_test_source_steps":len(test),
         "n_heldout_birds":len(bybird),"n_heldout_weeks":len(byweek),
         "test_model_MSE_equal_bird":perbird,
         "placebo_phase_true_original_h_level":True,
         "model_contrasts":{}}
    pairs={"M0_minus_Mactual":(e0,er),
           "M0_minus_Myear_ago":(e0,ep),
           "Myear_ago_minus_Mactual":(ep,er)}
    for j,(name,(ea,eb)) in enumerate(pairs.items()):
        bybirddiff=[float(np.mean(ea[idx]-eb[idx])) for idx in bybird.values()]
        byweekdiff=[]
        for ix in byweek.values():
            bird_ix=defaultdict(list)
            for i in ix:bird_ix[test[i]["id"]].append(i)
            byweekdiff.append(float(np.mean([np.mean(ea[js]-eb[js]) for js in bird_ix.values()])))
        bird_mean=float(np.mean(bybirddiff))
        week_mean=float(np.mean(byweekdiff))
        out["model_contrasts"][name]={
            "pooled_equal_bird_mean_gain":bird_mean,
            "pooled_equal_bird_95percentile_CI":percentile_interval(bybirddiff,bird_draws,seed+j),
            "separate_equal_week_bird_mean_gain":week_mean,
            "separate_equal_week_bird_95percentile_CI":percentile_interval(byweekdiff,week_draws,seed+j+100),
            "positive_birds":sum(d>0 for d in bybirddiff),
            "positive_weeks":sum(d>0 for d in byweekdiff),
            "note":"bird and week point estimates and their CIs are different estimands and must not be mixed"}
    return out

def run(path):
    out={"analysis":"V39_POSTRESULT_PREOUTCOME_YEARAGO_TIDE_PHASE_PLACEBO",
         "tide_placebo_offset_days":TIDE_PLACEBO_DAYS,
         "year_external_design":"each site 2010 train 2011 test",
         "source":"original provider MD5 verified GPS and measured RWS WATHTE NAP gauges",
         "evidence":"POST_v32_v34_OBSERVED_EXPLORATORY_CONTROL",
         "source_receipts":{},"scenarios":{},
         "mechanism":"NO_ACTUAL_EXPOSED_FRONT_PREY_OR_SOCIAL_FORCE_ESTIMATED"}
    with tempfile.TemporaryDirectory(prefix="boids_v39_field_") as td:
        for site in SITES:
            tide_source={}
            docs={}
            for year in (2009,2010,2011):
                if site=="schiermonnikoog":
                    tide,audit=real_rws_tide(year)
                    n=audit["gauge_rows"];station=audit["station"]
                else:
                    tide,audit=measured_nes(year)
                    n=audit["n_original_unique_gauge_fixes"];station=audit["station"]
                tide_source[year]=tide
                docs[str(year)]={"original_gauge_count":n,"original_station":station}
            site_rows={clock:{} for clock in CLOCKS}
            site_phases={clock:{} for clock in CLOCKS}
            for year in YEARS:
                path_gps=Path(td)/f"{site}_{year}_original.csv.gz"
                if site=="schiermonnikoog":
                    original=download_and_pin(year,path_gps)
                    original_rows=gps_hourly_steps
                else:
                    original=original_gps(year,path_gps)
                    original_rows=ameland_original_steps
                docs[str(year)]["original_gps_SHA256"]=original.get("original_sha256")
                docs[str(year)]["original_gps_md5_verified"]=original.get("provider_md5_match",original.get("provider_original_md5_matched"))
                for clock in CLOCKS:
                    rows,obs_audit=original_rows(path_gps,tide_source[year],clock_shift_s=clock)
                    aligned,ghost,omitted=previous_year_phase_join(rows,tide_source[year-1])
                    site_rows[clock][year]=aligned
                    site_phases[clock][year]=ghost
                    docs[str(year)][f"clock_{clock}s"]={
                        "actual_phase_source_steps":len(rows),
                        "common_real_and_previous_year_phase_steps":len(aligned),
                        "source_rejected_missing_previous_year_phase":omitted,
                        "source_original_admitted_tags":obs_audit.get("individuals_with_steps",obs_audit.get("birds_with_steps"))}
                path_gps.unlink(missing_ok=True)
            out["source_receipts"][site]=docs
            for clock in CLOCKS:
                obs=comparison(site_rows[clock][2010],site_rows[clock][2011],
                               site_phases[clock][2010],site_phases[clock][2011])
                out["scenarios"][f"{site}_GPSclock_{clock}s"]=obs
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.output),sort_keys=True))
