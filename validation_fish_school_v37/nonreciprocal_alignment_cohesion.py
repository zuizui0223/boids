"""v37 exact one-way follower analytic Boids-like alignment/cohesion counterexample.

Constructed mathematical examples ONLY: no PLOS fish trajectories or VR
experimental model coefficients fitted or acoustic/social causal claims.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

V0_CM_S=5.0
ALPHA_PER_S=1.0
GAMMA_PER_S=0.4
DELTAS_CM_S=(0.0,2.0,5.0)
BETAS_PER_S2=(0.25,0.5,1.0,2.0)
REFERENCE_DELTA_CM_S=5.0
REFERENCE_BETA_PER_S2=0.5
REFERENCE_T_SECONDS=40.0


class AnalyticStop(Exception):pass


def original_analytic_equilibrium(alpha,beta,gamma,delta):
    for val in (alpha,beta,gamma,delta):
        if not np.isfinite(val):
            raise AnalyticStop("V37_CONSTRUCTED_NONFINITE_COEFFICIENT")
    if alpha<=0 or beta<=0 or gamma<0 or delta<0:
        raise AnalyticStop("V37_CONSTRUCTED_OUTSIDE_FROZEN_POSITIVE_STABILITY_DOMAIN")
    # e=x_real-x_virtual; u=v_real-v_virtual. Virtual is fully
    # externally prescribed and receives NO edge from the real fish.
    A=np.array([[0.,1.],[-beta,-(alpha+gamma)]],dtype=float)
    forcing=np.array([0.,-gamma*delta])
    fixed=np.array([-gamma*delta/beta,0.],dtype=float)
    residual=A@fixed+forcing
    eig=np.linalg.eigvals(A)
    if not np.all(np.real(eig)<0) or np.linalg.norm(residual)>1e-12:
        raise AnalyticStop("V37_EXACT_ONE_WAY_STABLE_EQUILIBRIUM_DID_NOT_REPLAY")
    return A,forcing,fixed,eig


def exact_time_response(alpha,beta,gamma,delta,t,initial=(0.,0.)):
    if t<0 or not np.isfinite(t):
        raise AnalyticStop("V37_NEGATIVE_TIME_OR_NONFINITE")
    A,b,fixed,eig=original_analytic_equilibrium(alpha,beta,gamma,delta)
    vals,V=np.linalg.eig(A.astype(complex))
    flow=V@np.diag(np.exp(vals*t))@np.linalg.inv(V)
    result=fixed+flow@(np.asarray(initial,dtype=complex)-fixed)
    if np.max(np.abs(np.imag(result)))>1e-8:
        raise AnalyticStop("V37_COMPLEX_ARTIFACT_IN_REAL_LINEAR_SYSTEM")
    return np.asarray(np.real(result),dtype=float)


def run():
    table=[]
    for delta in DELTAS_CM_S:
        for beta in BETAS_PER_S2:
            _,_,fixed,eigs=original_analytic_equilibrium(
                ALPHA_PER_S,beta,GAMMA_PER_S,delta)
            row={
              "leader_speed_excess_cm_per_s_constructed":delta,
              "follower_position_attraction_beta_s_minus2_constructed":beta,
              "follower_own_speed_preference_gamma_s_minus1":GAMMA_PER_S,
              "relative_position_e_star_cm":float(fixed[0]),
              "relative_speed_u_star_cm_per_s":float(fixed[1]),
              "relative_speed_alignment_exact_at_equilibrium":True,
              "virtual_leader_never_responds_to_real_fish":True,
              "Jacobian_eigenvalue_real_parts":[float(np.real(z)) for z in eig],
              "Jacobian_eigenvalue_imag_parts":[float(np.imag(z)) for z in eig],
              "stable_for_arbitrary_finite_relative_initial_conditions":True,
              "original_animal_data_used":False,
            }
            table.append(row)
    A,force,eq,eigs=original_analytic_equilibrium(
        ALPHA_PER_S,REFERENCE_BETA_PER_S2,GAMMA_PER_S,
        REFERENCE_DELTA_CM_S)
    observed=exact_time_response(
        ALPHA_PER_S,REFERENCE_BETA_PER_S2,GAMMA_PER_S,
        REFERENCE_DELTA_CM_S,REFERENCE_T_SECONDS)
    if np.max(np.abs(observed-eq))>1e-8:
        raise AnalyticStop("V37_REFERENCE_ANALYTIC_EXPONENTIAL_NOT_CONVERGED")
    # Independent analytic scale checks, no original fish observations
    zero=original_analytic_equilibrium(ALPHA_PER_S,REFERENCE_BETA_PER_S2,
                                       GAMMA_PER_S,0)[2]
    stronger=original_analytic_equilibrium(ALPHA_PER_S,
                      4*REFERENCE_BETA_PER_S2,GAMMA_PER_S,
                      REFERENCE_DELTA_CM_S)[2]
    if zero[0]!=0 or abs(eq[0]/stronger[0]-4)>1e-12:
        raise AnalyticStop("V37_FROZEN_RECIPROCITY_NONNECESSARY_SCALE_TEST_FAILED")
    return {
      "status":"V37_EXACT_CONSTRUCTED_ONE_WAY_BOIDS_LIKE_ALIGNMENT_AND_COHESION_RESULT",
      "result_type":"EXACT_LINEAR_CONTROL_THEORY_NOT_NEW_ANIMAL_EMPIRICAL_EVIDENCE",
      "nonreciprocal_motion_law":"dv_real/dt=-alpha*(v_real-v_virtual)-beta*(x_real-x_virtual)-gamma*(v_real-v0); v_virtual=v0+Delta fully prescribed",
      "relative_equations":{"de_dt":"u",
                            "du_dt":"-(alpha+gamma)*u-beta*e-gamma*Delta"},
      "mathematical_existence_conditions":"beta>0 and alpha+gamma>0; all finite",
      "source_free_analytic_fixed_point":{"e_star":"-gamma*Delta/beta",
                                          "u_star":"0"},
      "source_free_example_predeclared_grid":table,
      "fixed_v0_cm_s":V0_CM_S,
      "fixed_alpha_per_s":ALPHA_PER_S,
      "fixed_gamma_per_s":GAMMA_PER_S,
      "fixed_reference_example":{
        "Delta_cm_s":REFERENCE_DELTA_CM_S,
        "beta_per_s2":REFERENCE_BETA_PER_S2,
        "time_s":REFERENCE_T_SECONDS,
        "original_relative_initial_e_u":[0,0],
        "analytic_relative_equilibrium_e_u":[float(z) for z in eq],
        "exact_matrix_exponential_relative_state_at_time":[float(z) for z in observed],
        "max_absolute_e_u_equilibrium_error":float(np.max(np.abs(observed-eq))),
        "root_real_parts":[float(np.real(z)) for z in eig],
        "no_real_fish_to_virtual_feedback":True,
      },
      "analytic_conclusion":"Even with ZERO real->virtual feedback, matched speeds/headings and finite separation coexist. Reciprocity is not necessary for cohesion, and intrinsic preferred-speed mismatch yields nonzero follower offset at unchanged speed alignment.",
      "claim_ceiling":"One-dimensional collinear continuous linear toy control law; excludes fish perception saturation, 3D turns, source smoothing, wall boundaries and independent fish data; original PLOS authors own their published results.",
      "source_experimental_fish_rows_read":False,
      "experimental_C2_C3_manipulation_effect_estimated":False,
      "fish_origin_sounds_or_causal_social_intervention_identified":False
    }


def main():
    path=Path("validation_fish_school_v37/results/constructed_nonreciprocal_alignment_spacing_equilibrium.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    result=run()
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],
        "analytic_fixed_point":result["source_free_analytic_fixed_point"],
        "reference":result["fixed_reference_example"],
        "n_analytic_grid":len(result["source_free_example_predeclared_grid"]),
        "fish_source_data_used":result["source_experimental_fish_rows_read"]},sort_keys=True))

if __name__=="__main__":main()
