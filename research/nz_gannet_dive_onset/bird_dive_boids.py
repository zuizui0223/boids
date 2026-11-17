"""Conditional comparison of a plunging seabird with no attack on the same school.
Distances in fish body lengths inside the solver, depths in meters in the results.
Run with python bird_dive_boids.py. Requires numpy, pandas and numba.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

BL = .20
CUTOFFS = (4., 5., 10.)


@njit
def fish_step(p, v, predators, dt):
    for i in range(len(p)):
        ax, ay, az = 0., 0., 0.
        fleeing = False
        for j in range(len(predators)):
            x, y, z = predators[j] - p[i]
            dist = np.sqrt(x*x + y*y + z*z)
            if 0 < dist < 10.:
                ax -= 12.*x/dist
                ay -= 12.*y/dist
                az -= 12.*z/dist
                fleeing = True
        if not fleeing:
            for j in range(len(p)):
                x = p[j,0] - p[i,0]
                y = p[j,1] - p[i,1]
                z = p[j,2] - p[i,2]
                dist = np.sqrt(x*x + y*y + z*z)
                if dist == 0. or 5. <= dist < 5.5:
                    continue
                if dist < 5.:
                    force = -12.*(1.-dist/5.)
                else:
                    force = min(1.2, 2.4*(dist-5.5))
                ax += force*x/dist
                ay += force*y/dist
                az += force*z/dist
        z = p[i,2]
        az += 1200.*(1./(1.+z*z) - 1./(1.+(100.-z)**2))
        v[i,0] += ax*dt
        v[i,1] += ay*dt
        v[i,2] += az*dt
        speed = np.sqrt(np.dot(v[i],v[i]))
        limit = 12. if fleeing else 3.
        if speed > limit:
            v[i] *= limit/speed
    p += dt*v
    assert p[:,2].min() >= 0. and p[:,2].max() <= 100.


@njit
def dive_depth(t, target_z):
    # Enters vertically at 70 BL/s. Brakes 10 BL above target at 210 BL/s^2.
    # Integrate the piecewise speeds exactly between fish update times.
    brake = max(0., target_z - 10.) / 70.
    stop = 70./210.
    if t < brake:
        return 70.*t
    age = t-brake
    if age < stop:
        return 70.*brake + 70.*age - 105.*age**2
    return 70.*brake + 70.*stop - 105.*stop**2 - 17.*(age-stop)


@njit
def run(start, velocity, offsets, nsteps, passes, dt):
    p = start.copy()
    v = velocity.copy()
    trace = np.empty(nsteps+1)
    targets = np.zeros((5,3))
    for k in range(nsteps):
        trace[k] = p[:,2].mean() * BL
        if k % round(2/dt) == 0 and k//round(2/dt) < passes:
            j = k//round(2/dt)
            targets[j] = p.sum(axis=0)/len(p) + offsets[j]
        pred = np.empty((5,3))
        count = 0
        for j in range(passes):
            t = k*dt - 2*j
            if t < 0:
                continue
            z = dive_depth(t,targets[j,2])
            if z >= 0.:
                pred[count] = targets[j]
                pred[count,2] = z
                count += 1
        fish_step(p,v,pred[:count],dt)
    trace[-1] = p[:,2].mean()*BL
    return p,v,trace


def conditioned_history(p, v, offsets, onset_m, dt, history_s=2.):
    """Set school translation before, never at, the attack; solve for onset centroid."""
    guess = onset_m
    previous = None
    for iteration in range(12):
        start = p.copy()
        start[:,2] += guess/BL - start[:,2].mean()
        assert start[:,2].min() > 0 and start[:,2].max() < 100
        final, velocity, trace = run(start,v,offsets,round(history_s/dt),0,dt)
        error = trace[-1]-onset_m
        if abs(error) < 1.e-5:
            return final,velocity,trace
        if previous is None:
            next_guess = guess-error
        else:
            old_guess, old_error = previous
            next_guess = guess-error*(guess-old_guess)/(error-old_error)
        previous = guess,error
        guess = next_guess
    raise RuntimeError('Failed to match onset depth')


def main():
    rows = []
    for seed in range(32):
        rng = np.random.default_rng(seed)
        direction = rng.normal(size=(100,3))
        cloud = direction / np.linalg.norm(direction,axis=1)[:,None]
        cloud *= (10*rng.random(100)**(1/3))[:,None]
        cloud[:,2] += 50.
        offsets = rng.uniform(-2,2,(5,3))
        for dt in (.1,.05):
            warm_p, warm_v, legacy_trace = run(cloud, np.zeros_like(cloud), offsets, round(10/dt), 0, dt)
            for onset in (1.6,3.5,4.5,10.,None):
                if onset is None:
                    p,v,pre = warm_p,warm_v,legacy_trace
                    label = 'legacy'
                else:
                    p,v,pre = conditioned_history(warm_p,warm_v,offsets,onset,dt,
                                                  history_s=.5 if onset==1.6 else 2.)
                    label = str(onset)
                for count in (0,1,5):
                    _,_,post = run(p,v,offsets,round(10/dt),count,dt)
                    assert abs(pre[-1]-post[0]) < 1.e-10
                    for seconds in (2,10):
                        n = round(seconds/dt)
                        for cutoff in CUTOFFS:
                            # Exclude instant t=0 from both windows. Model sampled at dt intervals.
                            b = pre[-1-min(n,len(pre)-1):-1]
                            a = post[1:1+n]
                            rows.append((seed,dt,label,count,seconds,len(b)*dt,cutoff,pre[-1],
                                b.mean(),a.mean(),a[-1],dt*np.sum(b<=cutoff),dt*np.sum(a<=cutoff)))
    data = pd.DataFrame(rows, columns=['seed','dt_s','start_label','n_plunges_scheduled',
        'post_window_s','pre_window_s','cutoff_m','actual_onset_m','pre_mean_m','post_mean_m',
        'post_end_m','pre_residence_s','post_residence_s'])
    keys = ['seed','dt_s','start_label','post_window_s','cutoff_m']
    control = data[data.n_plunges_scheduled==0].set_index(keys)
    key_values = pd.MultiIndex.from_frame(data[keys])
    for var in ['post_mean_m','post_end_m','post_residence_s']:
        data['vs_control_'+var] = data[var] - control[var].reindex(key_values).to_numpy()
    assert not data.duplicated(keys+['n_plunges_scheduled']).any()
    assert (data.post_residence_s<=data.post_window_s+1.e-8).all()
    assert (data.pre_residence_s<=data.pre_window_s+1.e-8).all()
    base = Path(__file__).parent
    data.to_csv(base/'bird_dive_boids_runs.csv',index=False,float_format='%.6f')
    outcomes = ['actual_onset_m','pre_mean_m','post_mean_m','pre_residence_s','post_residence_s',
                'vs_control_post_mean_m','vs_control_post_residence_s']
    groups = ['dt_s','start_label','n_plunges_scheduled','post_window_s','pre_window_s','cutoff_m']
    summary = data.groupby(groups)[outcomes].mean()
    disp = data.groupby(groups).vs_control_post_residence_s
    summary['seed_p10_change_s'] = disp.quantile(.10)
    summary['seed_p90_change_s'] = disp.quantile(.90)
    summary.to_csv(base/'bird_dive_boids_summary.csv',float_format='%.6f')


if __name__ == '__main__':
    main()
