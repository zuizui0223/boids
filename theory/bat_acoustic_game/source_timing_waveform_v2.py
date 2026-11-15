"""v2 source-timing and independent waveform sensitivity (SYNTHETIC ONLY).

Original source anchor: Hase et al 2026 DOI 10.1098/rspb.2026.0921.
Correct source input pulse 5 ms versus emitted FM pulse 3 ms; IPI gamma
mean70ms sd18.7ms; source law tau200ms, C(-4,+20), FD3kHz, dt1ms;
source reception window current-to-next own pulse.
NOT exact 2026 waveform, 2D moving flight, original group xcorr, or bat data.
"""
from __future__ import annotations
import bisect
import functools
import json
import math
from collections import Counter
import numpy as np
from common_physics_v1 import (
    FS, CHIRP_S, BANDWIDTH_HZ, initial_tf, points, receiver_powers,
    DT_S, TAU_S, CORRELATION_CUTOFF
)

SOURCE_RESPONSE_PULSE_MS=5  # not emitted FM duration
SOURCE_SOUND_MS=3
SOURCE_IPI_MEAN=70.
SOURCE_IPI_SD=18.7
SOURCE_IPI_GAMMA_SHAPE=(SOURCE_IPI_MEAN/SOURCE_IPI_SD)**2
SOURCE_IPI_GAMMA_SCALE=SOURCE_IPI_SD**2/SOURCE_IPI_MEAN
SOURCE_SPEED_MS=343. # m/s
MIN_SIMULATED_IPI_MS=10
GROUP_BEGIN_MS=5000
GROUP_END_MS=10000
TOTAL_MS=15000
SEED_BASE=20261102
CURVES={"linear":1., "power_0p6":.6, "power_2p0":2.}
FREQ_BIN_KHZ=.02
LOOKUP_MAX_ABS_ERROR=.025
N_SOUND=int(round(FS*CHIRP_S))
NFFT=1
while NFFT<2*N_SOUND-1: NFFT*=2


def source_schedules(n:int,scale:float):
    if n not in (4,8) or scale not in (.7,3.):
        raise ValueError("fixed four worlds only")
    rng=np.random.default_rng(SEED_BASE+100*n+(1 if scale==3. else 0))
    result=[]
    for bat in range(n):
        times=[]
        t=17*bat
        while t<TOTAL_MS:
            times.append(int(t))
            step=max(MIN_SIMULATED_IPI_MS,
                     int(round(float(rng.gamma(SOURCE_IPI_GAMMA_SHAPE,
                                                SOURCE_IPI_GAMMA_SCALE)))))
            t+=step
        result.append(times)
    return result


def source_receiver_drive(n,scale,schedules):
    coords=points(n,scale)
    p=np.asarray(receiver_powers(coords),dtype=float)
    drive=np.zeros((TOTAL_MS,n,n),dtype=np.float32)
    arrivals={}
    for i in range(n):
        for j in range(n):
            if i==j:continue
            dist=math.dist(coords[i],coords[j])
            delay=dist/SOURCE_SPEED_MS*1000.
            # Source-informed but time-of-flight quantization to 1ms is new.
            a=[int(round(t+delay)) for t in schedules[j]]
            arrivals[(i,j)]=a
            for t in a:
                low=max(t,GROUP_BEGIN_MS)
                high=min(t+SOURCE_RESPONSE_PULSE_MS,GROUP_END_MS)
                if high>low:
                    drive[low:high,i,j]=p[i,j]
    return drive,arrivals


def source_leaky_slope(state,f0,received):
    fd=state[:,None]-state[None,:]
    c=np.where(fd>0,20.,np.where(fd<0,-4.,0.))
    spectral=np.maximum(0.,1.-np.abs(fd)/3.)
    stim=np.sum(c*spectral*received,axis=1)
    return (f0-state+stim)/TAU_S


def source_rk4(old,f0,received):
    f=source_leaky_slope
    k1=f(old,f0,received)
    k2=f(old+.5*DT_S*k1,f0,received)
    k3=f(old+.5*DT_S*k2,f0,received)
    k4=f(old+DT_S*k3,f0,received)
    return old+DT_S/6*(k1+2*k2+2*k3+k4)


def source_tf_traces(n,scale,schedules,jar):
    f0=np.asarray(initial_tf(n),dtype=float)
    trace=np.tile(f0,(TOTAL_MS+1,1))
    if not jar:
        return trace
    drive,_=source_receiver_drive(n,scale,schedules)
    state=f0.copy()
    for ms in range(TOTAL_MS):
        state=source_rk4(state,f0,drive[ms])
        trace[ms+1]=state
    return trace


def normalized_wave(tf_khz,curve):
    exponent=CURVES[curve]
    t=(np.arange(N_SOUND,dtype=float)+.5)/FS
    fraction=t/CHIRP_S
    instantaneous=tf_khz*1000+BANDWIDTH_HZ*np.power(1-fraction,exponent)
    phase=2*np.pi*np.cumsum(instantaneous)/FS
    waveform=np.sin(phase)
    norm=np.linalg.norm(waveform)
    return waveform/norm


@functools.lru_cache(maxsize=8000)
def cached_fft(curve,key):
    signal=normalized_wave(key*FREQ_BIN_KHZ,curve)
    return np.fft.rfft(signal,n=NFFT)


@functools.lru_cache(maxsize=60000)
def binned_correlations(curve,ia,ib):
    if ia>ib:ia,ib=ib,ia
    a=cached_fft(curve,ia)
    b=cached_fft(curve,ib)
    cross=np.fft.irfft(a*np.conj(b),n=NFFT)
    return abs(float(cross[0])),float(np.max(np.abs(cross)))


def exact_correlations(curve,fa,fb):
    a=normalized_wave(fa,curve)
    b=normalized_wave(fb,curve)
    c=np.correlate(a,b,mode="full")
    return abs(float(np.dot(a,b))),float(np.max(np.abs(c)))


def get_correlations(curve,fa,fb,force_exact=False):
    if force_exact:
        return exact_correlations(curve,fa,fb)
    ia=int(round(fa/FREQ_BIN_KHZ));ib=int(round(fb/FREQ_BIN_KHZ))
    z,l=binned_correlations(curve,ia,ib)
    # Decision-near-threshold exact fallback avoids discretization-induced
    # spurious category changes (both lag and zero versions).
    if abs(z-CORRELATION_CUTOFF)<.055 or abs(l-CORRELATION_CUTOFF)<.055:
        return exact_correlations(curve,fa,fb)
    return z,l


def quantization_audit():
    # Predeclared 3 baseline anchors x 7 differences; no run outcome used.
    examples=[]
    for shape in CURVES:
        for f0 in (47.4,48.,49.2):
            for d in (.3,.7,1.,2.,3.,4.,5.):
                approx=get_correlations(shape,f0,f0+d,False)
                exact=exact_correlations(shape,f0,f0+d)
                err=max(abs(a-b) for a,b in zip(approx,exact))
                examples.append({"shape":shape,"f0":f0,"delta":d,"max_err":err})
    return max(x["max_err"] for x in examples),examples


def evaluate_world(n,scale,shape,schedules,arrival,trace,force_exact=False):
    eligible=0
    focused=0
    detected_zero=0
    detected_lag=0
    active_focal=0
    emissions_zero=0
    emissions_lag=0
    # Both arms use the same schedule and potential received pulses.
    for i in range(n):
        pul=schedules[i]
        for k,t in enumerate(pul[:-1]):
            if not GROUP_BEGIN_MS<=t<GROUP_END_MS:
                continue
            t_next=pul[k+1]
            active_focal+=1
            m0=m1=0
            for j in range(n):
                if i==j:continue
                arriving=arrival[(i,j)]
                lo=bisect.bisect_right(arriving,t)
                hi=bisect.bisect_left(arriving,t_next)
                for pos in range(lo,hi):
                    received_t=arriving[pos]
                    if received_t>=TOTAL_MS:continue
                    # Onset includes propagation delay, source emission time is known.
                    other_emit=schedules[j][pos]
                    fi=float(trace[t,i])
                    fj=float(trace[other_emit,j])
                    zero,lag=get_correlations(shape,fi,fj,force_exact=force_exact)
                    eligible+=1
                    if zero>CORRELATION_CUTOFF:m0+=1
                    if lag>CORRELATION_CUTOFF:m1+=1
            detected_zero+=m0
            detected_lag+=m1
            emissions_zero+=int(m0>0)
            emissions_lag+=int(m1>0)
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    tfmeans=np.mean(trace[8000:10000],axis=0)
    gap=np.mean([abs(tfmeans[i]-tfmeans[j]) for i,j in pairs])
    return {"focal_emissions":active_focal,
            "eligible_other_bat_pulses":eligible,
            "zero_count":detected_zero,
            "lag_count":detected_lag,
            "zero_per_focal":detected_zero/active_focal,
            "lag_per_focal":detected_lag/active_focal,
            "zero_focal_any_fraction":emissions_zero/active_focal,
            "lag_focal_any_fraction":emissions_lag/active_focal,
            "mean_pair_tf_gap_khz":float(gap)}


def run():
    max_err,errors=quantization_audit()
    # Audit is predeclared independently of any synthetic biological outcome.
    full_exact_fallback = max_err>LOOKUP_MAX_ABS_ERROR
    worlds=[]
    for n in (4,8):
        for scale in (.7,3.):
            pulses=source_schedules(n,scale)
            drive,arrival=source_receiver_drive(n,scale,pulses)
            baseline=source_tf_traces(n,scale,pulses,False)
            changed=source_tf_traces(n,scale,pulses,True)
            # Confirm source baseline actually restored 5s after input ended.
            baseline_tf=np.asarray(initial_tf(n))
            max_rest_error=float(np.max(np.abs(changed[-1]-baseline_tf)))
            for shape in CURVES:
                left=evaluate_world(n,scale,shape,pulses,arrival,baseline,full_exact_fallback)
                right=evaluate_world(n,scale,shape,pulses,arrival,changed,full_exact_fallback)
                if left["focal_emissions"]!=right["focal_emissions"] or left["eligible_other_bat_pulses"]!=right["eligible_other_bat_pulses"]:
                    raise ValueError("STOP_UNMATCHED_JAR_AND_NOJAR_OPPORTUNITY")
                worlds.append({"n":n,"scale":scale,"waveform":shape,
                    "baseline":left,"jar":right,
                    "delta_lag_per_focal":right["lag_per_focal"]-left["lag_per_focal"],
                    "delta_zero_per_focal":right["zero_per_focal"]-left["zero_per_focal"],
                    "delta_tf_gap_khz":right["mean_pair_tf_gap_khz"]-left["mean_pair_tf_gap_khz"],
                    "maximum_poststimulus_TF_baseline_error_khz":max_rest_error,
                    "source_fixed_schedules":True,
                    "source_timings_ms":{"input_rectangle":5,"emitted_chirp":3,
                          "IPI_target_mean":70,"IPI_target_sd":18.7}})
    return {"schema":2,"status":"SYNTHETIC_SOURCE_INFORMED_WAVEFORM_AND_WINDOW_SENSITIVITY",
            "new_bat_measurements":False,
            "source_original_2026_group_reproduced":False,
            "source_original_2020_capture_reproduced":False,
            "unverified_source_species_waveform":True,
            "source_2026_original_2D_dynamic_flight_reproduced":False,
            "quantization_max_err_fixed_fixtures":max_err,
            "cache_limit":LOOKUP_MAX_ABS_ERROR,
            "exact_correlation_fallback_from_lookup_error":full_exact_fallback,
            "worlds":worlds}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
