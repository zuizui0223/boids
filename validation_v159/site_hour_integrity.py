"""v159 exact original harbour porpoise C-POD site/region/hour integrity audit.

Uses v158 Europe PMC ORIGINAL CSV member with individual original content
SHA256 972b43b..., NOT the nonreproducible outer ZIP wrapper checksum.

The original CSV contains only click-positive hours as shown by v158. This
source gate cannot establish full recorder on-effort opportunity or absence
of foraging when no click records exist. In particular, unlisted hours MUST
NEVER be encoded as click=0 or no porpoise.

No new fitted ecological effect, p-value, tidally calibrated exposure or
individual animal inference. Raw animal event and exact timestamp rows are
NOT committed; all output is an aggregate source audit.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"validation_v158"))
from porpoise_source_gate import acquire

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"validation_v159/results/original_multiregion_hour_integrity_v159.json"
ORIGINAL_SHA="972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf"
ALL_ROWS=126231
COLS=32
FIELDS=("SITE","GROUP","COUNTRY","year","YDAY","hr","clicks","buzz",
        "regular","foraging_click","buzprop","DPM","DDDN","hr_day_year_SITE")
YEAR_RANGE=(2009,2023)
VALID_NUMBER_EXCEPTIONS=("NA","NaN","nan","","Inf","-Inf")

def as_int(s):
    try:
        x=float(s)
        if not math.isfinite(x) or abs(x-round(x))>1e-7:
            return None
        return int(round(x))
    except (ValueError,TypeError):
        return None

def as_float(s):
    try:
        v=float(s)
        return v if math.isfinite(v) else None
    except (ValueError,TypeError):
        return None

def iso_weekday_source_ordinal(year,daynum,hour):
    """Reject impossible 366 in non-leap year instead of rolling into next year."""
    if year is None or daynum is None or hour is None:
        return None
    if not YEAR_RANGE[0]<=year<=YEAR_RANGE[1] or not 0<=hour<24 or not 1<=daynum<=366:
        return None
    try:
        day=datetime(year,1,1)+timedelta(days=daynum-1)
        if day.year!=year:return None
        return day.toordinal()*24+hour
    except (ValueError,OverflowError):
        return None

def audit():
    raw,meta=acquire()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA or len(raw)!=26454371:
        raise AssertionError("Genuine original member CSV content SHA/size changed")
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text,newline=""))
    if len(reader.fieldnames or [])!=COLS or any(k not in reader.fieldnames for k in FIELDS):
        raise AssertionError("32-column original source schema changed")
    sites=defaultdict(lambda:{
        "n_rows":0,"n_buzz_positive_rows":0,"n_buzz_zero_rows":0,
        "sum_clicks":0,"sum_buzz":0,"sum_regular":0,"hour_keys":[],
        "years":Counter(),"group":Counter(),"country":Counter(),
        "n_local_period_dark":Counter(),"valid_buzz_fraction_rows":0,
        "n_buzprop_matches_buzz_div_clicks_1e3":0,
        "n_foraging_click_positive":0
    })
    region=defaultdict(lambda:{"n_rows":0,"n_buzz_positive_rows":0,
        "n_buzz_zero_rows":0,"n_clicks":0,"n_buzz":0,"years":Counter(),
        "sites":set(),"n_dark_period_labels":Counter()})
    all_rows=0
    validation=Counter()
    unique_composite=set()
    duplicate_sitehour=0
    source_ids=set()
    duplicate_original_composite_ids=0
    per_site_year=Counter()
    for row in reader:
        all_rows+=1
        if all_rows>500000:
            raise AssertionError("Source unexpected row expansion")
        site=(row["SITE"] or "").strip()
        group=(row["GROUP"] or "").strip()
        country=(row["COUNTRY"] or "").strip()
        y=as_int(row["year"]);d=as_int(row["YDAY"]);h=as_int(row["hr"])
        timekey=iso_weekday_source_ordinal(y,d,h)
        clicks=as_int(row["clicks"]);buzz=as_int(row["buzz"])
        regular=as_int(row["regular"])
        foraging=as_float(row["foraging_click"])
        buzzratio=as_float(row["buzprop"])
        label=(row["DDDN"] or "").strip()
        if not site or not group or not country:
            validation["missing_site_group_or_country"]+=1
            continue
        s=sites[site];g=region[group]
        s["n_rows"]+=1;g["n_rows"]+=1
        s["group"][group]+=1;s["country"][country]+=1
        g["sites"].add(site)
        s["n_local_period_dark"][label]+=1
        g["n_dark_period_labels"][label]+=1
        if timekey is None:validation["invalid_site_year_day_hour"]+=1
        else:
            identity=(site,timekey)
            if identity in unique_composite:duplicate_sitehour+=1
            unique_composite.add(identity)
            s["hour_keys"].append(timekey)
            s["years"][y]+=1;g["years"][y]+=1
            per_site_year[(site,y)]+=1
        uid=(row["hr_day_year_SITE"] or "").strip()
        if not uid:validation["missing_original_hour_site_key"]+=1
        if uid in source_ids:duplicate_original_composite_ids+=1
        source_ids.add(uid)
        if clicks is None or clicks<0:
            validation["invalid_click_count"]+=1
            continue
        if clicks==0:validation["zero_click_rows"]+=1
        s["sum_clicks"]+=clicks;g["n_clicks"]+=clicks
        if buzz is None or buzz<0:validation["invalid_buzz_count"]+=1
        else:
            s["sum_buzz"]+=buzz;g["n_buzz"]+=buzz
            if buzz>0:s["n_buzz_positive_rows"]+=1;g["n_buzz_positive_rows"]+=1
            else:s["n_buzz_zero_rows"]+=1;g["n_buzz_zero_rows"]+=1
            if buzz>clicks:validation["buzz_greater_than_all_clicks_rows"]+=1
        if regular is None or regular<0:validation["invalid_regular_count"]+=1
        else:
            s["sum_regular"]+=regular
            if buzz is not None and regular+buzz>clicks:
                validation["regular_plus_buzz_greater_than_clicks_rows"]+=1
        if foraging is not None and foraging>0:s["n_foraging_click_positive"]+=1
        if buzzratio is not None and clicks>0 and buzz is not None:
            s["valid_buzz_fraction_rows"]+=1
            if abs(buzzratio-buzz/clicks)<=1e-3:
                s["n_buzprop_matches_buzz_div_clicks_1e3"]+=1
        if buzzratio is not None and (buzzratio<0 or buzzratio>1):
            validation["original_buzprop_outside_unit_interval"]+=1
        if all_rows%30000==0:
            print("V159_PARSE_PROGRESS="+str(all_rows),flush=True)
    if all_rows!=ALL_ROWS or len(unique_composite)<1000:
        raise AssertionError("Original 126231 source rows or time keys not reconstructed")
    site_rows=[]
    total_true_consecutive=0
    for site,z in sorted(sites.items()):
        unique=sorted(set(z["hour_keys"]))
        # Only consecutive click-positive source records are paired; a gap is
        # unknown recorder effort, not a zero-click/zero-buzz observation.
        gap=Counter()
        for a,b in zip(unique,unique[1:]):
            dh=b-a
            if dh<=0:raise AssertionError("Unsorted source time keys")
            if dh==1: gap["adjacent_1h"]+=1
            elif dh<=6:gap["gap_2_to_6h"]+=1
            elif dh<=24:gap["gap_7_to_24h"]+=1
            else:gap["gap_above_24h"]+=1
        total_true_consecutive+=gap["adjacent_1h"]
        unique_years=sorted(z["years"])
        site_rows.append({
            "site":site,"country_names":sorted(z["country"]),
            "source_group_names":sorted(z["group"]),
            "original_positive_click_hour_rows":z["n_rows"],
            "unique_calendar_site_hours":len(unique),
            "duplicate_sitehour_rows":z["n_rows"]-len(unique),
            "years_present":unique_years,
            "per_year_click_positive_rows":dict(sorted(z["years"].items())),
            "buzz_positive_rows":z["n_buzz_positive_rows"],
            "buzz_zero_rows":z["n_buzz_zero_rows"],
            "total_original_clicks":z["sum_clicks"],
            "total_original_buzz_clicks":z["sum_buzz"],
            "original_buzz_per_detected_click":round(z["sum_buzz"]/z["sum_clicks"],8) if z["sum_clicks"] else None,
            "original_buzz_positive_fraction_of_clickpositive_hours":round(z["n_buzz_positive_rows"]/z["n_rows"],8) if z["n_rows"] else None,
            "source_buzprop_matches_buzz_over_clicks_rows":z["n_buzprop_matches_buzz_div_clicks_1e3"],
            "source_buzprop_comparable_rows":z["valid_buzz_fraction_rows"],
            "click_positive_hour_adjacency":dict(gap),
            "original_DDDN_categories":dict(sorted(z["n_local_period_dark"].items())),
            "on_effort_silent_hours":"NOT_AVAILABLE",
        })
    group_rows=[]
    for name,g in sorted(region.items()):
        group_rows.append({
            "source_GROUP":name,"n_source_SITE_ids":len(g["sites"]),
            "source_clickpositive_rows":g["n_rows"],
            "source_clickpositive_buzz_hours":g["n_buzz_positive_rows"],
            "source_clickpositive_no_buzz_hours":g["n_buzz_zero_rows"],
            "source_years":sorted(g["years"]),
            "source_n_clicks":g["n_clicks"],
            "source_n_buzz":g["n_buzz"],
            "buzz_click_fraction_given_detected_click":round(g["n_buzz"]/g["n_clicks"],8) if g["n_clicks"] else None,
            "buzz_presence_rate_among_clickpositive_hours":round(g["n_buzz_positive_rows"]/g["n_rows"],8) if g["n_rows"] else None,
            "original_DDDN_labels":dict(sorted(g["n_dark_period_labels"].items())),
            "site_IDs":sorted(g["sites"]),
        })
    if sum(x["source_clickpositive_rows"] for x in group_rows)!=ALL_ROWS or sum(x["original_positive_click_hour_rows"] for x in site_rows)!=ALL_ROWS:
        raise AssertionError("Rows not recovered across site and region")
    if sum(x["source_clickpositive_buzz_hours"] for x in group_rows)!=sum(x["buzz_positive_rows"] for x in site_rows):
        raise AssertionError("Buzz-positive row sums across regions/sites differ")
    return {
        "version":"v159_harbour_porpoise_original_6group_sitehour_integrity_1",
        "DOI":"10.1002/ece3.72566",
        "original_DataS2_member_CSV_SHA256":ORIGINAL_SHA,
        "original_CSV_rows":all_rows,"original_CSV_columns":COLS,
        "real_rows_with_invalid_composite_time":validation["invalid_site_year_day_hour"],
        "real_rows_with_duplicate_sitehour":duplicate_sitehour,
        "real_rows_with_duplicate_original_hr_day_year_SITE":duplicate_original_composite_ids,
        "unique_source_SITE_ids":len(site_rows),
        "unique_source_GROUP_labels":len(group_rows),
        "unique_SOURCE_COUNTRY_labels":len({c for x in site_rows for c in x["country_names"]}),
        "sites_with_multiple_groups":sum(len(x["source_group_names"])>1 for x in site_rows),
        "all_years_in_records":sorted({y for r in site_rows for y in r["years_present"]}),
        "clickpositive_observed_hour_rows":all_rows-validation["zero_click_rows"]-validation["invalid_click_count"],
        "zero_click_observed_rows":validation["zero_click_rows"],
        "buzz_zero_among_all_source_rows":sum(r["buzz_zero_rows"] for r in group_rows),
        "buzz_positive_among_all_source_rows":sum(r["buzz_positive_rows"] for r in group_rows),
        "genuine_previous_clickpositive_hour_pairs_not_verified_Cpod_effort":total_true_consecutive,
        "source_validation_warnings":dict(sorted(validation.items())),
        "region_rows":group_rows,
        "site_rows":site_rows,
        "reference_paper_43_sites_6_regions_not_assumed_to_equal_source":True,
        "calendar_hour_timezone":"UNKNOWN_FROM_SOURCE_SCHEMA",
        "true_on_effort_Cpod_click_negative_hours":"NOT_PRESENT_IN_CSV",
        "sample_unit":"click-positive hour conditional on at least one detected click; NOT all C-POD on-effort hours",
        "no_animal_occurrence_rate_or_population_inference":True,
        "no_original_event_rows_or_exact_timestamps_redistributed":True,
        "no_new_ecological_effect_fitted":True,
        "local_tide_current_or_waterlevel":"NOT_MATCHED",
        "global_tide_solar_effect":"NOT_ESTIMATED",
        "identified_social_Boids_interaction":"NOT_IDENTIFIED",
    }

def main():
    parser=argparse.ArgumentParser()
    x=parser.add_mutually_exclusive_group(required=True)
    x.add_argument("--emit",action="store_true")
    x.add_argument("--check",action="store_true")
    args=parser.parse_args()
    res=audit()
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if not RESULT.exists():
            raise AssertionError("Source v159 original receipt absent")
        frozen=json.loads(RESULT.read_text())
        if frozen!=json.loads(json.dumps(res,sort_keys=True)):
            raise AssertionError("Source v159 original CSV SHA/site/hour/buzz summary changed")
        print("V159_ORIGINAL_126231_SOURCE_ROW_INTEGRITY_PASS")
    else:
        RESULT.write_text(json.dumps(res,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V159_ORIGINAL_SOURCE_RESULT_START")
        print(json.dumps(res,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V159_ORIGINAL_SOURCE_RESULT_END")
    print("V159_SCOPE="+json.dumps({k:res[k] for k in ("original_CSV_rows","unique_source_SITE_ids","unique_source_GROUP_labels","unique_SOURCE_COUNTRY_labels","real_rows_with_duplicate_sitehour","real_rows_with_invalid_composite_time","clickpositive_observed_hour_rows","buzz_zero_among_all_source_rows","genuine_previous_clickpositive_hour_pairs_not_verified_Cpod_effort")},sort_keys=True))

if __name__=="__main__":main()
