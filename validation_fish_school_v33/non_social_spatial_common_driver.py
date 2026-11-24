"""v33 constructed analytic zero-social-arrow spatial common-input counterexample.

No real fish data, fitted effect, experimental intervention or neural source.
Even when no fish ever responds to any other fish, nearby fish may improve
focal prediction beyond current global speed because the same spatially
structured external environment drives all fish at nearby positions.
"""
from __future__ import annotations
import json
import numpy as np
from pathlib import Path

POSITIONS=np.array([0.,.12,.29,.5,.83,1.13,1.65,2.3],dtype=float)
L=.35
GLOBAL_VAR=1.
LOCAL_FIELD_VAR=2.
PRIVATE_MEASUREMENT_VAR=1.
FUTURE_PRIVATE_NOISE_VAR=1.
SEED="EXACT_GAUSSIAN_COVARIANCE_NO_STOCHASTIC_SIMULATION"


def exact_mse(noise_cov,yy,cxy,weights):
    observed=weights.T@noise_cov@weights
    conditional=weights.T@cxy
    return float(yy-conditional@np.linalg.solve(observed,conditional))

def run():
    x=POSITIONS
    n=len(x)
    # U~N(0,GLOBAL_VAR), W~GP(0,K), eps_j iid measurement noise.
    # X_j = U + W(x_j) + eps_j.
    # Y_i = U + W(x_i) + eta_i (no arrows from X_j to Y_i).
    K=LOCAL_FIELD_VAR*np.exp(-np.abs(x[:,None]-x[None,:])/L)
    Cx=K+GLOBAL_VAR*np.ones((n,n))+PRIVATE_MEASUREMENT_VAR*np.eye(n)
    Cxy=K+GLOBAL_VAR*np.ones((n,n))
    yy=GLOBAL_VAR+LOCAL_FIELD_VAR+FUTURE_PRIVATE_NOISE_VAR
    per=[]
    for i in range(n):
        other=np.array([j for j in range(n) if j!=i],dtype=int)
        near=other[np.argsort(np.abs(x[other]-x[i]),kind="stable")[:3]]
        far=other[np.argsort(np.abs(x[other]-x[i]),kind="stable")[-3:]]
        # columns focal current, all-seven global, near three, far three,
        # one-step cyclic assignment-surrogate neighbor speed.
        matrix=np.zeros((n,5))
        matrix[i,0]=1.
        matrix[other,1]=1./7
        matrix[near,2]=1./3
        matrix[far,3]=1./3
        surrogate=np.roll(other,1)
        for j in near:
            idx=int(np.flatnonzero(other==j)[0])
            matrix[surrogate[idx],4]+=1./3
        def mse(columns):
            # This is a fixed Gaussian population conditional linear MSE;
            # there is no finite-sample fit, cross-validation or fish source.
            sub=matrix[:,columns]
            return exact_mse(Cx,yy,Cxy[:,i],sub)
        scores={
            "source_focal_index_label_only":i,
            "MSE_global_after_focal":mse([0,1]),
            "MSE_global_nearest_true_after_focal":mse([0,1,2]),
            "MSE_global_farthest_true_after_focal":mse([0,1,3]),
            "MSE_global_nearest_rot1_after_focal":mse([0,1,4]),
        }
        scores["non_social_near_additional_MSE_gain"]=scores[
          "MSE_global_after_focal"]-scores["MSE_global_nearest_true_after_focal"]
        scores["non_social_true_vs_rotated_MSE_gain"]=scores[
          "MSE_global_nearest_rot1_after_focal"]-scores["MSE_global_nearest_true_after_focal"]
        scores["non_social_true_near_vs_far_MSE_gain"]=scores[
          "MSE_global_farthest_true_after_focal"]-scores["MSE_global_nearest_true_after_focal"]
        per.append(scores)
    comparisons=("non_social_near_additional_MSE_gain",
                 "non_social_true_vs_rotated_MSE_gain",
                 "non_social_true_near_vs_far_MSE_gain")
    summary={
        key:{
            "mean_population_optimal_MSE_gain":float(np.mean([z[key] for z in per])),
            "n_focals_with_positive_gain":int(sum(z[key]>0 for z in per)),
            "n_total_constructed_focals":len(per)
        } for key in comparisons
    }
    return {
        "status":"EXACT_CONSTRUCTED_ZERO_SOCIAL_ARROW_SPATIAL_COMMON_DRIVER_COUNTEREXAMPLE",
        "study_type":"mathematically constructed Gaussian covariance, NOT fish observation",
        "model":"X_j=U+W(x_j)+eps_j; Y_i=U+W(x_i)+eta_i with zero fish-fish behavioral edges",
        "global_source_variance":GLOBAL_VAR,
        "spatially_correlated_common_environment_variance":LOCAL_FIELD_VAR,
        "spatial_common_environment_correlation_length_arbitrary":L,
        "private_measurement_noise_variance":PRIVATE_MEASUREMENT_VAR,
        "private_future_noise_variance":FUTURE_PRIVATE_NOISE_VAR,
        "original_X_positions_arbitrary_constructed":POSITIONS.tolist(),
        "constructed_fixed_single_neighbor_rotation":1,
        "results":per,"comparisons":summary,
        "fish_or_boid_field_data_read":False,
        "social_fish_force_or_acoustic_causal_effect_identified":False,
        "interpretation":"Even positive near-vs-global, near-vs-far and near-vs-fixed-one-rotation predictive tests are possible with NO social interactions when an unmeasured spatial field drives nearby fish",
        "source_source_of_information":"exact Gaussian conditional covariance algebra, not empirical animal records"
    }

if __name__=="__main__":
    p=Path("validation_fish_school_v33/results/non_social_spatial_common_driver_exact.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    out=run()
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"comparisons":out["comparisons"]},sort_keys=True))
