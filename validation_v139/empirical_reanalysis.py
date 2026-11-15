"""v139: real Roscoff acoustic event counts and physical tide×diel prediction test.

Source: exact 2026 published hourly soundscape/environment workbook. Unit:
one hydrophone and 20 selected noon-to-noon periods (421 retained hourly
observations); 59 tidal-flow-masked hours excluded. NOT 421 independent
animals, 20 coasts, or an unbiased sample of natural days.

Fixed comparison: intercept, night, night+tide height, night+tide+night×tide.
5 folds each holding 4 whole source sampling periods with one period from each
of the original four tidal coefficient classes. No random hour leakage.
Poisson log-score for *acoustic annotations per retained recorded hour*, not
latent fish activity or animal count. Negative-control tide phase shifts.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import exp, log, lgamma, isfinite
from pathlib import Path
from statistics import mean, median
from source_probe import acquire, read_xlsx_table_rows
from hourly_diagnostic import SOURCE_SHA, acol, number, key_from

ROOT=Path(__file__).resolve().parent
MODELS=("constant","night","night_height","night_height_interaction",
        "night_height_coefficient","night_height_coefficient_interaction")
SHIFTS=(-12,-9,-6,-3,0,3,6,9,12)
RIDGE=0.5

def source_rows():
    raw=acquire()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise AssertionError("Original Roscoff XLSX SHA-256 altered")
    tabs=read_xlsx_table_rows(raw)
    t=tabs["Table S1"]
    headers=t[3]
    if (headers.get("AP"),headers.get("AQ"),headers.get("E"),
        headers.get("J"))!=("Abundance","Richness","Period","Water_height_m"):
        raise ValueError("Primary table headers changed; manual review mandatory")
    cols=[acol(c) for c in range(16,42)]
    records=[]
    for n,row in sorted(t.items()):
        if n<4:continue
        date,hh=key_from(row.get("C"),row.get("D"))
        rep=str(int(float(row["B"])))
        counts=[number(row.get(k)) for k in cols]
        if any(c is None or c<0 or abs(round(c)-c)>1e-8 for c in counts):
            raise ValueError("Missing/nonintegral original sound counts")
        y=sum(int(round(x)) for x in counts)
        richness=sum(x>0 for x in counts)
        if number(row.get("AP"))!=y or number(row.get("AQ"))!=richness:
            raise ValueError("Source totals in AP/AQ do not match rederived 26-sound sums")
        if row.get("E") not in ("Day","Night"):
            raise ValueError("Original Period not binary; do not guess dawn/dusk exposure")
        anchor=date if hh>=12 else date-1
        records.append({
            "source_period_id":rep,"anchor":anchor,"date":date,"hour":hh,
            "night":int(row["E"]=="Night"),
            "coefficient_level":row["L"],
            "water_m":number(row.get("J")),
            "n_acoustic_annotations":y,"n_sound_types":richness})
    if len(records)!=421 or len({(x["date"],x["hour"]) for x in records})!=421:
        raise AssertionError("Actual source hourly series differs from paper n=421")
    if sum(x["n_acoustic_annotations"] for x in records)!=6172:
        raise AssertionError("Source reported sound count cannot be reconstructed")
    periods=defaultdict(list)
    for r in records: periods[r["source_period_id"]].append(r)
    if len(periods)!=20:
        raise AssertionError("Must have 20 unique source 24h blocks")
    for pid,arr in periods.items():
        if len({x["anchor"] for x in arr})!=1 or len({x["coefficient_level"] for x in arr})!=1:
            raise ValueError("Calendar/level group not unique within source day")
    env={}
    for n,row in sorted(tabs["Table S2"].items()):
        if n<3:continue
        try: key=key_from(row.get("A"),row.get("B"),is_fraction=True)
        except ValueError:continue
        if key in env:raise ValueError("Duplicate source env timestamp")
        env[key]=number(row.get("G"))
    windows={}
    for pid,arr in periods.items():
        anchor=arr[0]["anchor"]
        keys=[(anchor,hh) for hh in range(12,24)]+[(anchor+1,hh) for hh in range(0,12)]
        if any(env.get(k) is None for k in keys):
            raise ValueError("Source did not provide all 24 environmental hours per selected period")
        windows[pid]=[env[k] for k in keys]
        for x in arr:
            pos=(x["date"]-anchor)*24+x["hour"]-12
            if not 0<=pos<24 or abs(windows[pid][pos]-x["water_m"])>1e-9:
                raise AssertionError("Exact observed tide heights do not match hourly source table")
            x["index_in_period"]=pos
    return records,periods,windows

def design(row,model,shift=0,windows=None):
    night=row["night"]
    if model=="constant":return [1.]
    if model=="night":return [1.,float(night)]
    level=(windows[row["source_period_id"]][(row["index_in_period"]+shift)%24]
           if windows is not None else row["water_m"])
    if level is None:raise ValueError("Missing physical water level for model")
    z=level-5.0
    if model=="night_height":return [1.,float(night),z]
    if model=="night_height_interaction":return [1.,float(night),z,float(night)*z]
    if model in ("night_height_coefficient","night_height_coefficient_interaction"):
        cats=("Medium","High","Very High")
        lev=row["coefficient_level"]
        if lev not in ("Low",)+cats:
            raise ValueError("Unrecognized source tide coefficient category")
        d=[float(lev==c) for c in cats]
        ans=[1.,float(night),z]+d
        if model.endswith("interaction"):
            ans.extend(float(night)*q for q in d)
        return ans
    raise ValueError("Unregistered model "+model)

def solve(matrix,vector):
    """Gaussian elimination with pivot; tiny, dense positive Hessian."""
    n=len(vector)
    a=[list(matrix[i])+[vector[i]] for i in range(n)]
    for j in range(n):
        k=max(range(j,n),key=lambda q:abs(a[q][j]))
        if abs(a[k][j])<1e-11:raise ValueError("Hessian singular")
        a[j],a[k]=a[k],a[j]
        pivot=a[j][j]
        for m in range(j,n+1):a[j][m]/=pivot
        for ii in range(n):
            if ii==j:continue
            fac=a[ii][j]
            for m in range(j,n+1):a[ii][m]-=fac*a[j][m]
    return [a[i][n] for i in range(n)]

def fit(data,model,shift=0,windows=None,ridge=RIDGE):
    x=[design(r,model,shift,windows) for r in data]
    y=[r["n_acoustic_annotations"] for r in data]
    k=len(x[0])
    betas=[log(mean(y))]+[0.]*(k-1)
    def objective(b):
        s=0.
        for xx,yy in zip(x,y):
            eta=sum(v*t for v,t in zip(xx,b))
            if eta>30:return float("-inf")
            s+=yy*eta-exp(eta)
        return s-0.5*ridge*sum(bj*bj for bj in b[1:])
    for _ in range(70):
        grad=[0.]*k
        hess=[[0.]*k for _ in range(k)]
        for xx,yy in zip(x,y):
            eta=sum(v*t for v,t in zip(xx,betas))
            mu=exp(min(eta,30))
            for i in range(k):
                grad[i]+=xx[i]*(yy-mu)
                for j in range(k):
                    hess[i][j]+=mu*xx[i]*xx[j]
        for j in range(1,k):
            grad[j]-=ridge*betas[j]
            hess[j][j]+=ridge
        delta=solve(hess,grad)
        prev=objective(betas)
        scale=1.
        while scale>1e-8:
            cand=[b+scale*d for b,d in zip(betas,delta)]
            if objective(cand)>=prev-1e-9:break
            scale/=2
        if scale<=1e-8:raise RuntimeError("Poisson Newton line search failed")
        betas=cand
        if max(abs(scale*z) for z in delta)<1e-8:break
    return betas

def predict(row,betas,model,shift=0,windows=None):
    xx=design(row,model,shift,windows)
    return exp(sum(a*b for a,b in zip(xx,betas)))

def row_score(y,mu):
    if not(mu>0):raise ValueError("Predicted intensity must be positive")
    return y*log(mu)-mu-lgamma(y+1)

def stratified_folds(periods):
    levels=defaultdict(list)
    for pid,arr in periods.items():
        levels[arr[0]["coefficient_level"]].append(pid)
    if {k:len(v) for k,v in levels.items()}!={"Low":5,"Medium":5,"High":5,"Very High":5}:
        raise ValueError("Original study's five 24h periods per coefficient class altered")
    folds={}
    for level,pids in levels.items():
        for i,pid in enumerate(sorted(pids,key=int)):
            folds[pid]=i
    if Counter(folds.values())!=Counter({i:4 for i in range(5)}):
        raise AssertionError("Grouped holdout not balanced on selected tidal coefficient level")
    return folds

def crossed_association(records):
    """Raw four-class means; 4-class effect not inferable if missing windows."""
    out={}
    for level in ("Low","Medium","High","Very High"):
        out[level]={}
        for night in (0,1):
            vals=[r["n_acoustic_annotations"] for r in records if r["coefficient_level"]==level and r["night"]==night]
            out[level]["night" if night else "day"]={"n":len(vals),"mean":round(mean(vals),6) if vals else None}
    return out

def run():
    rows,periods,windows=source_rows()
    folds=stratified_folds(periods)
    result={
        "version":"v139_real_acoustic_poisson_grouped_cv_v1",
        "primary_doi":"10.1186/s12862-026-02521-z",
        "sha256_original_xlsx":SOURCE_SHA,
        "site":"Roscoff nearshore kelp forest, one acoustic hydrophone, France",
        "source_noon_noon_periods":20,"original_annotated_hours":len(rows),
        "original_annotations":sum(r["n_acoustic_annotations"] for r in rows),
        "excluded_flow_masking_hours":59,
        "no_independent_coast_replicates":True,
        "folds":"five grouped, one entire selected 24h period from each of the four original tidal-coefficient categories",
        "fold_assignments":dict(sorted(folds.items(),key=lambda kv:int(kv[0]))),
        "model_family":"Poisson quasi-predictive log-score of ANNOTATED ACOUSTIC SOUNDS PER RETAINED HOUR; no fish or animal counts",
        "fixed_penalty":"0.5 ridge for non-intercept coefficients; water level centered at physical 5 m",
        "predictor_candidates":MODELS,
        "crossed_raw_retained_hour_means":crossed_association(rows),
        "cross_validated":{},
        "circular_shift_hours_within_selected_24h_block":SHIFTS,
        "shifted_prediction_scores":{},
        "physical_alignment_rank":None,
        "original_source_missingness_not_at_random":True,
        "no_recovery_of_masked_audio":True,
        "interpretation_scope":"Single site, 20 explicitly selected days, dependent hourly observations, 59 flow-masked hours; descriptive predictive association conditional on observed acoustic windows",
        "globally_pooled_tide_by_solar_effect":"NOT_ESTIMATED",
        "boids_motion_parameters":"NOT_ESTIMATED",
    }
    all_preds={}
    for model in MODELS:
        preds={}
        beta_by_fold={}
        for fold in range(5):
            train=[r for r in rows if folds[r["source_period_id"]]!=fold]
            test=[r for r in rows if folds[r["source_period_id"]]==fold]
            b=fit(train,model,windows=windows)
            beta_by_fold[str(fold)]=[round(v,8) for v in b]
            for row in test:
                key=(row["date"],row["hour"])
                if key in preds:raise AssertionError("Repeated prediction event")
                preds[key]=predict(row,b,model,windows=windows)
        if len(preds)!=len(rows):raise AssertionError("Source heldout predictions incomplete")
        mean_ll=mean(row_score(r["n_acoustic_annotations"],preds[(r["date"],r["hour"])]) for r in rows)
        mae=mean(abs(r["n_acoustic_annotations"]-preds[(r["date"],r["hour"])]) for r in rows)
        result["cross_validated"][model]={
            "mean_poisson_log_score_per_retained_hour":round(mean_ll,8),
            "mean_absolute_error_sounds_per_hour":round(mae,6),
            "fold_coefficients":beta_by_fold,
            "heldout_retained_hours":len(rows),
        }
        all_preds[model]=preds
    null_score=result["cross_validated"]["constant"]["mean_poisson_log_score_per_retained_hour"]
    for model in MODELS:
        result["cross_validated"][model]["score_gain_over_constant_nats_per_hour"]=round(
            result["cross_validated"][model]["mean_poisson_log_score_per_retained_hour"]-null_score,8)
    # Source-unit robustness: compare held-out log predictive likelihood
    # of each interaction versus its exact matched additive counterpart,
    # without treating 421 hourly bins as independent animals or coasts.
    comparisons={
        "continuous_height_by_night":("night_height","night_height_interaction"),
        "semilunar_coefficient_by_night":(
            "night_height_coefficient","night_height_coefficient_interaction"),
    }
    result["interaction_increment_diagnostics"]={}
    for name,(simple,complex) in comparisons.items():
        diffs={}
        group_differences=defaultdict(list)
        group_categories={}
        fold_differences=defaultdict(list)
        category_differences=defaultdict(list)
        for r in rows:
            key=(r["date"],r["hour"])
            y=r["n_acoustic_annotations"]
            diff=(row_score(y,all_preds[complex][key])
                  -row_score(y,all_preds[simple][key]))
            diffs[key]=diff
            period=r["source_period_id"]
            group_differences[period].append(diff)
            group_categories[period]=r["coefficient_level"]
            fold_differences[folds[period]].append(diff)
            category_differences[r["coefficient_level"]].append(diff)
        per_period={k:round(mean(v),8) for k,v in sorted(group_differences.items(),key=lambda z:int(z[0]))}
        all_diff=list(diffs.values())
        n=len(all_diff)
        whole_mean=mean(all_diff)
        leave_one_block=[
            mean([d for k,arr in group_differences.items() if k!=pid for d in arr])
            for pid in group_differences]
        result["interaction_increment_diagnostics"][name]={
            "additive_model":simple,
            "interaction_model":complex,
            "mean_heldout_log_score_gain_nats_per_retained_hour":round(whole_mean,8),
            "mean_gain_by_heldout_fold":{str(k):round(mean(v),8) for k,v in sorted(fold_differences.items())},
            "positive_heldout_folds":sum(mean(v)>0 for v in fold_differences.values()),
            "mean_gain_by_coefficient_class":{k:round(mean(v),8) for k,v in sorted(category_differences.items())},
            "low_medium_unmasked_hours_gain_original_fit":round(mean(
                d for category in ("Low","Medium") for d in category_differences[category]),8),
            "high_veryhigh_partly_masked_hours_gain_original_fit":round(mean(
                d for category in ("High","Very High") for d in category_differences[category]),8),
            "per_selected_24h_block_heldout_mean_gain":per_period,
            "positive_selected_24h_blocks":sum(v>0 for v in per_period.values()),
            "min_leave_one_24h_period_out_gain":round(min(leave_one_block),8),
            "max_leave_one_24h_period_out_gain":round(max(leave_one_block),8),
            "inference_warning":"Descriptive fold and group sensitivity; not a valid p-value or independent-coast effect",
        }
    # Stronger masking sensitivity: train/test ONLY the ten completely
    # unmasked Low/Medium tidal-coefficient source periods (10 x 24 = 240h).
    # These are 2 ecological conditions within the same hydrophone, NOT
    # a transfer test to a new coast or a biologically random 10-day sample.
    clean=[r for r in rows if r["coefficient_level"] in ("Low","Medium")]
    if len(clean)!=240 or len({r["source_period_id"] for r in clean})!=10:
        raise AssertionError("Unmasked Low/Medium source subset is incomplete")
    clean_scores={}
    for model in ("night_height_coefficient","night_height_coefficient_interaction"):
        pred={}
        for fold in range(5):
            train=[r for r in clean if folds[r["source_period_id"]]!=fold]
            held=[r for r in clean if folds[r["source_period_id"]]==fold]
            b=fit(train,model,windows=windows)
            for r in held:
                pred[(r["date"],r["hour"])]=predict(r,b,model,windows=windows)
        if len(pred)!=240:raise AssertionError("Clean heldout predictions missing")
        clean_scores[model]=round(mean(
            row_score(r["n_acoustic_annotations"],pred[(r["date"],r["hour"])])
            for r in clean),8)
    result["fully_unmasked_low_medium_only_refit"]={
        "retained_observed_hours":240,
        "original_24h_periods":10,
        "group_folds":5,
        "models_and_heldout_scores":clean_scores,
        "increment_interaction_over_additive_nats_per_hour":round(
            clean_scores["night_height_coefficient_interaction"]-
            clean_scores["night_height_coefficient"],8),
        "estimand":"acoustic count rate in chosen 10 original days, no missing flow-mask HOURS but still selected by original study",
        "global_replication":"NO",
    }
    shift_scores={}
    for offset in SHIFTS:
        preds={}
        for fold in range(5):
            train=[r for r in rows if folds[r["source_period_id"]]!=fold]
            test=[r for r in rows if folds[r["source_period_id"]]==fold]
            b=fit(train,"night_height_interaction",shift=offset,windows=windows)
            for row in test:
                preds[(row["date"],row["hour"])]=predict(row,b,"night_height_interaction",shift=offset,windows=windows)
        shift_scores[offset]=round(mean(row_score(r["n_acoustic_annotations"],preds[(r["date"],r["hour"])]) for r in rows),8)
    result["shifted_prediction_scores"]={str(k):v for k,v in shift_scores.items()}
    real=shift_scores[0]
    result["physical_alignment_rank"]=1+sum(sc>real+1e-9 for off,sc in shift_scores.items() if off!=0)
    result["physical_alignment_ranks_among_shift_tests"]=len(SHIFTS)
    result["full_sample_coefficients"]={}
    for model in MODELS:
        result["full_sample_coefficients"][model]=[round(x,8) for x in fit(rows,model,windows=windows)]
    return result

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--check',action='store_true')
    args=cli.parse_args()
    result=run()
    if args.check:
        ref=ROOT/'results'/'real_acoustic_grouped_cv.json'
        if result!=json.loads(ref.read_text()):
            raise AssertionError('Frozen original-hour prediction audit changed')
    out=ROOT/"results"/"real_acoustic_grouped_cv.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print("V139_REAL_CV_START")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    print("V139_REAL_CV_END")

if __name__=="__main__":
    main()
