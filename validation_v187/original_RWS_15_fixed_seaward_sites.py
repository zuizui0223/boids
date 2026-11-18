"""Exploratory v187: fix exactly one RWS sea-side station code per 2011 WEBTICS site
using v186 source CATALOGUE NAMES ONLY, before reading v187 2018/19 tide values.

2011 WEBTICS RD coordinates are NOT asserted to equal exact 2018/19 instruments.
v185 5/15 SOURCE_STOP is retained.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from rws_roompot_2020_source import publisher_post,META_ROUTE,SourceStop
from original_fifteen_wadden_gauge_inventory import ATLAS,check_original_48h

# Fixed exact native codes, selected from v186 station NAMES only.
# Prior five code matches from v185 are unchanged.
CODE={
"DenHelder":"denhelder.marsdiep",
"DenOever":"denoever.spuisluis.buiten",
"Kornwerderzand":"kornwerderzand.waddenzee.buitenhaven",
"Harlingen":"harlingen.waddenzee",
"Lauwersoog":"lauwersoog.waddenzee",
"Eemshaven":"eemshaven.waddenzee",
"Nieuwstatenzijl":"nieuwestatenzijl.buiten",
"Delfzijl":"delfzijl",
"Huibertgat":"huibertgat",
"Schiermonnikoog":"schiermonnikoog.waddenzee",
"Wierumergronden":"wierumergronden",
"Nes":"ameland.nes",
"WestTerschelling":"terschelling.west",
"VlielandHaven":"vlieland.haven",
"Oudeschild":"texel.oudeschild",
}
YEARS=(2018,2019)
OUT=Path(__file__).resolve().parent/"results/authentic_RWS_2018_2019_fixed_15_gauge_NAP_source_v187.json"

def norm(s):return re.sub("[^a-z]","",str(s).lower())

def freeze_selected(catalog):
    if catalog.get("Succesvol") is False:raise SourceStop("ORIGINAL_NATIVE_STATION_CATALOG_REJECTED")
    rows=catalog.get("LocatieLijst") or []
    if len(rows)<50:raise SourceStop("ORIGINAL_NATIVE_STATIONS_LT50")
    if set(CODE)!={row[0] for row in ATLAS} or len(set(CODE.values()))!=len(CODE):
        raise SourceStop("PREDECLARED_STATION_CODES_NOT_UNIQUE_OR_COMPLETE")
    selected=[]
    for name,x,y,aliases in ATLAS:
        matches=[row for row in rows if row.get("Code")==CODE[name]]
        if len(matches)!=1:
            selected.append({"reference_2011_station":name,"selected_code":CODE[name],
                "status":"STOP_FIXED_ORIGINAL_CODE_NOT_UNIQUE_OR_MISSING","n_source_rows":len(matches)})
            continue
        source=matches[0]
        if not any(alias in norm(source.get("Naam","")) for alias in aliases):
            selected.append({"reference_2011_station":name,"selected_code":CODE[name],
                "status":"STOP_SOURCE_NAME_GEOGRAPHY_DISAGREES"})
            continue
        selected.append({"reference_2011_station":name,"selected_code":CODE[name],
            "source_station_name":source.get("Naam"),
            "source_station_code":source.get("Code"),
            "source_natively_reported_horizontal_CRS":source.get("Coordinatenstelsel"),
            "source_native_X":source.get("X"),"source_native_Y":source.get("Y"),
            "reference_2011_RD_xy_m":[x,y],
            "instrument_position_equivalence_to_2011_NOT_VERIFIED":True,
            "source_seaward_choice_from_catalogue_name_not_tide_values":True,
            "status":"NAME_ONLY_SOURCE_CODE_MATCH"})
    return selected

def run(out=OUT):
    result={"version":"v187-post-v185-failure-exploratory-seaward-name-based-15-native-codes",
      "failed_v185_five_of_fifteen_gate_preserved":True,
      "v186_native_station_name_only_diagnosis_precedes_v187_gauge_fetch":True,
      "predeclared_source_code_map":CODE,
      "predeclared_RWS_48h_years":YEARS,
      "original_RWS_source_min8_both_years_NOT_confirmatory_after_v185":True,
      "original_2011_RD_to_native_instrument_horizontal_equivalence":"NOT_VERIFIED",
      "status":"SOURCE_STOP"}
    try:
        catalog,catsha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        selected=freeze_selected(catalog)
        result["native_RWS_catalogue_SHA256"]=catsha
        for s in selected:
            measurements={}
            for year in YEARS:
                if s["status"]=="NAME_ONLY_SOURCE_CODE_MATCH":
                    try:
                        measurements[str(year)]=check_original_48h(s,year)
                    except (SourceStop,ValueError,OSError,TimeoutError) as e:
                        measurements[str(year)]={"status":"SOURCE_STOP","reason":str(e)[:180]}
                else:measurements[str(year)]={"status":"SOURCE_STOP_STATION_IDENTITY"}
            s["original_source_by_year"]=measurements
        result["sites"]=selected
        accepted=[s["reference_2011_station"] for s in selected if all(
            s["original_source_by_year"][str(year)].get("status")==
             "ORIGINAL_WATHTE_cmNAP_48H_SOURCE_ADMITTED" for year in YEARS)]
        result["n_source_admitted_both_years"]=len(accepted)
        result["source_admitted_2018_2019_reference_sites"]=accepted
        result["source_8plus_gauge_coverage_exploratory"]=len(accepted)>=8
        result["status"]="EXPLORATORY_NATIVE_GAUGE_SOURCE_N8_PLUS_NOT_SITE_COORDINATES" if len(accepted)>=8 else "SOURCE_NETWORK_INSUFFICIENT"
    except (SourceStop,ValueError,OSError,TimeoutError) as e:
        result["source_stop_reason"]=str(e)[:200]
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V187_FIXED_SOURCE_SCOPE="+json.dumps({
        "status":result["status"],
        "n_admitted":result.get("n_source_admitted_both_years"),
        "admitted_site_names":result.get("source_admitted_2018_2019_reference_sites"),
        "site_year_status":{s["reference_2011_station"]:{
            "native_code":s["selected_code"],
            "name_status":s["status"],
            "years":{year:detail["status"] for year,detail in s["original_source_by_year"].items()}}
            for s in result.get("sites",[])},
        "still_NO_local_TIDE_at_GPS_or_vertical_datum":True},sort_keys=True),flush=True)
    return result

if __name__=="__main__":run()
