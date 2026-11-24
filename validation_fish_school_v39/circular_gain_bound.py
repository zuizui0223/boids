"""v39 exact constructed circular one-way follower speed-curvature geometry.

NO original fish animal trial/trajectory, fitted coefficients, acoustic events.
Leader externally follows published paper R=15cm six speeds; arbitrarily fixed
angular follower response kappa=1/s. Closed-form mathematics, not data fit.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

R_CM=15.0
SPEEDS_CM_S=(5.,7.5,10.,11.67,13.33,15.)
KAPPA0_PER_S=1.0
TARGET_ALIGNMENT_COS=.8
MAX_CHORD_CM=5.0
TIME_S=(0.,10.,40.)
SOURCE_FREE_RESULT_TYPE="CONSTRUCTED_ANALYTIC_ORBIT_NOT_ORIGINAL_FISH_DATA"

class TheoryStop(Exception):pass


def admitted_inputs(R,v,kappa):
    if not all(math.isfinite(x) for x in (R,v,kappa)) or min(R,v,kappa)<=0:
        raise TheoryStop("V39_CONSTRUCTED_CIRCULAR_POSITIVE_FINITE_VALUES_REQUIRED")
    lag=v/(R*kappa)
    if not 0<=lag<math.pi:
        raise TheoryStop("V39_OUTSIDE_NONAMBIGUOUS_NEARSIDE_CIRCULAR_PHASE_BRANCH")
    return lag


def exact_phase_lag(t,R,v,kappa,delta_initial=0.):
    if not math.isfinite(t) or t<0 or not math.isfinite(delta_initial):
        raise TheoryStop("V39_NEGATIVE_TIME_OR_NONFINITE_SOURCE_FREE_INITIAL")
    lag=admitted_inputs(R,v,kappa)
    return lag+(delta_initial-lag)*math.exp(-kappa*t)


def exact_steady_orbit(R,v,kappa):
    lag=admitted_inputs(R,v,kappa)
    return {
        "virtual_angular_rate_rad_s":v/R,
        "fixed_leader_angular_velocity_is_speed_divided_by_radius":True,
        "stable_angular_phase_lag_rad":lag,
        "steady_heading_alignment_cos":math.cos(lag),
        "steady_follower_heading_difference_rad":lag,
        "steady_follower_speed_cm_s":v,
        "steady_leader_speed_cm_s":v,
        "steady_speed_difference_cm_s":0.,
        "steady_real_virtual_chord_separation_cm":2*R*math.sin(lag/2),
        "linearized_phase_error_eigenvalue_s_minus1":-kappa,
        "reciprocal_real_to_virtual_feedback_strength":0.,
    }


def required_kappa(R,v,min_alignment_cos,max_chord):
    if not 0<min_alignment_cos<1 or not 0<max_chord<2*R:
        raise TheoryStop("V39_INVALID_CONSTRUCTED_ALIGNMENT_OR_CHORD_THRESHOLD")
    if R<=0 or v<=0:
        raise TheoryStop("V39_NO_POSITIVE_ORBIT_OR_SPEED")
    b_alignment=v/(R*math.acos(min_alignment_cos))
    b_cohesion=v/(2*R*math.asin(max_chord/(2*R)))
    return {
        "minimum_gain_for_heading_alignment_per_s":b_alignment,
        "minimum_gain_for_chord_distance_per_s":b_cohesion,
        "minimum_gain_for_both_per_s":max(b_alignment,b_cohesion),
        "dominant_constraint":"cohesion" if b_cohesion>b_alignment else "alignment",
    }


def run():
    rows=[]
    for v in SPEEDS_CM_S:
        free=exact_steady_orbit(R_CM,v,KAPPA0_PER_S)
        gain=required_kappa(R_CM,v,TARGET_ALIGNMENT_COS,MAX_CHORD_CM)
        adjusted=exact_steady_orbit(R_CM,v,gain["minimum_gain_for_both_per_s"])
        if adjusted["steady_heading_alignment_cos"]+1e-11<TARGET_ALIGNMENT_COS or adjusted["steady_real_virtual_chord_separation_cm"]>MAX_CHORD_CM+1e-11:
            raise TheoryStop("V39_EXACT_THEORETICAL_KINEMATIC_COMPENSATION_BOUND_FAILED")
        trajectory={str(t):exact_phase_lag(t,R_CM,v,KAPPA0_PER_S) for t in TIME_S}
        if abs(trajectory["40.0"]-free["stable_angular_phase_lag_rad"])>1e-14:
            raise TheoryStop("V39_EXACT_CLOSED_FORM_40S_CONVERGENCE_FAILED")
        rows.append({
            "original_paper_speed_value_USED_AS_KINEMATIC_INPUT_cm_s":v,
            "constructed_response_gain_fixed_kappa_per_s":KAPPA0_PER_S,
            "fixed_gain_orbit_prediction":free,
            "closed_form_phase_lag_at_0_10_40_seconds":trajectory,
            "required_gain_bounds":gain,
            "compensating_angular_gain_at_speed_per_s":gain["minimum_gain_for_both_per_s"],
            "speed_dependent_compensation_result":adjusted,
            "original_animal_speed_heading_spacing_results_read":False
        })
    alignment=[r["fixed_gain_orbit_prediction"]["steady_heading_alignment_cos"] for r in rows]
    distance=[r["fixed_gain_orbit_prediction"]["steady_real_virtual_chord_separation_cm"] for r in rows]
    if not all(a>b for a,b in zip(alignment,alignment[1:])):
        raise TheoryStop("V39_FIXED_GAIN_ALIGNMENT_NOT_STRICTLY_DECREASING_WITH_SPEED")
    if not all(a<b for a,b in zip(distance,distance[1:])):
        raise TheoryStop("V39_FIXED_GAIN_SPACING_NOT_STRICTLY_INCREASING_WITH_SPEED")
    low,high=rows[0],rows[-1]
    v_ratio=high["original_paper_speed_value_USED_AS_KINEMATIC_INPUT_cm_s"]/low["original_paper_speed_value_USED_AS_KINEMATIC_INPUT_cm_s"]
    k_ratio=(high["required_gain_bounds"]["minimum_gain_for_both_per_s"]/
             low["required_gain_bounds"]["minimum_gain_for_both_per_s"])
    if abs(v_ratio-k_ratio)>1e-12:
        raise TheoryStop("V39_FIXED_RADIUS_MUST_REQUIRE_PROPORTIONAL_GAIN_COMPENSATION")
    return {
       "status":"V39_EXACT_SOURCE_FREE_ONE_WAY_CIRCULAR_FISH_VR_SPEED_TURNING_COMPENSATION_RESULT",
       "source_type":SOURCE_FREE_RESULT_TYPE,
       "original_experiment_context":"Reynaud et al. 2026 Proc R Soc B DOI 10.1098/rspb.2026.0146; input R=15cm six published virtual fish speeds only",
       "original_paper_data_source_heldout_effects_or_trial_records_loaded":False,
       "source_original_fish_heading_or_distance_observations_used":False,
       "original_author_novel_speed_dependent_interaction_conclusion_claimed":False,
       "model":"virtual phi_V(t)=v*t/R independent of real; real phi_R_dot=kappa*(phi_V-phi_R) unwrapped near-side orbit",
       "model_phase_equation":"delta_dot=v/R-kappa*delta",
       "model_stable_phase_lag":"delta_star=v/(R*kappa) in [0,pi)",
       "model_speed_alignment":"steady real speed = virtual speed = v",
       "model_heading_alignment":"cos(v/(R*kappa))",
       "model_chord_separation":"2*R*sin(v/(2*R*kappa))",
       "model_minimum_gain_for_alignment":"kappa >= v/(R*acos(c))",
       "model_minimum_gain_for_cohesion":"kappa >= v/(2*R*asin(dmax/(2*R)))",
       "spherical_wall_external_field_and_perception_NOT_fitted":True,
       "frozen_radius_R_cm":R_CM,
       "six_published_virtual_speed_inputs_cm_s":list(SPEEDS_CM_S),
       "arbitrary_fixed_angular_tracking_gain_per_s":KAPPA0_PER_S,
       "predeclared_min_alignment_cos":TARGET_ALIGNMENT_COS,
       "predeclared_max_allowed_distance_cm":MAX_CHORD_CM,
       "exact_published_speed_input_ratio_low_to_high":v_ratio,
       "exact_required_gain_ratio_for_both_constraints_low_to_high":k_ratio,
       "fixed_response_gain_alignment_decreases_with_speed":True,
       "fixed_response_gain_following_distance_increases_with_speed":True,
       "example_constructed_orbits_not_real_fish":rows,
       "scientific_conclusion":"At a fixed VR orbit radius, more virtual speed mechanically demands faster angular response. Apparent lower alignment and larger spacing can arise without ANY change in intrinsic follower interaction gain. To infer fish gain adaptation, vary virtual curvature independently of speed and use original heldout experimental sessions.",
       "predeclared_source_free_protocol":"docs/V39_CIRCULAR_ONE_WAY_BOIDS_SPEED_TURNING_COMPENSATION_FREEZE.md",
       "fish_acoustics_or_causal_Boids_behavior_identified":False
    }


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",type=Path,required=True)
    a=arg.parse_args()
    d=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "status":d["status"],
        "observed_original_fish_data_used":d["source_original_fish_heading_or_distance_observations_used"],
        "radius_cm":d["frozen_radius_R_cm"],
        "n_constructed_speed_cases":len(d["example_constructed_orbits_not_real_fish"]),
        "speed_ratio":d["exact_published_speed_input_ratio_low_to_high"],
        "required_gain_ratio":d["exact_required_gain_ratio_for_both_constraints_low_to_high"],
        "fixed_gain_first":d["example_constructed_orbits_not_real_fish"][0]["fixed_gain_orbit_prediction"],
        "fixed_gain_last":d["example_constructed_orbits_not_real_fish"][-1]["fixed_gain_orbit_prediction"]
    },sort_keys=True))

if __name__=="__main__":main()
