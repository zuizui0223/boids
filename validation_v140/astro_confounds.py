"""v140 original Roscoff source: weather, lunar-light and temporal confounding audit.

This is a NEW robustness analysis of retained annotated acoustic hours, NOT
a causal effect, a reproduction of the source NB GLMM or a cross-coast meta.
Fivefold holdouts are the original S24_num 24h blocks, not individual hours.

No raw source data committed; original supplemental XLSX is redownloaded,
checked against the SHA256 frozen in v139, then source covariate rows are
matched exactly to the source 421 acoustic-hour rows.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from math import cos,sin,pi,exp,log,log1p,lgamma,isfinite
from pathlib import Path
from statistics import mean,median
import json,sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"validation_v139"))
from empirical_reanalysis import source_rows, stratified_folds, solve, row_score
from hourly_diagnostic import key_from,number
from source_probe import acquire,read_xlsx_table_rows

RIDGE=0.5
CATS=("Medium","High","Very High")
VARS=("temp","wind","wave","lux","moon","direction")
# All schemes are declared before data, not selected based on score.
SPECS={
 "minimal_add":("categorical",False,False,False),
 "minimal_tide_night":("categorical",False,True,False),
 "weather_add":("categorical",True,False,False),
 "weather_tide_night":("categorical",True,True,False),
 "weather_moon_night":("categorical",True,False,True),
 "weather_tide_and_moon_night":("categorical",True,True,True),
 "weather_continuous_add":("continuous",True,False,True),
 "weather_continuous_tide_night":("continuous",True,True,True),
}
PREDEFINED_COMPARISONS=(
 ("minimal_night_tidal_coefficient","minimal_add","minimal_tide_night"),
 ("adjusted_night_tidal_coefficient","weather_add","weather_tide_night"),
 ("adjusted_moonlight_night","weather_add","weather_moon_night"),
 ("adjusted_tide_given_moonlight","weather_moon_night","weather_tide_and_moon_night"),
 ("adjusted_moonlight_given_tide","weather_tide_night","weather_tide_and_moon_night"),
 ("adjusted_continuous_coefficient_given_moonlight",
      "weather_continuous_add","weather_continuous_tide_night"),
)

def augment_source(rows):
    raw=acquire()
    tab=read_xlsx_table_rows(raw)["Table S1"]
    expected={"F":"Temperature_degC","G":"Luminosity_lux",
              "H":"Wind_speed_m.s-1","I":"Wind_dir_deg","K":"Coeff_tide_mean_day",
              "M":"Moon_illum","O":"Sign_wave_height_m"}
    hdr=tab[3]
    for col,title in expected.items():
        if hdr[col]!=title:
            raise ValueError("Published environment column has changed: "+col)
    idx={}
    for no,r in sorted(tab.items()):
        if no<4:continue
        key=key_from(r.get("C"),r.get("D"))
        if key in idx:raise ValueError("Duplicate sound-hour keyed covariate")
        idx[key]={
            "temp":number(r.get("F")),"lux":number(r.get("G")),
            "wind":number(r.get("H")),"direction":number(r.get("I")),
            "wave":number(r.get("O")),"moon":number(r.get("M")),
            "tide_coefficient":number(r.get("K"))}
    if len(idx)!=421:raise ValueError("Not 421 source acoustic-hour covariate rows")
    for r in rows:
        val=idx[(r["date"],r["hour"])]
        if val["tide_coefficient"] is None:
            raise ValueError("Original tide coefficient unavailable")
        if val["moon"] is not None and not (0<=val["moon"]<=1):
            raise ValueError("Moon illumination fraction has unexpected scale")
        if val["lux"] is not None and val["lux"]<0:
            raise ValueError("Negative lux in original source")
        r.update(val)
    if len(rows)!=421:
        raise AssertionError("Original sample count changed")
    return rows

def scaled_value(field,v):
    if field=="temp":return (v-16)/4.
    if field=="wind":return (v-8)/5.
    if field=="wave":return (v-1)/1.
    if field=="lux":return log1p(v)/5.
    if field=="moon":return (v-0.5)/0.35
    if field=="direction":return v*pi/180
    raise ValueError(field)

def impute_from_training(train):
    out={}
    for k in VARS:
        v=[r[k] for r in train if r[k] is not None]
        if not v:raise ValueError("No measured training covariate: "+k)
        # Wind direction is cyclic; below we directly use raw cos/sin with wind
        # as a covariate; missing angle gets source-fold train circular mean.
        if k=="direction":
            s=mean(sin(x*pi/180) for x in v)
            c=mean(cos(x*pi/180) for x in v)
            angle=(180/pi)*(0 if s==0 and c==0 else __import__("math").atan2(s,c))
            out[k]=angle%360.
        else:out[k]=mean(v)
    return out

def design(r,spec,imputed):
    basis,weather,tide_night,moon_night=SPECS[spec]
    n=float(r["night"])
    z=r["water_m"]-5.
    if basis=="categorical":
        tid=[float(r["coefficient_level"]==cat) for cat in CATS]
    else:
        tid=[(r["tide_coefficient"]-70)/30.]
    feat=[1.,n,z]+tid
    if weather:
        value={k:(r[k] if r[k] is not None else imputed[k]) for k in VARS}
        feat.extend((
            scaled_value("temp",value["temp"]),
            scaled_value("wind",value["wind"]),
            scaled_value("wave",value["wave"]),
            scaled_value("lux",value["lux"]),
            scaled_value("moon",value["moon"]),
            sin(scaled_value("direction",value["direction"])),
            cos(scaled_value("direction",value["direction"])),
            (r["anchor"]-45158)/15.,
            ((r["anchor"]-45158)/15.)**2-1,
        ))
    if tide_night:
        feat.extend(n*t for t in tid)
    if moon_night:
        if not weather:raise ValueError("Moon interaction requires weather covariates")
        value=r["moon"] if r["moon"] is not None else imputed["moon"]
        feat.append(n*scaled_value("moon",value))
    return feat

def generalized_fit(rows,spec,outcome,means,ridge=RIDGE):
    xx=[design(r,spec,means) for r in rows]
    yy=[r[outcome] for r in rows]
    if not yy or min(yy)<0:raise ValueError("Nonnegative outcome required")
    k=len(xx[0])
    b=[log(mean(yy)+0.01)]+[0.]*(k-1)
    def objective(betas):
        ll=0.
        for vec,y in zip(xx,yy):
            eta=sum(c*v for c,v in zip(betas,vec))
            if abs(eta)>28:return float("-inf")
            ll+=y*eta-exp(eta)
        return ll-0.5*ridge*sum(x*x for x in betas[1:])
    for _ in range(80):
        g=[0.]*k
        h=[[0.]*k for _ in range(k)]
        for vec,y in zip(xx,yy):
            mu=exp(sum(c*v for c,v in zip(b,vec)))
            for j in range(k):
                g[j]+=vec[j]*(y-mu)
                for l in range(k):h[j][l]+=vec[j]*vec[l]*mu
        for j in range(1,k):
            g[j]-=ridge*b[j]
            h[j][j]+=ridge
        step=solve(h,g)
        scale=1.0
        base=objective(b)
        while scale>=1e-8:
            cand=[z+scale*d for z,d in zip(b,step)]
            if objective(cand)>=base-1e-8:break
            scale*=0.5
        if scale<1e-8:raise RuntimeError("Line search failed to improve Poisson fit")
        b=cand
        if max(abs(scale*d) for d in step)<1e-8:
            break
    return b

def pred(r,spec,means,b):
    return exp(sum(a*v for a,v in zip(b,design(r,spec,means))))

def nb_score(y,mu,shape):
    if not (mu>0 and shape>0):raise ValueError("Positive predicted mean and NB shape required")
    return (lgamma(y+shape)-lgamma(shape)-lgamma(y+1)+
            shape*log(shape/(shape+mu))+y*log(mu/(shape+mu)))

def estimate_nb_shape(train,add_model,means,coefs,outcome):
    expected=[pred(r,add_model,means,coefs) for r in train]
    excess=sum((r[outcome]-mu)**2-mu for r,mu in zip(train,expected))
    if excess<=0:return 10000.
    return min(10000.,max(.25,sum(mu**2 for mu in expected)/excess))

def compare(all_rows,folds,outcome,subgroup=None):
    if subgroup is not None:
        rows=[r for r in all_rows if r["coefficient_level"] in subgroup]
    else:rows=list(all_rows)
    allowed=set(SPECS)
    result={}
    held={}
    for fold in range(5):
        train=[r for r in rows if folds[r["source_period_id"]]!=fold]
        test=[r for r in rows if folds[r["source_period_id"]]==fold]
        if not train or not test:raise ValueError("Missing grouped train/test fold")
        missing=impute_from_training(train)
        for spec in SPECS:
            b=generalized_fit(train,spec,outcome,missing)
            trained={(r["date"],r["hour"]):pred(r,spec,missing,b) for r in test}
            if spec not in held:held[spec]={}
            held[spec].update(trained)
        for label,add,inter in PREDEFINED_COMPARISONS:
            ba=generalized_fit(train,add,outcome,missing)
            shape=estimate_nb_shape(train,add,missing,ba,outcome)
            if label not in result:result[label]=[]
            batch=[]
            for r in test:
                key=(r["date"],r["hour"])
                na=held[add][key];ni=held[inter][key]
                batch.append({
                    "id":r["source_period_id"],
                    "fold":fold,
                    "poisson":row_score(r[outcome],ni)-row_score(r[outcome],na),
                    "nb_common_shape":nb_score(r[outcome],ni,shape)-nb_score(r[outcome],na,shape),
                    "train_nb_shape":shape})
            result[label].extend(batch)
    out={}
    for label,add,inter in PREDEFINED_COMPARISONS:
        ds=result[label]
        if len(ds)!=len(rows):raise AssertionError("CV observations mismatched")
        per_fold={str(i):round(mean(x["poisson"] for x in ds if x["fold"]==i),8) for i in range(5)}
        by_id=defaultdict(list)
        for x in ds:by_id[x["id"]].append(x["poisson"])
        out[label]={
            "additive":add,"interaction":inter,
            "gain_poisson_per_retained_hour":round(mean(x["poisson"] for x in ds),8),
            "gain_nb_per_retained_hour_common_train_shape":round(mean(x["nb_common_shape"] for x in ds),8),
            "positive_folds":sum(v>0 for v in per_fold.values()),
            "fold_heldout_gain":per_fold,
            "n_heldout_source_days":len(by_id),
            "n_positive_source_days":sum(mean(v)>0 for v in by_id.values()),
            "min_source_day_loo_prediction_gain":round(min(mean(
                x["poisson"] for x in ds if x["id"]!=removed) for removed in by_id),8),
            "max_source_day_loo_prediction_gain":round(max(mean(
                x["poisson"] for x in ds if x["id"]!=removed) for removed in by_id),8),
            "train_fold_nb_shape_range":[round(min(x["train_nb_shape"] for x in ds),6),
                                         round(max(x["train_nb_shape"] for x in ds),6)],
            "source_period_prediction_gain":dict(sorted(
                ((id,round(mean(v),8)) for id,v in by_id.items()),key=lambda kv:int(kv[0]))),
        }
    out["candidate_scores_poisson"]={
        spec:round(mean(row_score(r[outcome],held[spec][(r["date"],r["hour"])]) for r in rows),8)
        for spec in SPECS}
    out["n_retained_hours"]=len(rows)
    out["n_source_24h_periods"]=len({r["source_period_id"] for r in rows})
    out["sound_count_or_richness"]=outcome
    return out

def run():
    rows,periods,windows=source_rows()
    augment_source(rows)
    folds=stratified_folds(periods)
    quality={
        k:{"present":sum(r[k] is not None for r in rows),
           "missing":sum(r[k] is None for r in rows)}
        for k in VARS+("tide_coefficient",)
    }
    # One coefficient per original source 24h sampling block?
    for pid,arr in periods.items():
        if len({r["tide_coefficient"] for r in arr})!=1:
            raise ValueError("Tidal coefficient source record differs within one 24h period")
    original_moon={pid:arr[0]["moon"] for pid,arr in periods.items()}
    original_coeff={pid:arr[0]["tide_coefficient"] for pid,arr in periods.items()}
    moon_corr=None
    if all(v is not None for v in original_moon.values()):
        u=list(original_moon.values());v=list(original_coeff.values())
        a=mean(u);b=mean(v)
        den=(sum((x-a)**2 for x in u)*sum((x-b)**2 for x in v))**0.5
        moon_corr=round(sum((x-a)*(y-b) for x,y in zip(u,v))/den,8) if den>0 else None
    return {
        "version":"v140_astro_confounding_acoustic_1",
        "source_original_primary_doi":"10.1186/s12862-026-02521-z",
        "original_source_SHA256":"2df8fac5749d804b8d16d98db065ba19dc3796a4a01ce1cfa87c56f5d622d0d0",
        "scope":"Roscoff 421 retained hours, 20 selected 24h blocks, 59 tide-related nonrandom masked hours; one independent coast",
        "weather_and_lunar_source_field_availability":quality,
        "moon_illum_tidal_coefficient_correlation_across_20_days":moon_corr,
        "predictor_transforms":"temp-16/4,wind-8/5,wave-1,log(1+lux)/5,moon=(fraction-.5)/.35,wind-direction sin/cos,day=(Excel anchor-45158)/15 and centered quadratic",
        "imputation":"train-fold-only mean for missing original weather covariate; circle mean for missing wind direction",
        "ridge_nonintercept":RIDGE,
        "heldout":"5 folds by whole source 24h period, each fold one day per tidal coefficient class; scores per retained hour",
        "nb_score":"negative binomial proper predictive score using training-only method-of-moments shape estimated from MATCHED additive Poisson mean; same shape for both compared models, not NB fitted model",
        "experiment_priorities":"Exploratory predeclared comparisons; no new ecological model selection supported from 421 hours",
        "results_sound_annotations_all":compare(rows,folds,"n_acoustic_annotations"),
        "results_sound_richness_all":compare(rows,folds,"n_sound_types"),
        "results_annotations_unmasked_low_medium":compare(rows,folds,"n_acoustic_annotations",("Low","Medium")),
        "one_coast_meta_effect":"NOT_ESTIMATED",
        "causal_tide_lunar_partition":"NOT_IDENTIFIED",
        "biological_individual_activity":"NOT_ESTIMATED",
        "observed_59_flow_masked_hours_imputed_as_zeros":False
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=run()
    path=Path(__file__).parent/"results"/"astro_confounds_source_cv.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    if args.check:
        assert json.loads(path.read_text())==result, "Source-refit differs from saved v140 values"
    else:path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    core=result["results_sound_annotations_all"]
    print("V140_ASTRO_DIAGNOSTIC_START")
    print(json.dumps({
        "moon_vs_coefficient_correlation":result["moon_illum_tidal_coefficient_correlation_across_20_days"],
        "data_quality":result["weather_and_lunar_source_field_availability"],
        "comparisons":{k:{i:v[i] for i in (
            "gain_poisson_per_retained_hour","gain_nb_per_retained_hour_common_train_shape",
            "positive_folds","n_positive_source_days")}
            for k,v in core.items() if k!="candidate_scores_poisson" and isinstance(v,dict) and "gain_poisson_per_retained_hour" in v},
        "richness":{k:round(v["gain_poisson_per_retained_hour"],8) for k,v in result["results_sound_richness_all"].items() if isinstance(v,dict) and "gain_poisson_per_retained_hour" in v},
        "unmasked":{k:round(v["gain_poisson_per_retained_hour"],8) for k,v in result["results_annotations_unmasked_low_medium"].items() if isinstance(v,dict) and "gain_poisson_per_retained_hour" in v},
        "all_results":result,
    },ensure_ascii=False))
    print("V140_ASTRO_DIAGNOSTIC_END")

if __name__=="__main__":
    main()
