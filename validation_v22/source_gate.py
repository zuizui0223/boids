#!/usr/bin/env python3
"""v22-A 2021 guineafowl original environment-season group schema, NO outcomes.

This is the SAME Movebank Avulturinum_Farine wild population as v20, not an
independent biological replication. Source is author derived group-season
tables, not telemetry. We inspect only data grain, type, season-type codes,
original source bytes and whether environment is shared by all groups.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

SOURCE_REPO="DanPapageorgiou/ranging_seasonality"
SOURCE_SHA="2a3aec308bb4a8449d1eeb16beed4aff8f387116"
FILES={
  "ddf_hr_dtd.Rdata":(8783,"65cbed930dd0924dec32fd7115f016f6b3fbc3d6"),
  "df_dhor.Rdata":(1911,"a365bea412cdb6eb3f7b4c76bb0f9dda2268ea8a"),
  "df_dshor.RData":(4002,"6b389efeed3c23c498735362cdd2befb5ff8b00a"),
}
MAX_BYTES=1_000_000
GROUP_COL_CANDIDATES=("groupss_","ID","group","Group","group_id")
SEASON_COL_CANDIDATES=("season_","SEASON","season","year_season","year_season_")
ENV_COL_CANDIDATES=("season_type","season_types","weather_regime","NDVI","rainfall")
USER_AGENT="boids-v22-2021-original-guineafowl-environment-structure/1.0"


def git_digest(content:bytes)->str:
    return hashlib.sha1(f"blob {len(content)}\0".encode()+content).hexdigest()


def download_pinned(name:str,to:Path)->dict:
    size,sha=FILES[name]
    if not 0<size<=MAX_BYTES:raise ValueError("Original metadata exceeds bounded limit")
    safe=name.replace(" ","%20")
    url=f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_SHA}/{safe}"
    request=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(request,timeout=55) as resp:
        length=resp.headers.get("Content-Length")
        if length is not None and int(length)!=size:
            raise ValueError("Original source byte count changed")
        raw=resp.read(MAX_BYTES+1)
    if len(raw)!=size or git_digest(raw)!=sha:
        raise ValueError("Original Git blob SHA1/byte count mismatch")
    to.write_bytes(raw)
    return {"name":name,"bytes":size,"git_blob_sha1_verified":True,
            "git_sha1":sha,"sha256":hashlib.sha256(raw).hexdigest(),
            "original_author_commit":SOURCE_SHA,"source_url":url}


def source_frame_profile(name:str,frame)->dict:
    import pandas as pd
    out={"table":name,"source_rows":int(len(frame)),
         "column_names":list(map(str,frame.columns)),
         "data_types":{str(c):str(frame[c].dtype) for c in frame.columns},
         "missing_values_by_column":{str(c):int(frame[c].isna().sum()) for c in frame.columns},
         "numeric_ecological_response_values_analyzed":False}
    group=next((k for k in GROUP_COL_CANDIDATES if k in frame),None)
    season=next((k for k in SEASON_COL_CANDIDATES if k in frame),None)
    environment=next((k for k in ENV_COL_CANDIDATES if k in frame),None)
    out.update({"identified_group_field":group,
                "identified_season_field":season,
                "identified_environment_field":environment})
    if group is None or season is None:
        out["repeated_group_season_status"]="NOT_IDENTIFIABLE_FROM_COLUMNS"
        return out
    df=frame.dropna(subset=[group,season])[[group,season]+(
             [environment] if environment and environment not in (group,season)
             else [])].copy()
    keys=df[[group,season]].astype(str)
    spans=keys.groupby(group)[season].nunique()
    dup=keys.duplicated(keep=False)
    counts=spans.value_counts().sort_index()
    out.update({
        "repeated_group_season_status":"SOURCE_KEYS_OBSERVED_NO_OUTCOMES",
        "complete_group_season_key_rows":len(keys),
        "unique_group_ids":int(spans.size),
        "unique_season_codes":int(df[season].nunique()),
        "groups_in_2_or_more_seasons":int((spans>=2).sum()),
        "groups_in_3_or_more_seasons":int((spans>=3).sum()),
        "groups_in_4_or_more_seasons":int((spans>=4).sum()),
        "duplicate_rows_of_same_group_season":int(dup.sum()),
        "source_observations_per_group_season_distribution":
           {str(k):int(v) for k,v in keys.groupby([group,season]).size().value_counts().items()},
        "original_repeated_season_distribution":
           {str(k):int(v) for k,v in counts.items()},
        "season_code_category_counts":{str(k):int(v) for k,v in df[season].astype(str).value_counts().items()},
    })
    if environment:
        cats=df[environment].astype(str)
        byseason=df[[season,environment]].astype(str).groupby(season)[environment].nunique()
        out["environment_label_categories_counts"]={
            str(k):int(v) for k,v in cats.value_counts().items()}
        out["source_seasons_with_exactly_one_environment_label"] = int((byseason==1).sum())
        out["source_seasons_with_multiple_environment_labels"] = int((byseason>1).sum())
        out["environment_categories"]=int(cats.nunique())
        out["environment_is_shared_source_season_label_not_group_specific"] = bool((byseason==1).all())
    else:
        out["environment_categories"]=0
    out["original_future_prediction_admission_UNDECIDED_due_to_season_chronology"]=True
    return out


def main_run()->dict:
    import pyreadr
    result={"study":"v22-2021-wild-guineafowl-seasonality-environment-source",
            "source_original":"Papageorgiou et al 2021 Movement Ecology, same Movebank 475851705 as v20",
            "original_author_repo":SOURCE_REPO,
            "original_author_sha":SOURCE_SHA,
            "source_license_context":"GitHub MIT code, telemetry licensing/consent separate",
            "source_integrity":{},
            "source_structure":{},
            "status":"SOURCE_PROVENANCE_ONLY_NO_FORECAST",
            "v20_is_same_biological_population":True,
            "raw_Movebank_GPS_acquired":False,
            "source_ecological_response_or_predictive_values_computed":False}
    with tempfile.TemporaryDirectory() as d:
        for name in FILES:
            p=Path(d)/name
            try:
                receipt=download_pinned(name,p)
                result["source_integrity"][name]=receipt
                objects=pyreadr.read_r(str(p))
                profile={}
                for key,frame in objects.items():
                    if hasattr(frame,"columns"):
                        profile[str(key)]=source_frame_profile(str(key),frame)
                    else:
                        profile[str(key)]={"status":"NON_TABLE_OBJECT","type":type(frame).__name__}
                result["source_structure"][name]=profile
            except Exception as exc:
                result["source_integrity"][name]={
                   "status":"ORIGINAL_BYTES_OR_RDATA_SOURCE_FAILED",
                   "reason":type(exc).__name__+": "+str(exc)[:160]}
    eligible=[]
    for name,objects in result["source_structure"].items():
        for key,pr in objects.items():
            if (pr.get("groups_in_3_or_more_seasons",0)>=8 and
                pr.get("environment_categories",0)>=3 and
                pr.get("source_seasons_with_multiple_environment_labels",1)==0):
                eligible.append({"original_file":name,"object":key,
                                 "repeated_groups":pr["groups_in_3_or_more_seasons"],
                                 "source_season_category_count":pr["environment_categories"],
                                 "source_unique_season_count":pr["unique_season_codes"],
                                 "group_season_duplicate_rows":pr["duplicate_rows_of_same_group_season"]})
    result["candidate_tables_for_separate_chronology_approval"]=eligible
    result["status"]=("SOURCE_REPEATED_GROUP_ENV_LABELS_AVAILABLE_CHRONOLOGY_UNVERIFIED"
                      if eligible else "NOT_ADMITTED_ENVIRONMENT_OR_GROUP_REPETITION_UNVERIFIED")
    return result


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",type=Path,
                     default=Path("validation_v22/results/original_seasonality_source_v22.json"))
    args=arg.parse_args()
    result=main_run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V22_SOURCE_INTEGRITY",json.dumps(result["source_integrity"],sort_keys=True))
    print("V22_ENV_SOURCE_SCHEMA",json.dumps(result["source_structure"],sort_keys=True))
    print("V22_ADMISSION_CANDIDATES",json.dumps(result["candidate_tables_for_separate_chronology_approval"],sort_keys=True))
    print("V22_STATUS",result["status"])
    print("V22_NO_ECOLOGY_RESPONSE_FORECAST_FITTED")


if __name__=="__main__":
    main()
