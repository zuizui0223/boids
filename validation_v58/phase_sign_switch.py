"""v58: controlled change of ONLY tide phase sign in a fitted next-heading predictor.

- Geometry: model-implied delta between predicted rising and falling bearings
  at exactly the same observed GPS-B feature state and water height.
- Observation: heldout genuine next GPS bearing scored against actual-sign vs
  flipped-sign model predictions on exactly the same original source episodes.

Neither output is an observed causal tide intervention, actual physical turn,
prey-front orientation, or social Boids steering coefficient.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np

MIN_ROWS=1000
MIN_BIRDS=3
MIN_WEEKS=4
MIN_PHASE_GROUP_ROWS=200
MIN_PHASE_QTRAIN_PER_SIGN=50
SEED=20261107

def phase_versions(rows):
    if not rows:raise ValueError("Empty original source sample")
    for row in rows:
        if row.get("phase") not in (-1,1):
            raise ValueError("SOURCE_STOP_ORIGINAL_ACTUAL_PHASE_NOT_PLUS_MINUS_ONE")
    plus=[{**r,"phase":1} for r in rows]
    minus=[{**r,"phase":-1} for r in rows]
    return plus,minus

def _vectors(rows,pred):
    target=np.asarray([[r["target_e"],r["target_n"]] for r in rows],dtype=float)
    p=np.asarray(pred,dtype=float)
    if target.shape!=p.shape or p.ndim!=2 or p.shape[1]!=2:
        raise ValueError("SOURCE_STOP_ORIGINAL_HEADING_VECTOR_DIMENSIONS")
    truthnorm=np.linalg.norm(target,axis=1)
    prednorm=np.linalg.norm(p,axis=1)
    if (not np.isfinite(target).all() or not np.isfinite(p).all() or
        np.any(truthnorm<=1e-10) or np.any(prednorm<=1e-10)):
        raise ValueError("SOURCE_STOP_UNDEFINED_NONFINITE_OR_ZERO_DIRECTION")
    cos=np.sum(target*p,axis=1)/(truthnorm*prednorm)
    cos=np.clip(cos,-1.,1.)
    return 1.-cos,np.rad2deg(np.arccos(cos))

def phase_rotation(pminus,pplus):
    """Signed east/north rotation, counterclockwise from predicted - to +."""
    a=np.asarray(pminus,dtype=float);b=np.asarray(pplus,dtype=float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=2:
        raise ValueError("SOURCE_STOP_ROTATION_2D_ARRAY_SHAPE")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or (
        np.linalg.norm(a,axis=1)<=1e-10).any() or (
        np.linalg.norm(b,axis=1)<=1e-10).any():
        raise ValueError("SOURCE_STOP_ROTATION_UNDEFINED_PREDICTION")
    cross=a[:,0]*b[:,1]-a[:,1]*b[:,0]
    dot=np.sum(a*b,axis=1)
    return np.degrees(np.arctan2(cross,dot))

def _summary(rows,gain_cos,gain_deg,rotation,indices,*,name,
             bird_draws=10000,week_draws=4000,seed=SEED,
             min_rows=MIN_PHASE_GROUP_ROWS,phase_train_counts=None):
    inds=np.asarray(indices,dtype=int)
    bybird=defaultdict(list);byweek=defaultdict(list)
    for i in inds:
        bybird[rows[i]["id"]].append(i)
        byweek[rows[i]["t"].isocalendar()[:2]].append(i)
    n=len(inds);nb=len(bybird);nw=len(byweek)
    admission=n>=min_rows and nb>=MIN_BIRDS and nw>=MIN_WEEKS
    if phase_train_counts is not None and min(phase_train_counts.values())<MIN_PHASE_QTRAIN_PER_SIGN:
        admission=False
    base={"source_group":name,"test_original_rows":n,
          "test_birds":nb,"test_weeks":nw,
          "training_phase_sign_source_counts":phase_train_counts,
          "same_source_rows_all_model_phase_signs":True}
    if not admission:
        return {**base,"admission":"NOT_ADMITTED_SOURCE_OR_BOTH_PHASES_IN_TRAIN",
                "new_group_predictive_effect":"NOT_ESTIMATED"}
    observed=np.column_stack((gain_cos[inds],gain_deg[inds],np.abs(rotation[inds])))
    pos=np.column_stack((gain_cos,gain_deg,np.abs(rotation)))
    bird=np.asarray([pos[k].mean(0) for k in bybird.values()])
    week=[]
    for ids in byweek.values():
        part=defaultdict(list)
        for i in ids:part[rows[i]["id"]].append(i)
        week.append(np.mean([pos[k].mean(0) for k in part.values()],axis=0))
    week=np.asarray(week)
    rng=np.random.default_rng(seed)
    # Rows are NEVER independently resampled; original bird/week clusters are.
    bb=bird[rng.integers(len(bird),size=(bird_draws,len(bird)))].mean(axis=1)
    bw=week[rng.integers(len(week),size=(week_draws,len(week)))].mean(axis=1)
    results={}
    for j,key in enumerate(("actual_minus_flipped_cosine_loss_gain",
                             "actual_minus_flipped_angle_error_gain_degrees",
                             "model_phase_switch_absolute_angle_degrees")):
        results[key]={
            "pooled_equal_bird_mean":float(bird[:,j].mean()),
            "paired_whole_bird_bootstrap95":np.quantile(bb[:,j],[.025,.975]).tolist(),
            "positive_birds":int(sum(bird[:,j]>0)),
            "separate_equal_week_then_bird_mean":float(week[:,j].mean()),
            "paired_whole_week_bootstrap95":np.quantile(bw[:,j],[.025,.975]).tolist(),
            "positive_weeks":int(sum(week[:,j]>0))}
    # Signed rotation is circular: do not arithmetically average angles near ±180.
    rad=np.deg2rad(rotation[inds])
    bird_complex=[np.mean(np.exp(1j*np.deg2rad(rotation[k]))) for k in bybird.values()]
    aggregate=np.mean(bird_complex)
    results["model_implied_signed_switch"]={
        "counterclockwise_is_positive_from_falling_to_rising":True,
        "equal_bird_circular_mean_degrees":float(np.rad2deg(np.angle(aggregate))),
        "equal_bird_circular_resultant_length":float(np.abs(aggregate)),
        "fraction_test_rows_counterclockwise":float(np.mean(rotation[inds]>0)),
        "fraction_test_rows_abs_switch_gt_10deg":float(np.mean(np.abs(rotation[inds])>10)),
        "not_an_observed_change_in_bird_heading":True}
    return {**base,"admission":"MODEL_SWITCH_AND_OBSERVED_ORIGINAL_HEADING_SCORING",
            "metrics":results}

def analyse_switch(train,test,forecast_fn,*,bird_draws=10000,week_draws=4000,seed=SEED):
    if not train or not test:raise ValueError("Missing training or evaluation source")
    ntrain=len(train);ntest=len(test)
    ids={r["id"] for r in test}
    weeks={r["t"].isocalendar()[:2] for r in test}
    if ntrain<MIN_ROWS or ntest<MIN_ROWS or len(ids)<MIN_BIRDS or len(weeks)<MIN_WEEKS:
        return {"admission":"NOT_ADMITTED_ORIGINAL_TRAIN_OR_TEST_SAMPLE",
                "train_source_rows":ntrain,"test_source_rows":ntest,
                "test_birds":len(ids),"test_weeks":len(weeks)}
    plus,minus=phase_versions(test)
    actual=np.asarray([r["phase"] for r in test],dtype=int)
    # One source model fit for all three evaluation conditions. Includes
    # original actually observed phase for exact row-by-row replay.
    pred=np.asarray(forecast_fn(train,list(test)+plus+minus,1),dtype=float)
    if pred.shape!=(3*ntest,2):
        raise ValueError("SOURCE_STOP_PHASE_PAIR_FORECAST_SHAPE")
    porig,pplus,pminus=pred[:ntest],pred[ntest:2*ntest],pred[2*ntest:]
    selected=np.where(actual[:,None]==1,pplus,pminus)
    if not np.allclose(porig,selected,atol=1e-10,rtol=1e-10):
        raise ValueError("SOURCE_STOP_SAME_COVARIATES_ACTUAL_PHASE_REPLAY")
    opposite=np.where(actual[:,None]==-1,pplus,pminus)
    cactual,aactual=_vectors(test,porig)
    cflip,aflip=_vectors(test,opposite)
    rotation=phase_rotation(pminus,pplus)
    gc=cflip-cactual
    ga=aflip-aactual
    q=np.quantile([r["h"] for r in train],[.25,.5,.75])
    bindex=np.searchsorted(q,[r["h"] for r in test],side="right")
    trainb=np.searchsorted(q,[r["h"] for r in train],side="right")
    output={"admission":"MODEL_FIXED_PHASE_SWAP_ON_ORIGINAL_HELDOUT_GPS",
            "train_original_rows":ntrain,"test_original_rows":ntest,
            "test_birds":len(ids),"test_weeks":len(weeks),
            "phase_mutation_only_changes_phase_and_interaction_h":True,
            "identical_actual_predictions_replayed":True,
            "not_a_realized_counterfactual_or_causal_steering_test":True,
            "source_train_height_quartiles_NAP_m":list(map(float,q)),
            "main":_summary(test,gc,ga,rotation,range(ntest),name="whole_test",
                min_rows=MIN_ROWS,bird_draws=bird_draws,week_draws=week_draws,seed=seed),
            "original_phase_subgroups":{},
            "source_height_quartile_subgroups":{}}
    for j,phase in enumerate((-1,1)):
        inds=np.flatnonzero(actual==phase)
        output["original_phase_subgroups"]["falling" if phase==-1 else "rising"]=_summary(
            test,gc,ga,rotation,inds,
            name="original_falling" if phase==-1 else "original_rising",
            bird_draws=bird_draws,week_draws=week_draws,seed=seed+j+10)
    for j in range(4):
        inds=np.flatnonzero(bindex==j)
        counts={p:int(sum((trainb==j)&(np.asarray([r["phase"] for r in train])==p)))
                for p in (-1,1)}
        output["source_height_quartile_subgroups"][str(j+1)]=_summary(
            test,gc,ga,rotation,inds,name="training_height_quartile_"+str(j+1),
            bird_draws=bird_draws,week_draws=week_draws,seed=seed+j+50,
            phase_train_counts={"falling":counts[-1],"rising":counts[1]})
    return output
