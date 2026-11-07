"""Fresh authoritative source replay and artifact identity for bat within-source contrast.

Only original 2024 source workbook is a strict byte-level authority; transport
ZIP metadata changes are not treated as original-data drift. No new bats.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
from molossus_withinbat_highdensity_v1 import run

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_SOURCE_LEDGER_V1.json"
BLOBS={
 "source_code_blob_sha":"molossus_withinbat_highdensity_v1.py",
 "preoutput_contract_blob_sha":"MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_PREOUTPUT_2026_11_07.md",
 "test_code_blob_sha":"test_molossus_withinbat_highdensity_v1.py"
}

def gitblob(p):
    b=(ROOT/p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def structurally_same(a,b,path=""):
    if isinstance(a,dict):
        assert isinstance(b,dict) and set(a)==set(b),(path,"keys",set(a)^set(b))
        for key,v in a.items():structurally_same(v,b[key],path+"/"+key)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),(path,"length")
        for i,(x,y) in enumerate(zip(a,b)):structurally_same(x,y,path+"/"+str(i))
    elif isinstance(a,float):
        assert isinstance(b,(int,float))
        assert math.isclose(a,b,rel_tol=2e-12,abs_tol=2e-12),(path,a,b)
    else:
        assert a==b,(path,a,b)

def main():
    pinned=json.loads(LEDGER.read_text())
    assert pinned["schema"]==1
    assert not pinned["new_measurements"]
    for key,p in BLOBS.items():
        assert pinned[key]==gitblob(p),"SOURCE_OR_FROZEN_CONTRACT_CHANGED "+p
    original=run()
    assert original["status"]=="SECONDARY_PUBLISHED_WITHIN_BAT_HIGH_CALL_DENSITY"
    assert original["source_workbook_sha256"]==pinned["original_XLSX_SHA256"]
    assert original["original_bats"]==10 and original["original_source_rows"]==4299
    assert not original["new_bat_measurements"]
    assert not original["original_bat_ids_or_five_second_rows_exported"]
    for source,reported in original.items():
        if source not in ("primary_original_all_ten","sensitivity_overlapping_nine_complete_secgroup"):continue
        prior=pinned["original_source_cohorts"][source]
        assert reported["source_bats"]==prior["source_bats"]
        assert reported["source_5s_windows"]==prior["observed_5s_rows"]
        assert reported["high_density_original_bats"]==prior["source_bats_with_high_call_windows"]
        assert reported["high_density_original_attacks"]==prior["total_high_attacks"]
        expected_windows=112 if source=="primary_original_all_ten" else 108
        assert reported["high_density_original_windows"]==expected_windows
        structurally_same(reported["by_reference"],prior["comparisons"],source+"/comparisons")
        structurally_same(reported["high_vs_moderate_time_thirds"],prior["flight_time_thirds"],source+"/flight_time_thirds")
    pair=original["primary_original_all_ten"]["by_reference"]["moderate"]
    time=original["primary_original_all_ten"]["high_vs_moderate_time_thirds"]
    assert pair["eligible_bats"]==6
    assert pair["high_attacks_eligible"]==36
    assert pair["reference_attacks_eligible"]==173
    assert pair["high_successes_eligible"]==10
    assert pair["reference_successes_eligible"]==119
    assert time["eligible_bat_flight_third_strata"]==9
    assert time["original_high_attacks_covered"]==36
    assert time["source_bats_with_time_matched_high_and_moderate_attacks"]==6
    print("ORIGINAL_SOURCE_WITHIN_BAT_10_AND_9_COHORTS_ALL_THREE_CONTRASTS_MATCH")
    print("ORIGINAL_2024_XLSX_SOURCE_SHA",original["source_workbook_sha256"])
    print("SIX_BATS_PAIRED_HIGH_VS_MODERATE_AND_9_TIME_STRATA_VERIFIED")
    print("NO_NEW_MEASUREMENTS_NO_CAUSAL_SONAR_MECHANISM_ORIGINAL_STUDY_PRIOR_ART")
    return 0

if __name__=="__main__":raise SystemExit(main())
