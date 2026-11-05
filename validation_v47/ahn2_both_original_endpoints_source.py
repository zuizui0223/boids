"""v47: only original GPS B+C and historical AHN2 source overlap, NO tide join.

This source-only gate applies exactly v46 source 2010 K=8 selected RD cells
and 256x256 original AHN2 WCS patches. C-only counts independently replay
v46's original source support before any 2-endpoint field admission.
"""
from __future__ import annotations

import argparse,json,math,tempfile
from collections import Counter,defaultdict
from pathlib import Path

from source_preflight import download_and_pin,haversine_m
from source_gate_2012 import get_ameland_original
from ameland_external_site import original_gps
from source_original_gps_ahn2_overlap import (
    SITES,YEARS,K_TILES,PATCH_PIXELS,
    source_hourly,freeze_training_cells,original_ahn2_layer,
    source_tile,source_triples,source_destination_support,rd_tile_at)

# All source gate conditions fixed before opening B+C source counts.
MIN_BOTH=500
MIN_BOTH_TIDAL_BAND=300
MIN_BIRDS=3
MIN_WEEKS=4
MIN_CELLS=2

def exact_source_triples_both(hourly_by_bird):
    """Return GPS A->B->C candidate metadata, B/C position in memory only.

    No RWS gauge source or tide-derived cohort exclusion.
    """
    outcome=[];excluded=Counter()
    for bird,fixes in hourly_by_bird.items():
        for a,b,c in zip(fixes,fixes[1:],fixes[2:]):
            dt1=(b[0]-a[0]).total_seconds()
            dt2=(c[0]-b[0]).total_seconds()
            if not (1800<=dt1<=7200 and 1800<=dt2<=7200):
                excluded["source_time_gap"]+=1;continue
            kmh1=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))*3.6/dt1
            kmh2=haversine_m((None,b[1],b[2]),(None,c[1],c[2]))*3.6/dt2
            if not(.4<=kmh1<=120 and .4<=kmh2<=120):
                excluded["source_stationary_or_outlier"]+=1;continue
            outcome.append({
                "bird":bird,"time":c[0],
                "lat":c[1],"lon":c[2],
                "B_lat":b[1],"B_lon":b[2],"B_time":b[0]})
    return outcome,dict(excluded)

def height_from_original_tile(latitude,longitude,selected,tiles):
    cell,(east,north)=rd_tile_at(latitude,longitude)
    if cell not in selected:return {"status":"OUTSIDE_ORIGINAL_2010_SELECTED_TILES","cell":cell}
    raster=tiles.get(cell)
    if not raster or "height" not in raster:
        return {"status":"NO_SOURCE_VALID_RASTER_TILE","cell":cell}
    col,row=(~raster["transform"])*(east,north)
    col,row=int(math.floor(col)),int(math.floor(row))
    if not(0<=col<PATCH_PIXELS and 0<=row<PATCH_PIXELS):
        return {"status":"OUTSIDE_ORIGINAL_RASTER_BOUNDS","cell":cell}
    z=float(raster["height"][row,col])
    if not math.isfinite(z):
        return {"status":"SOURCE_DTM_MASKED_OR_NODATA","cell":cell}
    return {"status":"ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE","cell":cell,"z":z}

def both_endpoint_support(triples,tiles,chosen_cells):
    selected=set(chosen_cells)
    count=Counter();birds=set();weeks=set();days=set();cells=set()
    tide_birds=set();tide_weeks=set();tide_cells=set()
    for r in triples:
        start=height_from_original_tile(r["B_lat"],r["B_lon"],selected,tiles)
        end=height_from_original_tile(r["lat"],r["lon"],selected,tiles)
        if start["status"]=="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE":
            count["B_original_source_valid_height"]+=1
        if end["status"]=="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE":
            count["C_original_source_valid_height"]+=1
        if start["status"]!="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE" or end["status"]!="ORIGINAL_AHN2_NAP_HEIGHT_CANDIDATE":
            continue
        count["B_C_both_original_source_valid_heights"]+=1
        birds.add(r["bird"]);weeks.add(r["time"].isocalendar()[:2])
        days.add(r["time"].date())
        cells.add(start["cell"]);cells.add(end["cell"])
        if all(-3<=v["z"]<=3 for v in (start,end)):
            count["B_C_both_in_broad_minus3_plus3_NAP"]+=1
            tide_birds.add(r["bird"]);tide_weeks.add(r["time"].isocalendar()[:2])
            tide_cells.add(start["cell"]);tide_cells.add(end["cell"])
    feasible=(count["B_C_both_original_source_valid_heights"]>=MIN_BOTH and
              len(birds)>=MIN_BIRDS and len(weeks)>=MIN_WEEKS and
              len(cells)>=MIN_CELLS)
    tide_feasible=(count["B_C_both_in_broad_minus3_plus3_NAP"]>=MIN_BOTH_TIDAL_BAND and
                   len(tide_birds)>=MIN_BIRDS and len(tide_weeks)>=MIN_WEEKS and
                   len(tide_cells)>=MIN_CELLS)
    return {
        "source_status":"B_C_SOURCE_FEASIBLE_FOR_PREREGISTERING_FRONT_TEST" if feasible and tide_feasible
                        else "NOT_ADMITTED_INSUFFICIENT_DUAL_END_DTM",
        "original_gps_movement_triples":len(triples),
        "n_B_source_valid":count["B_original_source_valid_height"],
        "n_C_source_valid":count["C_original_source_valid_height"],
        "n_B_C_source_valid":count["B_C_both_original_source_valid_heights"],
        "n_B_C_broad_NAP_minus3_plus3":count["B_C_both_in_broad_minus3_plus3_NAP"],
        "n_eligible_B_C_source_birds":len(birds),
        "n_eligible_B_C_source_ISO_weeks":len(weeks),
        "n_eligible_B_C_source_calendar_days":len(days),
        "n_B_C_contributing_selected_source_cells":len(cells),
        "broad_tide_band_B_C_birds":len(tide_birds),
        "broad_tide_band_B_C_weeks":len(tide_weeks),
        "broad_tide_band_B_C_cells":len(tide_cells),
        "B_C_geometry_gate_passed":feasible,
        "B_C_broad_tide_band_gate_passed":tide_feasible,
        "source_tide_gauge_join":False,
        "actual_exposure_or_prey_effect":"NOT_ESTIMATED"}

def run(site,output):
    if site not in SITES:raise ValueError("Unknown site")
    root={"analysis":"V47_HISTORICAL_AHN2_BOTH_GPS_ENDPOINT_SOURCE_ONLY",
          "site":site,
          "source":"Original_Zenodo_GPS_MD5_AHN2_WCS_RD_NAP",
          "GPS_tide_or_prey_effect":"NOT_ESTIMATED"}
    with tempfile.TemporaryDirectory(prefix="boids_v47_ahn2_") as temp:
        tracks={};gpsreceipts={}
        for year in YEARS:
            path=Path(temp)/f"{site}_{year}_orig.gz"
            original=(download_and_pin(year,path) if site=="schiermonnikoog"
                      else get_ameland_original(path) if year==2012
                      else original_gps(year,path))
            track,audit=source_hourly(path,site,year)
            tracks[year]=track
            gpsreceipts[str(year)]={
                "source_gps_MD5_valid":original.get("provider_md5_match",
                                               original.get("provider_original_md5_matched")),
                "original_gps_sha256":original["original_sha256"],
                "source_admission":audit}
            path.unlink(missing_ok=True)
        chosen,metadata=freeze_training_cells(tracks[2010])
        identifier,fmt=original_ahn2_layer()
        tiles={};patch_audit=[]
        for i,cell in enumerate(chosen):
            try:
                patch=source_tile(cell,identifier,fmt)
                tiles[cell]=patch
                patch_audit.append({
                    "2010_training_cell_rank":i+1,
                    "source_status":"AHN2_PATCH_READ",
                    "original_source_raster_sha256":patch["original_source_patch_SHA256"],
                    "valid_candidate_pixels":patch["valid_NAP_candidate_pixels"],
                    "candidate_minus3_plus3_NAP_pixels":patch["candidate_minus3_plus3_NAP_pixels"]})
            except Exception as e:
                tiles[cell]=None
                patch_audit.append({
                    "2010_training_cell_rank":i+1,
                    "source_status":"SOURCE_STOP",
                    "reason":(type(e).__name__+"_"+str(e).splitlines()[0])[:140]})
        outcome={}
        for year in (2011,2012):
            source_C,ce=source_triples(tracks[year])
            source_BC,be=exact_source_triples_both(tracks[year])
            if len(source_BC)!=len(source_C) or be!=ce:
                raise ValueError("SOURCE_STOP_ORIGINAL_THREE_FIX_COHORT_NOT_REPLAYED")
            # Independent original v46 C-only support calculation on same tiles.
            replay=source_destination_support(source_C,tiles,chosen)
            audit=both_endpoint_support(source_BC,tiles,chosen)
            if replay["n_original_C_with_valid_AHN2_height"]!=audit["n_C_source_valid"]:
                raise ValueError("SOURCE_STOP_V46_C_ONLY_GPS_AHN2_REPLAY_MISMATCH")
            audit["replay_v46_C_only_count_verified"]=True
            audit["v46_source_C_original_valid_count"]=replay["n_original_C_with_valid_AHN2_height"]
            audit["v46_source_C_original_total_candidate_count"]=replay["original_GPS_three_fix_destination_candidates"]
            outcome[str(year)]=audit
        root["original_gps_source_check_receipts"]=gpsreceipts
        root["original_2010_only_training_tile_ranks"]=metadata
        root["original_AHN2_WCS_tile_receipts"]=patch_audit
        root["test_year_original_B_C_source_coverage"]=outcome
        root["source_status"]="SOURCE_GEOMETRY_AUDIT_COMPLETE_WITH_NO_TIDE_JOIN"
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(root,indent=2,sort_keys=True)+"\n")
    return root

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.site,a.output),sort_keys=True))
