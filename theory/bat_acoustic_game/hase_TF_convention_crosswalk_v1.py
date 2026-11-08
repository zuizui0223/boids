"""Exact normalized MF cross-correlation for two distinct TF perturbation conventions.

Uses synthetic power-curve FM waveforms, not Hase 2018 or 2026 authors'
unpublished actual waveform synthesis. Source DOI metadata only; no bat audio.
"""
from __future__ import annotations
import json,math
from pathlib import Path
import numpy as np

FS=250_000
T=.003
FAMILIES={"linear":1.0,"power_0p6":.6,"power_2p0":2.}
GRID_KHZ=(0.,.25,.5,.75,1.,1.25,1.5,2.,3.,4.,5.,6.)
OUT=Path(__file__).resolve().parent/"HASE2018_2026_TF_CONVENTION_V1_RESULTS.json"

def signal(fstart_khz,fterm_khz,curve):
    if fstart_khz<=fterm_khz or curve not in FAMILIES:
        raise ValueError("Invalid pre-frozen downward FM curve")
    t=(np.arange(round(T*FS),dtype=float)+.5)/FS
    p=FAMILIES[curve]
    freq_hz=1000*(fterm_khz+(fstart_khz-fterm_khz)*(1-t/T)**p)
    phase=2*np.pi*np.cumsum(freq_hz)/FS
    wave=np.sin(phase)
    wave/=np.linalg.norm(wave)
    return wave

def corr(source,target):
    c=np.correlate(source,target,mode="full")
    return float(np.max(np.abs(c)))

def make_curve(protocol,shape):
    if protocol=="fixed_start_2018_like":
        initial=(90.,45.)
        make=lambda d:(90.,45.+d)
    elif protocol=="fixed_bandwidth_2026_like":
        initial=(88.,48.)
        make=lambda d:(88.+d,48.+d)
    else:
        raise ValueError("Unsupported predeclared protocol")
    baseline=signal(*initial,shape)
    pts=[]
    for d in GRID_KHZ:
        start,term=make(d)
        c=corr(baseline,signal(start,term,shape))
        pts.append({"terminal_shift_khz":d,"source_synthetic_Fs_khz":start,
                    "source_synthetic_TF_khz":term,
                    "normalized_max_lag_cross_correlation":c,
                    "other_bat_confusable_over_half":bool(c>.5)})
    threshold=None
    for old,new in zip(pts,pts[1:]):
        a=old["normalized_max_lag_cross_correlation"]
        b=new["normalized_max_lag_cross_correlation"]
        if a>.5 and b<=.5:
            d0=old["terminal_shift_khz"];d1=new["terminal_shift_khz"]
            threshold=d0+(d1-d0)*(a-.5)/(a-b)
            break
    return {"protocol":protocol,"waveform_family":shape,
            "source_synthetic_baseline_Fs_TF_khz":list(initial),
            "first_half_correlation_crossing_khz":threshold,
            "reported_2018_original_order_one_khz":
                "COMPARE_ONLY_NOT_FITTED",
            "points":pts}

def run():
    curves=[make_curve(protocol,shape)
            for protocol in ("fixed_start_2018_like","fixed_bandwidth_2026_like")
            for shape in FAMILIES]
    return {"schema":1,
        "status":"SYNTHETIC_2018_2026_FM_MANIPULATION_DEFINITION_CROSSWALK",
        "source_2018_publication_doi":"10.1038/s42003-018-0045-3",
        "source_2026_publication_doi":"10.1098/rspb.2026.0921",
        "2018_published_approx_2pct_terminal_frequency_halfwidth_khz":1.,
        "raw_2018_Dryad_audio_opened":False,
        "original_2026_author_waveform_reproduced":False,
        "original_2018_pulse_synthesis_reproduced":False,
        "new_animal_measurements":False,
        "cross_correlation_source": "synthetic finite-duration normalized amplitude FM with full lag optimization",
        "pre_frozen_grid_khz":list(GRID_KHZ),
        "curves":curves}
if __name__=="__main__":
    o=run()
    OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
    print("NO_NEW_BAT_MEASUREMENTS")
    for s in o["curves"]:
        print("SOURCE_CONVENTION",s["protocol"],s["waveform_family"],
              "first_half_correlation_crossing_khz",s["first_half_correlation_crossing_khz"],
              "at_TF_plus_1kHz",next(
                  z["normalized_max_lag_cross_correlation"] for z in s["points"]
                  if z["terminal_shift_khz"]==1.))
