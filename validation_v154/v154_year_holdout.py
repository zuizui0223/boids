"""v154 genuine heldout-year California fish chorus conditional forecast.

Question, limited to acoustic observation: do independently VERIFIED NOAA coastal
hourly-height proxies improve the next-calendar-year (within-site) Bocaccio
acoustic annotation forecast beyond calendar/solar, and does an additional
contemporaneously observed sound-class indicator improve further? The latter
is an associative predictor, NOT a prospective forecast or social fish force.

The two partner contrasts (UF440 and White Seabass) were selected AFTER
v145-v152 results; this is exploratory, not an independent confirmatory study.
Train ONLY earlier local calendar years; hold out the entire later year. The
same exact original hours/target Y are used for ALL models, including +3 and
+11 day shifted NOAA *phase ghost* alternatives. No new biological p values.

SOURCE QUALITY: all 60 original Dryad XLS(X) member SHA256 via v144.original(),
all v145 9 site/day original source hours (136032), all v153 original source
NOAA 14 gauge-year content SHA256, plus any source-year needed for ghosts.
No offshore local tidal exposure or instrument audibility calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
for path in ("validation_v144","validation_v145","validation_v153"):
    sys.path.insert(0,str(ROOT/path))
from v145_blockshift import original
from full9_temporal import local_time,sun_alt,EPOCH
from noaa_source_gate import plan_frozen_source_hours,fetch_year

FROZEN=ROOT/"validation_v153/results/noaa_verified_tide_source_admission_v153.json"
RESULT=ROOT/"validation_v154/results/heldout_acoustic_gauge_v154.json"
RECEIPT=ROOT/"validation_v154/results/frozen_source_model_receipt_v154.json"
PAIRS=("UF440","White Seabass")
TARGET="Bocaccio"
TIDE_SHIFTS_H=(0,72,264) # physically wrong dates diagnostic, 0 is real
MODELS=("constant","solar_clock","real_gauge","gauge_ghost_3d","gauge_ghost_11d","real_gauge_plus_partner")
MIN_TRAIN_HOURS=1500
MIN_TEST_HOURS=720
MIN_TRAIN_TARGET_POS=80
MIN_TEST_TARGET_POS=20
MIN_TRAIN_PARTNER_POS=30
MIN_TEST_PARTNER_POS=10
MIN_POSITIVE_AND_NEGATIVE=20
MIN_GAUGE_SOURCE_FRACTION=.95
ALPHA_C=0.25 # fixed weak regularization, NOT tuned on this source
MAX_ITER=400
Y_CLIP=1e-6
NEAR_GAUGE_DISTANCE_KM=80.0

def solar_clock_features(hour,site):
    dt=local_time(hour)
    clock=dt.hour + .5
    doy=dt.timetuple().tm_yday
    a=sun_alt(site,hour)
    theta=2*math.pi*clock/24
    ye=2*math.pi*(doy-.5)/365.2425
    return [
        math.sin(theta),math.cos(theta),
        math.sin(2*theta),math.cos(2*theta),
        math.sin(3*theta),math.cos(3*theta),
        math.sin(ye),math.cos(ye),
        math.sin(2*ye),math.cos(2*ye),
        a/45.0,max(0.0,-a)/45.0,
        float(a<-.833),
    ]

def tide_proxy_features(gauges,station,h,offset,dark):
    center=h+offset
    # All positions verified, not fitted/interpolated or extrapolated.
    heights=[gauges[(station,(EPOCH+timedelta(hours=t)).year)].get(t) for t in
             (center-1,center,center+1)]
    if any(v is None for v in heights):
        return None
    slope=(heights[2]-heights[0])/2
    height=heights[1]
    return [height,slope,abs(slope),height*dark,slope*dark]

def loss(y,p):
    y=np.asarray(y,dtype=float)
    p=np.clip(np.asarray(p,dtype=float),Y_CLIP,1-Y_CLIP)
    return float(np.mean(-y*np.log(p)-(1-y)*np.log1p(-p)))

def brier(y,p):
    return float(np.mean((np.asarray(y,dtype=float)-np.asarray(p,dtype=float))**2))

def model_predictions(x_train,x_test,y_train):
    scaler=StandardScaler()
    a=scaler.fit_transform(x_train)
    b=scaler.transform(x_test)
    model=LogisticRegression(C=ALPHA_C,solver="lbfgs",
                             max_iter=MAX_ITER,tol=1e-6,
                             random_state=20261115)
    model.fit(a,y_train)
    return model.predict_proba(b)[:,1]

def score_models(full_features,y,partners,years,test_year):
    years=np.asarray(years,dtype=int)
    train=(years<test_year)
    test=(years==test_year)
    ntr=int(np.sum(train));nte=int(np.sum(test))
    if ntr<MIN_TRAIN_HOURS or nte<MIN_TEST_HOURS:
        return {"status":"STOP_HOURS","train_hours":ntr,"test_hours":nte}
    pos_train=int(np.sum(y[train]));pos_test=int(np.sum(y[test]))
    bp_train=int(np.sum(partners[train]));bp_test=int(np.sum(partners[test]))
    neg_train=ntr-pos_train;neg_test=nte-pos_test
    neg_b_train=ntr-bp_train;neg_b_test=nte-bp_test
    support={
        "train_hours":ntr,"test_hours":nte,
        "train_target_positive":pos_train,"test_target_positive":pos_test,
        "train_partner_positive":bp_train,"test_partner_positive":bp_test,
        "train_target_negative":neg_train,"test_target_negative":neg_test,
        "train_partner_negative":neg_b_train,"test_partner_negative":neg_b_test,
    }
    if (pos_train<MIN_TRAIN_TARGET_POS or pos_test<MIN_TEST_TARGET_POS or
        bp_train<MIN_TRAIN_PARTNER_POS or bp_test<MIN_TEST_PARTNER_POS or
        min(neg_train,neg_test,neg_b_train,neg_b_test)<MIN_POSITIVE_AND_NEGATIVE):
        return {"status":"STOP_SOURCE_RESPONSE_SUPPORT",**support}
    yt=y[test]
    constant=np.full(nte,float(np.mean(y[train])),dtype=float)
    xs=full_features
    ps={"constant":constant}
    for name,extra in [
        ("solar_clock","base"),
        ("real_gauge","real"),
        ("gauge_ghost_3d","ghost3"),
        ("gauge_ghost_11d","ghost11"),
        ("real_gauge_plus_partner","partner"),
    ]:
        x=xs[extra]
        ps[name]=model_predictions(x[train],x[test],y[train])
    L={k:loss(yt,ps[k]) for k in MODELS}
    B={k:brier(yt,ps[k]) for k in MODELS}
    def r(x):return round(float(x),8)
    return {
        "status":"EVALUATED_EXPLORATORY_COMPLETE_YEAR",
        **support,
        "score_nats_per_original_recorder_hour":{k:r(v) for k,v in L.items()},
        "brier_per_original_recorder_hour":{k:r(v) for k,v in B.items()},
        "score_improvements_nats_per_hour":{
            "solar_vs_constant":r(L["constant"]-L["solar_clock"]),
            "real_NOAA_tide_over_solar":r(L["solar_clock"]-L["real_gauge"]),
            "NOAA_phase_specificity_vs_best_wrong_gauge":r(
                min(L["gauge_ghost_3d"],L["gauge_ghost_11d"])-L["real_gauge"]),
            "contemporaneous_partner_over_solar_and_gauge":r(
                L["real_gauge"]-L["real_gauge_plus_partner"]),
            "full_model_over_constant":r(L["constant"]-L["real_gauge_plus_partner"]),
        },
        "probabilities_clip":Y_CLIP,
        "scores_exclude_missing_NOAA_source_hour_and_all_shifted_ghost_covariates_equally":True,
    }

def merge_sources():
    old=json.loads(FROZEN.read_text())
    if (old["source_gauge_years_verified"]!=14 or
        old["source_original_hydrophone_recording_hours"]!=136032 or
        old["source_gauge_hour_matched_recorder_hours"]!=136032):
        raise AssertionError("V153 source-only verified receipt changed")
    planned,source_keys=plan_frozen_source_hours()
    all_keys=set(source_keys)
    # Identify any NOAA year needed by the +3/+11-day ghost controls.
    for site,info in planned.items():
        station=info["reference_station_id"]
        for h in info["site_source_hours"]:
            for offset in TIDE_SHIFTS_H:
                for dh in (-1,0,1):
                    year=(EPOCH+timedelta(hours=h+offset+dh)).year
                    all_keys.add((station,year))
    gauge={};rawqc={}
    with ThreadPoolExecutor(max_workers=4) as executor:
        for (st,year),samples,qc in executor.map(lambda v:fetch_year(*v),sorted(all_keys)):
            gauge[(st,year)]=samples;rawqc[(st,year)]=qc
    frozen={(q["station_id"],q["year"]):q for q in old["NOAA_reference_source_years_requested"]}
    if len(frozen)!=14:raise AssertionError("V153 NOAA 14-year source receipt missing")
    for key,row in frozen.items():
        newer=rawqc.get(key)
        if newer is None or newer["status"]!="SOURCE_NOAA_VERIFIED":
            raise AssertionError("NOAA prior source gauge/year not obtainable")
        if newer["actual_provider_content_sha256"]!=row["actual_provider_content_sha256"]:
            raise AssertionError("NOAA prior gauge/year source content bytes changed "+str(key))
        if newer["verified_numeric_hours"]!=row["verified_numeric_hours"]:
            raise AssertionError("NOAA prior gauge/year coverage changed")
    # This acquisition happens after method/eligibility rules were fixed;
    # we never update source support gates to select favorable response signs.
    observed=original()
    if set(observed)!=set(planned):raise AssertionError("Original acoustic 9 site codes changed")
    return planned,gauge,rawqc,observed,old

def run():
    planned,gauge,qc,fish,frozen=merge_sources()
    total_original=0;total_eligible=0
    site_quality=[];cohort_rows=[]
    for site,info in sorted(planned.items()):
        station=info["reference_station_id"]
        src_hours=sorted(info["site_source_hours"])
        total_original+=len(src_hours)
        extra={}
        for z in PAIRS:extra[z]=[]
        feature_vectors=[]
        aligned_hours=[]
        localyears=[]
        target=[]
        partner_present={k:[] for k in PAIRS}
        observations=fish[site]["fish"]
        for h in src_hours:
            base=solar_clock_features(h,site)
            dark=base[-1]
            extras={offset:tide_proxy_features(gauge,station,h,offset,dark) for offset in TIDE_SHIFTS_H}
            if any(z is None for z in extras.values()):
                continue
            aligned_hours.append(h)
            localyears.append(local_time(h).year)
            target.append(int(h in observations.get(TARGET,set())))
            for p in PAIRS:
                partner_present[p].append(int(h in observations.get(p,set())))
            feature_vectors.append((
                base,extras[0],extras[72],extras[264]
            ))
        total_eligible+=len(aligned_hours)
        frac=len(aligned_hours)/len(src_hours) if src_hours else 0.0
        all_source_years=sorted({local_time(h).year for h in src_hours})
        qual={"site":site,"gauge":info["reference_gauge_name"],
              "gauge_station_id":station,
              "site_to_gauge_geodesic_distance_km":info["geodesic_station_distance_km"],
              "original_frozen_audio_source_hours":len(src_hours),
              "same_source_hours_including_both_wrong_gauge_dates":len(aligned_hours),
              "fraction_of_audio_source_hours_with_all_gauge_controls":round(frac,8),
              "all_actual_source_local_years":all_source_years,
              "true_offshore_tidal_exposure":"NOT_CALIBRATED"}
        site_quality.append(qual)
        if frac<MIN_GAUGE_SOURCE_FRACTION:
            for partner in PAIRS:
                cohort_rows.append({"site":site,"partner_sound_type":partner,
                                    "status":"STOP_GAUGE_GHOST_COMMON_HOUR_COVERAGE",
                                    "source_hour_fraction":round(frac,8)})
            continue
        base=np.asarray([row[0] for row in feature_vectors],dtype=np.float64)
        true=np.asarray([row[1] for row in feature_vectors],dtype=np.float64)
        ghost3=np.asarray([row[2] for row in feature_vectors],dtype=np.float64)
        ghost11=np.asarray([row[3] for row in feature_vectors],dtype=np.float64)
        y=np.asarray(target,dtype=np.int8)
        years=np.asarray(localyears,dtype=np.int32)
        for partner in PAIRS:
            b=np.asarray(partner_present[partner],dtype=np.int8)
            mats={
                "base":base,
                "real":np.column_stack((base,true)),
                "ghost3":np.column_stack((base,ghost3)),
                "ghost11":np.column_stack((base,ghost11)),
                "partner":np.column_stack((base,true,b)),
            }
            for year in all_source_years:
                res=score_models(mats,y,b,years,year)
                cohort_rows.append({"site":site,"target_sound_type":TARGET,
                                    "partner_sound_type":partner,
                                    "source_holdout_local_year":year,
                                    "source_only_gauge_distance_km":info["geodesic_station_distance_km"],
                                    **res})
    if total_original!=136032 or len(site_quality)!=9:
        raise AssertionError("Original frozen 9-site 136032 audio hours lost")
    summaries={}
    for partner in PAIRS:
        group=[r for r in cohort_rows if r.get("partner_sound_type")==partner]
        eligible=[r for r in group if r["status"]=="EVALUATED_EXPLORATORY_COMPLETE_YEAR"]
        def summarize(rows):
            if not rows:return {"n_evaluated_site_years":0,"n_unique_sites":0,"no_effect":"NOT_ESTIMATED"}
            gains=rows[0]["score_improvements_nats_per_hour"].keys()
            return {
                "n_evaluated_site_years":len(rows),
                "n_unique_sites":len(set(r["site"] for r in rows)),
                "full_source_years":sorted(set(r["source_holdout_local_year"] for r in rows)),
                "equal_siteyear_descriptives":{
                   g:{"mean_gain_nats_per_hour":round(float(np.mean([r["score_improvements_nats_per_hour"][g] for r in rows])),8),
                      "positive_siteyears":sum(r["score_improvements_nats_per_hour"][g]>0 for r in rows),
                      "negative_siteyears":sum(r["score_improvements_nats_per_hour"][g]<0 for r in rows)}
                   for g in gains
                },
                "interpretation":"no covariance-aware SE or independent-coast p value; same California source and correlated years",
            }
        summaries[partner]={
            "all_source_cohort_records":len(group),
            "source_eligible_siteyears":len(eligible),
            "all_geographic_source_sites":summarize(eligible),
            "geographic_sensitivity_NOAA_distance_max80km":summarize([
                r for r in eligible if r["source_only_gauge_distance_km"]<=NEAR_GAUGE_DISTANCE_KM]),
        }
    return {
        "version":"v154_original_9site_NOAA_year_heldout_acoustic_logistic_1",
        "data":"Kim 2025 Dryad v7 original hourly manual chorus plus NOAA CO-OPS verified coastal height proxies",
        "source_all_60_original_fish_sha256_checked":True,
        "noaa_original_14_stationyear_content_sha256_replayed":True,
        "actual_NOAA_gauge_year_requests_total":len(qc),
        "actual_NOAA_gauge_years_verified":sum(x["status"]=="SOURCE_NOAA_VERIFIED" for x in qc.values()),
        "extra_years_beyond_frozen_v153":sorted(f"{x[0]}-{x[1]}" for x in qc if x not in
                                                     {(r["station_id"],r["year"]) for r in frozen["NOAA_reference_source_years_requested"]}),
        "requested_source_gauge_hashes":[
            {"station_id":st,"utc_year":year,"source_status":q["status"],
             "verified_numeric_hours":q.get("verified_numeric_hours"),
             "body_SHA256":q.get("actual_provider_content_sha256")}
             for (st,year),q in sorted(qc.items())],
        "fixed_design":{
            "target":TARGET,"partners":list(PAIRS),
            "covariate_model_order":list(MODELS),
            "phase_ghost_timing_offsets_hours":list(TIDE_SHIFTS_H),
            "source_train_test":"strictly earlier vs full later local calendar year per source site; independent coast NOT claimed",
            "min_train_hours":MIN_TRAIN_HOURS,"min_test_hours":MIN_TEST_HOURS,
            "min_train_target_positive":MIN_TRAIN_TARGET_POS,
            "min_test_target_positive":MIN_TEST_TARGET_POS,
            "min_train_partner_positive":MIN_TRAIN_PARTNER_POS,
            "min_test_partner_positive":MIN_TEST_PARTNER_POS,
            "min_negative_each_class":MIN_POSITIVE_AND_NEGATIVE,
            "minimum_all_gauge_phases_same_hour_source_fraction":MIN_GAUGE_SOURCE_FRACTION,
            "elastic_or_posthoc_hyperparameter_search":"NONE",
            "LogisticRegression_C":ALPHA_C,"solver":"lbfgs",
            "source_model_basis":"fixed linear and 3 harmonic hour clock, 2 harmonic annual season, solar elevation/dark, coastal NOAA height and rise/fall, same-hour other acoustic presence",
            "all_preprocessors_train_only":True,
            "model_outcome":"manually annotated hourly presence, not fish abundance or true hourly audibility",
            "same_site_hour_support_for_all_models":True
        },
        "source_original_audio_hours":total_original,
        "matched_same_audio_hours_in_all_physically_real_and_wrong_date_controls":total_eligible,
        "site_quality":site_quality,
        "all_exploratory_siteyear_gated_scores":cohort_rows,
        "source_grouped_descriptive_summary":summaries,
        "rejected_or_unqualified_cohorts_not_relabelled":True,
        "new_statistical_p_values":"NOT_COMPUTED",
        "local_hydrophone_tide_temperature_upwelling_audibility":"NOT_CONTROLLED_OR_MEASURED",
        "direct_species_interaction_causation":"NOT_IDENTIFIED",
        "global_multi_coast_tide_solar_effect":"NOT_ESTIMATED",
    }

def source_safe_receipt(result):
    canonical=json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    valid=[r for r in result["all_exploratory_siteyear_gated_scores"]
           if r["status"]=="EVALUATED_EXPLORATORY_COMPLETE_YEAR"]
    return {
        "version":result["version"],
        "original_model_all_output_SHA256":hashlib.sha256(canonical.encode()).hexdigest(),
        "original_model_all_output_bytes":len(canonical.encode()),
        "all_60_original_workbook_SHA256_confirmed":result["source_all_60_original_fish_sha256_checked"],
        "all_14_previous_NOAA_provider_body_SHA256_confirmed":result["noaa_original_14_stationyear_content_sha256_replayed"],
        "model_fixed_design":result["fixed_design"],
        "n_source_original_hours":result["source_original_audio_hours"],
        "n_same_hours_all_gauge_and_wrong_phase_models":result["matched_same_audio_hours_in_all_physically_real_and_wrong_date_controls"],
        "n_site_year_partner_gates":len(result["all_exploratory_siteyear_gated_scores"]),
        "n_evaluated_original_holdout_siteyear_partner_contrasts":len(valid),
        "status_totals":dict(sorted(Counter(r["status"] for r in result["all_exploratory_siteyear_gated_scores"]).items())),
        "NOAA_original_source_years_verified":result["actual_NOAA_gauge_years_verified"],
        "all_grouped_descriptive_results":result["source_grouped_descriptive_summary"],
        "all_evaluated_group_scores_and_source_support":[
            {"site":r["site"],"test_local_year":r["source_holdout_local_year"],
             "partner":r["partner_sound_type"],
             "gauge_distance_km":r["source_only_gauge_distance_km"],
             "train_hours":r["train_hours"],"test_hours":r["test_hours"],
             "test_target_positive":r["test_target_positive"],
             "test_partner_positive":r["test_partner_positive"],
             "gains":r["score_improvements_nats_per_hour"]}
            for r in valid
        ],
        "no_new_statistical_p_value":True,
        "full_source_details_available_as_CI_artifact":True,
        "direct_fish_social_and_global_tide_x_solar":"NOT_IDENTIFIED_OR_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=run()
    receipt=source_safe_receipt(result)
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("Frozen original model source receipt unavailable")
        frozen=json.loads(RECEIPT.read_text())
        if frozen!=receipt:
            differences=[]
            def inspect(prefix,left,right):
                if len(differences)>=50:return
                if isinstance(left,dict) and isinstance(right,dict):
                    for key in sorted(set(left)|set(right)):
                        inspect(prefix+"."+str(key),left.get(key,"<missing>"),right.get(key,"<missing>"))
                elif isinstance(left,list) and isinstance(right,list):
                    if len(left)!=len(right):differences.append([prefix+".length",len(left),len(right)])
                    for i in range(min(len(left),len(right))):
                        inspect(prefix+"["+str(i)+"]",left[i],right[i])
                elif left!=right:
                    differences.append([prefix,left,right])
            inspect("receipt",frozen,receipt)
            print("V154_FROZEN_REPLAY_DIFFERENCES="+json.dumps(differences,ensure_ascii=True,separators=(",",":")))
            raise AssertionError("Original member-hash NOAA-clock source or model scores changed")
        print("V154_ORIGINAL_YEAR_HELDOUT_SOURCE_RECEIPT_REPLAY_PASS")
    else:
        print("V154_SOURCE_MODEL_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V154_SOURCE_MODEL_RECEIPT_END")
    print("V154_ORIGINAL_ACOUSTIC_FORECAST_SCOPE="
          +json.dumps({"input_hours":receipt["n_source_original_hours"],
                       "eligible_pairs":receipt["n_evaluated_original_holdout_siteyear_partner_contrasts"],
                       "summary":receipt["all_grouped_descriptive_results"]},
                      sort_keys=True,ensure_ascii=True))

if __name__=="__main__":main()
