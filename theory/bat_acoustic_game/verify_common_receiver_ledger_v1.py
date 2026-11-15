"""Fail-closed replay of source-constrained synthetic ledger, not animal evidence."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"common_physics_v1.py"
LEDGER=ROOT/"COMMON_RECEIVER_SYNTHETIC_LEDGER_V1.json"

def git_blob_sha(path:Path):
    content=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()

def approx(a,b,tol=1e-5):
    assert math.isfinite(float(a))
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol),f"{a} != {b}"

def verify(actual,source):
    assert source["schema"]==1 and actual["schema"]==1
    assert source["source_code_blob_sha"]==git_blob_sha(SRC),"Source changed; freeze invalid"
    assert actual["scientific_status"]=="SYNTHETIC_SOURCE_CONSTRAINED_PROXY_NOT_ORIGINAL_REPLAY"
    assert not actual["source2020_numeric_reproduction"]
    assert not actual["source2026_group_numeric_reproduction"]
    assert not actual["added_bat_measurements"]
    assert len(actual["worlds"])==len(source["worlds"])==4
    assert source["species_specific_waveform_used"] is False
    for a,b in zip(actual["worlds"],source["worlds"]):
        assert (a["n"],a["scale"])==(b["n"],b["scale"])
        approx(a["mean_pair_gap_gain_kHz"],b["delta_gap_khz"])
        for key,assay in (("lag_possible_before","assay_noJAR"),
                           ("lag_possible_after","assay_JAR")):
            assert a[assay]["lag"]["possible_confusable_pairs"]==b[key]
        assert b["possible_denominator"]==a["n"]*(a["n"]-1)//2
        for key,assay in (("lag_prey_detection_before","assay_noJAR"),
                           ("lag_prey_detection_after","assay_JAR")):
            approx(a[assay]["lag"]["mean_echo_detection_across_margins"],b[key],1e-10)
    check={r["delta_tf_khz"]:r for r in actual["pure_FM_frequency_ambiguity_fixture"]}
    for v in source["frequency_time_fixture"]:
        s=check[v["delta_tf_khz"]]
        approx(s["zero_lag_absolute_corr"],v["zero_abs_corr"],1e-5)
        approx(s["max_delay_window_absolute_corr"],v["lag_abs_corr"],1e-5)
        expected_time=v["delta_tf_khz"]*3/40
        approx(v["delay_from_ideal_linear_chirp_ms"],expected_time,1e-12)
        approx(v["range_equivalent_cm"],expected_time/1000*343/2*100,1e-9)

def main():
    if len(sys.argv)!=2:raise SystemExit("Usage: verify_common_receiver_ledger_v1.py result.json")
    actual=json.loads(Path(sys.argv[1]).read_text())
    source=json.loads(LEDGER.read_text())
    verify(actual,source)
    print("SYNTHETIC_RECEIVER_SOURCE_SHA_AND_NUMERIC_LEDGER_EXACTLY_VERIFIED")
    print("NO_ANIMAL_DATA_ORIGINAL_MODELS_NOT_REPLAYED")
    return 0

if __name__=="__main__":raise SystemExit(main())
