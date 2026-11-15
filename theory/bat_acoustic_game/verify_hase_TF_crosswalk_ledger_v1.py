"""Fail-closed six-cell source-convention ledger verification (synthetic only).

The 2018 sound archive was not downloaded. This verifies ONLY source-sha
identity and exact synthetic code outputs; not bat sensory physiology.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import hase_TF_convention_crosswalk_v1 as model

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"HASE2018_2026_TF_MANIPULATION_EXACT_LEDGER_V1.json"
CONTRACT=ROOT/"HASE2018_2026_TERMINAL_FREQUENCY_CONVENTION_PREOUTPUT_V1.md"

def gitblob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def exact(a,b):
    if b is None:
        assert a is None,(a,b)
    else:
        assert a is not None and math.isclose(float(a),float(b),abs_tol=1e-12,rel_tol=1e-12),(a,b)

def verify():
    ledger=json.loads(LEDGER.read_text())
    original=model.run()
    assert ledger["schema"]==1 and original["schema"]==1
    assert ledger["source_implementation_sha_gitblob"]==gitblob(Path(model.__file__))
    assert ledger["preoutput_contract_sha_gitblob"]==gitblob(CONTRACT)
    assert ledger["original_sound_zip_metadata"]["file_download_http_status"]==401
    assert not ledger["original_sound_zip_metadata"]["bytes_accessed"]
    assert not original["raw_2018_Dryad_audio_opened"]
    assert not original["original_2026_author_waveform_reproduced"]
    assert not original["new_animal_measurements"]
    assert len(ledger["fixed_protocols"])==len(original["curves"])==6
    for expected,current in zip(ledger["fixed_protocols"],original["curves"]):
        assert expected["manipulation"]==current["protocol"]
        assert expected["waveform"]==current["waveform_family"]
        exact(current["first_half_correlation_crossing_khz"],expected["half_corr_0p5_first_khz"])
        at1=[p for p in current["points"] if p["terminal_shift_khz"]==1.]
        assert len(at1)==1
        exact(at1[0]["normalized_max_lag_cross_correlation"],
              expected["correlation_at_delta1khz"])
        assert len(current["points"])==len(model.GRID_KHZ)==12
    print("VOCAL_FM_SOURCE_CONVENTION_LEDGER_6_OF_6_MATCH")
    print("ORIGINAL_AUDIO_ACCESS_401_SOURCE_STOP_PRESERVED")
    print("NO_NEW_BAT_DATA_NO_AUTHENTIC_WAVEFORM_REPRODUCTION")
    return 0

if __name__=="__main__":
    raise SystemExit(verify())
