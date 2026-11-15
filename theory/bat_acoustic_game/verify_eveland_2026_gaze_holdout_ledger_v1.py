"""Re-run original 2026 Carollia 8-bat source data at original pinned SHA.

Full 0.1/0.2/0.3sec original animal heldout aggregate equality; no source
original animal identifiers/calls/3D locations are rehosted. Does not attempt
to reproduce paper's original 70% turn-direction classification.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
from eveland_2026_carollia_real_gaze_holdout_v1 import run

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"EVELAND_2026_REAL_CAROLLIA_GAZE_BAT_HOLDOUT_LEDGER_V1.json"

def blobsha(p):
    b=(ROOT/p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def strict_equivalent(a,b,path=""):
    if isinstance(a,dict):
        assert isinstance(b,dict) and set(a)==set(b),("source dictionary mismatch",path)
        for k,x in a.items():strict_equivalent(x,b[k],path+"/"+k)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),("source list mismatch",path)
        for i,(x,y) in enumerate(zip(a,b)):strict_equivalent(x,y,path+"/"+str(i))
    elif isinstance(a,float):
        assert isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=2e-11,abs_tol=2e-11),("source numeric difference",path,a,b)
    else:
        assert a==b,("source scalar difference",path,a,b)

def main():
    ledger=json.loads(LEDGER.read_text())
    assert ledger["schema"]==1
    assert not ledger["new_animal_measurements"]
    assert not ledger["original_source_bat_IDs_trial_paths_call_level_values_rehosted"]
    for p,sha in ledger["code_blob_SHA"].items():
        assert blobsha(p)==sha,"SOURCE_MODEL_OR_PREOUTPUT_CONTRACT_CHANGED:"+p
    x=run()
    assert x["status"]=="SOURCE_REAL_CAROLLIA_3D_GAZE_GEOMETRY_INCREMENTAL_HOLDOUT"
    assert x["source_upstream_commit"]==ledger["original_source_git_commit"]
    assert x["source_original_bat_species"]=="Carollia perspicillata"
    assert not x["new_bat_measurements"] and not x["original_data_record_redistributed"]
    assert x["source_original"]["source_original_MAT_SHA256_sorted_set_commitment"]==ledger["source_original_30_MAT_sha256_commitment"]
    strict_equivalent(x["source_original"],ledger["source_original_file_quality_aggregate"],"source")
    assert set(x["results"])==set(ledger["numerical_results_by_predeclared_horizon_s"])=={"0.1","0.2","0.3"}
    for k,a in x["results"].items():
        b=ledger["numerical_results_by_predeclared_horizon_s"][k]
        strict_equivalent(a["quality"],b["quality"],k+"/quality")
        strict_equivalent(a["bat_heldout"],b["bat_heldout"],k+"/heldout")
        assert a["bat_heldout"]["original_bat_independent_folds"]==8
        assert a["bat_heldout"]["original_source_trials_scored"]==30
    x20=x["results"]["0.2"]["bat_heldout"]
    assert x20["original_source_calls_scored"]==1632
    g=x20["comparisons"]["gaze_minus_geometry"]
    assert g["bats_improved"]==5 and g["bats_worsened"]==3
    assert g["mean_bat_MAE_difference_deg"]>0
    assert g["whole_bat_bootstrap95_deg"][0]<0<g["whole_bat_bootstrap95_deg"][1]
    print("ORIGINAL_CAROLLIA_8_BAT_30_TRIALS_ALL_3_HORIZONS_SOURCE_REPLAY_MATCH")
    print("SOURCE_REAL_1632_CALLS_H0P2_NONIMPROVED_ACOUSTIC_GAZE_BEYOND_GEOMETRY")
    print("NO_2026_AUTHOR_70PCT_FIGURE_REPRODUCTION_OR_TWO_SPECIES_CLAIM")
    print("NO_NEW_MEASUREMENTS_OR_ORIGINAL_RECORD_RELEASE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
