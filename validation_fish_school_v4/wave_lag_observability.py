"""Fixed original 6-WAV lag preflight. Not fish or Boids force inference.
Preserve the original 230-frame mismatch SOURCE_FRAME_SYNC_STOP.
Use first common 17 s for diagnostic only, not correction/alignment.
"""
import argparse,io,json,wave
from pathlib import Path
import numpy as np
from xav_source_gate import BLOBS,blob_sha,PIN
WINDOWS=(1,5,9,13);DURATION=.5;BAND=(200,2500);MAX_LAG_MS=10
class AudioStop(Exception):pass
def decode24(data):
    if len(data)%3:raise AudioStop("partial 24-bit frame")
    a=np.frombuffer(data,dtype=np.uint8).reshape(-1,3).astype(np.int32)
    u=a[:,0]|(a[:,1]<<8)|(a[:,2]<<16)
    return np.where(u>=2**23,u-2**24,u).astype(np.float64)/(2**23)
def filtered(x,fs):
    x=np.asarray(x,dtype=float)
    if fs<=2*BAND[1]:raise AudioStop("Invalid Nyquist band")
    spec=np.fft.rfft(x-np.mean(x));f=np.fft.rfftfreq(len(x),1/fs)
    spec[(f<BAND[0])|(f>BAND[1])]=0
    return np.fft.irfft(spec,n=len(x))
def lag_corr(a,b,fs=32000):
    if len(a)!=len(b):raise AudioStop("Unmatched audio windows")
    x,y=filtered(a,fs),filtered(b,fs)
    n=len(x);pad=1<<(2*n-2).bit_length()
    c=np.fft.irfft(np.fft.rfft(x,pad)*np.conj(np.fft.rfft(y,pad)),pad)
    m=int(np.ceil(MAX_LAG_MS*fs/1000))
    if m>=n:raise AudioStop("Lag exceeds window")
    r=np.concatenate((c[-m:],c[:m+1]));idx=int(np.argmax(abs(r)))
    denom=float(np.linalg.norm(x)*np.linalg.norm(y))
    if denom<1e-12:raise AudioStop("Quiet original source window")
    return (idx-m)/fs*1000.,float(abs(r[idx])/denom)
def analyze(root):
    root=Path(root)/"localization/large-array/data";recordings=[];frames=[]
    for name,sha in BLOBS:
        b=(root/name).read_bytes()
        if blob_sha(b)!=sha:raise AudioStop("Pinned original source sha changed")
        with wave.open(io.BytesIO(b),"rb") as w:
            if (w.getnchannels(),w.getsampwidth(),w.getframerate())!=(1,3,32000):
                raise AudioStop("Original native format changed")
            frames.append(w.getnframes())
            recordings.append(decode24(w.readframes(544000)))
    if (min(frames),max(frames))!=(544000,544230):raise AudioStop("Source frame mismatch changed")
    if any(len(a)!=544000 for a in recordings):raise AudioStop("Insufficient common 17s")
    scores=[]
    for t in WINDOWS:
        a=t*32000;b=a+int(DURATION*32000)
        base=recordings[0][a:b];pairs=[]
        for receiver in range(1,6):
            y=recordings[receiver][a:b]
            delta,corr=lag_corr(base,y)
            ghostdelta,ghostcorr=lag_corr(base,np.roll(y,len(y)//2))
            pairs.append({"receiver":receiver,"lag_ms":delta,"max_abs_norm_corr":corr,
                          "time_rotated_ghost_max_abs_norm_corr":ghostcorr})
        scores.append({"window_start_s":t,"pairs":pairs})
    observed=np.array([z["max_abs_norm_corr"] for row in scores for z in row["pairs"]])
    ghosts=np.array([z["time_rotated_ghost_max_abs_norm_corr"] for row in scores for z in row["pairs"]])
    return {"status":"REAL_ORIGINAL_AUDIO_LAG_DIAGNOSTIC_NOT_FISH_MOVEMENT",
            "source":"XAV-arrays, pinned public 2019 wild WAV example","pinned_sha":PIN,
            "source_frame_gate_still":"SOURCE_FRAME_SYNC_STOP",
            "first_common_17s_only_diagnostic":True,"sample_rate_hz":32000,
            "fixed_windows_s":list(WINDOWS),"window_duration_s":DURATION,
            "bandpass_hz":list(BAND),"lag_limit_ms":MAX_LAG_MS,
            "compared_receiver_windows":len(observed),"median_abs_corr":float(np.median(observed)),
            "median_ghost_abs_corr":float(np.median(ghosts)),"individual_window_results":scores,
            "animal_tracking":"NOT_OBSERVED","fish_call_onset_or_boids_force":"NOT_IDENTIFIED"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    p.add_argument("--output",default="validation_fish_school_v4/results/xav_original_wave_lags.json")
    a=p.parse_args()
    try:out=analyze(a.root)
    except (AudioStop,OSError,wave.Error) as exc:
        out={"status":"SOURCE_WAVEFORM_STOP","reason":str(exc),"pinned_sha":PIN}
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out.get(k) for k in ("status","reason","compared_receiver_windows","median_abs_corr","median_ghost_abs_corr")}))
if __name__=="__main__":main()
