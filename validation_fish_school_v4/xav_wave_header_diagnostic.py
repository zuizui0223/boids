"""XAV pinned-source WAV-format diagnostic after v4 synchronized-frame STOP.
No acoustic samples are scored and old source STOP remains preserved.
"""
import argparse,hashlib,io,json,wave
from pathlib import Path
from xav_source_gate import BLOBS,PIN,blob_sha
def inspect(root):
    root=Path(root);rows=[]
    for name,sha in BLOBS:
        payload=(root/"localization/large-array/data"/name).read_bytes()
        if blob_sha(payload)!=sha:raise AssertionError("PINNED_SOURCE_CHANGED "+name)
        with wave.open(io.BytesIO(payload),"rb") as w:
            rows.append({"name":name,"git_blob_sha":sha,"file_bytes":len(payload),
                         "channels":w.getnchannels(),"sample_width_bytes":w.getsampwidth(),
                         "rate_hz":w.getframerate(),"frames":w.getnframes(),
                         "duration_s":w.getnframes()/w.getframerate(),
                         "compression":w.getcomptype()})
    formats=[(x["channels"],x["sample_width_bytes"],x["rate_hz"],x["compression"]) for x in rows]
    times=[x["frames"]/x["rate_hz"] for x in rows]
    return {"source_commit":PIN,"source_only":True,"no_waveform_values_opened":True,
            "six_Git_blobs_verified":True,"status":"SAME_FORMAT" if len(set(formats))==1 else "FORMAT_DIFFERENCES",
            "wave_frame_equality":len({x["frames"] for x in rows})==1,
            "max_minus_min_duration_s":max(times)-min(times),"files":rows,
            "biological_effect":"NOT_TESTED"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    p.add_argument("--output",default="validation_fish_school_v4/results/xav_wave_header_diagnostic.json")
    a=p.parse_args();res=inspect(a.root)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print(json.dumps(res))
if __name__=="__main__":main()
