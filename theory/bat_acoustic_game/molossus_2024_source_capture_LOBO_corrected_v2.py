"""Corrected original 2024 PNAS Molossus source prey-capture bat holdout V2.

POSTOUTCOME DATA-GRAIN CORRECTION. Original v1 E=numel_5swindows is invalid,
and its score is QUARANTINED. This script uses exactly one observed 5-sec
source group row per exposure, discards no observed source groups in primary,
and separately examines 9 bats with contiguous original sec_group indices.

Original 2024 PNAS published inverted-U result is prior art. The new CV score
is source-internal ecological prediction, not independent bat confirmation.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean,median
import hashlib,io,json,math,zipfile

from molossus_2024_supplement_structure_v1 import download_bounded,URL,EXPECTED
from molossus_2024_source_capture_LOBO_v1 import (
  decode_sheet,parse_integer,SOURCE_SHA,bin_support,evaluate_source,
)

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"MOLOSSUS_2024_CAPTURE_CORRECTED_EXPOSURE_V2_PREOUTPUT.md"
OUT=ROOT/"MOLOSSUS_2024_CAPTURE_CORRECTED_SOURCE_MODEL_V2.json"

def admit_corrected_source(rawrows):
    new=[]
    groups=defaultdict(list)
    original_numel_field=0
    for original in rawrows:
        bat=str(original[0]).strip() if original[0] is not None else ""
        if not bat:raise ValueError("STOP_SOURCE_NO_ORIGINAL_BAT_ID")
        group=parse_integer(original[1],"sec_group")
        numel=parse_integer(original[2],"numel_5swindows")
        A=parse_integer(original[3],"sum_attacks")
        Y=parse_integer(original[4],"sum_success")
        C=parse_integer(original[5],"sum_cons")
        commute=parse_integer(original[6],"sum_commute")
        disrupt=parse_integer(original[7],"sum_disrupt")
        if Y>A:raise ValueError("STOP_SOURCE_SUCCESS_EXCEEDS_ATTEMPTS")
        if numel<=0:raise ValueError("STOP_SOURCE_NUMEL_NOT_POSITIVE_METADATA")
        # CORRECTION V2: E=1 original 5s group, not numel count
        E=1
        z=math.log1p(C)/math.log1p(100.)
        if not 0<=z<=2:raise ValueError("STOP_SOURCE_DENSITY_OUTSIDE_FROZEN_Z_RANGE")
        groups[bat].append(group)
        original_numel_field+=numel
        new.append({"bat":bat,"E":E,"A":A,"Y":Y,
                    "C":C,"commute":commute,"disrupt":disrupt,
                    "z":z,"density":float(C)})
    if len(groups)!=10 or len(new)!=4299:
        raise ValueError("STOP_SOURCE_BAT_GROUP_OR_ROW_COUNT_CHANGED")
    clean=set()
    anomalies=[]
    for bat,ids in groups.items():
        order=sorted(ids)
        no_repeats=len(set(order))==len(order)
        missing=sum(max(0,b-a-1) for a,b in zip(order,order[1:]))
        valid=no_repeats and missing==0
        if valid:clean.add(bat)
        else:anomalies.append({"original_source_row_count":len(ids),
             "original_sec_group_missing_indices":missing,
             "original_source_sec_group_duplicates":len(ids)-len(set(ids))})
    if len(clean)!=9 or len(anomalies)!=1:
        raise ValueError("STOP_FROZEN_SOURCE_CLEAN_NINE_BAT_GATE_CHANGED")
    if anomalies[0]["original_sec_group_missing_indices"]!=7 or anomalies[0]["original_source_sec_group_duplicates"]!=0:
        raise ValueError("STOP_SOURCE_ANOMALY_NO_LONGER_SEVEN_MISSING")
    return new,clean,{
        "original_source_rows":len(new),
        "original_source_biological_bats":len(groups),
        "source_bats_with_complete_5second_group_series":len(clean),
        "source_bats_with_one_seven_group_gap":len(anomalies),
        "source_anomaly_metadata_only":anomalies,
        "original_numel_5swindows_FIELD_SUM_NOT_EXPOSURE":original_numel_field,
        "invalid_previous_source_estimated_exposures":original_numel_field,
        "corrected_observed_5s_exposures_all_ten_bats":sum(x["E"] for x in new),
        "observed_5s_exposures_nine_clean_bats":sum(x["bat"] in clean for x in new),
        "original_confirmed_capture_count":sum(x["Y"] for x in new),
        "original_attack_count":sum(x["A"] for x in new),
        "original_neighbor_call_count":sum(x["C"] for x in new),
        "original_source_bat_IDs_or_5s_rows_released":False}


def read_original_pnas():
    if not CONTRACT.exists():
        raise ValueError("STOP_MISSING_CORRECTED_ORIGINAL_SOURCE_CONTRACT")
    b,http,contenttype=download_bounded(URL)
    z=zipfile.ZipFile(io.BytesIO(b))
    original=[x for x in z.infolist() if x.filename.split("/")[-1]==EXPECTED]
    if len(original)!=1:raise ValueError("STOP_NONUNIQUE_SOURCE_WORKBOOK")
    content=z.read(original[0])
    sha=hashlib.sha256(content).hexdigest()
    if sha!=SOURCE_SHA:raise ValueError("STOP_PNAS_ORIGINAL_SOURCE_SHA_CHANGED")
    rows=decode_sheet(content)
    obs,clean,meta=admit_corrected_source(rows)
    return obs,clean,meta,hashlib.sha256(b).hexdigest()


def run():
    records,clean,meta,zipsha=read_original_pnas()
    clean_rows=[r for r in records if r["bat"] in clean]
    return {"schema":2,
       "status":"CORRECTED_ORIGINAL_MOLOSSUS_2024_5S_SOURCE_BAT_LOBO",
       "date":"2026-11-05",
       "original_publication_DOI":"10.1073/pnas.2321724121",
       "original_data_source":"Europe PMC supplementaryFiles / PMC11287165 / pnas.2321724121.sd01.xlsx",
       "original_XLSX_SHA256":SOURCE_SHA,
       "original_PMC_supplement_zip_sha256":zipsha,
       "source_data_quality":meta,
       "quarantined_prior_v1_due_to_wrong_exposure":True,
       "corrected_source_exposure":"ONE original sec_group 5s observed row = ONE five-second exposure; missing original groups not filled",
       "original_numel_5swindows_NOT_exposure":True,
       "identical_model_family_and_penalty_to_v1":True,
       "primary_all_ten_source_bats":{
           "source_original_bats":10,
           "source_original_5s_rows":len(records),
           "density_exposure_support":bin_support(records),
           "bat_LOBO_result":evaluate_source(records)},
       "sensitivity_nine_source_time_consecutive_bats":{
           "source_original_bats":9,
           "source_original_5s_rows":len(clean_rows),
           "density_exposure_support":bin_support(clean_rows),
           "bat_LOBO_result":evaluate_source(clean_rows)},
       "new_animal_measurements":False,
       "no_original_bat_IDs_source_rows_or_sensitive_locations_released":True,
       "original_2024_authors_inverted_u_and_two_stage_tradeoff_prior_art":True,
       "cross_species_causal_inference_or_2026_Hase_replay":False,
       "interpretation":"LOBO tests secondary source-internal prediction across bats in the same original species/data collection. It does not prove social information or sonar interference mechanisms."
    }


def main():
    try:result=run()
    except Exception as e:
        result={"schema":2,"status":"STOP_CORRECTED_SOURCE_OR_MODEL",
                "reason":type(e).__name__+":"+str(e)[:240],
                "new_animal_measurements":False,
                "no_original_bat_IDs_source_rows_or_sensitive_locations_released":True}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("MOLOSSUS_SOURCE_CORRECTED_V2",result["status"])
    if result["status"].startswith("STOP"):
        print("STOP_REASON",result["reason"])
        return 3
    print("SOURCE_QC",result["source_data_quality"])
    for name in ("primary_all_ten_source_bats","sensitivity_nine_source_time_consecutive_bats"):
        a=result[name]
        print("SOURCE_COHORT",name,"bats",a["source_original_bats"],"five_second_rows",a["source_original_5s_rows"])
        print("SOURCE_DENSITY_SUPPORT",name,a["density_exposure_support"])
        print("SOURCE_PREDICTION",name,a["bat_LOBO_result"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
