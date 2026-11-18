"""v186 after frozen v185 5/15 source gate STOP: original RWS catalogue metadata only.

This is exploratory NAME/LOCATION diagnosis; never open levels or select gauges by tide
phase/height. Outputs candidate names and catalogue coords only, no bird or gauge Y.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from rws_roompot_2020_source import publisher_post,META_ROUTE,SourceStop
from original_fifteen_wadden_gauge_inventory import ATLAS

OUT=Path(__file__).resolve().parent/"results/native_RWS_catalogue_station_alias_candidates_v186.json"
PRIOR_V185_SUCCESS=("Delfzijl","Huibertgat","Wierumergronden","WestTerschelling","VlielandHaven")

def compact(s):
    return re.sub("[^a-z]","",str(s or "").lower())

def candidates_for_target(official_rows, atlas_row):
    name,xd,yd,aliases=atlas_row
    result=[]
    for r in official_rows:
        official_name=str(r.get("Naam") or "")
        original_code=str(r.get("Code") or "")
        if not official_name or not original_code:continue
        norm=compact(official_name)
        if name=="Nes":
            matched=bool(re.search(r"(?i)(?<![a-z])Nes(?![a-z])",official_name))
        else:
            matched=any(alias in norm for alias in aliases)
        if not matched:continue
        kind="EXACT" if norm in aliases else "ALIAS_CONTAINS_ORIGINAL_SITE_NAME"
        result.append({"original_native_station_name":official_name,
                       "original_native_station_code":original_code,
                       "original_RWS_coordinate_system":r.get("Coordinatenstelsel"),
                       "original_RWS_X":r.get("X"),"original_RWS_Y":r.get("Y"),
                       "match_kind":kind,
                       "2011_reference_RD_xy_m":[xd,yd],
                       "RWS_XY_are_NOT_assumed_RD_until_verified":True})
    return sorted(result,key=lambda x:(x["match_kind"]!="EXACT",x["original_native_station_name"],x["original_native_station_code"]))

def report_candidates(catalogue):
    if catalogue.get("Succesvol") is False:raise SourceStop("RWS_CATALOGUE_REJECTED")
    rows=catalogue.get("LocatieLijst") or []
    if len(rows)<50:raise SourceStop("RWS_NATIVE_CATALOGUE_TOO_SMALL")
    out=[]
    for site in ATLAS:
        c=candidates_for_target(rows,site)
        out.append({"reference_site":site[0],"n_original_catalogue_name_candidates":len(c),
                    "original_catalogue_candidates":c,
                    "no_height_values_evaluated":True})
    return out

def run(out=OUT):
    data={"analysis":"v186_catalogue_name_alias_diagnosis_after_v185_SOURCE_NETWORK_INSUFFICIENT",
          "predeclared_2011_reference_site_count":len(ATLAS),
          "v185_n_both_years_original_NAP_source_admitted":5,
          "v185_failed_min8_gate_not_overridden":True,
          "no_original_tide_heights_requested_or_scored":True,
          "status":"SOURCE_PENDING"}
    try:
        cat,sha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        data["RWS_native_full_catalogue_response_SHA256"]=sha
        sites=report_candidates(cat)
        data["sites"]=sites
        data["all_sites_with_any_original_name_candidates"]=[
            s["reference_site"] for s in sites if s["n_original_catalogue_name_candidates"]>0]
        data["sites_without_any_original_name_candidate"]=[
            s["reference_site"] for s in sites if s["n_original_catalogue_name_candidates"]==0]
        data["status"]="ORIGINAL_RWS_CATALOGUE_CANDIDATES_DIAGNOSED_NOT_GAUGE_ADMISSION"
    except (SourceStop,ValueError,OSError,TimeoutError) as exc:
        data["status"]="SOURCE_STOP"
        data["source_stop_reason"]=str(exc)[:200]
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V186_RWS_CATALOGUE_DIAGNOSTIC="+json.dumps({
        "status":data["status"],"no_tides_scored":True,
        "sites":{r["reference_site"]:{
            "n_candidates":r["n_original_catalogue_name_candidates"],
            "native_name_code_crs_xy":[{
                "name":k["original_native_station_name"],
                "code":k["original_native_station_code"],
                "crs":k["original_RWS_coordinate_system"],
                "X":k["original_RWS_X"],"Y":k["original_RWS_Y"],
                "kind":k["match_kind"]} for k in r["original_catalogue_candidates"]]
        } for r in data.get("sites",[])}},sort_keys=True),flush=True)
    return data

if __name__=="__main__":run()
