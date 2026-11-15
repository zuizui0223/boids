"""v143 exploratory joint *proxy* tide and solar-night chorus presence from California originals.

Source: Dryad v7 all 60 original workbooks, 2019-04-01 through 2019-07-31 UTC,
6 actually deployed hydrophone sites in two sanctuaries.
NOAA physically verified hourly_height at nearest geographically available
REFERENCE GAUGE, NOT the true tide at an offshore hydrophone.

This is conditional acoustic DETECTION within NOMINALLY monitored hours after
explicit 'Off effort' and 'Noise' masks, NOT a fish activity/density estimate.
No inferred zeros for time outside metadata deployment, and no sound-mask
events treated as fish. The full paper-vs-hour denominator discrepancy stays open.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from functools import lru_cache
from hashlib import sha256
from math import floor,ceil,log
from pathlib import Path
from statistics import median
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import argparse,io,json,math,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v142"))
sys.path.insert(0,str(ROOT/"validation_v141"))
from chorus_60_source_audit import acquire,excel_reader,extract_sheet,numeric_excel
from masking_corrections import source_label,overlapping_hours,fully_inside_hours,FISH
from site_gauge_distance import SITES
from noaa_tide_preflight import STATIONS, BASE, PARAMS
from astral import Observer
from astral.sun import elevation

START=datetime(2019,4,1,tzinfo=timezone.utc)
END=datetime(2019,8,1,tzinfo=timezone.utc)
START_H=int((START-datetime(1899,12,30,tzinfo=timezone.utc)).total_seconds()//3600)
END_H=int((END-datetime(1899,12,30,tzinfo=timezone.utc)).total_seconds()//3600)
SELECTED=("MB01","MB02","CI01","CI02","CI04","CI05")
GAUGE={"MB01":"Monterey","MB02":"Monterey","CI01":"Santa_Barbara",
       "CI02":"Santa_Barbara","CI04":"Santa_Barbara","CI05":"Santa_Barbara"}
TYPES=("Bocaccio","Midshipman","White Seabass","UF310","UF440")
TIDE_SHIFTS=(-1,0,1)
SOLAR_THRESHOLDS=(-0.833,-6.0)
DENOM_POLICIES=("nominal","without_off","without_off_or_noise")
MIN_CELL_OPPORTUNITIES=20
MIN_EVENT_EACH_CELL=5

def hour_range(a,b):
    return set(range(max(START_H,math.ceil(a*24-1e-8)),
                     min(END_H,math.floor(b*24+1e-8))))

def overlap_range(a,b):
    return set(range(max(START_H,math.floor(a*24+1e-8)),
                     min(END_H,math.ceil(b*24-1e-8))))

def read_fish():
    buf=acquire()
    counts={}
    for site in SELECTED:
        counts[site]={"nominal":set(),"off":set(),"noise":set(),
                      "fish":defaultdict(set),"matched_deployments":0,
                      "source_fish_annotation_rows":Counter(),
                      "source_off_rows":0,"source_noise_rows":0}
    with zipfile.ZipFile(io.BytesIO(buf)) as z:
        paths=[p for p in z.namelist() if p.endswith((".xls",".xlsx"))]
        if len(paths)!=60:raise AssertionError("Source version membership changed")
        for name in sorted(paths):
            site=name.split("_")[0]
            if site not in SELECTED:continue
            tabs=excel_reader(z.read(name),name)
            det,dc=extract_sheet(tabs,"Detections")
            meta,mc=extract_sheet(tabs,"MetaData")
            item=counts[site]
            my_hours=set()
            for r in meta[1:]:
                a=numeric_excel(r[mc["start"]] if len(r)>mc["start"] else None)
                b=numeric_excel(r[mc["end"]] if len(r)>mc["end"] else None)
                if a is None or b is None or b<=a:continue
                my_hours.update(hour_range(a,b))
            if not my_hours:continue
            item["nominal"].update(my_hours)
            item["matched_deployments"]+=1
            for r in det[1:]:
                a=numeric_excel(r[dc["start"]] if len(r)>dc["start"] else None)
                b=numeric_excel(r[dc["end"]] if len(r)>dc["end"] else None)
                if a is None or b is None or b<=a or b-a>100:continue
                label=r[dc["label"]] if len(r)>dc["label"] else ""
                cls,_=source_label(label)
                blocks=overlap_range(a,b) & my_hours
                if not blocks:continue
                if cls in FISH:
                    item["fish"][cls].update(blocks)
                    item["source_fish_annotation_rows"][cls]+=1
                elif cls=="OFF_EFFORT":
                    item["off"].update(blocks);item["source_off_rows"]+=1
                elif cls=="SOURCE_NOISE":
                    item["noise"].update(blocks);item["source_noise_rows"]+=1
    for site,info in counts.items():
        if len(info["nominal"])<1200:
            raise AssertionError("Six-source site May-Jul deployment coverage unexpected: "+site)
    return counts

def noaa_hourly():
    out={}
    stamps={}
    for label in sorted(set(GAUGE.values())):
        args=dict(PARAMS)
        args.update({
            "station":str(STATIONS[label]),
            "begin_date":START.strftime("%Y%m%d"),
            "end_date":(END-timedelta(days=1)).strftime("%Y%m%d")})
        url=BASE+"?"+urlencode(args)
        req=Request(url,headers={"User-Agent":"Boids Scientific Source Audit v143/1.0"})
        with urlopen(req,timeout=80) as response:
            raw=response.read(4_000_000+1)
        if len(raw)>4_000_000:raise ValueError("NOAA source larger than bound")
        obj=json.loads(raw)
        if obj.get("error"):raise ValueError("NOAA public source error "+str(obj["error"])[:150])
        if str(obj.get("metadata",{}).get("id"))!=str(STATIONS[label]):
            raise ValueError("NOAA station source identity mismatch")
        expected=(END-START).days*24
        if len(obj.get("data",[]))<.95*expected:
            raise ValueError("NOAA missing >5% scheduled hourly tides at "+label)
        measurements={}
        for z in obj["data"]:
            if z.get("v") in (None,""):continue
            try:
                dt=datetime.strptime(z["t"],"%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                val=float(z["v"])
            except (ValueError,KeyError,TypeError):continue
            if math.isfinite(val):
                idx=int((dt-datetime(1899,12,30,tzinfo=timezone.utc)).total_seconds()//3600)
                measurements[idx]=val
        out[label]={"records":measurements,"source_sha256":sha256(raw).hexdigest(),
                    "source_hour_count":len(measurements),
                    "tidal_reference_median_m":median(measurements.values()),
                    "requested_URL":url}
    return out

@lru_cache(maxsize=14000)
def sun_height(site,hour):
    info=SITES[site]
    utc=datetime(1899,12,30,tzinfo=timezone.utc)+timedelta(hours=hour+.5)
    return elevation(Observer(latitude=info["lat"],longitude=info["lon"]),utc)

def safe_or(vals):
    out=set()
    for v in vals:out|=v
    return out

def contrast(table):
    # Each key is 00/01/10/11 for night flag and high tide proxy flag.
    rates={}
    for night in (0,1):
      for high in (0,1):
        key=str(night)+str(high)
        e=table[key]["exposure_hours"];n=table[key]["positive_hours"]
        if e<MIN_CELL_OPPORTUNITIES or n<MIN_EVENT_EACH_CELL or e-n<MIN_EVENT_EACH_CELL:
            return {"status":"STOP_INSUFFICIENT_2X2_SUPPORT",
                    "min_cell_hrs_required":MIN_CELL_OPPORTUNITIES,
                    "min_positive_and_negative_each_cell":MIN_EVENT_EACH_CELL}
        # Descriptive half-event continuity correction; no valid robust SE
        rates[key]=math.log((n+.5)/(e-n+.5))
    did=(rates["11"]-rates["10"])-(rates["01"]-rates["00"])
    return {"status":"DESCRIPTIVE_ONLY_UNCALIBRATED_TIDE_PROXY",
            "night_vs_day_tide_log_odds_diffdiff":round(did,6),
            "exp_diffdiff":round(math.exp(did),6),
            "reproduction":"This is not an independent coast or valid cluster SE/CI/p; audibility and gauge phase uncalibrated"}

def compute():
    fish=read_fish()
    tide=noaa_hourly()
    result={
      "version":"v143_2019_04_to_07_original_california_crossed_proxy_tide_solar_1",
      "original_study_doi":"10.3354/meps14910",
      "original_Dryad_doi":"10.5061/dryad.q2bvq83sw",
      "original_full_year_chorus_paper_repro_status":"UNRESOLVED_SOURCE_PERCENT_DISCREPANCY",
      "status":"EXPLORATORY_COASTAL_GAUGE_PROXY_NOT_OFFSHORE_PHYSICAL_TIDE",
      "period_start_UTC":START.isoformat(),"period_end_exclusive_UTC":END.isoformat(),
      "solar_horizon_threshold_degrees":list(SOLAR_THRESHOLDS),
      "gauge_clock_sensitivity_hours":list(TIDE_SHIFTS),
      "nominal_effort_fails_complete_audibility_gate":True,
      "site_mapped_source_hour_counts":{name:{k:val for k,val in obs.items() if k!="records"}
                                         for name,obs in tide.items()},
      "source_sites":list(SELECTED),
      "observations":{},
      "global_pooled_tide_solar_effect":"NOT_ESTIMATED",
      "independent_coast_effects_admitted_for_meta":0
    }
    all_sites={}
    for site,info in fish.items():
        night={th:set() for th in SOLAR_THRESHOLDS}
        for hour in info["nominal"]:
            el=sun_height(site,hour)
            for th in SOLAR_THRESHOLDS:
                if el<th:night[th].add(hour)
        off=info["off"] & info["nominal"]
        noise=info["noise"] & info["nominal"]
        efforts={
            "nominal":info["nominal"],
            "without_off":info["nominal"]-off,
            "without_off_or_noise":info["nominal"]-off-noise}
        gauged=tide[GAUGE[site]]
        hh=gauged["records"]; threshold=gauged["tidal_reference_median_m"]
        site_out={
          "site":site,
          "sanctuary":SITES[site]["sanctuary"],
          "source_deployments_overlapping_4month_window":info["matched_deployments"],
          "source_annotations_for_2019_window":dict(info["source_fish_annotation_rows"]),
          "source_explicit_off_rows":info["source_off_rows"],
          "source_noise_rows":info["source_noise_rows"],
          "effort_hours_by_policy":{k:len(e) for k,e in efforts.items()},
          "reference_gauge":GAUGE[site],
          "distance_to_reference_gauge_km":"SEE_V142_GEOGRAPHY_SOURCE",
          "diel_rates_by_type":{},
          "crossed_cells_by_type":{},
        }
        for typ in TYPES:
            positive=info["fish"].get(typ,set())
            for policy,effort in efforts.items():
                dname=policy
                for threshold_solar in SOLAR_THRESHOLDS:
                    solar_id=str(threshold_solar)
                    day=effort-night[threshold_solar]
                    dark=effort & night[threshold_solar]
                    name=policy+"|solar_lt_"+solar_id
                    nday=len(day & positive);nnight=len(dark & positive)
                    if dname=="without_off_or_noise" and threshold_solar==-0.833:
                        site_out["diel_rates_by_type"][typ]={
                            "day_nominal_hours":len(day),"night_nominal_hours":len(dark),
                            "day_positive_hours":nday,"night_positive_hours":nnight,
                            "day_fraction":round(nday/len(day),7) if day else None,
                            "night_fraction":round(nnight/len(dark),7) if dark else None,
                            "night_to_day_fraction_ratio":round((nnight/len(dark))/(nday/len(day)),5) if len(day)>0 and len(dark)>0 and nday>0 else None
                        }
                    for shift in TIDE_SHIFTS:
                        valid={h for h in effort if h+shift in hh}
                        cells={}
                        for flag_n,solar_set in ((0,valid-night[threshold_solar]),(1,valid & night[threshold_solar])):
                            for flag_hi in (0,1):
                                subset={h for h in solar_set if int(hh[h+shift]>=threshold)==flag_hi}
                                cells[str(flag_n)+str(flag_hi)]={
                                    "exposure_hours":len(subset),
                                    "positive_hours":len(subset & positive)
                                }
                        id=policy+"|solar_lt_"+solar_id+"|shift_"+str(shift)
                        site_out["crossed_cells_by_type"].setdefault(typ,{})[id]={
                            "cells":cells,"estimand":contrast(cells)}
        all_sites[site]=site_out
    result["observations"]=all_sites
    summary=[]
    for typ in TYPES:
        a=[]
        for site,obs in all_sites.items():
            t=obs["crossed_cells_by_type"][typ]["without_off_or_noise|solar_lt_-0.833|shift_0"]
            if t["estimand"]["status"].startswith("DESCRIPTIVE"):
                a.append({"site":site,"delta":t["estimand"]["night_vs_day_tide_log_odds_diffdiff"]})
        summary.append({"chorus_type":typ,"sites_with_supported_4cells":len(a),
                        "n_sites_with_positive_interaction":sum(v["delta"]>0 for v in a),
                        "site_descriptives":a})
    result["descriptive_selected_4cell_admission"]=summary
    source_sensitivity=[]
    for typ in TYPES:
        supported=0
        sign_changes=0
        stable=[]
        for site,obs in all_sites.items():
            values=obs["crossed_cells_by_type"][typ]
            baseline=values["without_off_or_noise|solar_lt_-0.833|shift_0"]["estimand"]
            if baseline["status"]!="DESCRIPTIVE_ONLY_UNCALIBRATED_TIDE_PROXY":
                continue
            supported+=1
            all_valid=[]
            for policy in DENOM_POLICIES:
                for solar_th in SOLAR_THRESHOLDS:
                    for shift in TIDE_SHIFTS:
                        key=policy+"|solar_lt_"+str(solar_th)+"|shift_"+str(shift)
                        z=values[key]["estimand"]
                        if z["status"]=="DESCRIPTIVE_ONLY_UNCALIBRATED_TIDE_PROXY":
                            all_valid.append(z["night_vs_day_tide_log_odds_diffdiff"])
            primary_shift=[
                values["without_off_or_noise|solar_lt_-0.833|shift_"+str(shift)]["estimand"]
                for shift in TIDE_SHIFTS]
            primary_vals=[q["night_vs_day_tide_log_odds_diffdiff"]
                          for q in primary_shift
                          if q["status"]=="DESCRIPTIVE_ONLY_UNCALIBRATED_TIDE_PROXY"]
            flips=any(x*baseline["night_vs_day_tide_log_odds_diffdiff"]<0 for x in all_valid)
            if flips:sign_changes+=1
            stable.append({
              "site":site,"baseline_log_odds_diffdiff":baseline["night_vs_day_tide_log_odds_diffdiff"],
              "other_supported_sensitive_conditions":len(all_valid),
              "minimum_supported_delta":round(min(all_valid),6) if all_valid else None,
              "maximum_supported_delta":round(max(all_valid),6) if all_valid else None,
              "sign_changes_under_some_predefined_sensitivity":flips,
              "fixed_solar_and_mask_tide_shift_deltas":primary_vals
            })
        source_sensitivity.append({
            "chorus_type":typ,
            "supported_primary_sites":supported,
            "sign_flip_sites_among_primary_supported":sign_changes,
            "site_sensitivities":stable,
            "not_a_statistical_significance_test":True,
        })
    result["denominator_solar_threshold_and_proxy_hour_shift_sensitivity"]=source_sensitivity
    result["site_nominal_clean_effort_hours_total"]=sum(v["effort_hours_by_policy"]["without_off_or_noise"] for v in all_sites.values())
    return result

def main():
    out=compute()
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    path=Path(__file__).parent/"results"/"california_2019_4month_proxy_tide_diel.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if out!=json.loads(path.read_text()):raise AssertionError("Saved source-proxy result changed")
    else:
        path.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    core={site:{
        "effort":v["effort_hours_by_policy"],
        "diel":v["diel_rates_by_type"],
        "crossed_supported":{typ:v["crossed_cells_by_type"][typ]["without_off_or_noise|solar_lt_-0.833|shift_0"]
                              for typ in TYPES}}
        for site,v in out["observations"].items()}
    print("V143_EMPIRICAL_START")
    print(json.dumps({
        "source_sites":out["source_sites"],
        "source_gauge_hours":out["site_mapped_source_hour_counts"],
        "descriptive_admission":out["descriptive_selected_4cell_admission"],
        "source_sensitivity":out["denominator_solar_threshold_and_proxy_hour_shift_sensitivity"],
        "clean_total_hours":out["site_nominal_clean_effort_hours_total"],
        "original_site_diagnostics":core,
        "global_effect":out["global_pooled_tide_solar_effect"],
    },ensure_ascii=False))
    print("V143_EMPIRICAL_END")

if __name__=="__main__":
    main()
