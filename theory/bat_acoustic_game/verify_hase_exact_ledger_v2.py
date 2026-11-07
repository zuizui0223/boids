"""Compare committed exact-source-conditional bat theory results to full fresh replay.

No raw bat records, no 2020/2026 original executable reproduction.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"HASE_2026_SOURCE_TIMING_WAVEFORM_EXACT_LEDGER_V2.json"
AUDIT=ROOT/"HASE_WAVEFORM_V2_POSTOUTPUT_NUMERIC_AUDIT_V1.json"
SRC=ROOT/"source_timing_waveform_v2.py"
def sha_blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def close(a,b,tol=1e-10):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol),(a,b)
def main():
    a=json.loads(AUDIT.read_text())
    b=json.loads(LEDGER.read_text())
    assert a["schema"]==1 and b["schema"]==2
    assert b["source_implementation_git_blob_sha"]==sha_blob(SRC)
    assert a["source_original_code_git_blob_sha"]==sha_blob(SRC)
    assert not b["new_measurements"] and not b["original_2026_simulator_reproduced"]
    assert not a["new_animal_measurements"] and not a["source_2026_group_reproduced"]
    assert len(a["worlds"])==len(b["all_12_predeclared_scenes_exact_nonbinned"])==12
    for x,y in zip(a["worlds"],b["all_12_predeclared_scenes_exact_nonbinned"]):
        assert (x["n"],x["scale"],x["waveform"]) == (
            y["group_size"],y["synthetic_3D_scale"],y["waveform_family"])
        n=x["n_focal_emissions"]
        assert n==y["focal_emission_count"]
        assert x["n_eligible_other_pulses"]==y["eligible_other_pulse_count"]
        no=int(round(x["exact_lag_per_focal_no_JAR"]*n))
        yes=int(round(x["exact_lag_per_focal_JAR"]*n))
        assert no==y["no_JAR_lag_match_count"],(x["n"],x["waveform"],"baseline",no,y["no_JAR_lag_match_count"])
        assert yes==y["JAR_lag_match_count"],(x["n"],x["waveform"],"JAR",yes,y["JAR_lag_match_count"])
        close(x["exact_delta_lag"],y["JAR_minus_no_JAR_per_focal"])
        close(y["no_JAR_lag_match_per_focal"],no/n)
        close(y["JAR_lag_match_per_focal"],yes/n)
    audit=a["off_grid_fixture"];audit2=b["numeric_audit"]
    assert audit["n_non_grid_fixtures"]==audit2["offgrid_fixture_n"]==63
    close(audit["max_absolute_error"],audit2["offgrid_max_abs_correlation_error"])
    assert audit["n_violate_0p025_limit"]==audit2["offgrid_fixture_over_limit_0p025_n"]==16
    assert audit["n_classification_mismatch"]==audit2["offgrid_fixture_threshold_label_mismatch_n"]==0
    assert a["n_cells_cache_exact_JAR_DELTA_mismatch"]==audit2["exact_full_world_delta_label_discrepancies_n"]==0
    assert a["max_absolute_change_in_JAR_delta"]==audit2["max_absolute_change_in_JAR_effect_after_exact_replay"]==0
    print("HASE_V2_COMPLETE_EXACT_SOURCE_SHA_AND_ALL_12_CELLS_RECONCILED")
    print("NOT_ANIMAL_EVIDENCE_NOT_HASE_ORIGINAL_GROUP_REPRODUCTION")
    return 0
if __name__=="__main__":raise SystemExit(main())
