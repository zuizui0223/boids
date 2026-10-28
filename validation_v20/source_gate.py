#!/usr/bin/env python3
"""v20 source-only group-season metadata and Figshare provenance, NO outcome scores."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
import tempfile
import urllib.request
from pathlib import Path
import pandas as pd

AUTHOR_REPO="DanPapageorgiou/Group_size"
AUTHOR_SHA="15ea08ed10555beba227792f4ef106d87d52b6a4"
FILENAME="Computed_seasonal_measurements.Rdata"
ORIGINAL_BLOB_SHA1="3fe1e3245cb97026b03125582d5af14ab9fd5b39"
ORIGINAL_BYTE_COUNT=2717
MAX_BYTES=5_000_000
FIGSHARE_ID=28950032
FIGSHARE_API=f"https://api.figshare.com/v2/articles/{FIGSHARE_ID}"
RAW=f"https://raw.githubusercontent.com/{AUTHOR_REPO}/{AUTHOR_SHA}/{FILENAME}"


def git_blob_sha1(b:bytes)->str:
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()


def download_pinned(path:Path)->dict:
    req=urllib.request.Request(RAW,headers={
        "User-Agent":"boids-v20-wild-guineafowl-source-grain/1.0"})
    with urllib.request.urlopen(req,timeout=35) as resp:
        expected_header=resp.headers.get("Content-Length")
        if expected_header and int(expected_header)!=ORIGINAL_BYTE_COUNT:
            raise ValueError("Original compressed source size changed")
        b=resp.read(MAX_BYTES+1)
    if len(b)!=ORIGINAL_BYTE_COUNT:
        raise ValueError("Original Rdata byte length failed")
    if git_blob_sha1(b)!=ORIGINAL_BLOB_SHA1:
        raise ValueError("Original author git blob digest failed")
    path.write_bytes(b)
    return {"source_url":RAW,"source_git_commit":AUTHOR_SHA,
            "bytes":len(b),"git_blob_sha1":ORIGINAL_BLOB_SHA1,
            "sha256":hashlib.sha256(b).hexdigest(),
            "original_source_hash_match":True}


def profile_frames(objects:dict)->dict:
    info={}
    candidates={}
    for obj,table in objects.items():
        if not isinstance(table,pd.DataFrame):
            info[str(obj)]={"status":"not_tabular_dataframe","type":type(table).__name__}
            continue
        rows=len(table)
        names=list(map(str,table.columns))
        key_id="ID" if "ID" in table else None
        key_season="SEASON" if "SEASON" in table else None
        profile={"rows":rows,"columns":names,
                 "types":{str(c):str(table[c].dtype) for c in table.columns},
                 "id_column_present":key_id is not None,
                 "season_column_present":key_season is not None,
                 "missing_counts_by_column":{str(c):int(table[c].isna().sum())
                                              for c in table.columns},
                 "numeric_value_or_effect_scores_analyzed":False}
        if key_id and key_season and rows>0:
            valid=table.dropna(subset=[key_id,key_season])
            if valid.empty:
                profile["identity_status"]="all_null_keys"
            else:
                key=valid[[key_id,key_season]].astype(str)
                same=key.duplicated(keep=False)
                groups=key.groupby("ID")["SEASON"].nunique()
                seasonal=key.groupby("SEASON").size()
                counts=groups.value_counts().sort_index()
                profile.update({
                    "identity_status":"group_season_grain_profiled_only",
                    "n_unique_original_group_ids":int(groups.size),
                    "n_season_labels":int(key["SEASON"].nunique()),
                    "n_complete_group_season_keys":int(len(valid)),
                    "duplicate_group_season_key_rows":int(same.sum()),
                    "groups_observed_in_2_or_more_seasons":int((groups>=2).sum()),
                    "groups_observed_in_3_or_more_seasons":int((groups>=3).sum()),
                    "groups_observed_in_4_or_more_seasons":int((groups>=4).sum()),
                    "group_season_recurrence_count_distribution":
                        {str(int(k)):int(v) for k,v in counts.items()},
                    "season_row_counts":{str(k):int(v) for k,v in seasonal.items()},
                    "raw_GPS_and_individual_bird_IDs_available":False,
                    "future_group_season_admitted":
                        int((groups>=2).sum())>=8 and
                        int(key["SEASON"].nunique())>=2 and
                        int(same.sum())==0,
                    "three_season_memory_history_admitted":
                        int((groups>=3).sum())>=8 and
                        int(key["SEASON"].nunique())>=3 and
                        int(same.sum())==0,
                })
        info[str(obj)]=profile
        if profile.get("future_group_season_admitted"):
            candidates[str(obj)]=profile.get("groups_observed_in_2_or_more_seasons",0)
    return {"data_objects":info,
            "eligible_independent_group_season_tables":candidates,
            "source_is_derived_not_native_GPS":True,
            "prediction_scores_computed":False}


def discover_figshare()->dict:
    url=FIGSHARE_API
    try:
        req=urllib.request.Request(url,headers={
           "User-Agent":"boids-v20-independent-chain-reanalysis-metadata/1.0",
           "Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=40) as res:
            raw=res.read(4_000_001)
        if len(raw)>4_000_000:raise ValueError("Metadata too large")
        obj=json.loads(raw)
        if int(obj.get("id",-1))!=FIGSHARE_ID:raise ValueError("Wrong Figshare ID")
        fl=[]
        for source in obj.get("files",[]):
            fl.append({"name":source.get("name"),
                       "size_bytes":source.get("size"),
                       "provider_md5":source.get("computed_md5") or source.get("supplied_md5"),
                       "file_id":source.get("id"),
                       "url":source.get("download_url")})
        return {"status":"METADATA_ONLY","id":FIGSHARE_ID,
                "title":obj.get("title"),"doi":obj.get("doi"),
                "version":obj.get("version"),
                "license":obj.get("license"),
                "file_metadata":fl,
                "original_bird_data_independence_verified":False,
                "GPS_or_model_outcomes_opened":False}
    except Exception as e:
        return {"status":"METADATA_NOT_ACCESSIBLE","source":url,
                "error":type(e).__name__+": "+str(e)[:140]}


def run()->dict:
    fig=discover_figshare()
    out={"study":"boids-v20-wild-group-derived-season-source-admission",
         "date_registration":"2026-10-28",
         "source_paper":"Papageorgiou & Farine (2020) eLife.59902",
         "source_raw_movebank_status":"login_and_study_grant_required_not_acquired",
         "source_group_season_original":None,
         "source_metadata_profile":None,
         "independent_2026_figshare_reanalysis":fig,
         "status":"NOT_ADMITTED_UNCHECKED",
         "GPS_positions_and_response_values_not_analyzed":True}
    try:
        import pyreadr
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"published_seasonal_original.Rdata"
            src=download_pinned(path)
            objects=pyreadr.read_r(str(path))
            prof=profile_frames(objects)
        out["source_group_season_original"]=src
        out["source_metadata_profile"]=prof
        out["status"]=("SOURCE_METADATA_GROUP_SEASON_ADMITTED_FOR_NEW_PROTOCOL"
                       if prof["eligible_independent_group_season_tables"] else
                       "NOT_ADMITTED_INSUFFICIENT_REPEATED_GROUPS_OR_DATA_GRAIN")
    except Exception as e:
        out["status"]="NOT_ADMITTED_SOURCE_OR_RDATA_READ_FAILED"
        out["reason"]=type(e).__name__+": "+str(e)[:180]
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v20/results/wild_group_source_metadata_v20.json"))
    args=p.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V20_SOURCE_RESULT",json.dumps(r,sort_keys=True))
    print("V20_NO_OBSERVED_ECOLOGICAL_MODEL_FITTED")
if __name__=="__main__":
    main()
