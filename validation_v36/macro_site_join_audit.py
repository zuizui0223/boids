#!/usr/bin/env python3
"""v36 source-only protected coordinate joining; no bat movement outcomes."""
import argparse,csv,io,json,math
from pathlib import Path
from original_bat_macro_source_gate import FILES,download_original

OUT=Path("validation_v36/results/macro_bat_site_join_v36.json")
def number(s):
    try:
        x=float(str(s).strip().replace(",","."))
        return x if math.isfinite(x) else None
    except (ValueError,TypeError):return None
def nonempty(s):
    return str(s or "").strip().lower() not in ("","na","n/a","nan","null","-")
def parse(text):
    sep=max((";",",","\t"),key=text.splitlines()[0].count)
    return list(csv.DictReader(io.StringIO(text),delimiter=sep))
def distance(lon1,lat1,lon2,lat2):
    p1,p2=math.radians(lat1),math.radians(lat2)
    h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(h)))
def study(r):
    return tuple(str(r.get(x,"")).strip() for x in ("Authors","Year_pub","Journal"))
def audit(meta,land):
    pub={study(r) for r in meta}
    countries={r.get("Pays") for r in meta if nonempty(r.get("Pays"))}
    taxa={r.get("Species") for r in meta if nonempty(r.get("Species"))}
    site=[]
    for r in land:
        x,y=number(r.get("X")),number(r.get("Y"))
        if x is not None and y is not None:site.append((x,y))
    res={}
    for orientation in ("X_LON_Y_LAT","X_LAT_Y_LON"):
        pts=[(a,b) if orientation=="X_LON_Y_LAT" else (b,a) for a,b in site]
        pts=[(x,y) for x,y in pts if -180<=x<=180 and -90<=y<=90]
        parseable=matched=ambig=0
        used_site=set();used_pub=set();used_country=set();used_species=set()
        nonmissing={"MCP":0,"Dist":0}
        for r in meta:
            lat,lon=number(r.get("Lat")),number(r.get("Long"))
            if lat is None or lon is None or not(-90<=lat<=90 and -180<=lon<=180):continue
            parseable+=1
            d=sorted((distance(lon,lat,x,y),i) for i,(x,y) in enumerate(pts))
            if not d:continue
            smallest,idx=d[0];second=d[1][0] if len(d)>1 else float("inf")
            if smallest<=1.0 and second>=3.0:
                matched+=1;used_site.add(idx);used_pub.add(study(r))
                if nonempty(r.get("Pays")):used_country.add(r["Pays"])
                if nonempty(r.get("Species")):used_species.add(r["Species"])
                for field in nonmissing:
                    if nonempty(r.get(field)):nonmissing[field]+=1
            elif smallest<=1.0:ambig+=1
        res[orientation]={
            "valid_landscape_coordinate_sites":len(pts),
            "geographic_metadata_rows_parseable":parseable,
            "unique_match_rows_under_1km_and_3km_second_nearest":matched,
            "unique_match_fraction":matched/parseable if parseable else 0,
            "ambiguous_near_site_rows":ambig,"matched_landscape_site_count":len(used_site),
            "candidate_paper_groups_matched":len(used_pub),
            "countries_matched":len(used_country),"original_species_labels_matched":len(used_species),
            "nonmissing_target_field_rows_matched":nonmissing}
    a=res["X_LON_Y_LAT"]["unique_match_fraction"]
    b=res["X_LAT_Y_LON"]["unique_match_fraction"]
    choice=("X_LON_Y_LAT" if a>=.8 and b<=.1 else
            "X_LAT_Y_LON" if b>=.8 and a<=.1 else None)
    status="JOIN_OR_GRAIN_STOP_NO_PREDECLARED_UNIQUE_ORIENTATION"
    if choice:
        r=res[choice]
        if r["candidate_paper_groups_matched"]>=10 and r["countries_matched"]>=4 and \
           r["original_species_labels_matched"]>=10 and \
           max(r["nonmissing_target_field_rows_matched"].values())>=100:
            status="JOIN_STRUCTURALLY_ELIGIBLE_OUTCOMES_UNOPENED"
        else:status="JOIN_OR_GRAIN_STOP_INSUFFICIENT_GROUP_SUPPORT"
    return {"status":status,"meta_original_rows":len(meta),"landscape_original_rows":len(land),
            "candidate_paper_groups_all_meta":len(pub),"countries_all_meta":len(countries),
            "original_species_labels_all_meta":len(taxa),"fixed_orientations":res,
            "chosen_orientation":choice,"source_coordinates_exported":False,
            "movement_outcome_numeric_values_opened":False,
            "ecological_effects_fitted":False}
def run():
    data={}
    for key, spec in FILES.items():
        d=download_original(spec)
        if d["status"]!="ORIGINAL_CSV_PINNED":
            return {"status":"SOURCE_REDOWNLOAD_STOP","failed_file":key,
                    "movement_outcome_numeric_values_opened":False}
        data[key]=d["_csv_text"]
    result=audit(parse(data["published_meta"]),parse(data["published_landscape"]))
    result["both_original_MD5_verified"]=True
    return result
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",type=Path,default=OUT)
    args=parser.parse_args();z=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print("V36_MACRO_JOIN="+json.dumps(z,sort_keys=True))
    assert z["movement_outcome_numeric_values_opened"] is False
