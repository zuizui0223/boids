"""v156: Roscoff 2026 ORIGINAL sound-type source admission for a 3-layer transfer.

Original source Ethève et al. 2026 / PMC13179613 supplementary XLSX SHA256
2df8fac...; 26 P:AO source sound types (not independently identified
fish species), 20 author-selected noon-to-noon 24h periods, 421 annotated
hours of 480 scheduled, 59 flow-noise masked hours.

Source-only: real *contiguous* previous-hour annotations available in same
original sampling period, and pre-outcome support for future whole-period
heldout sound-type prediction. NO fitted acoustic effects or p-values.

The candidate labels are selected for measurability using observed prevalence;
that is data-dependent exploratory SOURCE QC, not independent preregistration.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v139"))
from source_probe import acquire,read_xlsx_table_rows
from hourly_diagnostic import SOURCE_SHA,acol,number,key_from
from empirical_reanalysis import stratified_folds

OUTPUT=Path(__file__).parent/"results/roscoff_original_26_soundtypes_source_gate_v156.json"
MAX_TYPES=26
MIN_OBSERVED_CONTIGUOUS_LAGS=220
MIN_POS_PER_ALL_FOLDS=3
MIN_NEG_PER_ALL_FOLDS=3
MIN_TRAIN_POS=20
MIN_TRAIN_NEG=20
MIN_SOURCE_PERIODS_POSITIVE=6

def source():
    raw=acquire()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA:
        raise AssertionError("Original Roscoff XLSX SHA256 changed")
    tables=read_xlsx_table_rows(raw)
    source_table=tables["Table S1"]
    headers=source_table[3]
    types={acol(i):headers.get(acol(i)) for i in range(16,42)}
    if (len(types)!=MAX_TYPES or
        any(not isinstance(name,str) or not name for name in types.values()) or
        len(set(types.values()))!=MAX_TYPES or
        headers.get("AP")!="Abundance" or headers.get("AQ")!="Richness"):
        raise AssertionError("Roscoff original 26 sound types or totals headers changed")
    periods=defaultdict(list)
    annotated=[]
    source_count=0
    for rowid,row in sorted(source_table.items()):
        if rowid<4:continue
        dt,hour=key_from(row.get("C"),row.get("D"))
        anchor=dt if hour>=12 else dt-1
        idx=(dt-anchor)*24+hour-12
        if idx<0 or idx>=24:
            raise AssertionError("Roscoff noon-noon source position outside 24h")
        period=str(int(float(row["B"])))
        counts={}
        for col,name in types.items():
            v=number(row.get(col))
            if v is None or v<0 or abs(round(v)-v)>1e-7:
                raise ValueError("Invalid original sound type integer count")
            counts[name]=int(round(v))
        n=sum(counts.values())
        if n!=number(row.get("AP")) or sum(z>0 for z in counts.values())!=number(row.get("AQ")):
            raise AssertionError("Original source sound type sum/richness disagrees with publication")
        source_count+=n
        item={"period":period,"anchor":anchor,"index":idx,"source_clock_hour":hour,
              "coefficient_level":row.get("L"),
              "night":row.get("E")=="Night",
              "sound_positive":{k:int(v>0) for k,v in counts.items()}}
        if row.get("E") not in ("Day","Night"):
            raise AssertionError("Original day/night source label changed")
        periods[period].append(item)
        annotated.append(item)
    if len(annotated)!=421 or source_count!=6172 or len(periods)!=20:
        raise AssertionError("Original paper source n(421,6172,20) changed")
    folds=stratified_folds(periods)
    expected=480
    if len({(x["anchor"],x["period"],x["index"]) for x in annotated})!=len(annotated):
        raise AssertionError("Original source has duplicate annotated period-hour")
    per_period=[]
    prev_pairs=[]
    period_first=[]
    byfold_eligible=Counter()
    for period,rows in sorted(periods.items(),key=lambda z:int(z[0])):
        if len({r["anchor"] for r in rows})!=1:
            raise AssertionError("Source 24h sampling period date changed")
        if len({r["coefficient_level"] for r in rows})!=1:
            raise AssertionError("Source tidal coefficient class varies within original source day")
        hourmap={r["index"]:r for r in rows}
        if len(hourmap)!=len(rows):
            raise AssertionError("Duplicate source hour in original period")
        valid=0
        allpresent=sum(len(row["sound_positive"]) for row in rows)
        for idx in sorted(hourmap):
            if idx==0 or idx-1 not in hourmap:
                period_first.append((period,idx))
                continue
            now=hourmap[idx]
            prev=hourmap[idx-1]
            if now["anchor"]!=prev["anchor"] or now["index"]!=prev["index"]+1:
                raise AssertionError("Supposed previous-hour observation not contiguous")
            prev_pairs.append({
                "period":period,"fold":folds[period],"source_index":idx,
                "current":now["sound_positive"],
                "previous":prev["sound_positive"],
            })
            byfold_eligible[folds[period]]+=1
            valid+=1
        per_period.append({
            "source_period_id":int(period),"tidal_coefficient_class":rows[0]["coefficient_level"],
            "fold":folds[period],"observed_annotated_hours":len(rows),
            "tidal_flow_masked_hours":24-len(rows),
            "source_hours_with_true_previous_hour":valid,
            "lost_hours_without_true_previous_hour":len(rows)-valid,
            "source_n_sounds_if_sum_counts":"not_retained_by_this_source_gate",
        })
    if sum(q["observed_annotated_hours"] for q in per_period)!=421 or sum(q["tidal_flow_masked_hours"] for q in per_period)!=59:
        raise AssertionError("Source 421 observed and 59 flow-masked hours cannot be reconstructed")
    if len(prev_pairs)!=sum(q["source_hours_with_true_previous_hour"] for q in per_period):
        raise AssertionError("Previous observation support mismatch")
    if len(prev_pairs)<MIN_OBSERVED_CONTIGUOUS_LAGS:
        raise AssertionError("Insufficient source-real adjacent-hour observations for intended transfer")
    if set(folds.values())!=set(range(5)):
        raise AssertionError("Expected five original complete-period folds")
    reports=[]
    for type_name in sorted(types.values()):
        per_fold=[]
        for fold in range(5):
            test=[r for r in prev_pairs if r["fold"]==fold]
            train=[r for r in prev_pairs if r["fold"]!=fold]
            tp=sum(r["current"][type_name] for r in test)
            tr=sum(r["current"][type_name] for r in train)
            per_fold.append({
                "fold":fold,"train_true_source_hours":len(train),
                "heldout_true_source_hours":len(test),
                "train_sound_positive_hours":tr,"train_sound_negative_hours":len(train)-tr,
                "heldout_sound_positive_hours":tp,"heldout_sound_negative_hours":len(test)-tp,
                "positive_train_periods":len({r["period"] for r in train if r["current"][type_name]}),
                "positive_heldout_periods":len({r["period"] for r in test if r["current"][type_name]}),
            })
        periods_positive=len({r["period"] for r in prev_pairs if r["current"][type_name]})
        n=sum(r["current"][type_name] for r in prev_pairs)
        passes=all(
            item["heldout_sound_positive_hours"]>=MIN_POS_PER_ALL_FOLDS and
            item["heldout_sound_negative_hours"]>=MIN_NEG_PER_ALL_FOLDS and
            item["train_sound_positive_hours"]>=MIN_TRAIN_POS and
            item["train_sound_negative_hours"]>=MIN_TRAIN_NEG
            for item in per_fold
        ) and periods_positive>=MIN_SOURCE_PERIODS_POSITIVE
        reports.append({
            "original_type":type_name,
            "source_type_is_not_identified_fish_species":True,
            "n_soundtype_positive_with_actual_prev_hour":n,
            "n_soundtype_negative_with_actual_prev_hour":len(prev_pairs)-n,
            "n_positive_selected_24h_periods":periods_positive,
            "qualified_all_five_original_period_holdouts":passes,
            "five_fold_source_support":per_fold,
        })
    eligible=sorted([x for x in reports if x["qualified_all_five_original_period_holdouts"]],
                    key=lambda x:(-x["n_soundtype_positive_with_actual_prev_hour"],x["original_type"]))
    # This ranking is by type frequency, NOT by observed interaction effects.
    designated_primary=eligible[0]["original_type"] if eligible else None
    designated_partner=eligible[1]["original_type"] if len(eligible)>=2 else None
    return {
        "version":"v156_real_Roscoff_26_soundtypes_previoushour_source_admission_1",
        "article_DOI":"10.1186/s12862-026-02521-z",
        "original_workbook_sha256":sha,
        "original_workbook_bytes":len(raw),
        "n_independent_biological_coasts":1,
        "author_selected_24hour_periods":20,
        "original_scheduled_hours":expected,
        "real_source_annotated_hours":len(annotated),
        "source_flownoise_masked_hours":expected-len(annotated),
        "original_annotated_sound_events":source_count,
        "distinct_acoustic_type_labels":MAX_TYPES,
        "n_true_observed_previous_hour_pairs":len(prev_pairs),
        "n_source_hours_missing_real_previous_hour":len(annotated)-len(prev_pairs),
        "real_adjacent_source_hours_by_fold":dict(sorted(byfold_eligible.items())),
        "all_source_original_periods":per_period,
        "all_26_original_acoustic_type_source_support":reports,
        "prelocked_sample_source_gate":{
           "min_true_prev_observations_total":MIN_OBSERVED_CONTIGUOUS_LAGS,
           "heldout_positive_and_negative_each_fold":MIN_POS_PER_ALL_FOLDS,
           "train_positive_and_negative_each_fold":MIN_TRAIN_POS,
           "min_source_periods_with_positive_label":MIN_SOURCE_PERIODS_POSITIVE,
           "candidate_rule":"all-five-fold source-label support, rank by source positive hours then label, never by cross-type association"
        },
        "n_acoustic_types_passing_all_five_grouped_holdouts":len(eligible),
        "all_type_labels_with_source_support":[x["original_type"] for x in eligible],
        "first_type_by_source_prevalence_for_next_exploratory_fit":designated_primary,
        "second_type_by_source_prevalence_for_next_exploratory_fit":designated_partner,
        "all_source_type_model_comparisons":"NOT_YET_FITTED",
        "source_missing_hour_observation":"NOT_A_FISH_ABSENCE",
        "source_masking_related_to_high_water":"YES_58_OF_59_MASKED_HOURS_ON_HIGHER_HALF",
        "direct_acoustic_social_response":"NOT_IDENTIFIED",
        "pooled_global_tide_solar_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=source()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    if a.check:
        if not OUTPUT.exists():raise AssertionError("No original verified Roscoff v156 source receipt")
        # JSON stringifies integer fold IDs; compare the exact serialized source
        # values/keys rather than Python int-key vs JSON str-key container types.
        if json.loads(OUTPUT.read_text()) != json.loads(json.dumps(result,sort_keys=True)):
            raise AssertionError("Original sound-type source support changed")
        print("V156_ROSCOFF_ORIGINAL_SOURCE_REPLAY_PASS")
    else:
        OUTPUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("V156_ROSCOFF_SOURCE_GATE_START")
    print(json.dumps(result,ensure_ascii=True,sort_keys=True,separators=(",",":")))
    print("V156_ROSCOFF_SOURCE_GATE_END")

if __name__=="__main__":main()
