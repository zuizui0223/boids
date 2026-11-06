"""Separate angular accuracy from magnitude in paired unit-direction forecasts.

Pure numerical code: no data downloads and no model fitting. The symmetric
four-hybrid allocation is exact algebra, not a causal mechanism decomposition.
"""
from __future__ import annotations
from collections import defaultdict
import numpy as np

MIN_NORM = 1e-12
UNIT_TOLERANCE = 1e-8

class UndefinedBearing(ValueError):
    """A near-zero prediction cannot define a unique direction."""

def decompose_predictions(truth, baseline, augmented):
    """Return per-row losses and the exact bearing/magnitude allocation."""
    y, a, b = [np.asarray(x, dtype=float) for x in (truth, baseline, augmented)]
    if y.ndim != 2 or y.shape[1] != 2 or len(y) == 0 or a.shape != y.shape or b.shape != y.shape:
        raise ValueError('Expected nonempty, aligned Nx2 arrays')
    if not all(np.isfinite(x).all() for x in (y,a,b)):
        raise ValueError('Nonfinite source truth or forecast')
    if np.any(np.abs(np.linalg.norm(y,axis=1)-1.) > UNIT_TOLERANCE):
        raise ValueError('Observed directions must already be unit vectors')
    r0, r1 = np.linalg.norm(a,axis=1), np.linalg.norm(b,axis=1)
    if np.any(r0 <= MIN_NORM) or np.any(r1 <= MIN_NORM):
        raise UndefinedBearing('NOT_ADMITTED_UNDEFINED_BEARING')
    u0, u1 = a/r0[:,None], b/r1[:,None]
    c0, c1 = np.sum(y*u0,axis=1), np.sum(y*u1,axis=1)
    loss0 = .5*np.square(y-a).sum(axis=1)
    loss1 = .5*np.square(y-b).sum(axis=1)
    bearing = .5*(r0+r1)*(c1-c0)
    magnitude = .5*(r0*r0-r1*r1) - .5*(r0-r1)*(c0+c1)
    if not np.allclose(bearing+magnitude,loss0-loss1,atol=1e-10,rtol=0.):
        raise ArithmeticError('Four-hybrid allocation does not sum to original loss difference')
    cross0 = y[:,0]*u0[:,1]-y[:,1]*u0[:,0]
    cross1 = y[:,0]*u1[:,1]-y[:,1]*u1[:,0]
    return {
        'vector_loss0':loss0,'vector_loss1':loss1,
        'bearing_component':bearing,'magnitude_component':magnitude,
        'cosine_loss0':1.-np.clip(c0,-1.,1.),
        'cosine_loss1':1.-np.clip(c1,-1.,1.),
        'angle_degrees0':np.degrees(np.arctan2(np.abs(cross0),c0)),
        'angle_degrees1':np.degrees(np.arctan2(np.abs(cross1),c1)),
        'radius0':r0,'radius1':r1,
    }

def summarize_rows(rows, losses, *, bird_draws=10000, week_draws=4000, seed=20261106):
    """Paired whole-bird and whole-week inference for distinct estimands."""
    keys=('vector_loss0','vector_loss1','bearing_component','magnitude_component',
          'cosine_loss0','cosine_loss1','angle_degrees0','angle_degrees1','radius0','radius1')
    n=len(rows)
    if n==0 or any(np.asarray(losses[k]).shape!=(n,) for k in keys):
        raise ValueError('Row identifiers and prediction losses are not aligned')
    if bird_draws<1 or week_draws<1:
        raise ValueError('Positive bootstrap draw count required')
    raw=np.column_stack([losses[k] for k in keys])
    if not np.isfinite(raw).all():
        raise ValueError('Nonfinite prediction diagnostics')
    bird=defaultdict(list); week=defaultdict(list)
    for i,r in enumerate(rows):
        bird[r['id']].append(i)
        week[r['t'].isocalendar()[:2]].append(i)
    bybird=np.stack([raw[ix].mean(0) for ix in bird.values()])
    byweek=[]
    for ix in week.values():
        present=defaultdict(list)
        for i in ix: present[rows[i]['id']].append(i)
        byweek.append(np.stack([raw[js].mean(0) for js in present.values()]).mean(0))
    byweek=np.stack(byweek)
    def gains(a):
        return np.stack((a[...,0]-a[...,1],a[...,2],a[...,3],
                         a[...,4]-a[...,5],a[...,6]-a[...,7]),axis=-1)
    def aggregate(cluster, draws, rng):
        mean=cluster.mean(0)
        index=rng.integers(len(cluster),size=(draws,len(cluster)))
        boot=gains(cluster[index].mean(1))
        point=gains(mean); individual=gains(cluster)
        if not np.allclose(boot[:,0],boot[:,1]+boot[:,2],atol=1e-10,rtol=0.):
            raise ArithmeticError('Bootstrap decomposition identity failed')
        names=('vector_loss_gain','bearing_component','magnitude_component',
               'cosine_loss_gain','absolute_angle_gain_degrees')
        result={'model_mean_losses':dict(zip(keys,map(float,mean)))}
        for j,name in enumerate(names):
            result[name]={'mean':float(point[j]),
                          'paired_bootstrap_CI95':np.quantile(boot[:,j],[.025,.975]).tolist(),
                          'positive_clusters':int(np.sum(individual[:,j]>0))}
        result['vector_relative_error_reduction']=float((mean[0]-mean[1])/mean[0]) if mean[0]>0 else None
        result['cosine_relative_error_reduction']=float((mean[4]-mean[5])/mean[4]) if mean[4]>0 else None
        result['exact_additive_identity_verified']=True
        return result
    return {
        'n_rows':n,'n_birds':len(bird),'n_weeks':len(week),
        'primary_endpoint':'cosine_loss_gain',
        'equal_bird':aggregate(bybird,bird_draws,np.random.default_rng(seed)),
        'equal_week_then_bird':aggregate(byweek,week_draws,np.random.default_rng(seed+1)),
        'prediction_norm_diagnostics':{
            'M0_min_median_max':np.quantile(raw[:,8],[0,.5,1]).tolist(),
            'M1_min_median_max':np.quantile(raw[:,9],[0,.5,1]).tolist(),
            'M0_count_above_one':int(np.sum(raw[:,8]>1.)),
            'M1_count_above_one':int(np.sum(raw[:,9]>1.)),
            'not_calibrated_directional_concentration':True},
        'maximum_per_row_allocation_residual':float(np.max(np.abs(raw[:,0]-raw[:,1]-raw[:,2]-raw[:,3]))),
        'interpretation':'Exact predictive-loss attribution; not causal steering or physical speed',
    }
