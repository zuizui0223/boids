"""v10b genuinely localized field sounds: time-to-space ordering null.

Genuine Mouy et al. 2023 original six OSF localization CSVs. Source SHA256
locked to pre-v10 original source-only run #44750614686. No fish ID, tracking,
or schooling/social inference.
"""
from __future__ import annotations
import csv,hashlib,io,json,math,random,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_audio_v6"))
from osf_joint_schema import FILE_IDS, json_get, download, SourceStop, MAX_CSV
SHA={
"6335fcfa31d65303352de2bc":"095f1f3dbe9b45c480c1987a83a3a2459d38baa3f2ccfccf4824e2f308d7143b",
"6335fd860db48e0365e127a5":"0e5d810a9ec43582c17425520b940ab9aff743971d842a84b9548b2e6b80ca85",
"6335fdb30db48e0364e11e09":"8c481590abc8f02f1631dd786d8162e85dee0f9a0072b3ced9bcd868645316b7",
"6335fdd331d65303352de44a":"6a2a8b8cda6cc1e361a577ad731875ae24cf4c2825bb201a96c3f331fbf1fb45",
"6335fdf4ec7f3f0332f61087":"b6327e96cb80377ed07f9a36b51e7fbba367921c44362756a71d2ed61483724b",
"6335fd3aec7f3f0337f5f9a4":"a2270a82dae5435ba992cdeef002e7cdca1aa054edf3e336f80f986f2d9c841b"
}
MIN_ROWS=6
MIN_PAIRS=5
MAX_GAP_SECONDS=120.
MIN_GAP_SECONDS=.001
NUM_PERM=1999
SEED=20261121
def parse_time(txt):
    s=str(txt or "").strip()
    if not s:raise ValueError("empty source timestamp")
    s=s.replace(" UTC","+00:00").replace("Z","+00:00")
    try:v=datetime.fromisoformat(s)
    except ValueError:
       v=None
       for fmt in ("%Y/%m/%d %H:%M:%S","%Y-%m-%d %H:%M:%S.%f",
                   "%Y-%m-%d %H:%M:%S","%m/%d/%Y %H:%M:%S"):
           try:v=datetime.strptime(s,fmt);break
           except ValueError:pass
       if v is None:raise ValueError("unrecognized source time format")
    if v.tzinfo is None:v=v.replace(tzinfo=timezone.utc)
    return v.timestamp()
def finite_number(value):
    try:
        f=float(value)
        return f if math.isfinite(f) else None
    except (TypeError,ValueError):
        return None
def parse_events(data):
    text=data.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    cols=reader.fieldnames or []
    for required in ("x","y","z","time_min_date","uuid","label_class"):
        if required not in cols:raise SourceStop("MISSING_SOURCE_EVENT_"+required)
    events=[];bad=Counter()
    for row in reader:
        coords=[finite_number(row.get(k)) for k in ("x","y","z")]
        if None in coords:bad["no_3d"]+=1;continue
        try:t=parse_time(row.get("time_min_date"))
        except ValueError:bad["invalid_time"]+=1;continue
        errs=[finite_number(row.get(k)) for k in ("x_err_span","y_err_span","z_err_span")]
        label=str(row.get("label_class") or "unlabeled").strip() or "unlabeled"
        if any(v is not None and v<0 for v in errs):bad["negative_error"]+=1;continue
        events.append({"t":t,"xyz":tuple(coords),"uncert":errs,"label":label,
              "uid":str(row.get("uuid") or "")})
    events.sort(key=lambda e:(e["t"],e["uid"]))
    return events,dict(bad)
def pair_indices(events):
    return [(i,i+1) for i in range(len(events)-1)
        if MIN_GAP_SECONDS<=events[i+1]["t"]-events[i]["t"]<=MAX_GAP_SECONDS]
def meddist(positions,pairs):
    if not pairs:return None
    return float(np.median([math.dist(positions[i],positions[j]) for i,j in pairs]))
def mean_euclidean_error(events):
    vals=[]
    for row in events:
        if all(x is not None for x in row["uncert"]):
            vals.append(float(np.linalg.norm(row["uncert"])))
    return {"n_uncertainty_3d_available":len(vals),
       "median_combined_xyz_span_m":float(np.median(vals)) if vals else None}
def shuffled(events,permute_rng,stratify):
    grouped=defaultdict(list)
    for i,e in enumerate(events):
        key=e["label"] if stratify else "*"
        grouped[key].append(i)
    orig=[x["xyz"] for x in events];new=orig.copy()
    for inds in grouped.values():
        assign=inds.copy()
        permute_rng.shuffle(assign)
        for source,target in zip(inds,assign):
            new[source]=orig[target]
    return new
def test(events,seed,strict_only=False):
    selected=[z for z in events if
        (not strict_only or all(u is not None and u<=1. for u in z["uncert"]))]
    pairs=pair_indices(selected)
    out={"n_eligible_events":len(selected),"n_adjacent_time_pairs_within_120_seconds":len(pairs),
         "max_gap_s":MAX_GAP_SECONDS,"strict_under_1m_per_axis":strict_only}
    if len(selected)<MIN_ROWS or len(pairs)<MIN_PAIRS:
        return {**out,"status":"STOP_INSUFFICIENT_NEAR_TIME_AUDIO_LOCALIZATIONS"}
    xyz=[z["xyz"] for z in selected]
    obs=meddist(xyz,pairs)
    all_pair=[math.dist(xyz[i],xyz[j])
              for i in range(len(selected)) for j in range(i+1,len(selected))]
    ntypes=len(set(z["label"] for z in selected))
    results={}
    for stratum in (False,True):
        rng=random.Random(seed+(13 if stratum else 0))
        sims=[meddist(shuffled(selected,rng,stratum),pairs) for _ in range(NUM_PERM)]
        if min(sims)==max(sims):
            status="STOP_DEGENERATE_PERMUTATION_LABELS"
        else:status="EVALUATED_EXPLORATORY_TIME_LABEL_SHUFFLE"
        sims.sort()
        expected=float(np.mean(sims))
        p_lower=(1+sum(x<=obs+1e-12 for x in sims))/(NUM_PERM+1)
        p_upper=(1+sum(x>=obs-1e-12 for x in sims))/(NUM_PERM+1)
        results["same_sound_label_only" if stratum else "all_acoustic_events"]={
             "status":status,"observed_median_consecutive_distance_m":obs,
             "permutation_mean_median_distance_m":expected,
             "observed_over_permutation_mean":obs/expected if expected>0 else None,
             "permutation_2p5_to_97p5": [sims[int(.025*NUM_PERM)],sims[int(.975*NUM_PERM)]],
             "smaller_distance_compatibility_p_model_conditional":p_lower,
             "larger_distance_compatibility_p_model_conditional":p_upper,
             "n_monte_carlo":NUM_PERM}
    return {**out,"status":"EXPLORATORY_EVENT_TIME_SPACE_TESTED",
            "median_all_event_pair_distance_m":float(np.median(all_pair)),
            "label_count":dict(Counter(z["label"] for z in selected)),
            "uncertainty":mean_euclidean_error(selected),"contrasts":results}
def get_original(fid):
    obj=json_get(f"https://api.osf.io/v2/files/{fid}/")
    item=obj["data"];a=item.get("attributes") or {}
    url=(item.get("links") or {}).get("download")
    size=int(a.get("size") or 0)
    if a.get("name")!="localization_results.csv" or size<=0 or size>MAX_CSV:
        raise SourceStop("ORIGINAL_OSF_FILENAME_OR_SIZE_CHANGED")
    b=download(url)
    if len(b)!=size or hashlib.sha256(b).hexdigest()!=SHA[fid]:
        raise SourceStop("PREV_SOURCE_SHA256_DRIFT")
    return b
def run():
    data={"version":"v10b_osf_original_localized_sound_spatiotemporal_structure",
      "source":"Mouy et al 2023 OSF q8dz4",
      "source_shas_prelocked":True,"main_fish_schooling_mechanism":"NOT_IDENTIFIED",
      "individual_calling_fish_id":"NOT_OBSERVED","results":[]}
    for i,(fid,label) in enumerate(FILE_IDS.items()):
        try:
            b=get_original(fid)
            events,quality=parse_events(b)
            d={"source_array":label,"original_sha256":SHA[fid],
               "n_source_event_rows":len(events),"source_bad_event_counts":quality,
               "source_labels":dict(Counter(e["label"] for e in events)),
               "all_publisher_localizations":test(events,SEED+i*10),
               "good_3d_uncertainty_under_1m":test(events,SEED+i*10+1,strict_only=True)}
        except (SourceStop,ValueError,OSError,TypeError) as ex:
            d={"source_array":label,"status":"SOURCE_STOP","reason":str(ex)}
        data["results"].append(d)
    data["n_source_authenticated"]=sum("original_sha256" in a for a in data["results"])
    data["n_arrays_primary_evaluated"]=sum(x.get("all_publisher_localizations",{}).get("status")
                                   =="EXPLORATORY_EVENT_TIME_SPACE_TESTED" for x in data["results"])
    data["status"]="COMPLETE_ORIGINAL_ARRAYS_SOURCE_REPLAY" if data["n_source_authenticated"]==6 else "SOURCE_STOP"
    return data
def main():
    a=run()
    p=Path("validation_fish_chorus_v10/results/osf_time_space_original.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(a,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":a["status"],"authenticated":a["n_source_authenticated"],
        "primary_arrays":a["n_arrays_primary_evaluated"],
        "results":[{"array":x["source_array"],"n":x.get("n_source_event_rows"),
          "labels":x.get("source_labels"),
          "test":x.get("all_publisher_localizations"),
          "strict_test":x.get("good_3d_uncertainty_under_1m",{}).get("status"),
          "error":x.get("reason")} for x in a["results"]]}))
if __name__=="__main__":main()
