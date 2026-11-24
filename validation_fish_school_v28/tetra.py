"""v28 Puy 6 original recordings: target-free conditional school-motion innovation."""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for rel in ("validation_fish_school_v5","validation_fish_school_v7",
"validation_fish_school_v8","validation_fish_school_v22","validation_fish_school_v24"):
    sys.path.insert(0,str(ROOT/rel))
from forecast_transfer import read_json,ZENODO,RECORDINGS,download_and_audit,SourceStop,source_csv,make_trial,FPS,N_FISH,SPEED_DIFF_LAG
from assignment_and_delay import original_indices
from tetra import tetra_one
from tetra_age import delayed_rows_original
from age_curve import source_age_panels
from validation_fish_school_v28.conditional_residual import source_panels,assess,save,SourceStop as ResidualSourceStop

def run():
    r=read_json(ZENODO)
    available={t.get("key"):t for t in r.get("files",[]) if isinstance(t,dict)}
    if not set(RECORDINGS).issubset(available):
        raise SourceStop("V28_PUY_ORIGINAL_FILE_MANIFEST_STOP")
    with tempfile.TemporaryDirectory(prefix="v28_puy_target_free_") as folder:
        blobs={name:download_and_audit(available[name],Path(folder)/name) for name in RECORDINGS}
        cases={}
        for j,name in enumerate(RECORDINGS):
            frame,pos=source_csv(Path(folder)/name)
            v5=make_trial(frame,pos,j)
            src=tetra_one(frame,pos,v5,blobs[name]["sha256"])
            idx=original_indices(frame,pos)
            rows=delayed_rows_original(frame,pos,idx)
            panel=source_age_panels(src,pos,idx,FPS,SPEED_DIFF_LAG,rows)
            cases[name]=source_panels(panel["X"]["short"])
        return assess(cases,"tetra",{
          "source":"Puy et al. PNAS 2024 original six 8-fish Zenodo files",
          "original_six_provider_MD5_verified":True,
          "native_fps":FPS,"source_cohort":"v24 same original source t and future eligibility",
          "original_sha256":[blobs[name]["sha256"] for name in RECORDINGS],
          "target_fish_future_velocities_used":False})

def main():
    try:obj=run()
    except (SourceStop,ResidualSourceStop,ValueError,IndexError,KeyError,OSError) as ex:
        obj={"status":"SOURCE_OR_NUISANCE_SUPPORT_STOP","reason":str(ex),"field_effect":None}
    save("validation_fish_school_v28/results/tetra_conditional_residual.json",obj)
    print(json.dumps(obj,sort_keys=True))
if __name__=="__main__":main()
