"""v4 synthetic acoustic inverse known-truth: NOT empirical fish or Boids forces."""
import argparse,json
from pathlib import Path
import numpy as np
MICROPHONES=np.array([[-7.,-4.],[6.,-5.],[-5.,7.],[8.,6.],[0.,0.]])
FISH=np.array([[-6.1,-2.],[-3.2,-2.3],[-1.5,3.1],[2.4,1.6],[4.7,-1.4],[5.2,4.1],
               [-2.7,5.3],[.5,-4.5],[-4.5,.7],[2.7,-2.1],[.3,3.7],[4.8,-4.7]])
def attenuation(receivers,sources,spread=5.):
    receivers=np.asarray(receivers,float);sources=np.asarray(sources,float)
    if receivers.ndim!=2 or sources.ndim!=2 or receivers.shape[1]!=2 or sources.shape[1]!=2 or spread<=0:
        raise ValueError("invalid geometry/spread")
    d2=np.sum((receivers[:,None,:]-sources[None,:,:])**2,axis=2)
    return np.exp(-d2/(2*spread**2))
def emission_ambiguity():
    K=attenuation(MICROPHONES,FISH); n=K.shape[1]
    u,s,vt=np.linalg.svd(K,full_matrices=True)
    rank=int(np.sum(s>max(K.shape)*np.finfo(float).eps*s[0]))
    v=vt[rank:].T; d=v@(v.T@np.ones(n));d/=max(abs(d))
    q0=np.full(n,.5);q1=q0+.4*d
    e0,e1=K@q0,K@q1
    err=float(max(abs(e0-e1)))
    assert 0<=min(q1) and max(q1)<=1 and err<1e-10
    return {"status":"SYNTHETIC_IDENTIFIABILITY_ONLY","receivers":K.shape[0],"fish":n,
            "operator_rank":rank,"null_dimension":n-rank,"total_emission_A":float(sum(q0)),
            "total_emission_B":float(sum(q1)),"weights_A":q0.tolist(),"weights_B":q1.tolist(),
            "received_A":e0.tolist(),"received_B":e1.tolist(),
            "max_receiver_difference":err}
def centroid_ambiguity(shift=1.2):
    if shift<=0:raise ValueError("shift must be positive")
    p0=FISH;p1=p0+np.array([shift,0.])
    K0=attenuation(MICROPHONES,p0);K1=attenuation(MICROPHONES,p1)
    q0=np.full(len(p0),.5);q1=q0+np.linalg.pinv(K1)@(K0@q0-K1@q0)
    if min(q1)<0 or max(q1)>1:raise ValueError("intensity compensation invalid")
    e0,e1=K0@q0,K1@q1
    err=float(max(abs(e0-e1)))
    assert err<1e-10
    return {"status":"SYNTHETIC_DIFFERENT_CENTROIDS_SAME_RECEIVED_INTENSITIES",
            "centroid_displacement_m":float(np.linalg.norm(p1.mean(axis=0)-p0.mean(axis=0))),
            "centroid_A":p0.mean(axis=0).tolist(),"centroid_B":p1.mean(axis=0).tolist(),
            "min_weight_B":float(min(q1)),"max_weight_B":float(max(q1)),
            "weights_B":q1.tolist(),"received_A":e0.tolist(),"received_B":e1.tolist(),
            "max_receiver_difference":err}
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",default="validation_fish_school_v4/results/inverse_known_truth.json")
    a=p.parse_args();result={"case_1":emission_ambiguity(),"case_2":centroid_ambiguity(),
                            "scope":"SIMULATOR ONLY: conditional intensity expectations, not field evidence"}
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SYNTHETIC_ONLY","rank":result["case_1"]["operator_rank"],
                      "null_dim":result["case_1"]["null_dimension"],
                      "total_emissions":[result["case_1"]["total_emission_A"],result["case_1"]["total_emission_B"]],
                      "centroid_shift_m":result["case_2"]["centroid_displacement_m"],
                      "max_audio_error":max(result["case_1"]["max_receiver_difference"],result["case_2"]["max_receiver_difference"])}))
if __name__=="__main__":main()
