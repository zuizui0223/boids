"""v138 tidal/solar observational design identifiability; synthetic harmonic scenarios.

No wild-animal observations, source tide gauge heights or empirical effect estimates.
Equal synthetic observation opportunities; no ecological event/power model is fitted.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import product
from math import cos, pi
from pathlib import Path
import argparse
import json

M2_H = 12.4206012
S2_H = 12.0
K1_H = 23.93447213
SAMPLE_MINUTES = 10
DAYLIGHT = (6, 18)  # fixed 12-hour equinoctial illustration; not actual local sunrise
DURATIONS_DAYS = (1, 3, 7, 15, 30)
SCHEMES = {
    "daylight_only_8h": ((8, 16),),
    "one_day_one_night_8h": ((8, 12), (20, 24)),
    "four_2h_blocks_8h": ((2, 4), (8, 10), (14, 16), (20, 22)),
    "continuous_24h_reference": ((0, 24),),
}
REGIMES = {
    "M2_only": (1.0, 0.0, 0.0),
    "M2_plus_S2": (1.0, 0.5, 0.0),
    "M2_plus_S2_plus_K1": (1.0, 0.5, 0.5),
}

def phase_beat_days(a_h=M2_H, b_h=S2_H):
    """Exact harmonic phase-wrap period; not a statistical sample-size rule."""
    if a_h <= 0 or b_h <= 0 or a_h == b_h:
        raise ValueError("positive unequal periods required")
    return 1.0 / abs(1.0 / a_h - 1.0 / b_h) / 24.0

def information_balance(cell_bins):
    """Normalized inverse design variance of four-cell log-rate contrast.

    Under purely hypothetical identical independent Poisson event intensity,
    E[n_events,k] = lambda*observation_opportunities_k,
    Var(log rate difference-in-differences) ~ 1/lambda * sum_k 1/n_k.
    B = 16/(N*sum_k 1/n_k) has optimum 1 at equal effort and zero
    if any cell is unobserved. Not power, precision, or animal behavior.
    """
    if len(cell_bins) != 4 or any((not isinstance(x, int) or x < 0) for x in cell_bins):
        raise ValueError("exactly four nonnegative integer cell counts required")
    if not all(cell_bins):
        return 0.0
    n = sum(cell_bins)
    return 16.0 / (n * sum(1.0 / x for x in cell_bins))

def step_indices():
    clock = [(j + 0.5) * SAMPLE_MINUTES / 60 for j in range(24 * 60 // SAMPLE_MINUTES)]
    mask = {
        scheme: [j for j, h in enumerate(clock)
                 if any(a <= h < b for a, b in windows)]
        for scheme, windows in SCHEMES.items()
    }
    assert sum(len(x) for x in (mask["daylight_only_8h"],)) == 48
    assert len(mask["one_day_one_night_8h"]) == 48
    assert len(mask["four_2h_blocks_8h"]) == 48
    assert len(mask["continuous_24h_reference"]) == 144
    for name in ("one_day_one_night_8h","four_2h_blocks_8h"):
        ds = [DAYLIGHT[0] <= clock[j] < DAYLIGHT[1] for j in mask[name]]
        assert sum(ds) == len(ds)//2
    return clock, mask

def phase_grid():
    """Discrete deterministic grid, NOT a probability sample of natural coasts."""
    return product(range(24), range(4), range(4))

def run():
    clock, schedules = step_indices()
    trials = 24 * 4 * 4
    out = {
        "version": "v138_deterministic_harmonic_sampling_design_1",
        "source_periods_hours": {"M2": M2_H, "S2": S2_H, "K1": K1_H},
        "m2_s2_phase_beat_days": round(phase_beat_days(), 6),
        "time_step_minutes": SAMPLE_MINUTES,
        "synthetic_daylight_local_clock": "06:00-18:00, fixed each day",
        "regime_amplitudes_are_assumptions": {key:list(amps) for key, amps in REGIMES.items()},
        "phase_grid": {"M2_angles": 24,"S2_angles": 4, "K1_angles": 4,
                       "combinations_each_regime": trials,
                       "irrelevant_phase_axes_are_duplicates": True,
                       "sampling_is_phase_grid_not_natural_coast_distribution": True},
        "schemes_local_clock_windows": {key:[list(a) for a in windows] for key,windows in SCHEMES.items()},
        "summary": {},
        "outcome_type": "MODEL_ONLY_DESIGN_BALANCE",
        "tide_height_classification": "synthetic height >= 0 versus < 0; NOT inundation or ebb/flood",
        "animal_activity_or_tide_solar_interaction": "NOT_ESTIMATED",
        "cross_coast_meta_effect": "NOT_ESTIMATED",
    }
    max_days = max(DURATIONS_DAYS)
    n_clock = len(clock)
    daylight = [DAYLIGHT[0] <= h < DAYLIGHT[1] for h in clock]
    for regime, (amp_m, amp_s, amp_k) in REGIMES.items():
        cells_by_phase = defaultdict(list)
        for im, iss, ik in phase_grid():
            phase_m = 2*pi*im/24
            phase_s = 2*pi*iss/4
            phase_k = 2*pi*ik/4
            counts = {name: [0,0,0,0] for name in SCHEMES}
            for d in range(max_days):
                high = []
                for h in clock:
                    t = d*24 + h
                    level = amp_m*cos(2*pi*t/M2_H + phase_m)
                    if amp_s:
                        level += amp_s*cos(2*pi*t/S2_H + phase_s)
                    if amp_k:
                        level += amp_k*cos(2*pi*t/K1_H + phase_k)
                    high.append(level >= 0.0)
                for name, indices in schedules.items():
                    c = counts[name]
                    for j in indices:
                        c[2*int(daylight[j]) + int(high[j])] += 1
                    if d+1 in DURATIONS_DAYS:
                        cells_by_phase[(name,d+1)].append(information_balance(c))
        out["summary"][regime] = {}
        for name in SCHEMES:
            out["summary"][regime][name] = {}
            for d in DURATIONS_DAYS:
                v = cells_by_phase[(name,d)]
                assert len(v) == trials
                out["summary"][regime][name][str(d)] = {
                    "mean_balance": round(sum(v)/trials,4),
                    "min_balance": round(min(v),4),
                    "max_balance": round(max(v),4),
                    "all_four_cells_fraction": round(sum(1 for x in v if x>0)/trials,6),
                    "zero_cell_phase_cases": sum(x==0 for x in v),
                    "phase_cases": trials,
                    "sampled_hours_per_day": len(schedules[name])*SAMPLE_MINUTES/60,
                }
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    path = Path(__file__).parent/"results"/"sampling_design_phase_grid.json"
    if args.check:
        assert result == json.loads(path.read_text()), "Saved harmonic design disagrees with code"
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    compact = {
        regime: {
            scheme: {str(d): result["summary"][regime][scheme][str(d)]["mean_balance"]
                     for d in (1,3,7,15)}
            for scheme in ("daylight_only_8h","one_day_one_night_8h","four_2h_blocks_8h")}
        for regime in REGIMES}
    print("V138_SUMMARY_JSON_START")
    print(json.dumps({"beat_days":result["m2_s2_phase_beat_days"],"balances":compact,
                      "full_result":result},sort_keys=True))
    print("V138_SUMMARY_JSON_END")

if __name__=="__main__":
    main()
