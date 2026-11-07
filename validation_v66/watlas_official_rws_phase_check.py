"""v66: source-only external Dutch RWS gauge corroboration of WATLAS tide sign.

Frozen: docs/V66_FROZEN_WATLAS_INDEPENDENT_RWS_TIDE_SOURCE.md.
No observed bird B->C heading, social Boids force, model or ecological effect.
Raw tracking IDs, positions, UNIX timestamps and waterlevel series stay in memory.
"""
from __future__ import annotations
import csv
import io
import json
import math
import time
from bisect import bisect_left
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

from watlas_cross_taxon_tide_source import original_source,source_only_audit
from watlas_original_slope_source import (
    SOURCE_SHA,EXACT_RAW,EXACT_V64_MOVING_WITH_TIDE,
    _native_valid_bins,_gauge_reference,source_waterlevel_rate,
    audit_slope_source_only,_phase,
    MIN_GAP,MAX_GAP,MIN_SPEED,MAX_SPEED,
    MIN_TRIPLES,MIN_BIRDS,MIN_TIDES,MIN_PER_PHASE,
    MIN_TIDES_PER_PHASE,MIN_HOLDOUT_CYCLES,
    MIN_HOLDOUT_CYCLE_TRIPLES
)

RWS_URL=("https://ddapi20-waterwebservices.rijkswaterstaat.nl"
         "/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen")
RWS_STATION="terschelling.west"
RWS_BEGIN="2018-08-01T00:00:00.000+01:00"
RWS_END="2018-09-01T00:00:00.000+01:00"
RWS_EXPECTED=4465
BRACKET_TARGET_SECONDS=1800
BRACKET_TOL_SECONDS=300
VALIDATION_SHIFTS_MIN=(0,-30,30)
SOURCE_PAIRS_EXPECTED={"red_knot":(155,87,68,5,3),
                       "sanderling":(434,222,212,5,9)}
SHARE_REQUIRED=.95
AGREEMENT_REQUIRED=.80
MAX_OFFICIAL_BYTES=12_000_000

def request_body():
    return {"Locatie":{"Code":RWS_STATION},
            "AquoPlusWaarnemingMetadata":{
                "AquoMetadata":{"Compartiment":{"Code":"OW"},
                                "Grootheid":{"Code":"WATHTE"},
                                "ProcesType":"meting"}},
            "Periode":{"Begindatumtijd":RWS_BEGIN,
                       "Einddatumtijd":RWS_END}}

def get_original_official_rws(*,request_fn=None):
    """Single *official* fixed-month source, transport retry only."""
    if request_fn is None:
        def request_fn(payload):
            body=json.dumps(payload,separators=(",",":")).encode()
            req=Request(RWS_URL,data=body,method="POST",
                        headers={"Content-Type":"application/json",
                                 "Accept":"application/json",
                                 "User-Agent":"boids-source-audit-v66/1.0"})
            with urlopen(req,timeout=55) as r:
                data=r.read(MAX_OFFICIAL_BYTES+1)
                if len(data)>MAX_OFFICIAL_BYTES:
                    raise ValueError("SOURCE_STOP_V66_RWS_BODY_EXCEEDS_LIMIT")
            return json.loads(data)
    payload=request_body()
    last=None
    for attempt in range(3):
        try:
            reply=request_fn(payload)
            return validate_official_rws(reply,payload)
        except (TimeoutError,URLError,ConnectionError) as e:
            last=e
        except HTTPError as e:
            if e.code not in (429,500,502,503,504):
                raise ValueError("SOURCE_STOP_V66_OFFICIAL_RWS_HTTP_ERROR") from e
            last=e
        # Do not retry source/schema/coverage validation errors.
        if attempt<2:
            time.sleep(2*(attempt+1))
    raise RuntimeError("SOURCE_STOP_V66_AUTHENTIC_RWS_TRANSPORT_EXHAUSTED") from last

def validate_official_rws(response,payload,*,expected_count=RWS_EXPECTED):
    """UTC-aware actual 10-minute source readings in cm/NAP. No interpolation."""
    if payload!=request_body():
        raise ValueError("SOURCE_STOP_V66_RWS_STATION_OR_SOURCE_PERIOD_NOT_FROZEN")
    if not isinstance(response,dict) or response.get("Succesvol") is not True:
        raise ValueError("SOURCE_STOP_V66_OFFICIAL_RWS_SERVICE_FAILURE")
    begin=datetime.fromisoformat(RWS_BEGIN)
    end=datetime.fromisoformat(RWS_END)
    values={}
    original_records=0
    original_series=0
    for series in response.get("WaarnemingenLijst") or []:
        meta=series.get("AquoMetadata") or {}
        if (meta.get("Grootheid") or {}).get("Code")!="WATHTE":
            raise ValueError("SOURCE_STOP_V66_NOT_OFFICIAL_WATHTE")
        if (meta.get("Eenheid") or {}).get("Code")!="cm":
            raise ValueError("SOURCE_STOP_V66_WRONG_OFFICIAL_CM_UNIT")
        if (meta.get("Hoedanigheid") or {}).get("Code")!="NAP":
            raise ValueError("SOURCE_STOP_V66_WRONG_OFFICIAL_NAP_DATUM")
        if (series.get("Locatie") or {}).get("Code") not in (None,RWS_STATION):
            raise ValueError("SOURCE_STOP_V66_DIFFERENT_ORIGINAL_STATION")
        original_series+=1
        for r in series.get("MetingenLijst") or []:
            stamp=datetime.fromisoformat(str(r["Tijdstip"]).replace("Z","+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset()!=timedelta(hours=1):
                raise ValueError("SOURCE_STOP_V66_ORIGINAL_GAUGE_NOT_FIXED_PLUS01")
            if not begin<=stamp<=end or (
                (stamp-begin).total_seconds()%600)!=0:
                raise ValueError("SOURCE_STOP_V66_RWS_OUT_OF_MONTH_OR_TEN_MIN_GRID")
            try:
                height=float((r.get("Meetwaarde") or {})["Waarde_Numeriek"])
            except (TypeError,ValueError,KeyError) as exc:
                raise ValueError("SOURCE_STOP_V66_MISSING_OFFICIAL_HEIGHT") from exc
            if not math.isfinite(height) or abs(height)>500:
                raise ValueError("SOURCE_STOP_V66_NONPHYSICAL_GAUGE_HEIGHT")
            t=round(stamp.timestamp())  # fixed +01 original -> real UTC seconds
            if t in values and abs(values[t]-height)>1e-5:
                raise ValueError("SOURCE_STOP_V66_CONFLICTING_GAUGE_DUPLICATE")
            values[t]=height
            original_records+=1
    if (len(values)!=expected_count or
        (expected_count==RWS_EXPECTED and
          (min(values)!=round(begin.timestamp())
           or max(values)!=round(end.timestamp())))):
        raise ValueError("SOURCE_STOP_V66_ORIGINAL_2018_AUG_GAUGE_COVERAGE")
    sorted_t=sorted(values)
    if any(sorted_t[i+1]-sorted_t[i]!=600 for i in range(len(sorted_t)-1)):
        raise ValueError("SOURCE_STOP_V66_MISSING_TEN_MINUTE_GAUGE_INTERVAL")
    return {
        "original_UTC_second_to_cm_NAP":values,
        "source_manifest":{
            "station":RWS_STATION,"parameter":"WATHTE",
            "unit":"cm","datum":"NAP","year_month":"2018-08",
            "original_fixed_RWS_timezone":"+01:00",
            "official_10minute_distinct_samples":len(values),
            "official_series":original_series,
            "original_series_records_before_deduplication":original_records,
            "official_month_complete_without_interpolation":True,
            "actual_UTC_converted_not_WATLAS_ts":True}}

def reassemble_original_source_episodes(raw):
    """Reconstruct v65 B and its published source-phase, NEVER next angle."""
    tracks,tide_data,_=_native_valid_bins(raw)
    source_ref,_=_gauge_reference(tide_data)
    samples=[]
    stage=Counter()
    for bird,trace in tracks.items():
        for a,b,c in zip(trace,trace[1:],trace[2:]):
            dt_before=b["t"]-a["t"]
            dt_after=c["t"]-b["t"]
            if not (MIN_GAP<=dt_before<=MAX_GAP and
                    MIN_GAP<=dt_after<=MAX_GAP):
                continue
            stage["real_B_three_fix_time"]+=1
            if not a["tid"] or a["tid"]!=b["tid"] or b["tid"]!=c["tid"]:
                continue
            stage["original_same_tideID"]+=1
            speed_a=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt_before
            speed_c=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/dt_after
            if not (MIN_SPEED<=speed_a<=MAX_SPEED and
                    MIN_SPEED<=speed_c<=MAX_SPEED):
                continue
            stage["two_original_speed_magnitudes"]+=1
            if b["height"] is None or b["clock"] is None:
                continue
            stage["same_original_published_tide_metadata"]+=1
            published_slope=source_waterlevel_rate(b["t"],b["tid"],source_ref)
            phase=_phase(published_slope)
            if phase in ("rising","falling"):
                samples.append((bird,b["tid"],b["t"],phase))
    return samples,stage

def _closest_official_time(sorted_original_times,target):
    j=bisect_left(sorted_original_times,target)
    near=[]
    if j<len(sorted_original_times):
        near.append(sorted_original_times[j])
    if j>0:
        near.append(sorted_original_times[j-1])
    if not near:
        return None
    found=min(near,key=lambda t:(abs(t-target),t))
    if abs(found-target)>BRACKET_TOL_SECONDS:
        return None
    return found

def _official_phase_at(utc_second,values,sorted_t,shift_minutes):
    current=utc_second+shift_minutes*60
    pre=_closest_official_time(sorted_t,current-BRACKET_TARGET_SECONDS)
    post=_closest_official_time(sorted_t,current+BRACKET_TARGET_SECONDS)
    if pre is None or post is None or post<=pre:
        return "unbracketed"
    cm_per_hour=(values[post]-values[pre])/((post-pre)/3600.)
    if cm_per_hour>=3:
        return "rising"
    if cm_per_hour<=-3:
        return "falling"
    return "slack"

def compare_original_source_with_RWS(samples,real_source,*,shift_minutes):
    """All 2018 historical source candidates fixed before querying official slope."""
    if shift_minutes not in VALIDATION_SHIFTS_MIN:
        raise ValueError("SOURCE_STOP_V66_UNREGISTERED_RWS_TIME_SHIFT")
    vals=real_source["original_UTC_second_to_cm_NAP"]
    sorted_t=sorted(vals)
    cells=Counter()
    covered=set()
    agreeing=set()
    qualifying_cycles=Counter()
    covered_phases=defaultdict(set)
    agreeing_phases=defaultdict(set)
    agreeing_birds=set()
    source_phase=Counter()
    for bird,tid,t,original_phase in samples:
        if original_phase not in ("rising","falling"):
            raise ValueError("SOURCE_STOP_V66_MISCLASSIFIED_SOURCE_EXPERIMENT")
        source_phase[original_phase]+=1
        outside=_official_phase_at(t,vals,sorted_t,shift_minutes)
        cells[(original_phase,outside)]+=1
        if outside!="unbracketed":
            covered.add((bird,tid,t))
        if original_phase==outside:
            agreeing.add((bird,tid,t))
            agreeing_phases[original_phase].add(tid)
            agreeing_birds.add(bird)
            qualifying_cycles[tid]+=1
        if outside in ("rising","falling"):
            covered_phases[original_phase].add(tid)
    def rowcounts(label):
        return {out:cells[(label,out)] for out in
                ("rising","falling","slack","unbracketed")}
    valid=sum(cells[(p,r)] for p in ("rising","falling")
              for r in ("rising","falling"))
    agree=sum(cells[(p,p)] for p in ("rising","falling"))
    coverage=len(covered)/len(samples) if samples else 0
    byphase={}
    for phase in ("rising","falling"):
        d=sum(cells[(phase,target)] for target in ("rising","falling"))
        byphase[phase]={
            "source_original_phase_triples":source_phase[phase],
            "official_non_slack_comparisons":d,
            "agree":cells[(phase,phase)],
            "conditional_agreement_rate":cells[(phase,phase)]/d if d else None,
            "distinct_source_tides_with_agreement":len(agreeing_phases[phase])}
    cycles_ge20=sum(n>=MIN_HOLDOUT_CYCLE_TRIPLES
                    for n in qualifying_cycles.values())
    enough=(len(samples)>0 and coverage>=SHARE_REQUIRED
            and all(byphase[k]["conditional_agreement_rate"] is not None
                    and byphase[k]["conditional_agreement_rate"]>=AGREEMENT_REQUIRED
                    for k in ("rising","falling"))
            and len(agreeing)>=MIN_TRIPLES
            and len(agreeing_birds)>=MIN_BIRDS
            and len(qualifying_cycles)>=MIN_TIDES
            and byphase["rising"]["agree"]>=MIN_PER_PHASE
            and byphase["falling"]["agree"]>=MIN_PER_PHASE
            and len(agreeing_phases["rising"])>=MIN_TIDES_PER_PHASE
            and len(agreeing_phases["falling"])>=MIN_TIDES_PER_PHASE
            and cycles_ge20>=MIN_HOLDOUT_CYCLES)
    return {
        "external_official_source_time_shift_minutes":shift_minutes,
        "fixed_test_samples":len(samples),
        "official_two_bracket_coverage_fraction":coverage,
        "source_phase_vs_independently_observed_RWS_2x4":{
            "source_rising":rowcounts("rising"),
            "source_falling":rowcounts("falling")},
        "original_source_phase_agreement_by_phase":byphase,
        "official_non_slack_compared":valid,
        "official_phase_agree":agree,
        "official_phase_disagree":valid-agree,
        "overall_non_slack_agreement_fraction":agree/valid if valid else None,
        "original_source_birds_with_independent_agreement":len(agreeing_birds),
        "distinct_original_tideID_cycles_with_independent_agreement":len(qualifying_cycles),
        "independent_RWS_agree_cycles_with_at_least_twenty":cycles_ge20,
        "fixed_prior_source_eligibility_satisfied":bool(enough),
        "no_original_triple_heading_or_model_scored":True}

def run(species,output):
    if species not in SOURCE_SHA:
        raise ValueError("SOURCE_STOP_V66_UNKNOWN_SPECIES")
    raw,sha=original_source(species)
    if sha["original_sha256"]!=SOURCE_SHA[species]:
        raise ValueError("SOURCE_STOP_V66_ORIGINAL_FIGSHARE_SOURCE_SHA_CHANGED")
    v64=source_only_audit(raw)
    v65=audit_slope_source_only(raw)
    if (v64["original_raw_rows"]!=EXACT_RAW[species]
        or v64["three_fix_candidates_with_original_tide_metadata"]!=
            EXACT_V64_MOVING_WITH_TIDE[species]):
        raise ValueError("SOURCE_STOP_V66_SOURCE_V64_ORIGINAL_QC_DRIFT")
    expected_total,expected_plus,expected_minus,expected_birds,expected_cycles=(
        SOURCE_PAIRS_EXPECTED[species])
    if (v65["non_slack_bracketed_original_moving_triples"]!=expected_total or
        v65["source_phase_classification_counts"]["rising"]!=expected_plus or
        v65["source_phase_classification_counts"]["falling"]!=expected_minus or
        v65["original_birds_with_rising_or_falling_triples"]!=expected_birds or
        v65["source_distinct_tideIDs_with_rising_or_falling_triples"]!=expected_cycles):
        raise ValueError("SOURCE_STOP_V66_FROZEN_V65_PHASE_COUNT_DRIFT")
    private,stage=reassemble_original_source_episodes(raw)
    if (len(private)!=expected_total or
        stage["same_original_published_tide_metadata"]!=
        EXACT_V64_MOVING_WITH_TIDE[species] or
        Counter(p for bird,tid,t,p in private)!=
        {"rising":expected_plus,"falling":expected_minus}):
        raise ValueError("SOURCE_STOP_V66_REASSEMBLED_V65_GPS_SOURCE_DRIFT")
    from datetime import datetime,timezone
    # Preserve original dates only in-memory; published Fig9 examples are August
    # 12–19 2018. No other period may be silently inserted.
    if any(datetime.fromtimestamp(t,timezone.utc).year!=2018 or
           datetime.fromtimestamp(t,timezone.utc).month!=8
           for _,_,t,_ in private):
        raise ValueError("SOURCE_STOP_V66_ORIGINAL_OUTSIDE_FROZEN_AUG_2018")
    print("V66_ORIGINAL_WATLAS_SOURCE_ADMITTED "+json.dumps({
        "species":species,"original_raw_rows":v64["original_raw_rows"],
        "original_moving_with_tide":stage["same_original_published_tide_metadata"],
        "same_original_v65_bracketed_rising":expected_plus,
        "same_original_v65_bracketed_falling":expected_minus,
        "no_original_next_direction_read":True},sort_keys=True),flush=True)
    official=get_original_official_rws()
    measurements=official["source_manifest"]
    result_by_shift={}
    for delay in VALIDATION_SHIFTS_MIN:
        result_by_shift[str(delay)]=compare_original_source_with_RWS(
            private,official,shift_minutes=delay)
    primary=result_by_shift["0"]
    status=("SOURCE_FEASIBLE_FOR_FUTURE_V67_HEADING_OUT_OF_TIDE_CYCLE"
            if species=="sanderling" and
            v65["admission"]==
              "SOURCE_FEASIBLE_FOR_FUTURE_INDEPENDENT_TIDAL_SLOPE_FORECAST" and
            primary["fixed_prior_source_eligibility_satisfied"]
            else "NOT_ADMITTED_FOR_V67_EXTERNAL_RWS_GAUGE_GATE")
    report={
        "analysis":"V66_OFFICIAL_RWS_2018_WEST_TERSCHELLING_PHASE_CROSSCHECK",
        "species":species,
        "published_original_source":{
            "sha256":sha["original_sha256"],"MD5_provider_verified":True,
            "original_count":v64["original_raw_rows"],
            "frozen_v65_non_slack":expected_total,
            "published_source_rising":expected_plus,
            "published_source_falling":expected_minus,
            "v65_previous_source_admission":v65["admission"]},
        "official_independent_RWS_manifest":measurements,
        "registered_primary_zero_shift":result_by_shift["0"],
        "registered_companion_minus30_shift":result_by_shift["-30"],
        "registered_companion_plus30_shift":result_by_shift["30"],
        "v67_actual_heading_source_admission":status,
        "source_only_no_original_bird_heading_prediction_or_economic_effect":True,
        "no_original_TAG_ID_UTM_UTC_times_or_RWS_station_series_in_export":True}
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V66_ORIGINAL_OFFICIAL_RWS_PHASE_CHECK "+json.dumps({
        "species":species,
        "official_original_NAP_samples":measurements["official_10minute_distinct_samples"],
        "primary_original_bracket_coverage":primary["official_two_bracket_coverage_fraction"],
        "primary_agree":primary["official_phase_agree"],
        "primary_disagree":primary["official_phase_disagree"],
        "primary_rising_agreement":primary["original_source_phase_agreement_by_phase"]["rising"]["conditional_agreement_rate"],
        "primary_falling_agreement":primary["original_source_phase_agreement_by_phase"]["falling"]["conditional_agreement_rate"],
        "primary_agree_distinct_tideIDs":primary["distinct_original_tideID_cycles_with_independent_agreement"],
        "source_admission":status},sort_keys=True),flush=True)
    print("V66_ORIGINAL_RWS_SOURCE_CHECK_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--species",choices=tuple(SOURCE_SHA),required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    run(args.species,args.output)
