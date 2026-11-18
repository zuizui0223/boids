"""Source-only: original 2018/2019 measured RWS NAP Vlieland Haven vs West-Terschelling.
Do not use any bird behavior, GPS cells or local tide model.
"""
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import median,mean
import json,math,re
from rws_roompot_2020_source import publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop

YEARS=(2018,2019)
WINDOW=("06-01T00:00:00.000+01:00","06-03T00:00:00.000+01:00")
PRIMARY="vlieland.haven"
SECONDARY={"westterschelling","terschellingwest"}
SHIFT_MIN=tuple(range(-120,121,10))
OUT=Path(__file__).resolve().parent/"results/original_two_gauge_2018_2019_physical_contrast_v183.json"

def freeze_sites(catalog):
    if catalog.get("Succesvol") is False: raise SourceStop("RWS_ORIGINAL_STATION_CATALOGUE_REJECTED")
    rows=catalog.get("LocatieLijst") or []
    if len(rows)<50:raise SourceStop("RWS_ORIGINAL_STATION_CATALOGUE_TOO_SMALL")
    a=[r for r in rows if str(r.get("Code","")).lower()==PRIMARY and "vlieland" in str(r.get("Naam","")).lower()]
    b=[r for r in rows if re.sub("[^a-z]","",str(r.get("Naam","")).lower()) in SECONDARY]
    if len(a)!=1 or len(b)!=1 or a[0]["Code"]==b[0]["Code"]:
        raise SourceStop("RWS_ORIGINAL_TWO_SITES_MISSING_OR_AMBIGUOUS")
    return [{"code":a[0]["Code"],"name":a[0]["Naam"]},{"code":b[0]["Code"],"name":b[0]["Naam"]}]

def original_nap_series(obj):
    if obj.get("Succesvol") is not True:raise SourceStop("RWS_NATIVE_GAUGE_REQUEST_REJECTED")
    d={};excluded=Counter()
    for series in obj.get("WaarnemingenLijst") or []:
        meta=series.get("AquoMetadata") or {}
        if ((meta.get("Grootheid") or {}).get("Code")!="WATHTE" or
            (meta.get("Eenheid") or {}).get("Code")!="cm" or
            (meta.get("Hoedanigheid") or {}).get("Code")!="NAP"):
            excluded["wrong_native_gauge_type_unit_or_datum"]+=1
            continue
        for item in series.get("MetingenLijst") or []:
            try:
                t=datetime.fromisoformat(item["Tijdstip"].replace("Z","+00:00"))
                if t.utcoffset()!=timedelta(hours=1):
                    excluded["unexpected_native_clock"]+=1
                    continue
                z=float(item["Meetwaarde"]["Waarde_Numeriek"])/100
                if not math.isfinite(z) or abs(z)>5:
                    excluded["invalid_mNAP"]+=1
                    continue
                t=t.astimezone(timezone.utc)
                if t in d and abs(d[t]-z)>1e-8:raise SourceStop("RWS_NATIVE_CONTRADICTORY_DUPLICATE")
                d[t]=z
            except (KeyError,TypeError,ValueError):
                excluded["unparsed_record"]+=1
    if len(d)<200:raise SourceStop("RWS_GAUGE_48H_OBS_LT200")
    return d,dict(excluded)

def physical_gauge_contrast(v,w):
    ticks=sorted(set(v)&set(w))
    if len(ticks)<190:raise SourceStop("TWO_GAUGES_SHARED_TIMESTAMPS_LT190")
    diffs=[w[t]-v[t] for t in ticks]
    def quantile(x,p):
        x=sorted(x);return round(x[int((len(x)-1)*p)],6)
    candidate=[]
    for shift in SHIFT_MIN:
        dt=timedelta(minutes=shift)
        pairs=[(v[t],w[t+dt]) for t in ticks if t+dt in w]
        if len(pairs)<166:continue
        mx=mean(x for x,y in pairs);my=mean(y for x,y in pairs)
        numerator=sum((x-mx)*(y-my) for x,y in pairs)
        vx=sum((x-mx)**2 for x,y in pairs)
        vy=sum((y-my)**2 for x,y in pairs)
        if vx*vy<=0:continue
        candidate.append((shift,numerator/math.sqrt(vx*vy)))
    if not candidate or not any(s==0 for s,r in candidate):
        raise SourceStop("NO_VALID_ZERO_SHIFT_GAUGE_COMPARISON")
    best=max(candidate,key=lambda x:x[1])
    return {"exact_original_UTC_timestamps_both":len(ticks),
            "west_minus_vlieland_signed_height_m_median":round(median(diffs),6),
            "absolute_height_difference_m_median":round(median(map(abs,diffs)),6),
            "absolute_height_difference_m_p95":quantile(list(map(abs,diffs)),.95),
            "signed_height_difference_m_p05_p95":[quantile(diffs,.05),quantile(diffs,.95)],
            "zero_shift_correlation":round(next(r for s,r in candidate if s==0),6),
            "best_descriptive_shift_min_west_after_vlieland":best[0],
            "best_descriptive_shift_correlation":round(best[1],6),
            "NOT_a_spatial_tide_surface_at_bird_GPS":True}

def run(out=OUT):
    result={"version":"v183-physical-source-only","prespecified_station1":PRIMARY,
        "prespecified_station2":"unique official West Terschelling name",
        "prespecified_years":YEARS,"prespecified_48h_local_windows":WINDOW,
        "prespecified_crosscorrelation_shifts_min":SHIFT_MIN,
        "status":"SOURCE_STOP_ORIGINAL_TWO_GAUGES"}
    try:
        cat,catsha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        sites=freeze_sites(cat)
        result["official_station_catalog_SHA256"]=catsha
        result["original_site_identities"]=sites
        years={}
        for year in YEARS:
            series={};receipts={}
            for station in sites:
                payload={"Locatie":{"Code":station["code"]},
                    "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
                    "Periode":{"Begindatumtijd":f"{year}-{WINDOW[0]}",
                               "Einddatumtijd":f"{year}-{WINDOW[1]}"}}
                obj,sha=publisher_post(DATA_ROUTE,payload)
                values,excluded=original_nap_series(obj)
                series[station["code"]]=values
                receipts[station["name"]]={"original_RWS_response_SHA256":sha,
                    "n_true_WATHTE_cmNAP":len(values),"excluded_count":excluded}
            years[str(year)]={"original_publisher_receipts":receipts,
                "two_station_contrast":physical_gauge_contrast(series[sites[0]["code"]],
                                                               series[sites[1]["code"]])}
        result["years"]=years
        result["status"]="REAL_TWO_GAUGE_PHYSICAL_SOURCE_ADMITTED_NOT_LOCAL_GPS_TIDE"
    except (SourceStop,ValueError,OSError,TimeoutError) as exc:
        result["failure_reason"]=str(exc)[:250]
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V183_TWO_GAUGE_SCOPE="+json.dumps({"status":result["status"],
        "failure_reason":result.get("failure_reason"),
        "years":{k:v["two_station_contrast"] for k,v in result.get("years",{}).items()}},
        sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    run()
