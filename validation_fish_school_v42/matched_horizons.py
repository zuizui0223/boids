"""v42: frozen v33 panels generalized to 8 or 10 fish and native 25/30/50fps.
All other features, eligible time, velocity windows and outcomes follow v30.
"""
from __future__ import annotations
import numpy as np
from validation_fish_school_v30.harmonized_forecast import (
    build_original_recording,SourceStop,FEAT_DIM
)

PANELS=(
    "G_geometry","GLOBAL","NEAR_TRUE","FAR_TRUE",
    "NEAR_ROT1","NEAR_STALE_0.2S"
)
DT=.2
FROZEN_AGES=(0.,.2,.4,1.,2.)

def frozen_original_source_clock_and_cohort(frame,pos,fps):
    f=np.asarray(frame,dtype=float)
    p=np.asarray(pos,dtype=float)
    if fps not in (25,30,50) or p.ndim!=3 or p.shape[1] not in (8,10) or p.shape[2]!=2 or len(f)!=len(p) or len(p)<4000:
        raise SourceStop("V33_ORIGINAL_8_FISH_NATIVE_TIME_SHAPE_STOP")
    if not np.isfinite(f).all() or not np.all(np.diff(f)>0):
        raise SourceStop("V33_ORIGINAL_FRAME_ONE_STEP_SOURCE_STOP")
    s=int(round(fps*DT))
    offsets=np.array([-11*s,-10*s,-6*s,-5*s,-3*s,-2*s,-s,0,s,3*s,4*s],dtype=int)
    current=np.arange(11*s,len(p)-4*s,s,dtype=int)
    picked=current[:,None]+offsets[None,:]
    valid=np.isfinite(p[picked]).all(axis=(1,2,3))
    valid&=((f[picked]-f[current,None])==offsets[None,:]).all(axis=1)
    out=current[valid]
    if len(out)<300:
        raise SourceStop("V33_ORIGINAL_COMPLETE_SOURCE_COHORT_TOO_FEW")
    return out


def original_panels(frame,pos,fps,source_name="SOURCE"):
    base=build_original_recording(frame,pos,fps,source_name)
    idx=frozen_original_source_clock_and_cohort(frame,pos,fps)
    N_FISH=pos.shape[1]
    s=int(round(fps*DT))
    if len(idx)!=base["n_original_eligible_group_times"]:
        raise SourceStop("V33_V30_FROZEN_ORIGINAL_COHORT_REPLAY_FAILED")
    p=np.asarray(pos,dtype=float)
    now=p[idx]
    vel=(p[idx]-p[idx-s])/DT
    stale=(p[idx-s]-p[idx-2*s])/DT
    d2=np.sum((now[:,None,:,:]-now[:,:,None,:])**2,axis=-1)
    d2[:,np.arange(N_FISH),np.arange(N_FISH)]=np.inf
    ranking=np.argsort(d2,axis=2)[:,:,:N_FISH-1]
    near=ranking[:,:,:3]
    far=ranking[:,:,-3:]
    focal=np.arange(N_FISH)
    if (np.any(near==focal[None,:,None]) or
        np.any(far==focal[None,:,None]) or
        not np.all(np.take_along_axis(d2,near,axis=2)[:,:,-1] <=
                   np.take_along_axis(d2,far,axis=2)[:,:,0])):
        raise SourceStop("V33_ORIGINAL_NEAR_FAR_POSITION_MAP_STOP")
    allothers=(vel.sum(axis=1,keepdims=True)-vel)/(N_FISH-1)
    global_rel=allothers-vel
    curr_near=vel[np.arange(len(idx))[:,None,None],near].mean(axis=2)-allothers
    curr_far=vel[np.arange(len(idx))[:,None,None],far].mean(axis=2)-allothers
    oldall=(stale.sum(axis=1,keepdims=True)-stale)/(N_FISH-1)
    stale_near=stale[np.arange(len(idx))[:,None,None],near].mean(axis=2)-oldall
    assigned=np.zeros_like(curr_near)
    for focus in range(N_FISH):
        rest=np.array([j for j in range(N_FISH) if j!=focus],dtype=int)
        old_source_values=vel[:,rest,:]
        surrogate=np.roll(old_source_values,1,axis=1)
        if not np.allclose(surrogate.sum(axis=1),old_source_values.sum(axis=1),atol=1e-9,rtol=0):
            raise SourceStop("V33_ROT1_ORIGINAL_GLOBAL_VELOCITY_NOT_PRESERVED")
        ranks=near[:,focus,:]-(near[:,focus,:]>focus).astype(int)
        assignment=np.take_along_axis(surrogate,ranks[:,:,None],axis=1)
        assigned[:,focus,:]=assignment.mean(axis=1)-allothers[:,focus,:]
    G=base["X"]["G_geometry"]
    globe=base["X"]["age_0s"]
    if G.shape!=(len(idx)*N_FISH,FEAT_DIM) or globe.shape!=(len(idx)*N_FISH,FEAT_DIM+2):
        raise SourceStop("V33_V30_ORIGINAL_FOCAL_SOURCE_MATRIX_SHAPE_STOP")
    if not np.array_equal(globe[:,:FEAT_DIM],G) or not np.allclose(
            globe[:,FEAT_DIM:],global_rel.reshape(-1,2),atol=1e-10,rtol=0):
        raise SourceStop("V33_V30_GLOBAL_ALL_OTHERS_VELOCITY_REPLAY_STOP")
    out={
        "G_geometry":G,
        "GLOBAL":globe,
        "NEAR_TRUE":np.concatenate((globe,curr_near.reshape(-1,2)),axis=1),
        "FAR_TRUE":np.concatenate((globe,curr_far.reshape(-1,2)),axis=1),
        "NEAR_ROT1":np.concatenate((globe,assigned.reshape(-1,2)),axis=1),
        "NEAR_STALE_0.2S":np.concatenate((globe,stale_near.reshape(-1,2)),axis=1)
    }
    if tuple(out)!=PANELS or any(not np.isfinite(z).all() for z in out.values()):
        raise SourceStop("V33_ORIGINAL_NEAR_FAR_SURROGATE_NONFINITE")
    if any(not np.array_equal(out[x][:,:16],globe) for x in PANELS[2:]):
        raise SourceStop("V33_LOCAL_PANELS_CHANGED_FROZEN_CURRENT_GLOBAL_OR_GEOMETRY")
    if any(out[x].shape!=(len(base["Y"]),18) for x in PANELS[2:]):
        raise SourceStop("V33_NON_MATCHED_TWO_VECTOR_EXTRA_FEATURES_STOP")
    return {
        "X":out,"Y":base["Y"],
        "n_source_rows":base["n_source_rows"],
        "n_original_eligible_group_times":base["n_original_eligible_group_times"],
        "n_original_test_fish_frame_rows":base["n_original_eligible_fish_frames"],
        "n_discarded_original_source_group_times":base["n_original_rows_excluded_nonfinite_or_noncontiguous"],
        "same_source_frozen_Y_and_G14_and_GLOBAL":True,
        "source_velocity_to_position_original_or_rotated":"CURRENT_NEAREST_NEIGHBOR_IDS_WITH_FIXED_ONE_STEP_ROTATION",
        "source_native_fps":fps,
        "source_original_animal_XY_exported":False
    }

import argparse, hashlib, json, sys, tempfile, unittest
from pathlib import Path
from validation_fish_school_v30.harmonized_forecast import predict_train_file_only, HORIZONS, save

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs"
PIN_V30={
    "tetra":"3749a11ca74a17513fb97c606c15fbbf65164e90",
    "ayu":"f3283876b3797524627ca920f4cd006b138353c6",
}
PIN_TETRA_V28="d884b2403899452a0b1379a1d869f6a2a6bb5adc"

def pinned_json(path,blob):
    data=path.read_bytes()
    if hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()!=blob:
        raise SourceStop("FROZEN_PRIOR_RECEIPT_DRIFT")
    return json.loads(data)

def reference(study):
    return pinned_json(DOC/"v30_verification"/(study.upper()+"_COMMON_MODEL_ORIGINAL_REAGGREGATION.json"),PIN_V30[study])

def tetra_cases():
    sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
    from trajectory_source_gate import RECORDINGS,download_and_audit
    from source_inventory import read_json,ZENODO
    from forecast_transfer import source_csv
    pin=pinned_json(DOC/"v28_verification/TETRA_CONDITIONAL_GROUP_STATE_RESIDUAL_RECEIPT.json",PIN_TETRA_V28)
    expected=pin["source"]["original_sha256"]
    available={f["key"]:f for f in read_json(ZENODO)["files"]}
    if len(RECORDINGS)!=6 or len(expected)!=6 or not set(RECORDINGS)<=set(available):
        raise SourceStop("TETRA_MANIFEST_STOP")
    with tempfile.TemporaryDirectory(prefix="v42_tetra_") as tmp:
        checks={name:download_and_audit(available[name],Path(tmp)/name) for name in RECORDINGS}
        if [checks[name]["sha256"] for name in RECORDINGS]!=expected:
            raise SourceStop("TETRA_PRIOR_ORIGINAL_SHA256_DRIFT")
        cases={}
        for name in RECORDINGS:
            f,p=source_csv(Path(tmp)/name)
            cases[name]=original_panels(f,p,50,name)
    return cases,{"provider_MD5_verified":True,"prior_SHA256_verified":True,
                  "SHA256":{name:x["sha256"] for name,x in checks.items()}}

def ayu_cases(root):
    sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
    from ayu_source_gate import FILES,PIN,blobsha
    from ayu_global_local import source_data
    if len(FILES)!=7 or not (Path(root)/".git").exists():
        raise SourceStop("AYU_SOURCE_STOP")
    import subprocess
    if subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()!=PIN:
        raise SourceStop("AYU_COMMIT_DRIFT")
    base=Path(root)/"Compute_IIT/fish_revised"
    sha={}
    for name,(blob,size) in FILES.items():
        data=(base/name).read_bytes()
        if len(data)!=size or blobsha(data)!=blob:
            raise SourceStop("AYU_BLOB_DRIFT")
        sha[name]=hashlib.sha256(data).hexdigest()
    cases={}
    for name,(blob,size) in FILES.items():
        f,_,p=source_data(base/name,blob,size)
        cases[name]=original_panels(f,p,30,name)
    return cases,{"original_commit":PIN,"all_original_blob_sha1_and_size_verified":True,"SHA256":sha}

def score_panels(cases,panels):
    rows={}
    for held,case in cases.items():
        train=[v for k,v in cases.items() if k!=held]
        y=np.concatenate([v["Y"] for v in train])
        rows[held]={}
        for name in panels:
            x=np.concatenate([v["X"][name] for v in train])
            pred=predict_train_file_only(x,y,case["X"][name])
            err=(pred-case["Y"])**2
            rows[held][name]={"short":float(err[:,:2].mean()),"delayed":float(err[:,2:].mean())}
    return rows

def summarize(scores,study):
    names=list(scores)
    n=len(names)
    vals={}
    ok=True
    rng=np.random.default_rng(20261124)
    def stats(a):
        a=np.asarray(a,float)
        if not np.isfinite(a).all():raise SourceStop("NONFINITE_CONTRAST")
        boot=a[rng.integers(0,len(a),size=(10000,len(a)))].mean(1)
        return {"mean":float(a.mean()),"positive":int((a>0).sum()),"negative":int((a<0).sum()),
                "descriptive_bootstrap95":np.quantile(boot,[.025,.975]).tolist()}
    for h in HORIZONS:
        def m(k):return np.array([scores[x][k][h] for x in names])
        d=m("GLOBAL")-m("NEAR_TRUE")
        num={"Qdist":m("FAR_TRUE")-m("NEAR_TRUE"),
             "Qage":m("NEAR_STALE_0.2S")-m("NEAR_TRUE"),
             "Qmap":m("NEAR_ROT1")-m("NEAR_TRUE")}
        valid=bool(np.all(d>0))
        ok=ok and valid
        vals[h]={"D":d.tolist(),"D_summary":stats(d),
                 "per_file_signed_contrasts":{k:v.tolist() for k,v in num.items()},
                 "signed_contrast_summary":{k:stats(v) for k,v in num.items()},
                 "ratio_of_means":{k:float(v.mean()/d.mean()) if d.mean()>0 else None for k,v in num.items()},
                 "all_file_ratios_admitted":valid}
        if valid:
            qs={k:v/d for k,v in num.items()}
            vals[h]["within_file_ratios"]={k:v.tolist() for k,v in qs.items()}
            vals[h]["equal_file_ratio_summary"]={k:stats(v) for k,v in qs.items()}
            vals[h]["mapping_vs_distance_and_age_positive_files"]=int(((qs["Qmap"]>qs["Qdist"])&(qs["Qmap"]>qs["Qage"])).sum())
    out={"study":study,"source_files":names,"horizons":vals,"paired_ratio_test_admitted":ok,
         "scientific_status":"RATIO_GATE_STOP_NONPOSITIVE_DENOMINATOR","paired_changes":None}
    if ok:
        delta={k:np.array(vals["delayed"]["within_file_ratios"][k])-np.array(vals["short"]["within_file_ratios"][k]) for k in ("Qdist","Qage","Qmap")}
        both=int(((delta["Qdist"]<0)&(delta["Qage"]>0)).sum())
        threshold={"tetra":5,"ayu":6}[study]
        supported=bool(delta["Qdist"].mean()<0 and delta["Qage"].mean()>0 and both>=threshold)
        out.update(scientific_status="DESCRIPTIVE_JOINT_DIRECTION_REPLICATED" if supported else "DESCRIPTIVE_JOINT_DIRECTION_NOT_REPLICATED",
                   paired_changes={k:{"per_file":v.tolist(),**stats(v)} for k,v in delta.items()},
                   both_predicted_sign_files=both,required_both_sign_files=threshold)
    return out

def run(study,root):
    cases,auth=tetra_cases() if study=="tetra" else ayu_cases(root)
    prior=reference(study)
    expected={x["name"]:x for x in prior["original_eligible_cohorts"]["files"]}
    if set(cases)!=set(expected):raise SourceStop("SOURCE_FILES_DRIFT")
    for name,c in cases.items():
        x=expected[name]
        for left,right in (("n_source_rows","n_source_rows"),("n_original_eligible_group_times","n_eligible_group_times"),
                           ("n_original_test_fish_frame_rows","n_eligible_fish_frames"),("n_discarded_original_source_group_times","n_removed_source_times")):
            if c[left]!=x[right]:raise SourceStop("SOURCE_COHORT_DRIFT_"+name+"_"+left)
    # Baseline scored and checked before computing new panel outcomes.
    scores=score_panels(cases,PANELS[:2])
    for h in HORIZONS:
        for model,old in (("G_geometry","G_geometry"),("GLOBAL","age_0s")):
            actual=np.mean([v[model][h] for v in scores.values()])
            target=prior["source_numeric_results_reaggregated"][h]["equal_original_file_mean_MSE"][old]
            if not np.isclose(actual,target,rtol=1e-6,atol=1e-8):
                raise SourceStop("V30_BASELINE_REPLAY_STOP_"+model+"_"+h)
    extra=score_panels(cases,PANELS[2:])
    for name in scores:scores[name].update(extra[name])
    out=summarize(scores,study)
    out.update(status="V42_ORIGINAL_SOURCE_SCORED",source_authentication=auth,baseline_v30_replay=True,
               source_cohorts=expected,source_file_scores=scores,source_files_not_confirmed_independent_shoals=True,
               raw_XY_or_audio_exported=False,causal_interpretation=False)
    return out

class Fixtures(unittest.TestCase):
    def test_8fish_exact_v33_parity(self):
        from validation_fish_school_v33.test_neighbor_panels import fake_source
        from validation_fish_school_v33.neighbor_panels import original_panels as v33
        f,p=fake_source()
        a,b=original_panels(f,p,25),v33(f,p)
        np.testing.assert_array_equal(a["Y"],b["Y"])
        for k in PANELS:np.testing.assert_allclose(a["X"][k],b["X"][k],atol=1e-12,rtol=0)
    def test_10fish_manual_all_local_vectors(self):
        from validation_fish_school_v33.test_neighbor_panels import fake_source
        f,p=fake_source(nfish=10)
        a=original_panels(f,p,30)
        idx=frozen_original_source_clock_and_cohort(f,p,30)[0]
        for i in range(10):
            v=(p[idx]-p[idx-6])/.2
            z=(p[idx-6]-p[idx-12])/.2
            ids=np.argsort(np.where(np.arange(10)==i,np.inf,((p[idx]-p[idx,i])**2).sum(1)))[:9]
            others=[k for k in range(10) if k!=i]
            g=v[others].mean(0)
            near,far=ids[:3],ids[-3:]
            rotation=np.roll(v[others],1,axis=0)
            for k,target in (("NEAR_TRUE",v[near].mean(0)-g),("FAR_TRUE",v[far].mean(0)-g),
                             ("NEAR_ROT1",rotation[[others.index(j) for j in near]].mean(0)-g),
                             ("NEAR_STALE_0.2S",z[near].mean(0)-z[others].mean(0))):
                np.testing.assert_allclose(a["X"][k][i,-2:],target,atol=1e-10,rtol=0)
                np.testing.assert_array_equal(a["X"][k][:,:16],a["X"]["GLOBAL"])
    def test_ratio_gate_and_signed_controls(self):
        def fake(d):
            return {k:{h:v for h in HORIZONS} for k,v in zip(PANELS,[12,10,10-d,9,10,9])}
        bad={str(i):fake(2 if i else -1) for i in range(6)}
        o=summarize(bad,"tetra")
        self.assertFalse(o["paired_ratio_test_admitted"])
        self.assertIsNone(o["paired_changes"])
        good={str(i):fake(2) for i in range(6)}
        o=summarize(good,"tetra")
        self.assertTrue(o["paired_ratio_test_admitted"])
        self.assertEqual(o["scientific_status"],"DESCRIPTIVE_JOINT_DIRECTION_NOT_REPLICATED")
        self.assertAlmostEqual(o["horizons"]["short"]["ratio_of_means"]["Qmap"],1)
    def test_future_response_not_predictor(self):
        from validation_fish_school_v33.test_neighbor_panels import fake_source
        f,p=fake_source(nfish=10)
        a=original_panels(f,p,30)
        idx=frozen_original_source_clock_and_cohort(f,p,30)
        changed=p.copy();changed[idx[-1]+24]+=2
        b=original_panels(f,changed,30)
        for k in PANELS:np.testing.assert_array_equal(a["X"][k],b["X"][k])
        self.assertGreater(np.max(np.abs(a["Y"]-b["Y"])),0)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--study",choices=["tetra","ayu"])
    parser.add_argument("--root",default="external_ayu")
    parser.add_argument("--test",action="store_true")
    args=parser.parse_args()
    if args.test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Fixtures)
        sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
    if not args.study:parser.error("--study required")
    try:out=run(args.study,args.root)
    except Exception as e:
        out={"status":"SOURCE_OR_MODEL_STOP","study":args.study,"reason":str(e),"new_observed_fish_result":None}
        save("validation_fish_school_v42/results/"+args.study+".json",out)
        raise
    save("validation_fish_school_v42/results/"+args.study+".json",out)
    print(json.dumps({k:out[k] for k in ("status","study","scientific_status","paired_ratio_test_admitted","paired_changes")},sort_keys=True))
