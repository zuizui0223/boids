"""XAV original six-receiver field WAV source gate; no fish movement fitted."""
import argparse,csv,hashlib,io,json,wave
from pathlib import Path
import numpy as np
PIN="5258350fe78f107a7f3e03ca50ff08bc0e8d0362"
BLOBS=(
 ("AMAR173.1.20190920T163858Z.wav","2871094af4872f5f22c8a240e0ce4fbe6608c9d5"),
 ("AMAR173.2.20190920T163858Z.wav","fdfe23149ab25eb73551161bb3d40827c6170ae4"),
 ("AMAR173.3.20190920T163858Z.wav","75a21f2f0cc842443ed9b32ba2761c7e6cee2dca"),
 ("AMAR173.4.20190920T163858Z.wav","ed447fee627d1eb240f302c6d29885822360257c"),
 ("AMAR173.5.20190920T163858Z.wav","2c0e010b108c68cfbd386b0d34a11461114f1b74"),
 ("AMAR173.6.20190920T163858Z.wav","4043081ebf0f586965b44ead022e2d3449ee5255"),
)
class SourceStop(Exception):pass
def blob_sha(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\0"+x).hexdigest()
def inspect(root):
    root=Path(root)
    with (root/"localization/large-array/hydrophones_config_07-HI.csv").open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=6 or [int(z["array_channel"]) for z in rows]!=list(range(6)):
        raise SourceStop("SOURCE_GEOMETRY_STOP")
    locations=np.array([[float(z[k]) for k in ("x","y","z")] for z in rows])
    if np.linalg.matrix_rank(locations[1:]-locations[0])!=3:
        raise SourceStop("SOURCE_GEOMETRY_RANK_STOP")
    records=[]
    for name,sha in BLOBS:
        raw=(root/"localization/large-array/data"/name).read_bytes()
        if blob_sha(raw)!=sha:raise SourceStop("SOURCE_SHA_STOP "+name)
        with wave.open(io.BytesIO(raw),"rb") as w:
            records.append({"file":name,"source_blob_sha":sha,"nchannel":w.getnchannels(),
                            "sample_width_bytes":w.getsampwidth(),"rate_hz":w.getframerate(),
                            "nframes":w.getnframes(),"seconds":w.getnframes()/w.getframerate(),
                            "compression_type":w.getcomptype()})
    if len({(z["nchannel"],z["sample_width_bytes"],z["rate_hz"],z["nframes"],z["compression_type"])
            for z in records})!=1:raise SourceStop("SOURCE_FRAME_SYNC_STOP")
    maxdist=float(np.max(np.linalg.norm(locations[:,None,:]-locations[None,:,:],axis=-1)))
    return {"status":"ORIGINAL_FIELD_AUDIO_STRUCTURE_PASS_NOT_FISH_EFFECT","repo":"xaviermouy/XAV-arrays",
            "pinned_commit":PIN,"n_hydrophones":6,"three_dimensional_coordinate_rank":3,
            "max_hydrophone_separation_m":maxdist,"original_wav":records,
            "individual_fish_positions":"NOT_OBSERVED","group_movement":"NOT_EVALUATED",
            "social_causality":"NOT_IDENTIFIED"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    p.add_argument("--output",default="validation_fish_school_v4/results/xav_field_audio_source.json")
    a=p.parse_args()
    try:ans=inspect(a.root)
    except (OSError,ValueError,wave.Error,SourceStop) as exc:
        ans={"status":"SOURCE_STRUCTURE_STOP","error":str(exc),"pinned_commit":PIN}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(ans,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":ans["status"],"error":ans.get("error"),
                      "n_hydrophones":ans.get("n_hydrophones"),
                      "sample_audio":ans.get("original_wav",[{}])[0].get("seconds")}))
if __name__=="__main__":main()
