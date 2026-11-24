"""v23 independent 2026 Hemigrammus source gate, metadata only.

NO movement metrics, no trajectories redistributed, no third-species test.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
from scipy.io import loadmat

OWNER_REPO="DerekZhengEvosil/Nested-Interaction-Network-Enhances-Responsiveness-in-Collective-Behavior"
COMMIT="5a2a834580c3212b3f69f33517869add934513b5"
ROOT="https://raw.githubusercontent.com/"+OWNER_REPO+"/"+COMMIT+"/data/biological_data/"
FILES={
 "high_maneuverability.mat":(128481,"f438dc0a87cd8c4bcf9c516720d0e552559938c1","high_maneuverability_example"),
 "low_maneuverability.mat":(55133,"52feee019a0f11125c23c59a8c6ab264db427937","low_maneuverability_example"),
 "NODF_curvature_polarization.mat":(12669,"b46b03d22238c4a164a409cad049ebac72fb550b",None)
}
MAX_BYTES=512*1024

class SourceStop(Exception):pass


def gitsha(blob):
    return hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()


def inspect_blob(name,blob):
    if name not in FILES:raise SourceStop("UNKNOWN_ORIGINAL_SOURCE")
    size,sha,var=FILES[name]
    if len(blob)!=size or gitsha(blob)!=sha:
        raise SourceStop("ORIGINAL_SOURCE_GIT_BLOB_OR_BYTE_COUNT_MISMATCH")
    try:
        mat=loadmat(io.BytesIO(blob),squeeze_me=False,struct_as_record=False)
    except Exception as exc:
        raise SourceStop("ORIGINAL_MAT_SCHEMA_OR_VERSION_UNSUPPORTED") from exc
    visible={k:v for k,v in mat.items() if not k.startswith("__")}
    variables={k:{"shape":list(v.shape),"dtype_kind":v.dtype.kind} for k,v in visible.items()}
    result={
       "original_file":name,"expected_provider_git_sha1":sha,
       "observed_sha256":hashlib.sha256(blob).hexdigest(),
       "exact_original_bytes":len(blob),"variables":variables}
    if var is not None:
        arr=visible.get(var)
        if not isinstance(arr,np.ndarray) or arr.dtype.kind!="O" or arr.size<2:
            raise SourceStop("ORIGINAL_EXAMPLE_CELL_LAYOUT_STOP")
        x,y=arr.ravel(order="C")[:2]
        if (not isinstance(x,np.ndarray) or not isinstance(y,np.ndarray)
            or x.shape!=y.shape or x.ndim!=2 or x.shape[1]!=15
            or x.dtype.kind not in "biuf" or y.dtype.kind not in "biuf"):
            raise SourceStop("ORIGINAL_EXAMPLE_POS_XY_SHAPES_STOP")
        result["curated_example"]={
           "cell_shape":list(arr.shape),"source_position_matrix_shape":list(x.shape),
           "original_fish_count_per_example":15,
           "individual_positions_read_for_analysis":False}
    return result


def run(opener=urlopen):
    out={"status":"SOURCE_ACCESS_OR_SCHEMA_STOP","study":"Zheng et al 2026 Communications Physics",
         "upstream_commit":COMMIT,"recordings_fully_admitted":0,
         "observed_third_species_predictive_score":None,"original_trajectories_redistributed":False}
    rows=[]
    for filename in FILES:
        url=ROOT+filename
        try:
            req=Request(url,headers={"User-Agent":"boids-v23-metadata-only/1.0"})
            with opener(req,timeout=25) as response:
                blob=response.read(MAX_BYTES+1)
            if len(blob)>MAX_BYTES:
                raise SourceStop("SOURCE_SIZE_LIMIT_STOP")
            row=inspect_blob(filename,blob)
        except Exception as exc:
            out.update({"stop_filename":filename,"stop_reason":type(exc).__name__+":"+str(exc),
                        "files_verified_before_stop":rows})
            return out
        rows.append(row)
    out.update({
       "status":"TWO_CURATED_EXEMPLARS_METADATA_ADMITTED",
       "original_files":rows,
       "curated_15_fish_examples":2,
       "full_5_10_15_fish_study_cohorts":"NOT_ADMITTED_AUTHOR_REQUEST_REQUIRED",
       "third_species_independent_generalization":"NOT_TESTED",
       "actual_original_fish_xy_values_exported":False
    })
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    opts=p.parse_args()
    o=run()
    encoded=json.dumps(o,indent=2,sort_keys=True)+"\n"
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(encoded,encoding="utf-8")
    print(encoded,end="")


if __name__=="__main__": main()
