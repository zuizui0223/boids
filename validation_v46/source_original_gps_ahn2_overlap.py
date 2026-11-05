"""v46 source-only original 2010 GPS hotspot -> AHN2 historical NAP height coverage.

No tide gauges, tidal phase, prey, exposed-waterline or bird selection effect
is opened. Select 8 2km RD source cells solely on 2010 source GPS bird-days,
then report 2011 and 2012 raw original next-position terrain coverage.
"""
from __future__ import annotations

import argparse,csv,gzip,hashlib,json,math,tempfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from pyproj import Transformer
from rasterio.io import MemoryFile

from source_preflight import parse_stamp,haversine_m,download_and_pin
from source_gate_2012 import REGIONS,get_ameland_original
from ameland_external_site import original_gps
from ahn2_original_dtm_source_gate import (
    OFFICIAL_DTM_WCS,OFFICIAL_AHN_DATAROOM,bounded_get,
    parse_wcs_caps,parse_coverage_description,SourceStop)
    
SITES=("schiermonnikoog","ameland")
YEARS=(2010,2011,2012)
CELL_M=2000
PATCH_PIXELS=256
K_TILES=8
MIN_VALID_C=500
MIN_VALID_BIRDS=3
MIN_VALID_WEEKS=4
MIN_VALID_CELLS=2
MAX_SOURCE_GEOTIFF_BYTES=3_000_000
SOURCE_REQUIRED={"event-id","timestamp","location-lat","location-long",
                 "individual-local-identifier","visible"}

PROJ=Transformer.from_crs("EPSG:4326","EPSG:28992",always_xy=True)

def source_hourly(original_gz,site,year):
    if site not in SITES or year not in YEARS:
        raise ValueError("Unfrozen site or original GPS year")
    bounds=REGIONS[site]
    bybird=defaultdict(dict);seen=set();read=0;drop=Counter()
    with gzip.open(original_gz,"rt",newline="",encoding="utf-8-sig") as stream:
        reader=csv.DictReader(stream)
        if not SOURCE_REQUIRED<=set(reader.fieldnames or ()):
            raise ValueError("Original Movebank source schema missing")
        for row in reader:
            read+=1
            eid=(row.get("event-id") or "").strip()
            if not eid or eid in seen:
                drop["duplicate_event_id"]+=1;continue
            seen.add(eid)
            if row.get("visible","").strip().upper() in ("FALSE","0"):
                drop["not_visible"]+=1;continue
            bird=(row.get("individual-local-identifier") or "").strip()
            if not bird:
                drop["missing_source_bird"]+=1;continue
            try:
                stamp=parse_stamp(row["timestamp"])
                lat=float(row["location-lat"]);lon=float(row["location-long"])
            except (ValueError,TypeError):
                drop["original_time_or_position_unreadable"]+=1;continue
            if stamp.year!=year or not all(map(math.isfinite,(lat,lon))) or not (
                bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]):
                drop["out_of_original_site_year"]+=1;continue
            h=stamp.replace(minute=0,second=0,microsecond=0)
            earlier=bybird[bird].get(h)
            if earlier is None or stamp<earlier[0]:
                bybird[bird][h]=(stamp,lat,lon)
    selected={bird:sorted(d.values()) for bird,d in bybird.items()}
    return selected,{"original_raw_source_fixes":read,
                      "original_hourly_selected_fixes":sum(map(len,selected.values())),
                      "original_source_individuals_in_area":len(selected),
                      "original_source_discard_reasons":dict(drop),
                      "gps_native_clock_status":"UTC_OR_GPS_TIME_UNVERIFIED"}

def rd_tile_at(lat,lon):
    x,y=PROJ.transform(lon,lat)
    return (math.floor(x/CELL_M), math.floor(y/CELL_M)),(x,y)

def freeze_training_cells(only_2010_fixes,k=K_TILES):
    if k!=K_TILES:raise ValueError("Original tile count is frozen to eight")
    unique_days=defaultdict(set)
    counts=Counter()
    for bird,fixes in only_2010_fixes.items():
        for stamp,lat,lon in fixes:
            cell,_=rd_tile_at(lat,lon)
            unique_days[cell].add((bird,stamp.date()))
            counts[cell]+=1
    ranked=sorted(counts,
                  key=lambda cell:(-len(unique_days[cell]),-counts[cell],cell))
    if len(ranked)<k:
        raise SourceStop("SOURCE_STOP_TRAINING_GPS_OCCUPIES_FEWER_THAN_8_RD_CELLS")
    chosen=ranked[:k]
    metadata=[{"rank":j+1,
               "source_training_bird_days":len(unique_days[cell]),
               "source_training_hourly_fixes":counts[cell]}
              for j,cell in enumerate(chosen)]
    return chosen,metadata

def source_triples(hourly_fixes):
    """Only original geometric eligibility; NO tide or next-heading effect."""
    triples=[];excluded=Counter()
    for bird,fixes in hourly_fixes.items():
        for a,b,c in zip(fixes,fixes[1:],fixes[2:]):
            dt1=(b[0]-a[0]).total_seconds()
            dt2=(c[0]-b[0]).total_seconds()
            if not(1800<=dt1<=7200 and 1800<=dt2<=7200):
                excluded["source_time_gap"]+=1;continue
            d1=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))*3.6/dt1
            d2=haversine_m((None,b[1],b[2]),(None,c[1],c[2]))*3.6/dt2
            if not (.4<=d1<=120 and .4<=d2<=120):
                excluded["source_stationary_or_outlier"]+=1;continue
            # Original destination coordinates stay local; only counts output.
            triples.append({"bird":bird,"time":c[0],"lat":c[1],"lon":c[2]})
    return triples,dict(excluded)

def original_ahn2_layer():
    raw,_=bounded_get(OFFICIAL_DTM_WCS,
        {"service":"WCS","request":"GetCapabilities","version":"1.0.0",
         "requestedEpsg":"28992"},2_000_000)
    caps=parse_wcs_caps(raw)
    identifier=caps["chosen_original_DTM_coverage"]
    desc_raw,_=bounded_get(OFFICIAL_DTM_WCS,
        {"service":"WCS","request":"DescribeCoverage","version":"1.0.0",
         "coverage":identifier,"requestedEpsg":"28992"},2_000_000)
    details=parse_coverage_description(desc_raw,identifier)
    return identifier,details["requested_format"]

def source_tile(cell,identifier,wcs_format):
    east,north=cell[0]*CELL_M,cell[1]*CELL_M
    bbox=",".join(f"{v:.3f}" for v in
                  (east,north,east+CELL_M,north+CELL_M))
    raw,content_type=bounded_get(OFFICIAL_DTM_WCS,
        {"service":"WCS","request":"GetCoverage","version":"1.0.0",
         "coverage":identifier,"crs":"EPSG:28992",
         "response_crs":"EPSG:28992",
         "bbox":bbox,"width":str(PATCH_PIXELS),
         "height":str(PATCH_PIXELS),
         "format":wcs_format,"requestedEpsg":"28992"},
        MAX_SOURCE_GEOTIFF_BYTES)
    if not(raw.startswith(b"II*\x00") or raw.startswith(b"MM\x00*")):
        raise SourceStop("SOURCE_STOP_NOT_ORIGINAL_GEO_TIFF")
    with MemoryFile(raw) as mem:
        with mem.open() as ds:
            if ds.count not in (1,2) or ds.crs is None or ds.crs.to_epsg()!=28992:
                raise SourceStop("SOURCE_STOP_AHN2_RASTER_WRONG_CRS_OR_BANDS")
            if ds.width!=PATCH_PIXELS or ds.height!=PATCH_PIXELS:
                raise SourceStop("SOURCE_STOP_AHN2_RASTER_UNEXPECTED_DIMENSIONS")
            bounds=ds.bounds
            if not(east<=bounds.left+50 and east+CELL_M>=bounds.right-50 and
                   north<=bounds.bottom+50 and north+CELL_M>=bounds.top-50):
                raise SourceStop("SOURCE_STOP_AHN2_RASTER_TILE_GEOMETRY_MISMATCH")
            surface=np.asarray(ds.read(1,masked=True).filled(np.nan),dtype=float)
            valid=np.isfinite(surface)&(surface>=-20)&(surface<=50)
            if ds.count==2:
                aux=np.asarray(ds.read(2,masked=True).filled(np.nan),dtype=float)
                known=np.isfinite(aux)
                if known.any() and (np.any(aux[known]<-1e-6) or
                                    np.any(aux[known]>1.000001)):
                    raise SourceStop("SOURCE_STOP_AHN2_AUXILIARY_NOT_NORMALIZED")
                valid &= known&(aux>=.999)
            heights=np.where(valid,surface,np.nan)
            return {"height":heights,"transform":ds.transform,
                    "original_source_patch_SHA256":hashlib.sha256(raw).hexdigest(),
                    "valid_NAP_candidate_pixels":int(valid.sum()),
                    "candidate_minus3_plus3_NAP_pixels":
                        int(np.sum(valid&(surface>=-3)&(surface<=3))),
                    "original_provider_band_count":ds.count,
                    "source_CRS_epsg":28992,
                    "horizontal_cell_metres":CELL_M/PATCH_PIXELS,
                    "auxiliary_band_semantics_unverified":ds.count==2}

def source_destination_support(triples,tiles,chosen_cells):
    target=Counter();birds=set();weeks=set();days=set();eligible_cells=set()
    source_cells=set(chosen_cells)
    for point in triples:
        cell,(e,n)=rd_tile_at(point["lat"],point["lon"])
        if cell not in source_cells:continue
        target["original_C_in_2010_selected_cells"]+=1
        raster=tiles.get(cell)
        if raster is None or "height" not in raster:continue
        inv=~raster["transform"]
        col,row=inv*(e,n)
        row=int(math.floor(row));col=int(math.floor(col))
        if not(0<=row<PATCH_PIXELS and 0<=col<PATCH_PIXELS):
            continue
        h=float(raster["height"][row,col])
        if not math.isfinite(h):continue
        target["original_C_at_source_valid_NAP_height"]+=1
        if -3<=h<=3:
            target["original_C_at_tide_plausible_minus3_plus3_NAP"]+=1
        birds.add(point["bird"])
        weeks.add(point["time"].isocalendar()[:2])
        days.add(point["time"].date())
        eligible_cells.add(cell)
    admitted=(target["original_C_at_source_valid_NAP_height"]>=MIN_VALID_C and
              len(birds)>=MIN_VALID_BIRDS and len(weeks)>=MIN_VALID_WEEKS and
              len(eligible_cells)>=MIN_VALID_CELLS)
    return {"source_status":"SAMPLE_SUPPORT_FEASIBLE_ONLY" if admitted else
                         "NOT_ADMITTED_INSUFFICIENT_HISTORICAL_DTM_OVERLAP",
            "original_GPS_three_fix_destination_candidates":len(triples),
            "n_C_in_fixed_2010_selected_2km_cells":
                target["original_C_in_2010_selected_cells"],
            "n_original_C_with_valid_AHN2_height":
                target["original_C_at_source_valid_NAP_height"],
            "n_original_C_in_broad_minus3_plus3_NAP":
                target["original_C_at_tide_plausible_minus3_plus3_NAP"],
            "n_test_birds_with_valid_C_height":len(birds),
            "n_test_ISO_weeks_with_valid_C_height":len(weeks),
            "n_test_calendar_days_with_valid_C_height":len(days),
            "n_distinct_2010_selected_cells_with_valid_C":len(eligible_cells),
            "no_original_RWS_tide_join_or_phase_estimated":True,
            "real_front_or_prey_mechanism":"NOT_ESTIMATED"}

def run(site,output):
    if site not in SITES:raise ValueError("Unregistered site")
    root={"analysis":"V46_AHN2_ORIGINAL_GPS_DESTINATION_COVERAGE_SOURCE_ONLY",
          "site":site,"source_period":"AHN2_2007_2012",
          "provider":OFFICIAL_AHN_DATAROOM,
          "original_bird_tide_association":"NOT_ESTIMATED",
          "original_animal_locations_persisted":False}
    with tempfile.TemporaryDirectory(prefix="v46_ahn2_original_") as folder:
        tracks={};receipts={}
        for year in YEARS:
            path=Path(folder)/f"{site}_{year}_original.gz"
            original=(download_and_pin(year,path) if site=="schiermonnikoog"
                      else get_ameland_original(path) if year==2012
                      else original_gps(year,path))
            track,audit=source_hourly(path,site,year)
            tracks[year]=track
            receipts[str(year)]={
                "original_provider_MD5_verified":original.get(
                    "provider_md5_match",original.get("provider_original_md5_matched")),
                "original_source_SHA256":original["original_sha256"],
                "original_GPS_source_quality":audit}
            path.unlink(missing_ok=True)
        chosen,ranking=freeze_training_cells(tracks[2010])
        original_id,original_format=original_ahn2_layer()
        patches={};patch_recs=[]
        for rank,cell in enumerate(chosen):
            try:
                patch=source_tile(cell,original_id,original_format)
                patches[cell]=patch
                patch_recs.append({"source_training_rank":rank+1,
                                   "status":"SOURCE_PATCH_READ",
                                   "original_patch_SHA256":patch["original_source_patch_SHA256"],
                                   "valid_source_NAP_candidate_pixels":patch["valid_NAP_candidate_pixels"],
                                   "tide_band_pixels":patch["candidate_minus3_plus3_NAP_pixels"],
                                   "sample_pixel_width_metres":patch["horizontal_cell_metres"],
                                   "unverified_auxiliary":patch["auxiliary_band_semantics_unverified"]})
            except Exception as exc:
                patches[cell]=None
                patch_recs.append({"source_training_rank":rank+1,
                                   "status":"SOURCE_PATCH_STOP",
                                   "reason":(type(exc).__name__+"_"+str(exc).splitlines()[0])[:120]})
        if not any(p is not None and p["valid_NAP_candidate_pixels"]>0
                   for p in patches.values()):
            root["source_status"]="SOURCE_STOP_NO_SOURCE_VALID_AHN2_TILE"
        else:root["source_status"]="SOURCE_HEIGHT_COVERAGE_AUDIT_COMPLETED"
        root["original_provider_MD5_source_receipts"]=receipts
        root["training_only_2010_top_eight_source_cell_ranks"]=ranking
        root["source_AHN2_top_eight_tile_quality"]=patch_recs
        root["source_2010_selected_tile_count"]=len(chosen)
        source_scores={}
        for year in (2011,2012):
            triples,exclusions=source_triples(tracks[year])
            comparison=source_destination_support(triples,patches,chosen)
            comparison["original_movement_geometry_source_exclusions"]=exclusions
            source_scores[str(year)]=comparison
        root["heldout_year_source_destination_overlap"]=source_scores
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(root,indent=2,sort_keys=True)+"\n")
    return root

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.site,args.output),sort_keys=True))
