"""Real 2019-06-01..07 NOAA gauge-to-gauge phase and amplitude preflight.

These are four physically distinct CO-OPS water level gauges, not four
independent marine bioacoustic deployments and not physical tide at an
offshore hydrophone. Preserves each gauge's real time stamps and datum.
"""
from __future__ import annotations
from collections import OrderedDict
from datetime import datetime
from statistics import mean
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import argparse,hashlib,json,math

from noaa_tide_preflight import STATIONS, PARAMS, BASE

def pearson(a,b):
    if len(a)!=len(b) or len(a)<3:raise ValueError("At least 3 matched pairs required")
    am=mean(a);bm=mean(b)
    aa=sum((x-am)**2 for x in a)
    bb=sum((y-bm)**2 for y in b)
    if not aa>0 or not bb>0:raise ValueError("Cannot correlate flat gauge series")
    return sum((x-am)*(y-bm) for x,y in zip(a,b))/math.sqrt(aa*bb)

def best_lag(a,b,max_lag=6):
    """Positive lag: target b(t+lag) best matches reference a(t)."""
    results=[]
    for lag in range(-max_lag,max_lag+1):
        if lag>=0:
            aa,bb=a[:len(a)-lag or len(a)],b[lag:]
        else:
            aa,bb=a[-lag:],b[:lag]
        if len(aa)<20:raise ValueError("Insufficient matched samples")
        results.append((lag,pearson(aa,bb)))
    results.sort(key=lambda p:(-p[1],abs(p[0]),p[0]))
    return results[0],sorted(results)

def download_stations():
    d={}
    for label,station in STATIONS.items():
        p=dict(PARAMS);p["station"]=str(station)
        url=BASE+"?"+urlencode(p)
        with urlopen(Request(url,headers={"User-Agent":"Boids Independent Research Source Validation/1.0"}),timeout=40) as response:
            raw=response.read(2_000_000)
        o=json.loads(raw)
        if "error" in o:raise ValueError("NOAA reported source error: "+str(o["error"])[:150])
        if str(o.get("metadata",{}).get("id"))!=str(station):raise ValueError("NOAA station metadata mismatch")
        times={}
        for v in o.get("data",[]):
            try:
                t=datetime.strptime(v["t"],"%Y-%m-%d %H:%M")
                h=float(v["v"])
            except (ValueError,KeyError,TypeError):
                continue
            if not math.isfinite(h):continue
            if t in times:raise ValueError("Duplicate observed NOAA hour")
            times[t]=h
        if len(times)!=168:raise ValueError("One physical gauge lacks full 168 measured hours")
        d[label]=times
    if len(set(frozenset(x) for x in d.values()))!=1:
        raise ValueError("Gauge sources do not share all 168 GMT timestamps")
    return d

def analyze():
    gauges=download_stations()
    clock=sorted(gauges["Monterey"])
    reference=[gauges["Monterey"][t] for t in clock]
    result={
        "version":"v141_reference_tide_gauge_phase_vs_amplitude_1",
        "original_time_range_UTC":"2019-06-01 00:00 to 2019-06-07 23:00",
        "real_verified_NOAA_gauge_hours_per_station":168,
        "gauge_stations":list(STATIONS.keys()),
        "datum":"MLLW","units":"meters",
        "baseline_gauge":"Monterey (9413450)",
        "cross_site_hydrophone_tide_alignment":"NOT_CALIBRATED",
        "estimates_of_fish_tide_effect":"NOT_ESTIMATED",
        "gauge_comparisons":{},
    }
    for label,series in gauges.items():
        values=[series[t] for t in clock]
        (lag,corr),lag_scores=best_lag(reference,values,max_lag=6)
        result["gauge_comparisons"][label]={
            "zero_lag_gauge_height_pearson":round(pearson(reference,values),7),
            "best_integer_hour_gauge_lag_vs_Monterey":lag,
            "best_lag_pearson":round(corr,7),
            "all_tested_lags":{"%+d"%k:round(v,7) for k,v in lag_scores},
            "mean_height_m":round(mean(values),6),
            "height_range_m":round(max(values)-min(values),6),
            "hours":len(values),
        }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=analyze()
    path=Path(__file__).parent/"results"/"noaa_gauge_phase_comparisons.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    if a.check:
        saved=json.loads(path.read_text())
        if saved!=result:raise AssertionError("Original NOAA phase comparisons changed")
    else:path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V141_GAUGE_PHASE_START")
    print(json.dumps(result,sort_keys=True))
    print("V141_GAUGE_PHASE_END")

if __name__=="__main__":main()
