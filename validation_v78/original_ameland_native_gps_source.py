"""v78 genuinely different Ameland 2010 original wild GPS source vs Schier.

Historical external site, same shorebird species and Wadden NIOZ model provider.
The source-only Ameland hourly GPS/native 2010 NIOZ monthly geography is tested
BEFORE looking at bird-used model \`time_expo\` ranks or any 4-way outcome.
No 2011 NIOZ latitude recovery or invented available bird food habitat.
"""
from __future__ import annotations
import csv
import gzip
import math
from collections import Counter,defaultdict
from datetime import datetime
import numpy as np

from scipy.spatial import cKDTree
from source_preflight import parse_stamp
from ameland_external_site import BBOX
from wild_2010_modelled_tidal_exposure_rank import (
    MONTHS,_locxy,NATIVE_EXPECTED)

AMELAND_RAW_2010=119507
AMELAND_SHA_2010="c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c"
AMELAND_MD5_2010="71e0b66230b508873897c99464146167"
AMELAND_STATUS="SOURCE_ADMITTED_V78_AMELAND_2010_GPS_ORIGINAL_NIOZ_MONTH_1KM"
MIN_MONTH_FIXES=200
MIN_MONTH_BIRDS=5
NATIVE_GEO_MAX_M=300.
MIN_GEO_FRACTION=.8
NATIVE_REFERENCE_RADIUS_M=1000.
NATIVE_REFERENCE_MIN_CELLS=20
MIN_SOURCE_FIXES_PER_BIRD_MONTH=20
MIN_MONTH_BIRDS_WITH_BACKGROUND=5

def original_ameland_2010_hourly(path,*,expected=AMELAND_RAW_2010):
    """Native GPS source, earliest original visible fix in each bird-hour."""
    expected_cols={"event-id","timestamp","location-lat","location-long",
                   "individual-local-identifier","visible"}
    first=defaultdict(dict)
    seen=set();errors=Counter();raw=0
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        if not expected_cols<=set(reader.fieldnames or []):
            raise ValueError("SOURCE_STOP_V78_ORIGINAL_AMELAND_GPS_FIELD_LIST_CHANGED")
        for r in reader:
            raw+=1
            eid=(r.get("event-id") or "").strip()
            if not eid or eid in seen:
                errors["original_missing_or_duplicate_event_ID"]+=1
                continue
            seen.add(eid)
            if (r.get("visible") or "").strip().upper() in ("FALSE","0"):
                errors["native_invisible_original_fix"]+=1;continue
            bird=(r.get("individual-local-identifier") or "").strip()
            if not bird:
                errors["missing_original_native_animal"]+=1;continue
            try:
                stamp=parse_stamp(r["timestamp"])
                lat=float(r["location-lat"]);lon=float(r["location-long"])
            except (ValueError,TypeError):
                errors["original_bad_native_clock_or_coords"]+=1;continue
            if stamp.year!=2010 or not (math.isfinite(lat) and math.isfinite(lon)
                    and BBOX[0]<=lat<=BBOX[1] and BBOX[2]<=lon<=BBOX[3]):
                errors["outside_predeclared_2010_Ameland_region"]+=1;continue
            if stamp.month not in MONTHS:
                errors["outside_fixed_Aug_Dec_original_months"]+=1;continue
            hr=stamp.replace(minute=0,second=0,microsecond=0)
            old=first[bird].get(hr)
            if old is None or stamp<old[0]:
                first[bird][hr]=(stamp,lat,lon)
    if raw!=expected:
        raise ValueError("SOURCE_STOP_V78_AMELAND_119507_ORIGINAL_GPS_RAW_ROWS_CHANGED")
    month=defaultdict(list)
    for bird,fixes in first.items():
        for t,lat,lon in fixes.values():
            month[t.month].append((bird,t,lat,lon))
    public={
        "original_Ameland_year":2010,
        "original_provider_RAW_GPS_fixes":raw,
        "source_fixed_2010_Aug_to_Dec_hourly_bird_fixes":{},
        "original_QC_and_source_exclusions":dict(errors),
        "no_original_bird_tags_lat_lon_or_exact_times_written":True}
    for m in MONTHS:
        q=month[m]
        public["source_fixed_2010_Aug_to_Dec_hourly_bird_fixes"][str(m)]={
            "original_Ameland_native_hourly_locations":len(q),
            "original_distinct_birds":len({r[0] for r in q})}
    return month,public

def original_ameland_month_native_source_gate(month,fixes,native_model):
    """MUST not read original NIOZ used numerical model index in this step."""
    if month not in MONTHS:
        raise ValueError("SOURCE_STOP_V78_OUTSIDE_FIVE_ORIGINAL_NATIVE_MONTHS")
    if native_model["n_native"]!=NATIVE_EXPECTED:
        raise ValueError("SOURCE_STOP_V78_ORIGINAL_NIOZ_NATIVE_MAP_NOT_VALID")
    tree=native_model["tree"]
    pts=_locxy([r[2] for r in fixes],[r[3] for r in fixes])
    if len(fixes):
        nearest,index=tree.query(pts,k=1)
        allowed=nearest<=NATIVE_GEO_MAX_M
        neighbors=tree.query_ball_point(pts,r=NATIVE_REFERENCE_RADIUS_M)
        enough_nearby=np.asarray([
            len(z)>=NATIVE_REFERENCE_MIN_CELLS for z in neighbors],dtype=bool)
    else:
        nearest=np.asarray([])
        index=np.asarray([],dtype=int)
        allowed=np.asarray([],dtype=bool)
        neighbors=[]
        enough_nearby=np.asarray([],dtype=bool)
    valid=allowed & enough_nearby
    birds=Counter(fixes[i][0] for i in np.flatnonzero(valid))
    good_birds={bird for bird,n in birds.items()
                if n>=MIN_SOURCE_FIXES_PER_BIRD_MONTH}
    count=len(fixes);orig_birds=len({r[0] for r in fixes})
    qa={
        "original_Ameland_site":"O_AMELAND_2010",
        "original_calendar_month":month,
        "source_original_native_hourly_fixes":count,
        "source_original_distinct_birds":orig_birds,
        "genuine_original_NIOZ_native_model_cells":native_model["n_native"],
        "original_GPS_nearest_NIOZ_grid_within_300m":int(allowed.sum()),
        "original_GPS_geolocation_fraction_at_most_300m":
            float(allowed.mean()) if count else 0,
        "original_GPS_with_1km_native_model_background_20cells":int(valid.sum()),
        "original_birds_with_20plus_source_locations_and_1km_background":
            len(good_birds),
        "original_source_locations_in_supported_bird_months":
            sum(birds[b] for b in good_birds),
        "original_NIOZ_time_expo_used_location_values_not_read":True}
    good=(count>=MIN_MONTH_FIXES and orig_birds>=MIN_MONTH_BIRDS
          and allowed.mean()>=MIN_GEO_FRACTION
          and valid.sum()>=MIN_MONTH_FIXES
          and len(good_birds)>=MIN_MONTH_BIRDS_WITH_BACKGROUND)
    qa["fixed_source_admission"]=(
        AMELAND_STATUS if good
        else "NOT_ADMITTED_V78_ORIGINAL_AMELAND_MONTH_GPS_NATIVE_MODEL")
    return {
        "source_receipt":qa,
        "fixes":fixes,
        "valid":valid,"valid_birds":good_birds,
        "closest":index,
        "circles":neighbors,
        "model_expo":native_model["index"],
        "tree":tree,
        "xy":pts}
