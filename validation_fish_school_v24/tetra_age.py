"""v24 original Puy eight-fish recordings: age-of-other-school movement.

Six recording files are authenticated BEFORE observed fish movement is scored.
"""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for p in ("validation_fish_school_v5","validation_fish_school_v7",
          "validation_fish_school_v8","validation_fish_school_v22",
          "validation_fish_school_v24"):
    sys.path.insert(0,str(ROOT/p))
from forecast_transfer import (
 read_json,ZENODO,RECORDINGS,download_and_audit,SourceStop,source_csv,
 make_trial,FPS,N_FISH,SPEED_DIFF_LAG)
from assignment_and_delay import original_indices
from tetra import tetra_one
from age_curve import source_age_panels,assess,save_result


def delayed_rows_original(frame,pos,idx):
    # Source-exact copied mask from frozen v22 tetra_one, not a new eligibility policy.
    start,end=25,35
    keep=(idx+end<len(frame))
    ix=idx[keep]
    good=np.isfinite(pos[ix+start]).all(axis=(1,2))
    good &= np.isfinite(pos[ix+end]).all(axis=(1,2))
    good &= (frame[ix+start]-frame[ix]==start)
    good &= (frame[ix+end]-frame[ix+start]==end-start)
    chosen=np.flatnonzero(keep)[good]
    if len(chosen)<3000:
        raise SourceStop("V24_TETRA_V22_DELAYED_ROSTER_NOT_REPLAYED")
    return (chosen[:,None]*N_FISH+np.arange(N_FISH)[None,:]).ravel()


def run():
    meta=read_json(ZENODO)
    records={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
    if not set(RECORDINGS).issubset(records):
        raise SourceStop("V24_ZENODO_PUBLISHED_SOURCE_FILES_MISSING")
    with tempfile.TemporaryDirectory(prefix="v24_verified_original_tetra_") as dirname:
        # All six provider MD5 checksums checked before source outcomes opened.
        digests={name:download_and_audit(records[name],Path(dirname)/name)
                 for name in RECORDINGS}
        samples={}
        for i,name in enumerate(RECORDINGS):
            frames,pos=source_csv(Path(dirname)/name)
            v5=make_trial(frames,pos,i)
            previous=tetra_one(frames,pos,v5,digests[name]["sha256"])
            idx=original_indices(frames,pos)
            rows=delayed_rows_original(frames,pos,idx)
            samples[i]=source_age_panels(previous,pos,idx,FPS,SPEED_DIFF_LAG,rows)
        result=assess(samples,study="tetra")
        result["published_original_recording_filenames"]=list(RECORDINGS)
        result["source_sha256"]=[digests[name]["sha256"] for name in RECORDINGS]
        result["original_puy_source_provider_MD5_verified"]=True
        result["native_original_hz"]=FPS
        result["source_mse_units"]="(cm/s)^2"
        return result


def main():
    try:ans=run()
    except (SourceStop,OSError,ValueError,IndexError,KeyError) as e:
        ans={"status":"SOURCE_OR_REPLAY_STOP","reason":str(e),
             "v24_original_fish_prediction":None}
    save_result("validation_fish_school_v24/results/tetra_age_curve.json",ans)
    print(json.dumps({"status":ans["status"],"reason":ans.get("reason"),
                      "results_by_horizon":ans.get("results_by_horizon")},sort_keys=True))


if __name__=="__main__":main()
