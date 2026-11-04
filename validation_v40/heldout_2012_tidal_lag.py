"""v40: original 2012 external-year evaluation of the previously chosen -120min phase.
All 2012 tide outcomes remain unopened when this fixed specification is committed.
"""
from __future__ import annotations
import argparse,json,math,tempfile,time
from datetime import datetime,timedelta,timezone
from collections import defaultdict
from pathlib import Path
import numpy as np
from source_preflight import download_and_pin
from source_gate_2012 import get_ameland_original,eligible_source_steps
from ameland_external_site import original_gps,ameland_original_steps
from observed_phase import gps_hourly_steps
from source_fetch_resilience import observed_rws_year,retry_transport_only
from rws_source_probe import WATHTE
from tidal_front import TideSeries
from phase_rate_ablation import predict_fixed
from tide_phase_yearago_placebo import percentile_interval

STATIONS={"schiermonnikoog":"schiermonnikoog.waddenzee","ameland":"ameland.nes"}
FROZEN_LAGS=(-120,0)
TRAIN_YEARS=(2010,2011)
TEST_YEAR=2012
CLOCKS=(0,-15)

def original_2012_gauge(station, *,request_fn=None,sleeper=time.sleep,min_unique=50000):
    from source_fetch_resilience import original_month_request
    if station not in STATIONS.values():raise ValueError("Unfrozen RWS gauge")
    req=original_month_request if request_fn is None else request_fn
    water={};quarters=[]
    for m in (1,4,7,10):
        if m!=1:sleeper(2)
        start=datetime(2012,m,1)
        end=datetime(2013,1,1) if m==10 else datetime(2012,m+3,1)
        payload={"Locatie":{"Code":station},
                 "AquoPlusWaarnemingMetadata":{"AquoMetadata":dict(WATHTE,ProcesType="meting")},
                 "Periode":{"Begindatumtijd":start.strftime("%Y-%m-%dT%H:%M:%S.000+01:00"),
                            "Einddatumtijd":end.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")}}
        print(f"Original 2012 RWS source {station}, quarter {m}",flush=True)
        result=retry_transport_only("/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen",
                                    payload,request_fn=req,sleeper=sleeper)
        if result.get("Succesvol") is not True:raise ValueError("RWS 2012 source rejected")
        count=0
        for series in result.get("WaarnemingenLijst") or []:
            meta=series.get("AquoMetadata") or {}
            if (meta.get("Grootheid") or {}).get("Code")!="WATHTE":continue
            if (meta.get("Eenheid") or {}).get("Code")!="cm" or (meta.get("Hoedanigheid") or {}).get("Code")!="NAP":
                raise ValueError("RWS 2012 source unit or vertical datum changed")
            for sample in series.get("MetingenLijst") or []:
                t=datetime.fromisoformat(sample["Tijdstip"].replace("Z","+00:00"))
                if t.tzinfo is None or t.utcoffset()!=timedelta(hours=1):
                    raise ValueError("RWS 2012 source timestamp not fixed UTC+01")
                q=(sample.get("Meetwaarde") or {}).get("Waarde_Numeriek")
                if q is None:continue
                val=float(q)
                if not math.isfinite(val) or abs(val)>500:continue
                utc=t.astimezone(timezone.utc)
                if utc in water and abs(water[utc]-val/100)>1e-4:raise ValueError("Conflicting RWS duplicate")
                water[utc]=val/100;count+=1
        quarters.append({"start_month":m,"original_measured_values":count})
    if len(water)<min_unique:raise ValueError("Incomplete 2012 real RWS gauge")
    tide=TideSeries(sorted(water.items()),datum="NAP_m",provenance="observed")
    gaps=[(y-x).total_seconds()/60 for x,y in zip(tide.times,tide.times[1:])]
    if gaps and max(gaps)>30:raise ValueError("Original 2012 RWS gauge has >30min gap")
    return tide,{"station":station,"original_year":2012,"gauge_rows":len(water),
                 "largest_gap_min":max(gaps) if gaps else None,
                 "source":"RWS_original_measured_WATHTE_cm_NAP_fixed_UTC_plus1",
                 "quarters":quarters}

def with_fixed_lags(rows,tide):
    kept=[];ph=[];missing=0
    for r in rows:
        try:
            before=int(tide.at_with_phase(r["t"]-timedelta(minutes=120))[1])
            current=int(tide.at_with_phase(r["t"])[1])
        except ValueError:
            missing+=1;continue
        kept.append(r);ph.append((before,current))
    return kept,np.array(ph,dtype=np.int8).reshape(-1,2),missing

def score(train,test,p_train,p_test,seed=20261103,bird_draws=10000,week_draws=4000):
    if len(train)!=len(p_train) or len(test)!=len(p_test):raise ValueError("Unmatched source or lag arrays")
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i,r in enumerate(test):
        if r["t"].year!=2012:raise ValueError("Evaluation accidentally includes training year")
        bybird[r["id"]].append(i);byweek[r["t"].isocalendar()[:2]].append(i)
    if len(train)<1000 or len(test)<1000 or len(bybird)<3 or len(byweek)<4:
        return {"status":"NOT_ADMITTED_2012_SOURCE_TOO_SMALL",
                "test_birds":len(bybird),"test_weeks":len(byweek),"test_steps":len(test)}
    trnew=[{**r,"phase":int(p_train[i,0])} for i,r in enumerate(train)]
    tenew=[{**r,"phase":int(p_test[i,0])} for i,r in enumerate(test)]
    tr0=[{**r,"phase":int(p_train[i,1])} for i,r in enumerate(train)]
    te0=[{**r,"phase":int(p_test[i,1])} for i,r in enumerate(test)]
    y=np.array([r["response"] for r in test])
    p0=predict_fixed(tr0,te0,"Mphase")
    if not np.allclose(p0,predict_fixed(train,test,"Mphase"),atol=1e-9,rtol=1e-9):
        raise ValueError("0-lag diverges from source-frozen v33 Mphase")
    pm=predict_fixed(trnew,tenew,"Mphase")
    ref=predict_fixed(train,test,"M0")
    errors={"M0":(y-ref)**2,"Mphase0":(y-p0)**2,"Mphase_minus120":(y-pm)**2}
    avg={key:float(np.mean([np.mean(v[ix]) for ix in bybird.values()])) for key,v in errors.items()}
    comparisons={
      "Mphase0_minus_Mphase_minus120":("Mphase0","Mphase_minus120"),
      "M0_minus_Mphase_minus120":("M0","Mphase_minus120"),
      "M0_minus_Mphase0":("M0","Mphase0")}
    contrasts={}
    for j,(label,(first,second)) in enumerate(comparisons.items()):
        a,b=errors[first],errors[second]
        bd=[float(np.mean(a[ix]-b[ix])) for ix in bybird.values()]
        wd=[]
        for idx in byweek.values():
            local=defaultdict(list)
            for i in idx:local[test[i]["id"]].append(i)
            wd.append(float(np.mean([np.mean(a[v]-b[v]) for v in local.values()])))
        contrasts[label]={
          "pooled_equal_bird_gain":float(np.mean(bd)),
          "whole_bird_bootstrap95":percentile_interval(bd,bird_draws,seed+j),
          "positive_birds":sum(v>0 for v in bd),
          "separate_equal_week_bird_gain":float(np.mean(wd)),
          "whole_week_bootstrap95":percentile_interval(wd,week_draws,seed+j+100),
          "positive_weeks":sum(v>0 for v in wd)}
    return {"status":"2012_ORIGINAL_HELDOUT_SOURCE_OBSERVED_NO_CAUSAL_CLAIM",
            "training_steps":len(train),"test_steps":len(test),
            "test_birds":len(bybird),"test_weeks":len(byweek),
            "models_equal_bird_MSE":avg,"comparisons":contrasts,
            "primary_contrast":"Mphase0_minus_Mphase_minus120",
            "zero_lag_predictor_exact_v33_replay":True}

def run(site,out):
    if site not in STATIONS:raise ValueError("Unfrozen 2012 site")
    station=STATIONS[site]
    years=(2010,2011,2012)
    data={c:{} for c in CLOCKS};lags={c:{} for c in CLOCKS};receipts={}
    with tempfile.TemporaryDirectory(prefix="v40_2012_original_") as d:
        for year in years:
            path=Path(d)/f"{site}_{year}.gz"
            if site=="schiermonnikoog":
                manifest=download_and_pin(year,path);read=gps_hourly_steps
            else:
                manifest=get_ameland_original(path) if year==2012 else original_gps(year,path)
                read=ameland_original_steps
            source_gate=eligible_source_steps(path,site) if year==2012 else None
            if source_gate is not None and source_gate["tide_test_admission"]!="SOURCE_FEASIBLE_ONLY":
                raise ValueError("2012 original GPS failed before-outcome source admission")
            tide,meta=(original_2012_gauge(station) if year==2012 else observed_rws_year(station,year))
            n=meta["gauge_rows"]
            if n<50000:raise ValueError("Original RWS annual measured tide insufficient")
            receipts[str(year)]={"original_provider_sha256":manifest["original_sha256"],
                                 "original_provider_md5_verified":manifest.get("provider_md5_match",manifest.get("provider_original_md5_matched")),
                                 "original_measured_NAP_gauge_count":n,
                                 "original_station":station,
                                 "2012_source_eligible":source_gate["tide_test_admission"] if source_gate else None}
            for clock in CLOCKS:
                raw,audit=read(path,tide,clock_shift_s=clock)
                joined,p,missing=with_fixed_lags(raw,tide)
                data[clock][year]=joined;lags[clock][year]=p
                receipts[str(year)][f"source_clock_{clock}s"]={
                    "original_joined_hourly_steps":len(raw),
                    "exact_both_lag_support_steps":len(joined),
                    "missing_tidal_lag_source":missing}
            path.unlink(missing_ok=True)
    outcomes={}
    for clock in CLOCKS:
        x=data[clock][2010]+data[clock][2011]
        xp=np.concatenate([lags[clock][2010],lags[clock][2011]],axis=0)
        outcomes[f"original_clock_shift_{clock}s"]=score(x,data[clock][2012],xp,lags[clock][2012])
    result={"analysis":"V40_2012_UNTOUCHED_TIDAL_LAG_EXTERNAL_YEAR",
            "site":site,"original_source_status":"GPS_MD5_AND_RWS_NAP_VERIFIED",
            "frozen_test_year":2012,"fit_years":[2010,2011],
            "chosen_from_2011_result_lag_minutes":-120,"baseline_phase_lag_minutes":0,
            "source_receipts":receipts,"outcomes":outcomes,
            "clock_limit":"SOURCE_NATIVE_UTC_OR_GPS_TIME_AMBIGUOUS_2012_LEAP_CHANGE",
            "ecological_limit":"NO_LOCAL_DEM_EXPOSURE_PREY_OR_BOIDS_SOCIAL_FORCE"}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=tuple(STATIONS),required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
