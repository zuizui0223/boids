"""v28 target-free conditional residual correlation between current and aged others.

All nuisance preprocessing/ridge fits exclude the heldout recording. This is an
OBSERVATIONAL conditional redundancy diagnostic; never infer fish social forces.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

AGES=(0.,.2,1.)
RIDGE_ALPHA=10.

class SourceStop(Exception):
    pass


def source_panels(age_panels, geometry="geometry"):
    """Extract original source-verified v24/v26d G and other-speed columns only."""
    if geometry not in age_panels: raise SourceStop("V28_MISSING_GEOMETRY")
    g=np.asarray(age_panels[geometry],dtype=float)
    if g.ndim!=2 or g.shape[1]<3 or len(g)<1000:
        raise SourceStop("V28_SOURCE_GEOMETRY_SCHEMA_STOP")
    out={"geometry":g}
    for age in AGES:
        name=f"age_{age:g}s"
        z=np.asarray(age_panels[name],dtype=float)
        if z.ndim!=2 or z.shape!=(len(g),g.shape[1]+2):
            raise SourceStop("V28_AGE_REPRESENTATION_SCHEMA_STOP")
        if not np.allclose(z[:,:g.shape[1]],g,rtol=0,atol=1e-10):
            raise SourceStop("V28_AGE_FEATURE_ORIGINAL_FOCAL_GEOMETRY_DRIFT")
        out[name]=z[:,-2:].copy()
    if not all(np.isfinite(x).all() for x in out.values()):
        raise SourceStop("V28_NONFINITE_VELOCITY_FEATURE_STOP")
    return out


def _oof_residual(trains, held_g, held_target):
    """Estimate others' velocity from focal G using OTHER FILES ONLY."""
    x=np.concatenate([f["geometry"] for f in trains],axis=0)
    scaler=StandardScaler().fit(x)
    train_y=np.concatenate([f["vfield"] for f in trains],axis=0)
    model=Ridge(alpha=RIDGE_ALPHA).fit(scaler.transform(x),train_y)
    predicted=model.predict(scaler.transform(held_g))
    return held_target-predicted


def partial_vec_correlation(a,b):
    aa=np.asarray(a,dtype=float);bb=np.asarray(b,dtype=float)
    if aa.shape!=bb.shape or aa.ndim!=2 or aa.shape[1]!=2 or len(aa)<1000:
        raise SourceStop("V28_PARTIAL_CORRELATION_COHORT_SHAPE")
    aa=aa-aa.mean(axis=0);bb=bb-bb.mean(axis=0)
    den=float(np.linalg.norm(aa)*np.linalg.norm(bb))
    if not den>1e-8:
        raise SourceStop("V28_ZERO_RESIDUAL_COVARIANCE_SUPPORT_STOP")
    corr=float(np.sum(aa*bb)/den)
    if not np.isfinite(corr) or abs(corr)>1+1e-10:
        raise SourceStop("V28_INVALID_RESIDUAL_CORRELATION")
    return corr


def assess(files,study,source_receipt):
    ids=list(files)
    need={"tetra":6,"ayu":7,"stickleback":3}.get(study)
    if need is None or len(files)!=need or len(set(ids))!=need:
        raise SourceStop("V28_ORIGINAL_STUDY_FILE_COUNT_STOP")
    if any(set(x)!={"geometry","age_0s","age_0.2s","age_1s"} for x in files.values()):
        raise SourceStop("V28_ONLY_FROZEN_SOURCE_AGES_ALLOWED")
    observations=[]
    for held in ids:
        held_g=files[held]["geometry"]
        residual={}
        for age in AGES:
            label=f"age_{age:g}s"
            training=[{"geometry":files[k]["geometry"],"vfield":files[k][label]}
                      for k in ids if k!=held]
            residual[label]=_oof_residual(training,held_g,files[held][label])
        stats={}
        for age in AGES[1:]:
            label=f"age_{age:g}s"
            stats[label]=partial_vec_correlation(residual["age_0s"],residual[label])
        observations.append({"source_file":held,"n_fish_frame_rows":len(held_g),
                             "test_file_held_out_from_nuisance_models":True,
                             "residual_vec_correlation":stats})
    means={f"age_{age:g}s":float(np.mean([rec["residual_vec_correlation"][f"age_{age:g}s"] for rec in observations]))
           for age in AGES[1:]}
    return {
      "status":"V28_ORIGINAL_TARGET_FREE_HELDOUT_CONDITIONAL_RESIDUAL_CORRELATION",
      "study":study,"source_receipt":source_receipt,"original_source_files":len(files),
      "recording_scores":observations,"equal_recording_mean_conditional_residual_correlation":means,
      "ages_seconds":list(AGES),"alpha_pre_registered":RIDGE_ALPHA,
      "train_test_split":"every whole source FILE is held out from standardization and nuisance R regression",
      "original_fish_future_target_scores_computed":False,
      "source_fish_coordinates_redistributed":False,
      "cohort_independent_biological_schools_unknown":True,
      "social_causal_or_acoustic_mechanism_inferred":False,
      "scientific_ceiling":"out-of-file residual movement association only, not active fish communication"}
def save(path,obj):
    x=Path(path);x.parent.mkdir(parents=True,exist_ok=True)
    x.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
