"""Familywise correction for THREE related acoustic screens, not ecological causality.

Strict versioned source values were already re-acquired and checked by
v145_blockshift.py and v145_onset_null.py. This stage does not use raw source
files; it adjusts all predeclared screened conditional shift-null comparisons
as one conservative family (32 presence, 27 exact onset, 32 ±1h onset).

Holm-Bonferroni only controls family-wise diagnostic error *if* each p-value
from its restricted shift null is valid. Exchangeability is not guaranteed;
daily shared weather/tide/noise and detector audibility remain potential
common causes; it cannot yield p-values for organismal social interactions.
"""
from __future__ import annotations
import json,argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRESENCE=ROOT/"results"/"source_blockshift_cochorus_null.json"
ONSET=ROOT/"results"/"onset_transition_original_blocknull.json"

def holm_adjust(pvalues):
    idx=sorted(range(len(pvalues)),key=lambda i:(pvalues[i],i))
    m=len(idx);last=0.;out=[None]*m
    for rank,j in enumerate(idx):
        last=min(1.0,max(last,(m-rank)*pvalues[j]))
        out[j]=round(last,6)
    return out

def combined():
    a=json.loads(PRESENCE.read_text())
    b=json.loads(ONSET.read_text())
    if a["screened_site_pairs"]!=32 or b["screened_comparisons_by_tolerance"]!={"0":27,"1":32}:
        raise AssertionError("Full prespecified source family changed")
    refs=[]
    for item in a["per_site_type_pair"]:
        if not item["shift_null"]:continue
        s=item["shift_null"]
        refs.append({
          "site":item["site"],"chorus_A":item["chorus_A"],"chorus_B":item["chorus_B"],
          "test_type":"same_hour_presence",
          "source_eligible_hours":item["retained_nominal_source_hours"],
          "observed":s["observed_simultaneous_chorus_hours"],
          "expected_under_restricted_day_shift":s["exact_uniform_shift_expectation_hours"],
          "observed_over_expected":s["observed_over_shift_expectation"],
          "restricted_shift_null_p_two_sided":s["two_sided_monte_carlo_compatibility_p"],
          "BH_q_reported_within_original_screen":s["BH_FDR_q_within_all_screened_site_pairs"],
        })
    for item in b["per_site_type_pair_timing"]:
        if not item["shift_null"]:continue
        s=item["shift_null"]
        refs.append({
          "site":item["site"],"chorus_A":item["chorus_A"],"chorus_B":item["chorus_B"],
          "test_type":"first_positive_hour_onset_tol"+str(item["tolerance_hours"]),
          "source_eligible_hours":item["source_hours_in_complete_runs"],
          "observed":s["observed_simultaneous_chorus_hours"],
          "expected_under_restricted_day_shift":s["exact_uniform_shift_expectation_hours"],
          "observed_over_expected":s["observed_over_shift_expectation"],
          "restricted_shift_null_p_two_sided":s["two_sided_monte_carlo_compatibility_p"],
          "BH_q_reported_within_original_screen":s["BH_FDR_q_within_all_screened_site_pairs"],
        })
    if len(refs)!=91:raise AssertionError("Expected 91 source screened tests")
    adj=holm_adjust([v["restricted_shift_null_p_two_sided"] for v in refs])
    for v,p in zip(refs,adj):
        v["Holm_familywise_91_comparison_adjusted_p"]=p
        v["screen_p_le_0p05_under_shift_null_only"]=p<=.05
    flagged=[v for v in refs if v["screen_p_le_0p05_under_shift_null_only"]]
    selected_total=sum(r["selected_source_eligible_hours"] for r in a["source_site_block_qc"])
    quality={
        "complete_7day_yearmonth_source_hours":selected_total,
        "original_nominal_recording_hours_after_explicit_off_and_noise":155871,
        "retained_source_fraction":round(selected_total/155871,6),
        "site_yearmonth_seven_day_run_blocks":sum(
            r["continuous_local_yearmonth_run_blocks_7days_plus"] for r in a["source_site_block_qc"]),
        "sites_with_less_than_80_percent_source_hours_retained":[
            r["site"] for r in a["source_site_block_qc"] if r["selected_fraction_of_nominal_effort"]<.8],
    }
    return {
      "version":"v145_source_fingerprint_combined_three_null_family_1",
      "original_source_DOI":"10.5061/dryad.q2bvq83sw",
      "source_published_study_DOI":"10.3354/meps14910",
      "source_workbooks_individual_sha256_matched":60,
      "selected_observability_qc":quality,
      "source_screened_family":{
          "same_hour_chorus_presence":32,
          "same_hour_hourly_presence_transition":27,
          "within_one_hour_hourly_presence_transition":32,
          "total_related_tests":91,
          "Monte_Carlo_repetitions_per_test":1999,
          "Monte_Carlo_minimal_nonzero_two_sided_p":.0005,
          "Holm_familywise_diagnostic_flags_at_0p05":len(flagged),
          "distinct_source_site_chorus_pairs_with_flags":len({
              (v["site"],v["chorus_A"],v["chorus_B"]) for v in flagged}),
          "reported_Holm_is_assumption_conditional_not_causal":True,
      },
      "all_screened_source_test_results":refs,
      "familywise_diagnostic_flags_only":flagged,
      "testable_acoustic_co_occurrence":"OBSERVED_BUT_POTENTIALLY_COMMON_ENVIRONMENT_DRIVEN",
      "true_interspecific_interaction":"NOT_IDENTIFIED",
      "instrument_audibility":"UNVERIFIED",
      "tidal_solar_global_pooled_biological_effect":"NOT_ESTIMATED",
    }

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--check",action="store_true")
    args=cli.parse_args()
    result=combined()
    p=ROOT/"results"/"joint_91_constrained_null_family.json"
    if args.check:
        assert result==json.loads(p.read_text()),"Saved v145 cross-family Holms differ"
    else:
        p.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V145_FAMILY_FINAL_START")
    print(json.dumps({
      "observation":result["selected_observability_qc"],
      "family":result["source_screened_family"],
      "Holm_flags":result["familywise_diagnostic_flags_only"],
      "ecological_causal_claim":result["true_interspecific_interaction"],
      "meta_effect":result["tidal_solar_global_pooled_biological_effect"],
    },ensure_ascii=False))
    print("V145_FAMILY_FINAL_END")
if __name__=="__main__":main()
