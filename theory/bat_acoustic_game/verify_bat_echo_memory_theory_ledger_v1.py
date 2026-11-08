"""Fail-closed source-code/contract and exact 70/240-cell theory ledger replay.

Only synthesized filter-model uncertainty; no bat animal observation is read.
Original 2026 eLife MATLAB simulation remains a separate prior-art source.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
import bat_echo_memory_static_dynamic_v1 as base
import bat_echo_masking_availability_v1 as masked

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"BAT_ECHO_MEMORY_TASK_CONDITIONED_THEORY_LEDGER_V1.json"
BLOBS={
  "source_gaussian_randomwalk_filter_CodeBlob":"bat_echo_memory_static_dynamic_v1.py",
  "gaussian_randomwalk_preoutput_ContractBlob":"BAT_ECHO_MEMORY_STATIC_VS_MOVING_PREOUTPUT_2026_11_07.md",
  "source_echo_availability_CodeBlob":"bat_echo_masking_availability_v1.py",
  "echo_availability_preoutput_ContractBlob":"BAT_ECHO_MASKING_AVAILABILITY_PREOUTPUT_2026_11_07.md"
}

def gitblob(p):
    data=(ROOT/p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def near(a,b,tol=2e-12):
    if a is None or b is None:
        assert a is b,(a,b)
    else:
        assert math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol),(a,b)

def run():
    d=json.loads(LEDGER.read_text())
    assert d["schema"]==1
    for k,p in BLOBS.items():
        assert gitblob(p)==d[k],f"Frozen science code/contract changed: {p}"
    assert not d["no_new_measurements"] if False else d["no_new_measurements"]
    assert not d["original_Mazar_MATLAB_replayed"]
    a=base.run()
    b=masked.run()
    assert a["monte_carlo_check_pass"] and a["schema"]==1
    assert b["schema"]==1 and b["fixed_exact_cases"]==240
    assert not a["new_bat_measurements"] and not b["new_bat_measurements"]
    assert not b["authentic_MATLAB_model_rerun"]
    near(a["max_relative_mc_error_all_70"],d["all_echo_max_relative_MC_disagreement"])
    assert len(a["worlds"])==len(d["all_echo_rho_to_optimal_K"])==7
    for original,pinned in zip(a["worlds"],d["all_echo_rho_to_optimal_K"]):
        near(original["q_over_r"],pinned["ratio"])
        assert original["integer_optimal_K_1_to_10"]==pinned["k_optimal"]
        near(original["analytic_MSE_for_K_1"],pinned["MSE_K1"])
        near(original["analytic_MSE_for_K_5"],pinned["MSE_K5"])
    assert len(b["worlds"])==len(d["echo_dropout_condition_K5_source_motivated_summary"])==24
    for original,pinned in zip(b["worlds"],d["echo_dropout_condition_K5_source_motivated_summary"]):
        near(original["usable_echo_probability_per_pulse"],pinned["usable_echo_probability"])
        near(original["target_change_to_obs_error_q_over_r"],pinned["target_drift_to_noise_ratio"])
        compare=original["memory_five"]
        near(compare["probability_all_missing"],pinned["k5_all_missing_probability"])
        near(compare["conditional_MSE"],pinned["k5_conditional_MSE"])
        near(compare["conditional_MSE_minus_one_call"],pinned["k5_minus_k1_conditional_MSE"])
        assert original["nondominated_K_without_arbitrary_reward"]==pinned["memory_length_pareto_nondominated"]
    for v in d["five_call_accuracy_break_even_post_output_algebra_from_locked_model"]:
        p=v["usable_echo_probability"]
        intercept=masked.exact_conditional_memory(5,p,0)["conditional_MSE"]
        slope=masked.exact_conditional_memory(5,p,1)["conditional_MSE"]-intercept
        near(v["five_call_analytic_accuracy_gain_max_q_over_r"],(1-intercept)/slope)
        near(v["five_call_all_missing_probability"],(1-p)**5)
    assert d["echo_loss_exact_cases"]==240
    assert d["all_echo_synthetic_independent_histories_per_ratio"]==40000
    print("PINNED_BAT_SENSOR_TIME_SCALE_THEORY_70_MC_AND_240_MASKING_CELLS_MATCH")
    print("ALL_ORIGINAL_SOURCE_CODE_BLOBS_AND_CONTRACTS_UNCHANGED")
    print("ORIGINAL_2026_MAZAR_MATLAB_NOT_RERUN_NO_NEW_BAT_MEASUREMENTS")
    return 0

if __name__=="__main__":
    raise SystemExit(run())
