"""v142 empirical gauge-to-gauge exposure misclassification in held-out 2019 week.

Physical-source method only: real NOAA CO-OPS hourly water heights for 4 gauges.
This does NOT locate offshore fish chorus hydrophones or estimate animal
tide/solar interaction. 3d (72h) phase/median training then 4d heldout;
the site high/low category is site-wise *gauge median*, NOT inundation.
A simplified fixed local clock day=06:00..18:00 in America/Los_Angeles is
an illustration, not true solar elevation or measured night illumination.
"""
from __future__ import annotations
import json
from collections import Counter
from datetime import timezone
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo
from noaa_phase_compare import download_stations, best_lag, pearson

ROOT=Path(__file__).resolve().parent
TZ=ZoneInfo("America/Los_Angeles")
TRAIN_H=72

def exposure_errors(ref,local,lag,training_ref_median,training_target_median,clocks):
    """Best integer-hour lag convention: ref(t) resembles target(t+lag);
    thus predict target(i) from ref(i-lag)."""
    if len(ref)!=len(local) or len(ref)!=len(clocks):
        raise ValueError("Source gauge series length mismatch")
    ids=[i for i in range(TRAIN_H,len(ref)) if 0 <= i-lag < len(ref)]
    if not ids:raise ValueError("Empty heldout physical source period")
    errors=[]
    for i in ids:
        actual=local[i]>=training_target_median
        naive=ref[i]>=training_ref_median
        aligned=ref[i-lag]>=training_ref_median
        hour=clocks[i].replace(tzinfo=timezone.utc).astimezone(TZ).hour
        group="local_06_18_proxy_day" if 6<=hour<18 else "local_proxy_night"
        errors.append({
          "group":group,
          "naive_wrong":int(naive!=actual),
          "shifted_wrong":int(aligned!=actual),
          "actual_high":int(actual),
          "naive_high":int(naive),
          "shifted_high":int(aligned),
          "ref_height":ref[i],
          "shifted_ref_height":ref[i-lag],
          "target_height":local[i]
        })
    summary={}
    for group in ("all","local_06_18_proxy_day","local_proxy_night"):
        d=errors if group=="all" else [x for x in errors if x["group"]==group]
        if not d:raise ValueError("Missing day/night heldout segment")
        summary[group]={
          "n_heldout_hours":len(d),
          "wrong_highlow_naive":sum(x["naive_wrong"] for x in d),
          "wrong_highlow_corrected":sum(x["shifted_wrong"] for x in d),
          "fraction_wrong_naive":round(sum(x["naive_wrong"] for x in d)/len(d),6),
          "fraction_wrong_corrected":round(sum(x["shifted_wrong"] for x in d)/len(d),6),
          "naive_correl_source_water_height":round(pearson([x["ref_height"] for x in d],[x["target_height"] for x in d]),7),
          "shifted_correl_source_water_height":round(pearson([x["shifted_ref_height"] for x in d],[x["target_height"] for x in d]),7),
          "true_local_high_hour_count":sum(x["actual_high"] for x in d),
          "unshifted_reference_high_hour_count":sum(x["naive_high"] for x in d),
          "phase_shift_reference_high_hour_count":sum(x["shifted_high"] for x in d),
        }
    return summary

def run():
    source=download_stations()
    times=sorted(source["Monterey"])
    ref=[source["Monterey"][t] for t in times]
    cutoff=median(ref[:TRAIN_H])
    result={
      "version":"v142_source_noaa_heldout_gauge_exposure_disagreement_1",
      "original_source":"NOAA CO-OPS verified hourly_height; reference_gauges",
      "utc_week":"2019-06-01T00:00Z through 2019-06-07T23:00Z",
      "training":{"first_hours":TRAIN_H,"rule":"max Pearson over -3..+3 hourly lags, site-specific median high/low threshold from training only"},
      "heldout":{"following_hours":96,"last_hour_may_be_dropped_if_clock_shift_needs_future_sample":True},
      "night_definition":"clock 18:00-06:00 in America/Los_Angeles (approximation; NOT solar zenith)",
      "true_local_exposure":"above vs below the particular gauge train-period median (NOT actual inundation)",
      "source_reference_gauge":"Monterey 9413450",
      "statistics":{},
      "site_local_hydrophone_exposure":"NOT_MEASURED",
      "animal_tide_solar_effect":"NOT_ESTIMATED",
      "meta_effect":"NOT_ESTIMATED",
    }
    for site,levels in source.items():
        measured=[levels[t] for t in times]
        best,all_train=best_lag(ref[:TRAIN_H],measured[:TRAIN_H],max_lag=3)
        lag=best[0]
        summary=exposure_errors(ref,measured,lag,cutoff,median(measured[:TRAIN_H]),times)
        result["statistics"][site]={
          "lag_hours_chosen_exclusively_on_first_72h":lag,
          "training_reference_vs_site_correlation_at_chosen_lag":round(best[1],7),
          "original_site_168_hour_reference_median_m":round(cutoff,5),
          "site_training_72_hour_median_m":round(median(measured[:TRAIN_H]),5),
          "heldout_by_group":summary
        }
    return result

def main():
    result=run()
    path=ROOT/"results"/"gauge_heldout_exposure_error.json"
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    path.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if result!=json.loads(path.read_text()):
            raise AssertionError("Saved physical exposure diagnostic inconsistent with original NOAA data")
    else:path.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print("V142_GAUGE_DISAGREEMENT_START")
    print(json.dumps(result,ensure_ascii=False))
    print("V142_GAUGE_DISAGREEMENT_END")

if __name__=="__main__":main()
