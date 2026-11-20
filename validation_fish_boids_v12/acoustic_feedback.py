"""Acoustic Boids v12: testable synthetic sound->cohesion->calling feedback.

This is NOT a fitted 2016 bigeye model or empirical fish mechanism.
2016 van Oosterom et al. established signs of playback effects, not these gains.
Independent implementation of Reynolds-style 2D steering, not copied Unity.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.special import expit,logit
from scipy.optimize import brentq
from scipy.spatial import ConvexHull

P0=0.07072018168003617
PULSE=(30,50)
LOW=(2.,1.)    # beta, eta = 3
HIGH=(4.,2.)   # beta, eta = 6
SEEDS=12

def fixed_points(gain,theta):
    xs=np.linspace(1e-9,1.-1e-9,20001)
    d=expit(theta+gain*xs)-xs
    roots=[]
    for i in range(len(xs)-1):
        if d[i]*d[i+1]<0:
            root=float(brentq(lambda x:expit(theta+gain*x)-x,xs[i],xs[i+1],xtol=1e-13))
            if not any(abs(root-r)<1e-7 for r in roots):roots.append(root)
    for k in np.where(abs(d)<1e-11)[0]:
        root=float(xs[k])
        if not any(abs(root-r)<1e-6 for r in roots):roots.append(root)
    return sorted(roots)

def meanfield(beta,eta,pulse=True,steps=150):
    # g is dimensionless collective-cohesion index, NOT actual tank shoal area.
    gain=beta+eta
    theta=float(logit(P0)-gain*P0)
    p=P0;g=P0
    timeline=[]
    for t in range(steps):
        cue=.6 if pulse and PULSE[0]<=t<PULSE[1] else 0.
        g1=.65*g+.35*(p+.2*cue)
        p1=float(expit(theta+beta*g+eta*p+.6*cue))
        g,p=g1,p1
        timeline.append({"t":t,"cue":cue,"p":p,"g":g})
    return {"loop_gain":gain,"theta":theta,"equilibria":fixed_points(gain,theta),
            "last_call_probability":timeline[-1]["p"],"trajectory":timeline}

def microscopic(seed=0,playback=True,n=32,steps=300,audio_weight=5.,heard_weight=3.):
    rng=np.random.default_rng(seed);dt=.06
    pos=rng.normal(size=(n,2))*4.
    headings=rng.uniform(-np.pi,np.pi,n)
    velocity=np.stack((np.cos(headings),np.sin(headings)),1)*1.7
    calling=rng.binomial(1,.08,n).astype(float)
    history=[]
    for t in range(steps):
        diff=pos[None,:,:]-pos[:,None,:]
        dist=np.linalg.norm(diff,axis=2)
        mask_eye=np.eye(n,dtype=bool)
        neigh=(dist<7.)&(~mask_eye)
        counts=np.maximum(neigh.sum(1),1)
        delta_v=velocity[None,:,:]-velocity[:,None,:]
        separation=np.sum(np.where(((dist<1.2)&(~mask_eye))[:,:,None],
                         -diff/np.maximum(dist[:,:,None]**2,.05),0.),1)/counts[:,None]
        cohesion=np.sum(neigh[:,:,None]*diff,1)/counts[:,None]
        alignment=np.sum(neigh[:,:,None]*delta_v,1)/counts[:,None]
        hearing=np.exp(-dist/5)*(~mask_eye)
        perceived=(hearing@calling)/(n/4)
        toward_callers=(hearing[:,:,None]*calling[None,:,None]*diff/
                        np.maximum(dist[:,:,None],.5)).sum(1)/n
        r=np.linalg.norm(pos,axis=1,keepdims=True)
        wall=-np.maximum(r-10.,0.)*pos/np.maximum(r,1.)
        force=8*separation+.012*cohesion+.8*alignment+audio_weight*toward_callers+2*wall
        velocity+=dt*force
        speed=np.linalg.norm(velocity,axis=1,keepdims=True)
        velocity=velocity/np.maximum(speed,.001)*np.clip(speed,.6,3.)
        pos+=dt*velocity
        cue=.8 if playback and 80<=t<120 else 0.
        probabilities=expit(-2.8+heard_weight*perceived+cue)
        calling=(rng.random(n)<probabilities).astype(float)
        history.append({"t":t,"call_fraction":float(calling.mean()),
                        "hull_area":float(ConvexHull(pos).volume),"cue":cue})
    return history

def run(nseeds=SEEDS):
    mf={"weak":meanfield(*LOW),"strong":meanfield(*HIGH),
        "strong_no_playback":meanfield(*HIGH,pulse=False)}
    traces={}
    for cue in (False,True):
        records=[microscopic(k,playback=cue) for k in range(nseeds)]
        fraction=np.array([[v["call_fraction"] for v in rec] for rec in records])
        area=np.array([[v["hull_area"] for v in rec] for rec in records])
        traces["playback" if cue else "no_playback"]={
             "call_mean_time":fraction.mean(0).tolist(),
             "area_mean_time":area.mean(0).tolist(),
             "call_post":fraction[:,130:170].mean(1).tolist(),
             "call_late":fraction[:,240:280].mean(1).tolist(),
             "area_post":area[:,130:170].mean(1).tolist(),
             "area_late":area[:,240:280].mean(1).tolist()}
    differences={}
    for k in ("call_post","call_late","area_post","area_late"):
        z=np.array(traces["playback"][k])-np.array(traces["no_playback"][k])
        differences[k]={"paired_mean_difference":float(z.mean()),
                        "positive_seed_pairs":int((z>0).sum()),
                        "negative_seed_pairs":int((z<0).sum()),
                        "n_seeds":nseeds,
                        "per_seed_differences":z.tolist()}
    return {"status":"SYNTHETIC_ONLY_NOT_FIELD_RESULT",
       "model_version":"v12_bidirectional_acoustic_boids",
       "source_prior":"van Oosterom et al. 2016, Sci Rep, playback effects qualitative signs only",
       "fitted_to_original_fish_data":False,
       "threshold":4.,"threshold_scope":"Only this sigmoid response + linear cohesion model; necessary not sufficient for multistability",
       "meanfield":mf,"microscopic_replicates":nseeds,
       "microscopic":traces,"pair_differences":differences}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="validation_fish_boids_v12/results/acoustic_feedback_synthetic.json")
    args=parser.parse_args()
    out=run()
    path=Path(args.output);path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":out["status"],
       "weak_equilibria":out["meanfield"]["weak"]["equilibria"],
       "strong_equilibria":out["meanfield"]["strong"]["equilibria"],
       "weak_postplayback":out["meanfield"]["weak"]["last_call_probability"],
       "strong_postplayback":out["meanfield"]["strong"]["last_call_probability"],
       "paired_microscopic_effects":{
           k:{"mean":v["paired_mean_difference"],"positive":v["positive_seed_pairs"],
              "negative":v["negative_seed_pairs"]}
           for k,v in out["pair_differences"].items()}}))
if __name__=="__main__":main()
