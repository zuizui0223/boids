"""NOAA CO-OPS verified hourly WATER HEIGHT *tide gauge* availability preflight.

These are physical water levels at coastal reference stations, not physical
water levels at the nine offshore fish chorus hydrophone locations, which
have not been spatially/phase calibrated. NOT a fish+tide effect.
"""
from __future__ import annotations
from urllib.parse import urlencode
from urllib.request import urlopen,Request
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
import argparse, hashlib, json, math, sys

STATIONS={"Monterey":9413450,"Port_San_Luis":9412110,
          "Santa_Barbara":9411340,"Los_Angeles":9410660}
START="20190601"
END="20190607"
BASE="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
ROOT=Path(__file__).resolve().parent
PARAMS={"product":"hourly_height","application":"Boids_Source_Research_Audit",
        "begin_date":START,"end_date":END,
        "datum":"MLLW","time_zone":"GMT",
        "units":"metric","format":"json"}

def parse_noaa(raw,station):
    doc=json.loads(raw)
    if "error" in doc:raise ValueError("NOAA source error "+str(doc["error"])[:170])
    observed=doc.get("data")
    if not isinstance(observed,list) or not observed:
        raise ValueError("NOAA verified-hourly-height returned no measured rows")
    meta=doc.get("metadata",{})
    if str(meta.get("id"))!=str(station):
        raise ValueError("NOAA station metadata ID mismatch")
    seq=[]
    for row in observed:
        if not row.get("t") or row.get("v") in (None,""):
            continue
        try:
            t=datetime.strptime(row["t"],"%Y-%m-%d %H:%M")
            v=float(row["v"])
        except ValueError:
            continue
        if not math.isfinite(v):continue
        seq.append((t,v))
    seq.sort()
    if len(set(t for t,v in seq))!=len(seq):
        raise ValueError("Duplicated hourly timestamp for tidal station")
    if any((b[0]-a[0]).total_seconds()%3600!=0 for a,b in zip(seq,seq[1:])):
        raise ValueError("Timestamp gap not an integer hour")
    start=datetime.strptime(START,"%Y%m%d")
    end=datetime.strptime(END,"%Y%m%d")+timedelta(days=1)
    if any(t<start or t>=end for t,v in seq):
        raise ValueError("Source NOAA returned data outside requested UTC week")
    v=[x[1] for x in seq]
    return {
      "NOAA_station_id":str(station),"NOAA_station_name":meta.get("name"),
      "NOAA_lat":meta.get("lat"),"NOAA_lon":meta.get("lon"),
      "n_verified_hourly_source_rows":len(seq),
      "n_expected_hours_in_7_days":168,
      "n_missing_hours_in_range":168-len(seq),
      "height_min_m_over_MLLW":round(min(v),4),
      "height_max_m_over_MLLW":round(max(v),4),
      "height_range_m":round(max(v)-min(v),4),
      "height_mean_m_over_MLLW":round(mean(v),4),
      "first_timestamp_UTC":seq[0][0].isoformat()+"Z",
      "last_timestamp_UTC":seq[-1][0].isoformat()+"Z",
      "raw_NOAA_JSON_SHA256":hashlib.sha256(raw).hexdigest(),
      "observation_basis":"NOAA verified hourly station gauge, not near-offshore hydrophone physical tide",
    }

def run():
    result={"version":"v141_noaa_gauge_hourly_preflight_1",
            "date_range_UTC":"2019-06-01 through 2019-06-07",
            "chosen_date_is_exemplar_not_joined_to_acoustic_deployments":True,
            "no_source_hydrophone_positions_yet":True,
            "physical_tide_at_acoustic_sites":"NOT_ESTIMATED",
            "time_zone":"GMT","NOAA_datum":"MLLW","station_gauges":{}}
    for label,id in STATIONS.items():
        p=dict(PARAMS);p["station"]=str(id)
        url=BASE+"?"+urlencode(p)
        try:
            with urlopen(Request(url,headers={"User-Agent":"Boids Scientific Data Quality Monitor/1.0"}),
                         timeout=40) as resp:
                raw=resp.read(2_000_000+1)
            if len(raw)>2_000_000:raise ValueError("NOAA source payload larger than cap")
            dat=parse_noaa(raw,id)
            dat["requested_URL"]=url
            result["station_gauges"][label]=dat
        except Exception as exc:
            result["station_gauges"][label]={"NOAA_station_id":str(id),"status":"SOURCE_UNAVAILABLE",
                                            "error_type":type(exc).__name__,
                                            "error":str(exc)[:240],
                                            "requested_URL":url}
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=run()
    out=ROOT/"results"/"noaa_hourly_verified_reference_gauges.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        # NOAA source verified observations and hashes may update; compare
        # ONLY source rows metadata, not speculative ecological interpretation.
        saved=json.loads(out.read_text())
        for label in STATIONS:
            a=result["station_gauges"][label]
            b=saved["station_gauges"][label]
            if a.get("n_verified_hourly_source_rows") != b.get("n_verified_hourly_source_rows"):
                raise AssertionError("Source gauge completeness changed: "+label)
            if a.get("height_range_m")!=b.get("height_range_m"):
                raise AssertionError("Source gauge range changed: "+label)
    else:
        out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V141_NOAA_GAUGES_START")
    print(json.dumps(result,ensure_ascii=False))
    print("V141_NOAA_GAUGES_END")
    if not any(x.get("n_verified_hourly_source_rows",0)>=150
               for x in result["station_gauges"].values()):
        sys.exit(2)

if __name__=="__main__":
    main()
