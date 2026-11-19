#!/usr/bin/env python3
"""v39 frozen out-of-year bat acoustic quartile composition forecast, Finland."""
import argparse,collections,hashlib,io,json,math,re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from bat_diel_source_gate import original
from finland_night_bin_source import NS,values_of_cell

URL="https://zenodo.org/records/18298435/files/Data.xlsx?download=1"
MD5="444c510bcb154bf9272d620f1ce0ec5a"
OUT=Path("validation_v39/results/finland_thermal_night_allocation_v39.json")
BINS=("1","2","3","4")
ALLBINS=set(BINS+("BSS","ASR"))
FIELDS=("region","location","device","year","startdate","period","quartiles","n",
        "mean_temp","night_length","sum_rain","mean_wind")
SEED=20261119

def number(x):
    try:
        f=float(str(x).strip().replace(",","."))
        return f if math.isfinite(f) else None
    except (TypeError,ValueError):return None

def read_rows(data):
    """Read only frozen fields on first worksheet; never location coordinates."""
    groups=collections.defaultdict(list)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            a=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(t.text or "" for t in q.iter(NS+"t")) for q in a.findall(NS+"si")]
        with z.open("xl/worksheets/sheet1.xml") as fh:
            header=None
            for _,row in ET.iterparse(fh,events=("end",)):
                if row.tag!=NS+"row":continue
                vals={}
                for c in list(row):
                    m=re.match(r"([A-Z]+)",c.attrib.get("r",""))
                    if not m:continue
                    idx=0
                    for letter in m.group(1):idx=idx*26+ord(letter)-64
                    idx-=1
                    if header is None or header.get(idx) in FIELDS:
                        vals[idx]=values_of_cell(c,shared)
                if header is None:
                    header={i:str(v).strip() for i,v in vals.items()}
                    if not set(FIELDS).issubset(header.values()):
                        raise ValueError("PINNED_XLSX_SCHEMA_CHANGED")
                    row.clear();continue
                d={header.get(i,"UNKNOWN"):str(v).strip() for i,v in vals.items()}
                key=tuple(d.get(f,"") for f in ("region","location","device","year","startdate"))
                groups[key].append(d)
                row.clear()
    return groups

def source_nights(groups):
    good=[];exclude=collections.Counter()
    for key,obs in groups.items():
        by={r.get("quartiles"):r for r in obs}
        if len(obs)!=6 or set(by)!=ALLBINS:
            exclude["incomplete_original_six_bins"]+=1;continue
        q=[by[b] for b in BINS]
        counts=[number(r.get("n")) for r in q]
        if any(x is None or x<0 for x in counts):
            exclude["invalid_original_activity_minute_bins"]+=1;continue
        total=float(sum(counts))
        if total<=0:
            exclude["no_activity_in_sunset_to_sunrise_quartiles"]+=1;continue
        weather_names=("mean_temp","night_length","sum_rain","mean_wind")
        climate=[number(q[0].get(field)) for field in weather_names]
        if any(x is None for x in climate) or climate[1]<=0:
            exclude["invalid_climate_or_night_length"]+=1;continue
        if any(any(number(r.get(field)) is None or abs(number(r.get(field))-value)>1e-7
                   for field,value in zip(weather_names,climate)) for r in q[1:]):
            exclude["climate_differed_within_same_night"]+=1;continue
        period=q[0].get("period","")
        if not key[0] or not key[3] or not period:
            exclude["missing_region_year_or_period"]+=1;continue
        good.append({"year":key[3],"region":key[0],"period":period,
                     "weather":np.asarray(climate,float),
                     "count":np.asarray(counts,float),
                     "share":np.asarray(counts,float)/total})
    return good,dict(exclude)

def features(train,test,include_rain_wind=False):
    periods=sorted({r["period"] for r in train})
    xtrain=np.asarray([r["weather"] for r in train])
    xtest=np.asarray([r["weather"] for r in test])
    scaler=StandardScaler().fit(xtrain)
    a=scaler.transform(xtrain);b=scaler.transform(xtest)
    def make(rows,x):
        cat=np.asarray([[float(row["period"]==p) for p in periods[:-1]] for row in rows])
        cols=np.column_stack((cat,x[:,0],x[:,1],x[:,0]*x[:,1]))
        return np.column_stack((cols,x[:,2],x[:,3])) if include_rain_wind else cols
    return make(train,a),make(test,b)

def softmax(logits):
    a=np.column_stack((logits,np.zeros(len(logits))))
    a=np.exp(a-a.max(axis=1,keepdims=True))
    return a/a.sum(axis=1,keepdims=True)

def predict(train,test,which):
    if which=="M0":
        by=collections.defaultdict(list)
        for row in train:by[row["period"]].append(row["share"])
        global_mean=(np.asarray([r["share"] for r in train]).sum(axis=0)+.5)/(len(train)+2.)
        means={k:(np.asarray(v).sum(axis=0)+.5)/(len(v)+2.) for k,v in by.items()}
        return np.asarray([means.get(r["period"],global_mean) for r in test])
    a,b=features(train,test,include_rain_wind=(which=="M2"))
    counts=np.stack([r["count"] for r in train])
    target=np.log((counts[:,:3]+.5)/(counts[:,3:4]+.5))
    model=Ridge(alpha=10.,fit_intercept=True)
    model.fit(a,target)
    return softmax(model.predict(b))

def losses(train,test):
    actual=np.stack([r["share"] for r in test])
    result={}
    for m in ("M0","M1","M2"):
        predicted=np.clip(predict(train,test,m),1.e-10,1.)
        result[m]=float(np.mean(-(actual*np.log(predicted)).sum(axis=1)))
    return result

def exact_sign(k,n):
    return float(sum(math.comb(n,i) for i in range(k,n+1))/2**n) if n else None

def summary(gains,base,thermal):
    n=len(gains)
    if n==0:return {"status":"NO_TEST_GROUPS"}
    rng=np.random.default_rng(SEED)
    x=np.asarray(gains)
    b=np.asarray([np.mean(rng.choice(x,size=n,replace=True)) for _ in range(10000)])
    lo,hi=np.percentile(b,[2.5,97.5])
    k=int(np.sum(x>0));p=exact_sign(k,n)
    return {"status":"EVALUATED","group_n":n,"positive_group_n":k,
            "equal_group_loss_M0":float(np.mean(base)),
            "equal_group_loss_M1":float(np.mean(thermal)),
            "equal_group_M0_minus_M1_nats":float(x.mean()),
            "whole_group_bootstrap_95":[float(lo),float(hi)],
            "one_sided_exact_positive_sign_p":p,
            "primary_positive_gate":bool(x.mean()>0 and lo>0 and p<=.05)}

def transfer(rows,group,min_groups,min_test):
    groups=collections.defaultdict(list)
    for r in rows:groups[r[group]].append(r)
    support={g:v for g,v in groups.items() if len(v)>=min_test}
    if len(support)<min_groups:
        return {"status":"GROUP_HOLDOUT_SUPPORT_STOP",
                "groups_over_predeclared_min":len(support)}
    primary=[];secondary=[];base=[];therm=[];per=[]
    for label,test in sorted(support.items()):
        train=[r for r in rows if r[group]!=label]
        if len(train)<300:continue
        losses_=losses(train,test)
        delta=losses_["M0"]-losses_["M1"]
        primary.append(delta);secondary.append(losses_["M1"]-losses_["M2"])
        base.append(losses_["M0"]);therm.append(losses_["M1"])
        per.append({"group":str(label) if group=="year" else "region_group_"+str(len(per)+1),
                    "n_nights":len(test),"loss_M0":losses_["M0"],
                    "loss_M1":losses_["M1"],"loss_M2":losses_["M2"],"M0_minus_M1":delta,
                    "M1_minus_M2":losses_["M1"]-losses_["M2"]})
    r=summary(primary,base,therm)
    r["fixed_secondary_M1_minus_M2_equal_group_nats"]=float(np.mean(secondary)) if secondary else None
    r["per_holdout_group"]=per
    return r

def evaluate(groups):
    rows,exc=source_nights(groups)
    years=collections.Counter(r["year"] for r in rows)
    regions=collections.Counter(r["region"] for r in rows)
    eligible_years=sum(n>=30 for n in years.values())
    eligible_regions=sum(n>=30 for n in regions.values())
    support={"original_active_detector_night_keys":len(groups),
             "valid_night_compositions":len(rows),"excluded":exc,
             "years_n":len(years),"regions_n":len(regions),
             "years_with_30_nights":eligible_years,"regions_with_30_nights":eligible_regions,
             "source_publication_active_nights_conditioned":True}
    result={"source":"Zenodo18298435_original_Data.xlsx","source_provider_md5":MD5,
            "programme":"v39_post_structure_outcome_blind_six_label_Q1_Q4",
            "frozen_contract":"docs/V39_FINLAND_THERMAL_NIGHT_ALLOCATION_TRANSFER_FREEZE.md",
            "source_support":support,"source_phenomenon_in_original_article_is_prior_art":True,
            "bat_population_or_cognitive_causality_claim":False,
            "independent_cross_country_replication":False,
            "source_original_bat_coords_or_raw_rows_exported":False}
    if len(rows)<1000 or eligible_years<5 or eligible_regions<2:
        result["status"]="NIGHT_SOURCE_SUPPORT_STOP";return result
    result["primary_whole_year"]=transfer(rows,"year",5,30)
    result["secondary_whole_region"]=transfer(rows,"region",2,30)
    result["status"]="FROZEN_EVALUATED" if result["primary_whole_year"]["status"]=="EVALUATED" else "HOLDOUT_SUPPORT_STOP"
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    status,mime,data=original(URL)
    if status!=200 or hashlib.md5(data).hexdigest()!=MD5:
        raise RuntimeError("SOURCE_MD5_ACCESS_STOP")
    r=evaluate(read_rows(data))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    compact={k:r.get(k) for k in ("status","source_support")}
    for kind in ("primary_whole_year","secondary_whole_region"):
        if kind in r:
            compact[kind]={k:v for k,v in r[kind].items() if k!="per_holdout_group"}
    print("V39_FROZEN_FINLAND_THERMAL_TRANSFER="+json.dumps(compact,sort_keys=True))
    print("V39_NO_GLOBAL_OR_CAUSAL_BAT_BEHAVIOR_LAW")

if __name__=="__main__":
    main()
