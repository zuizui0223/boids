#!/usr/bin/env python3
"""v40 post-outcome DESCRIPTIVE environment-support diagnostic, no refit."""
import argparse,collections,hashlib,json
from pathlib import Path
import numpy as np
from bat_diel_source_gate import original
from finland_night_activity_transfer import read_rows,source_nights,URL,MD5

OUT=Path("validation_v40/results/finland_region_climate_support_v40.json")
VAR=("mean_temp_C","night_length_h","sum_rain_mm","mean_wind_m_s")
def support(train,test):
    a=np.stack([r["weather"] for r in train]);b=np.stack([r["weather"] for r in test])
    q1=np.percentile(a,5,axis=0);q2=np.percentile(a,95,axis=0)
    outside=(b<q1)|(b>q2)
    result={}
    for i,name in enumerate(VAR):
        result[name]={"train_q05":float(q1[i]),"train_q95":float(q2[i]),
                       "train_median":float(np.median(a[:,i])),
                       "test_median":float(np.median(b[:,i])),
                       "test_outside_training_q05_q95_fraction":float(np.mean(outside[:,i]))}
    periods={r["period"] for r in train}
    result["joint_temp_or_nightlength_outside_fraction"]=float(np.mean(outside[:,:2].any(axis=1)))
    result["test_period_labels_unseen_in_training_nights"]=sum(r["period"] not in periods for r in test)
    result["year_labels_train_n"]=len({r["year"] for r in train})
    result["year_labels_test_n"]=len({r["year"] for r in test})
    result["source_test_nights"]=len(test)
    return result
def run():
    status,mime,blob=original(URL)
    if status!=200 or hashlib.md5(blob).hexdigest()!=MD5:
        raise RuntimeError("ORIGINAL_PROVIDER_MD5_STOP")
    rows,exc=source_nights(read_rows(blob))
    if len(rows)!=4208:raise ValueError("FROZEN_V39_SUPPORT_CHANGED_STOP")
    groups=sorted({r["region"] for r in rows})
    out={"status":"POST_OUTCOME_DESCRIPTIVE_SUPPORT_ONLY",
         "source_original_sha256":hashlib.sha256(blob).hexdigest(),
         "prior_v39_year_primary_gate":"NOT_SUPPORTED",
         "prior_v39_region_mean_M0_minus_M1_nats":-0.0388353233129198,
         "original_region_n":len(groups),"original_valid_nights":len(rows),
         "nighttime_activity_model_refitted":False,
         "new_pvalue_or_ecological_effect_inferred":False,
         "region_support":{}}
    for i,g in enumerate(groups,1):
        tr=[r for r in rows if r["region"]!=g]
        te=[r for r in rows if r["region"]==g]
        out["region_support"][f"region_group_{i}"]=support(tr,te)
    out["per_event_weather_or_activity_values_exported"]=False
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);args=p.parse_args()
    result=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V40_FINLAND_CLIMATE_SUPPORT="+json.dumps(result,sort_keys=True))
    assert result["nighttime_activity_model_refitted"] is False
