"""v185: source-only 15 Wadden gauges from pre-existing WEBTICS station appendix.

2011 reference RD coordinates are context, NOT 2018/2019 exact instrument positions.
No tide amplitudes, bird positions or behavioral outcomes are exported.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,re
from rws_roompot_2020_source import publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop
from original_RWS_two_gauge_comparison import original_nap_series

REFERENCE_URL = "https://nam-feitenencijfers.data-app.nl/download/rapport/d360edf8-1955-4ee4-b0e9-58826d7e0a53?open=true"
# Rappoldt & Ens 2011 (WEBTICS), Appendix A Table A.1. RD Netherlands / EPSG:28992.
# Freeze all names and original 2011 approx RD metres BEFORE reading RWS 2018/2019 stations.
ATLAS=(
 ("DenHelder",111850,553230,("denhelder",)),
 ("DenOever",132030,549440,("denoever","denoeverbuiten")),
 ("Kornwerderzand",151610,564780,("kornwerderzand",)),
 ("Harlingen",156480,576550,("harlingen",)),
 ("Lauwersoog",208850,602790,("lauwersoog",)),
 ("Eemshaven",250750,607900,("eemshaven",)),
 ("Nieuwstatenzijl",276540,584310,("nieuwstatenzijl","nieuwestatenzijl")),
 ("Delfzijl",258000,594430,("delfzijl",)),
 ("Huibertgat",221990,621330,("huibertgat",)),
 ("Schiermonnikoog",209170,609500,("schiermonnikoog",)),
 ("Wierumergronden",192882,614562,("wierumergronden",)),
 ("Nes",179707,604916,("nes",)),
 ("WestTerschelling",143870,597420,("westterschelling","terschellingwest")),
 ("VlielandHaven",135280,590000,("vlielandhaven",)),
 ("Oudeschild",118980,561460,("oudeschild",)),
)
YEARS=(2018,2019)
N_MIN_BOTH_YEARS=8
OUT=Path(__file__).resolve().parent/"results/original_fifteen_wadden_gauge_source_inventory_v185.json"

def normalized(text):
    return re.sub("[^a-z]","",str(text).lower())

def select_fixed_catalogue(catalogue):
    if catalogue.get("Succesvol") is False:raise SourceStop("REAL_RWS_CATALOG_REJECTED")
    allsites=catalogue.get("LocatieLijst") or []
    if len(allsites)<50:raise SourceStop("REAL_RWS_CATALOG_UNEXPECTEDLY_SMALL")
    assigned=[]
    for name,x,y,aliases in ATLAS:
        matches=[r for r in allsites if normalized(r.get("Naam","")) in aliases]
        unique_codes={str(r.get("Code","")).strip() for r in matches}
        if len(matches)==1 and len(unique_codes)==1 and "" not in unique_codes:
            v=matches[0]
            selected={"match_status":"SINGLE_NATIVE_RWS_NAME","source_station_name":v.get("Naam"),
                      "source_station_code":v.get("Code"),
                      "original_coordinate_system":v.get("Coordinatenstelsel"),
                      "original_coordinate_X":v.get("X"),"original_coordinate_Y":v.get("Y")}
        else:
            selected={"match_status":"NO_MATCH" if not matches else "AMBIGUOUS_MATCH_STOP",
                      "n_matching_provider_rows":len(matches),
                      "n_unique_provider_codes":len(unique_codes)}
        assigned.append({"webtics_2011_station_name":name,
            "webtics_2011_xRD_m":x,"webtics_2011_yRD_m":y,
            "webtics_2011_original_reference_not_field_2019_coordinates":True,
            **selected})
    return assigned

def check_original_48h(site,year):
    request={"Locatie":{"Code":site["source_station_code"]},
       "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
       "Periode":{"Begindatumtijd":f"{year}-06-01T00:00:00.000+01:00",
                  "Einddatumtijd":f"{year}-06-03T00:00:00.000+01:00"}}
    obj,sha=publisher_post(DATA_ROUTE,request)
    try:
        levels,qa=original_nap_series(obj)
    except (SourceStop,ValueError) as exc:
        return {"status":"SOURCE_STOP","reason":str(exc)[:160],
                "response_SHA256":sha}
    return {"status":"ORIGINAL_WATHTE_cmNAP_48H_SOURCE_ADMITTED",
            "response_SHA256":sha,
            "n_native_observations":len(levels),
            "native_qa_exclusions":qa,
            "not_yet_a_tide_interpolation_validation":True}

def run(out=OUT):
    report={"version":"v185-predeclared-WEBTICS-15-Wadden-stations",
        "webtics_atlas_original_url":REFERENCE_URL,
        "reference_atlas_station_count":len(ATLAS),
        "predeclared_years":YEARS,
        "source_only_original_station_metadata_and_RWS_48h_NAP_counts":True,
        "status":"SOURCE_STOP"}
    try:
        cat,sha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        selected=select_fixed_catalogue(cat)
        report["publisher_original_catalogue_SHA256"]=sha
        for s in selected:
            if s["match_status"]!="SINGLE_NATIVE_RWS_NAME":
                s["original_data_years"]={str(y):{"status":"SOURCE_NOT_SELECTED"} for y in YEARS}
                continue
            years={}
            for year in YEARS:
                try:years[str(year)]=check_original_48h(s,year)
                except (SourceStop,ValueError,OSError,TimeoutError) as exc:
                    years[str(year)]={"status":"SOURCE_STOP","reason":str(exc)[:200]}
            s["original_data_years"]=years
        report["stations"]=selected
        admitted=[s["webtics_2011_station_name"] for s in selected if
                  all(s["original_data_years"][str(y)]["status"]==
                      "ORIGINAL_WATHTE_cmNAP_48H_SOURCE_ADMITTED" for y in YEARS)]
        report["original_station_NAP_source_admitted_both_2018_2019"]=admitted
        report["n_original_station_NAP_source_admitted_both_years"]=len(admitted)
        report["station_coverage_gate_minimum_8_original_pairs"]=len(admitted)>=N_MIN_BOTH_YEARS
        report["status"]="SOURCE_NETWORK_ATLAS_ADMITTED_NOT_WETDRY_OR_LOOCV" if len(admitted)>=N_MIN_BOTH_YEARS else "SOURCE_NETWORK_INSUFFICIENT"
    except (SourceStop,ValueError,OSError,TimeoutError) as exc:
        report["source_stop_reason"]=str(exc)[:200]
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V185_REAL_WADDEN_ATLAS="+json.dumps({
       "status":report["status"],
       "source_stop_reason":report.get("source_stop_reason"),
       "n_2018_2019_NAP_stations":report.get("n_original_station_NAP_source_admitted_both_years"),
       "both_years_station_names":report.get("original_station_NAP_source_admitted_both_2018_2019"),
       "all_station_statuses":[{
           "name":r["webtics_2011_station_name"],
           "catalog_status":r["match_status"],
           "years":{y:v["status"] for y,v in r.get("original_data_years",{}).items()}
       } for r in report.get("stations",[])]},sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    run()
