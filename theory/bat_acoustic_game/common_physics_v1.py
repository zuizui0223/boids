"""Independent common-scene bat sonar proxy; no new measurements.

Source-derived core: Hase et al (2026), Proc R Soc B, DOI
10.1098/rspb.2026.0921, tau=.2s, asymmetric C=-4/+20, triangular
3-kHz susceptibility, 1ms RK4, 3ms/40kHz FM waveform, and correlation
threshold 0.5. 3D positions, deterministic pulse schedule, linear-FM
waveform, receiver noise gain and target-power test are NEW ASSUMPTIONS.
Neither original 2020 nor 2026 complete published simulator is rerun.
"""
from __future__ import annotations
from itertools import combinations
import json
import math
import numpy as np

FS=250_000
CHIRP_S=.003
BANDWIDTH_HZ=40_000
DT_S=.001
TAU_S=.200
PULSE_IPI_MS=70
PULSE_DURATION_MS=3
ACTIVE_START_MS=5_000
ACTIVE_END_MS=10_000
LAG_ACCEPTANCE_MS=.35
CORRELATION_CUTOFF=.5
ECHO_MARGINS_DB=(3.,6.,9.,12.)
RECEIVER_BACKGROUND_MULTIPLIER=10.
RECEIVER_THRESHOLD_DB=3.
BASE_3D=((0.,0.,0.),(.8,.4,.2),(.3,1.0,.7),(1.2,1.1,.3),
         (.5,.1,1.1),(1.4,.2,1.2),(.2,1.4,1.0),(1.1,1.6,.6))

def initial_tf(n):
    if n not in (4,8):
        raise ValueError("Only predeclared 4 and 8 bat groups")
    return tuple(48.+.4*(k-(n-1)/2) for k in range(n))

def points(n,scale):
    if scale not in (.7,3.):
        raise ValueError("Only predeclared synthetic scales")
    return tuple(tuple(x*scale for x in BASE_3D[i]) for i in range(n))

def receiver_powers(coords):
    n=len(coords)
    return tuple(tuple(
        0. if i==j else min(1.,1./sum(
            (coords[i][k]-coords[j][k])**2 for k in range(3)))
        for j in range(n)) for i in range(n))

def aij(fi,fj):
    return max(0.,1.-abs(fi-fj)/3.)

def pulse_flags(ms,n):
    if not ACTIVE_START_MS <= ms < ACTIVE_END_MS:
        return (False,)*n
    return tuple(
        (ms-(j*17)%PULSE_IPI_MS)%PULSE_IPI_MS < PULSE_DURATION_MS
        for j in range(n))

def drift(ff,f0,gain,flags):
    output=[]
    for i,fi in enumerate(ff):
        e=0.
        for j,fj in enumerate(ff):
            if j==i or not flags[j]:
                continue
            c=20. if fi>fj else -4.
            e+=c*gain[i][j]*aij(fi,fj)
        output.append((f0[i]-fi+e)/TAU_S)
    return output

def rk4(ff,f0,gain,flags):
    def add(x,y,m):
        return [a+m*b for a,b in zip(x,y)]
    k1=drift(ff,f0,gain,flags)
    k2=drift(add(ff,k1,DT_S/2),f0,gain,flags)
    k3=drift(add(ff,k2,DT_S/2),f0,gain,flags)
    k4=drift(add(ff,k3,DT_S),f0,gain,flags)
    return [a+DT_S*(p+2*q+2*r+s)/6
            for a,p,q,r,s in zip(ff,k1,k2,k3,k4)]

def time_series(n,scale,jar):
    f0=initial_tf(n)
    gain=receiver_powers(points(n,scale))
    state=list(f0)
    recorded=[]
    for ms in range(15_000):
        if ms in (0,5_000,10_000,14_999) or (
                8_000<=ms<10_000 and ms%20==0):
            recorded.append((ms,tuple(state)))
        if jar:
            state=rk4(state,f0,gain,pulse_flags(ms,n))
    late=[x for t,x in recorded if 8_000<=t<10_000]
    means=[sum(x[i] for x in late)/len(late) for i in range(n)]
    return {"initial_tf_khz":list(f0),"late_tf_khz":means,
            "last_tf_khz":state,"sampled_trace":recorded}

def chirp(tf_khz):
    t=np.arange(round(FS*CHIRP_S),dtype=float)/FS
    # Linear-FM waveform is NOT the 2026 species-informed pulse formula.
    phase=2*np.pi*((tf_khz*1000+BANDWIDTH_HZ)*t
                    -.5*(BANDWIDTH_HZ/CHIRP_S)*t*t)
    a=np.sin(phase)
    return a/np.linalg.norm(a)

def correlations(frequencies):
    waves=[chirp(f) for f in frequencies]
    n=len(waves)
    lag_span=round(FS*LAG_ACCEPTANCE_MS/1000.)
    mid=len(waves[0])-1
    zero=np.eye(n)
    lag=np.eye(n)
    for i in range(n):
        for j in range(i+1,n):
            cc=np.correlate(waves[i],waves[j],mode="full")
            a=abs(float(cc[mid]))
            b=float(np.max(np.abs(cc[mid-lag_span:mid+lag_span+1])))
            zero[i,j]=zero[j,i]=a
            lag[i,j]=lag[j,i]=b
    return {"zero":zero,"lag":lag}

def group_summary(frequencies,power):
    n=len(frequencies)
    matrices=correlations(frequencies)
    result={}
    for name,mat in matrices.items():
        unique=[float(mat[i,j]) for i in range(n) for j in range(i+1,n)]
        positives=sum(v>CORRELATION_CUTOFF for v in unique)
        masking=[sum(power[i][j]*float(mat[i,j])**2
                     for j in range(n) if j!=i) for i in range(n)]
        detections=[]
        for echo_db in ECHO_MARGINS_DB:
            hits=sum(echo_db>=RECEIVER_THRESHOLD_DB+
                10*math.log10(1+RECEIVER_BACKGROUND_MULTIPLIER*x)
                for x in masking)
            detections.append({"echo_margin_db":echo_db,
                               "detected_fraction":hits/n})
        result[name]={
            "mean_absolute_corr":sum(unique)/len(unique),
            "confusable_pair_fraction":positives/len(unique),
            "possible_confusable_pairs":positives,
            "mean_mask_proxy":sum(masking)/n,
            "echo_detection_by_margin":detections,
            "mean_echo_detection_across_margins":
                sum(d["detected_fraction"] for d in detections)/len(detections)
        }
    return result

def run():
    worlds=[]
    for n in (4,8):
        for scale in (.7,3.):
            p=receiver_powers(points(n,scale))
            base=time_series(n,scale,False)
            jar=time_series(n,scale,True)
            b=group_summary(base["late_tf_khz"],p)
            a=group_summary(jar["late_tf_khz"],p)
            pairs=list(combinations(range(n),2))
            def spread(fs):
                return sum(abs(fs[i]-fs[j]) for i,j in pairs)/len(pairs)
            worlds.append({
               "n":n,"scale":scale,
               "source_frequency_law":"Hase2026_NoNoise_RK4",
               "synthetic_positions_3D":True,
               "mean_pair_frequency_gap_noJAR_kHz":spread(base["late_tf_khz"]),
               "mean_pair_frequency_gap_JAR_kHz":spread(jar["late_tf_khz"]),
               "mean_pair_gap_gain_kHz":
                    spread(jar["late_tf_khz"])-spread(base["late_tf_khz"]),
               "assay_noJAR":b,"assay_JAR":a,
               "difference":{mode:{
                   "confusable_pair_fraction":
                     a[mode]["confusable_pair_fraction"]-
                     b[mode]["confusable_pair_fraction"],
                   "mean_echo_detection_across_margins":
                     a[mode]["mean_echo_detection_across_margins"]-
                     b[mode]["mean_echo_detection_across_margins"]}
                   for mode in ("zero","lag")},
               "freq_baselines":base["initial_tf_khz"],
               "freq_after_JAR":jar["late_tf_khz"]
            })
    fixture=[]
    for d in (0.,.3,.7,1.,2.,3.,5.,8.):
        c=correlations((48.,48.+d))
        fixture.append({
            "delta_tf_khz":d,
            "zero_lag_absolute_corr":float(c["zero"][0,1]),
            "max_delay_window_absolute_corr":float(c["lag"][0,1]),
            "crosses_half_zero":bool(c["zero"][0,1]>.5),
            "crosses_half_lag":bool(c["lag"][0,1]>.5)})
    return {
       "schema":1,
       "scientific_status":"SYNTHETIC_SOURCE_CONSTRAINED_PROXY_NOT_ORIGINAL_REPLAY",
       "source2020_numeric_reproduction":False,
       "source2026_group_numeric_reproduction":False,
       "added_bat_measurements":False,
       "source_equation":{
           "tau_ms":200,"C_high":20,"C_low":-4,
           "FD_khz":3,"FM_duration_ms":3,
           "FM_bandwidth_khz":40,"correlation_threshold":.5},
       "non_source_assumptions":{
           "sample_rate_hz":FS,"linear_FM":True,
           "fixed_3D_geometry":True,
           "receiver_noise_multiplier":RECEIVER_BACKGROUND_MULTIPLIER,
           "receiver_threshold_db":RECEIVER_THRESHOLD_DB,
           "echo_margins_db":ECHO_MARGINS_DB,
           "constant_pulse_IPI_ms":PULSE_IPI_MS,
           "source_extra_gaussian_noise_excluded":True,
           "unobserved_prey_or_false_reaction_not_modeled":True},
       "worlds":worlds,
       "pure_FM_frequency_ambiguity_fixture":fixture}

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
