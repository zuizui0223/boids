"""v142: off-effort and noise annotations are OBSERVATION PROCESS, not fish.

Read source original 60 Excel workbooks. Construct conservative time masks from
explicit "Off effort"/"Noise" intervals and compare 3 denominator candidates.
Zeros remain *no logged chorus under nominal source conditions*, not verified
individual absence or perfect detectability.
"""
from __future__ import annotations
from collections import defaultdict,Counter
from datetime import datetime
from pathlib import Path
from statistics import mean
from hashlib import sha256
import io, math, json, zipfile, argparse

from chorus_60_source_audit import (acquire,SHAPES,PUBLISHED,excel_reader,
                                    extract_sheet,numeric_excel,classify)

ROOT=Path(__file__).resolve().parent
FISH=set(PUBLISHED)
KNOWN_ALIASES={
    "Boaccio sunset":"Bocaccio",
    "Bocaccio susnet":"Bocaccio",
    "Bocacio sunrise":"Bocaccio",
    "Midhsipman":"Midshipman",
}
CONTROL_LABELS={"off effort":"OFF_EFFORT","noise":"SOURCE_NOISE","hf sunrise":"OTHER_UNKNOWN"}

def source_label(label):
    raw=str(label or "").strip()
    if raw in KNOWN_ALIASES:return KNOWN_ALIASES[raw],"TYPO_ALIAS_REVIEWABLE"
    canon=classify(raw)
    if canon in FISH:return canon,"FISH"
    control=CONTROL_LABELS.get(raw.lower())
    if control:return control,"OBSERVATION_PROCESS_OR_UNRESOLVED"
    return "UNRESOLVED:"+raw[:45],"UNKNOWN"

def overlapping_hours(start,end):
    return set(range(math.floor(start*24+1e-8),math.ceil(end*24-1e-8)))
def fully_inside_hours(start,end):
    return set(range(math.ceil(start*24-1e-8),math.floor(end*24+1e-8)))

def analyze():
    raw=acquire()
    result={
        "version":"v142_source_california_denoise_effort_1",
        "original_doi":"10.5061/dryad.q2bvq83sw",
        "archive_may_be_reassembled_per_request":True,
        "actual_original_workbook_count":60,
        "original_source_daynight_observation_time_precision":"source UTC Excel datetimes",
        "off_effort_annotations_are_observation_process":True,
        "noise_annotations_are_potential_mask_not_verified_full_detector_outage":True,
        "source_off_effort_time_overlap_disagreement":"two bounds: any-overlapping vs full-hour contained; union across deployments",
        "site_data":[],
        "all_site_chorus_type_fraction":{},
        "unknown_detector_quality":"uncorrected ambient, vessel and technical masking outside explicit labels",
        "causal_tide_night_effect":"NOT_ESTIMATED",
        "meta_global_interaction":"NOT_ESTIMATED"}
    sites=defaultdict(lambda:{
        "nominal":set(),
        "fish":defaultdict(set),
        "off_overlap":set(),"off_full":set(),
        "noise_overlap":set(),"noise_full":set(),
        "control_labels":Counter(),
        "alias":Counter(),
        "start_serials":[],
        "end_serials":[],
        "deployments":0,
        "source_valid_event_rows":0,
        "source_invalid_time_rows":0
    })
    filemask=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        entries=[n for n in z.namelist() if n.lower().endswith((".xls",".xlsx"))]
        if len(entries)!=60:raise ValueError("Original book count mismatch")
        for path in sorted(entries):
            original=z.read(path)
            site=path.split("_")[0]
            tables=excel_reader(original,path)
            det,dc=extract_sheet(tables,"Detections")
            meta,mc=extract_sheet(tables,"MetaData")
            s=sites[site]
            s["deployments"]+=1
            effort=[]
            for r in meta[1:]:
                a=numeric_excel(r[mc["start"]] if len(r)>mc["start"] else None)
                b=numeric_excel(r[mc["end"]] if len(r)>mc["end"] else None)
                if a is not None and b is not None and b>a:
                    effort.append((a,b))
                    s["start_serials"].append(a)
                    s["end_serials"].append(b)
                    s["nominal"].update(fully_inside_hours(a,b))
            if not effort:
                raise ValueError("Missing original deployment effort "+path)
            summary=Counter()
            for r in det[1:]:
                a=numeric_excel(r[dc["start"]] if len(r)>dc["start"] else None)
                b=numeric_excel(r[dc["end"]] if len(r)>dc["end"] else None)
                if a is None and b is None:continue
                if a is None or b is None or b<=a or b-a>100:
                    s["source_invalid_time_rows"]+=1
                    continue
                label=r[dc["label"]] if len(r)>dc["label"] else ""
                cls,kind=source_label(label)
                summary[cls]+=1
                s["source_valid_event_rows"]+=1
                if kind=="TYPO_ALIAS_REVIEWABLE":
                    s["alias"][str(label)]+=1
                if cls in FISH:
                    s["fish"][cls].update(overlapping_hours(a,b))
                elif cls=="OFF_EFFORT":
                    s["off_overlap"].update(overlapping_hours(a,b))
                    s["off_full"].update(fully_inside_hours(a,b))
                    s["control_labels"]["OFF_EFFORT"]+=1
                elif cls=="SOURCE_NOISE":
                    s["noise_overlap"].update(overlapping_hours(a,b))
                    s["noise_full"].update(fully_inside_hours(a,b))
                    s["control_labels"]["SOURCE_NOISE"]+=1
                else:
                    s["control_labels"][cls]+=1
            filemask.append({"file":path,"source_annotation_counts":dict(summary)})
    overall_nominal=set()
    sum_nom=0;sum_off=0;sum_off_noise=0
    for site in sorted(sites):
        s=sites[site]
        nominal=s["nominal"]
        off=s["off_overlap"] & nominal
        off_full=s["off_full"] & nominal
        noise=s["noise_overlap"] & nominal
        noise_full=s["noise_full"] & nominal
        after_off=nominal-off
        after_both=after_off-noise
        nonoverlap_nominal=len(nominal)
        result["site_data"].append({
          "site":site,"n_deployments":s["deployments"],
          "source_valid_time_annotations":s["source_valid_event_rows"],
          "source_invalid_time_rows":s["source_invalid_time_rows"],
          "nominal_full_hour_union":len(nominal),
          "off_effort_source_event_rows":s["control_labels"]["OFF_EFFORT"],
          "source_noise_event_rows":s["control_labels"]["SOURCE_NOISE"],
          "other_unresolved_controls":{k:v for k,v in sorted(s["control_labels"].items()) if k not in ("OFF_EFFORT","SOURCE_NOISE")},
          "source_typo_alias_rows":dict(sorted(s["alias"].items())),
          "hours_overlapping_explicit_off_effort":len(off),
          "full_hours_entirely_inside_explicit_off_effort":len(off_full),
          "hours_overlapping_explicit_noise":len(noise),
          "full_hours_entirely_inside_explicit_noise":len(noise_full),
          "nominal_full_hours_excluding_any_off_effort":len(after_off),
          "nominal_full_hours_excluding_any_off_effort_and_noise":len(after_both),
          "Published_effort_days":SHAPES[site],
          "source_fish_positive_hours_by_type":{
            cls:{
              "unmasked_as_published_nominal":len(s["fish"][cls] & nominal),
              "exclude_explicit_off_effort":len(s["fish"][cls] & after_off),
              "exclude_explicit_off_effort_and_noise":len(s["fish"][cls] & after_both),
              "fraction_over_nominal":round(len(s["fish"][cls] & nominal)/len(nominal),6),
              "fraction_over_off_effort_excluded":round(len(s["fish"][cls] & after_off)/len(after_off),6) if after_off else None,
              "fraction_over_off_effort_noise_excluded":round(len(s["fish"][cls] & after_both)/len(after_both),6) if after_both else None,
            } for cls in PUBLISHED},
        })
        sum_nom+=len(nominal)
        sum_off+=len(after_off)
        sum_off_noise+=len(after_both)
    result["overall"]={
      "original_sites":len(sites),
      "nominal_full_hours":sum_nom,
      "hours_after_excluding_any_annotated_off_effort":sum_off,
      "hours_after_excluding_any_annotated_off_effort_and_noise":sum_off_noise,
      "total_source_off_effort_rows":sum(x["off_effort_source_event_rows"] for x in result["site_data"]),
      "total_source_noise_rows":sum(x["source_noise_event_rows"] for x in result["site_data"]),
      "total_ambiguous_source_time_rows":sum(x["source_invalid_time_rows"] for x in result["site_data"]),
      "original_source_label_alias_rows":sum(sum(x["source_typo_alias_rows"].values()) for x in result["site_data"]),
      "safe_usable_audio_hours":"UNVERIFIED_NO_EXHAUSTIVE_NOISE_OR_INSTRUMENT_UPTIME_SERIES",
      "strict_tide_daynight_negative_event_gate":"NOT_ADMITTED"
    }
    for label in PUBLISHED:
        def total(which):
            return sum(x["source_fish_positive_hours_by_type"][label][which] for x in result["site_data"])
        result["all_site_chorus_type_fraction"][label]={
            "reported_paper_percent":PUBLISHED[label],
            "nominal_percent":round(100*total("unmasked_as_published_nominal")/sum_nom,5),
            "off_effort_excluded_percent":round(100*total("exclude_explicit_off_effort")/sum_off,5),
            "off_effort_noise_excluded_percent":round(100*total("exclude_explicit_off_effort_and_noise")/sum_off_noise,5),
            "same_as_published_percent":"NOT_ASSERTED"
        }
    result["source_control_file_totals"]=[
       x for x in filemask if any(k in x["source_annotation_counts"] for k in ("OFF_EFFORT","SOURCE_NOISE"))
    ][:60]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    out=analyze()
    path=Path(__file__).parent/"results"/"source_effort_noise_sensitivity.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    if a.check:
        assert out==json.loads(path.read_text()),"Masking result changed"
    else:path.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print("V142_EFFORT_MASK_START")
    print(json.dumps(out,ensure_ascii=False))
    print("V142_EFFORT_MASK_END")
    if out["overall"]["original_sites"]!=9:raise AssertionError("Source workbooks missing")

if __name__=="__main__":main()
