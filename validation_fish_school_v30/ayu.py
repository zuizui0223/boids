"""v30 source Niizato ayu: exact 7 pinned Git blobs, common 200ms model."""
from __future__ import annotations
import json,sys,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
from ayu_source_gate import FILES,PIN,blobsha,SourceStop as AuthorSourceStop
from ayu_global_local import source_data
from validation_fish_school_v30.harmonized_forecast import (
    build_original_recording,evaluate_source_files,save,SourceStop)


def run(root):
    base=Path(root)
    if not (base/".git").exists():
        raise SourceStop("V30_AYU_PINNED_ORIGINAL_REPOSITORY_MISSING")
    originals=base/"Compute_IIT/fish_revised"
    hashes={}
    for name,(sha,size) in FILES.items():
        b=(originals/name).read_bytes()
        if len(b)!=size or blobsha(b)!=sha:
            raise SourceStop("V30_AYU_ORIGINAL_SOURCE_BYTES_OR_COMMIT_DRIFT")
        hashes[name]=hashlib.sha256(b).hexdigest()
    if len(FILES)!=7:
        raise SourceStop("V30_AYU_SEVEN_AUTHOR_RECORDINGS_REQUIRED")
    cases={}
    for name,(sha,size) in FILES.items():
        frame,seconds,pos=source_data(originals/name,sha,size)
        cases[name]=build_original_recording(frame,pos,30,name)
    res=evaluate_source_files(cases,"ayu",7,
              "Niizato et al. 2024 Scientific Reports Plecoglossus altivelis 10-fish tracks")
    res["source_authentication"]={
        "original_pinned_upstream_commit":PIN,
        "all_seven_original_Git_blob_SHA_and_size_verified":True,
        "original_author_blob_SHA1":{n:FILES[n][0] for n in FILES},
        "original_author_file_SHA256":hashes,
        "original_native_clock_verified":True,
        "original_numeric_units":"author native XY units/sec, physical scale unknown"}
    return res


def main():
    import argparse
    cli=argparse.ArgumentParser()
    cli.add_argument("--root",required=True)
    args=cli.parse_args()
    try:out=run(args.root)
    except (SourceStop,AuthorSourceStop,OSError,ValueError,IndexError,KeyError) as e:
        out={"status":"SOURCE_OR_MODEL_STOP","reason":str(e),"new_observed_fish_result":None}
    save("validation_fish_school_v30/results/ayu_common_model.json",out)
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
                      "results_by_horizon":out.get("results_by_horizon"),
                      "source_file_cohorts":out.get("original_source_cohort")},sort_keys=True))
if __name__=="__main__":main()
