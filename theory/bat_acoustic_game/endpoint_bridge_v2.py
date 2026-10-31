"""Mechanistic ENDPOINT BRIDGE v2, NOT a reproduction or animal-level fit.

2026 published group-simulation means are transcribed from Hase et al. 2026
Proc R Soc B, DOI 10.1098/rspb.2026.0921, Fig. 5f: potential
misdetections with and without JAR; these are NOT observed false-alarm acts.
2020 Mazar & Yovel tested prey detection/capture in a different model.
A renewal-reward coupling creates transparent counterfactuals only.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import math

# Published rounded group-simulation means: NOT independently reproduced here.
# n: (without JAR possible misdetections, with JAR possible misdetections).
HASE_2026_POTENTIAL_MISDETECTIONS = {
    4: (0.14, 0.01), 8: (1.37, 0.12),
    16: (5.98, 2.49), 32: (15.77, 10.01)
}


@dataclass(frozen=True)
class BridgeParams:
    # All illustrative; no empirical calibration or true time-unit conversion.
    prey_encounter_rate: float = 1.0
    true_detection_unshifted: float = 0.85
    capture_given_detection: float = 0.70
    prey_handling_time: float = 0.25

    def __post_init__(self):
        if self.prey_encounter_rate <= 0 or self.prey_handling_time < 0:
            raise ValueError("Invalid rates or handling time")
        if not 0 < self.true_detection_unshifted <= 1:
            raise ValueError("Invalid true detection")
        if not 0 < self.capture_given_detection <= 1:
            raise ValueError("Invalid capture conditional probability")


def capture_rate(detection, false_workload, p=BridgeParams()):
    """Renewal-reward capture rate per calendar time.

    Events arrive per ACTIVE time. Detectable prey at lambda*d, each with
    expected capture q and handling cost h; false alarms impose workload W.
    Both rate and workload are dimensionless toy quantities until calibrated.
    """
    if not 0 <= detection <= 1 or false_workload < 0:
        raise ValueError("Invalid detection or false workload")
    l = p.prey_encounter_rate
    return l*detection*p.capture_given_detection / (
        1+l*detection*p.prey_handling_time+false_workload)


def normalized_rho(group_size):
    """JAR/no-JAR potential misdetection RATIO only; not a false-alarm rate."""
    no, yes = HASE_2026_POTENTIAL_MISDETECTIONS[group_size]
    return yes/no


def gain(delta, unshifted_workload, rho, p=BridgeParams()):
    """JAR minus no-JAR capture rate under an explicit HYPOTHETICAL mapping.

    delta = fractional loss of genuine prey-detection sensitivity under JAR.
    unshifted_workload = kappa*false_event_recovery_time*F0.
    rho = modeled potential misdetection ratio, ASSUMED equal to true false
      alarms' ratio solely for this illustrative counterfactual.
    """
    if not 0 <= delta <= 1 or unshifted_workload < 0 or not 0 <= rho <= 1:
        raise ValueError("Invalid bridge controls")
    d = p.true_detection_unshifted
    return (capture_rate(d*(1-delta),rho*unshifted_workload,p)
            -capture_rate(d,unshifted_workload,p))


def crossing_workload(delta, rho):
    """Exact workload W* at capture neutral when 0<delta<1-rho.
    Independent of lambda, q and prey handling time IF those are unchanged.
    None indicates NO FINITE positive W makes JAR strictly better.
    """
    if not 0 <= delta <= 1 or not 0 <= rho <= 1:
        raise ValueError("Invalid bridge controls")
    if delta == 0:
        return 0.0 if rho < 1 else None  # rho=1 => identically tied
    g = 1-delta
    if g <= rho:
        return None
    return delta/(g-rho)


def reported_ratios():
    return [{
        "group_size":n,
        "published_model_no_JAR":raw[0],
        "published_model_JAR":raw[1],
        "possible_misdetection_ratio":normalized_rho(n),
        "possible_misdetection_reduction":1-normalized_rho(n),
    } for n,raw in sorted(HASE_2026_POTENTIAL_MISDETECTIONS.items())]


def run():
    fixed_delta=0.02
    workloads=(0,0.01,0.025,0.05,0.1,0.25)
    groups=[]
    for rec in reported_ratios():
        rho=rec["possible_misdetection_ratio"]
        threshold=crossing_workload(fixed_delta,rho)
        effects=[{
            "unshifted_false_workload":w,
            "capture_gain":gain(fixed_delta,w,rho),
            "capture_gain_pct_of_no_JAR":100*gain(fixed_delta,w,rho)/
                   capture_rate(BridgeParams().true_detection_unshifted,w),
        } for w in workloads]
        groups.append({**rec,
             "illustrative_detection_penalty":fixed_delta,
             "capture_neutral_false_workload":threshold,
             "effects":effects})
    grid=[]
    for delta in (0,0.005,0.02,0.05,0.15):
        for w in workloads:
            row={"genuine_detection_penalty":delta,
                 "unshifted_false_workload":w}
            for n in sorted(HASE_2026_POTENTIAL_MISDETECTIONS):
                g=gain(delta,w,normalized_rho(n))
                row[f"group_{n}"]="POSITIVE" if g>1e-12 else "NEGATIVE" if g< -1e-12 else "TIE"
            grid.append(row)
    return {
        "schema":2,
        "status":"LITERATURE_MEANS_PLUS_UNCALIBRATED_ANALYTIC_COUNTERFACTUAL",
        "observed_bat_measurements_added":False,
        "source_code_2020_reproduced":False,
        "group_model_2026_reproduced":False,
        "source_reference":"Hase et al. 2026 Proc R Soc B Fig.5f DOI:10.1098/rspb.2026.0921",
        "source_means_precision":"reported published means, not original simulation replicates",
        "bridge_unmeasured":"conversion from potential misdetection into costly false alarms; genuine detection penalty",
        "params":BridgeParams().__dict__,
        "assumption":"rho potential misdetection is treated as relative costly false-alarm rate only illustratively; workload W is unmeasured",
        "all_groups":groups,
        "grid":grid
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
