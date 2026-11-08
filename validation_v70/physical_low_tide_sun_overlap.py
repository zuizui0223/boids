"""v70: authenticated measured RWS low-water × astronomical daylight opportunity.

Each RWS official observed 10-minute waterheight is held for its OWN next
recorded 10-minute source interval. No interpolation across missing samples,
no future gauge covariate in GPS prediction, no GPS endpoint in physical window.
Low-water means below fixed 2010 *station quantile*, not exposed mudflat.
"""
from __future__ import annotations

from bisect import bisect_right
from collections import Counter,defaultdict
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
import math
from statistics import median

import numpy as np
from astral import Observer
from astral.sun import sunrise,sunset

STATION_COORDS={
    "schiermonnikoog":(53.46894,6.20291),
    "ameland":(53.42977,5.75945)
}
FIXED_SOURCE_CLOCK=timezone(timedelta(hours=1))
SOURCE_GAUGE_EACH_YEAR=52561
TEN_MIN_SECONDS=600
TWELVE_HOURS_SECONDS=43200
DECLARED_LOW_QUANTILE=.25
MIN_DAYLENGTH_PAIR_DISTANCE_DAYS=14
MAX_PAIR_DAYLENGTH_DIFFERENCE_H=5/60
LOW_WINDOW_HIGH_H=1.0
LOW_WINDOW_ZERO_H=.10

def _official_year_segments(year,water):
    """Unmodified original year has 52,561 10-minute observations incl end."""
    if len(water.times)!=SOURCE_GAUGE_EACH_YEAR or len(water.heights)!=SOURCE_GAUGE_EACH_YEAR:
        raise ValueError("SOURCE_STOP_V70_OFFICIAL_YEAR_52561_RECORDS_REQUIRED")
    stamps=np.asarray([round(t.timestamp()) for t in water.times],dtype=np.int64)
    low=datetime(year,1,1,tzinfo=FIXED_SOURCE_CLOCK).timestamp()
    end=datetime(year+1,1,1,tzinfo=FIXED_SOURCE_CLOCK).timestamp()
    if stamps[0]!=low or stamps[-1]!=end:
        raise ValueError("SOURCE_STOP_V70_ORIGINAL_RWS_FIXED_PLUS01_YEAR_RANGE")
    if not np.all(np.diff(stamps)==TEN_MIN_SECONDS):
        raise ValueError("SOURCE_STOP_V70_OFFICIAL_MISSING_TEN_MIN_OR_DUPLICATE")
    h=np.asarray(water.heights,dtype=float)
    if not np.isfinite(h).all() or np.abs(h).max()>5.:
        raise ValueError("SOURCE_STOP_V70_OFFICIAL_NAP_HEIGHT_INVALID")
    return stamps,h

def measured_2010_low_cutoff(water_2010):
    _,heights=_official_year_segments(2010,water_2010)
    return float(np.quantile(heights[:-1],DECLARED_LOW_QUANTILE))

class ObservedGaugeSolarOpportunity:
    def __init__(self,source_2009_2011,*,site,cutoff):
        if site not in STATION_COORDS:
            raise ValueError("SOURCE_STOP_V70_UNREGISTERED_SITE_COORDS")
        if not math.isfinite(cutoff):
            raise ValueError("SOURCE_STOP_V70_INVALID_2010_Q25")
        self.site=site;self.cutoff=cutoff
        self.coords=STATION_COORDS[site]
        self.observer=Observer(latitude=self.coords[0],longitude=self.coords[1],elevation=0)
        times=np.asarray([round(t.timestamp()) for t in source_2009_2011.times],dtype=np.int64)
        heights=np.asarray(source_2009_2011.heights,dtype=float)
        if not np.all(np.diff(times)==TEN_MIN_SECONDS):
            raise ValueError("SOURCE_STOP_V70_SOURCE_GAUGE_GAPS_NO_INTERPOLATION")
        if len(times)!=len(heights):
            raise ValueError("SOURCE_STOP_V70_GAUGE_TIMESTAMP_HEIGHT_LENGTH")
        self.times=times
        self.heights=heights
        self.low=np.less_equal(heights[:-1],cutoff)
        solar=np.zeros(len(self.low),dtype=np.bool_)
        # Fixed site astronomy; UTC date of actual timestamp+5 min is the
        # astronomical date of this genuine 10-minute gauge source interval.
        sun_cache={}
        for i,t in enumerate(times[:-1]):
            midpoint=datetime.fromtimestamp(int(t+300),timezone.utc)
            d=midpoint.date()
            if d not in sun_cache:
                a=sunrise(self.observer,date=d,tzinfo=timezone.utc)
                b=sunset(self.observer,date=d,tzinfo=timezone.utc)
                if a>=b:raise ValueError("SOURCE_STOP_V70_NO_VALID_SOURCE_SUNRISE_SUNSET")
                sun_cache[d]=(a.timestamp(),b.timestamp())
            a,b=sun_cache[d]
            solar[i]=(a<=t+300<b)
        self.sun=solar
        self.joint=self.sun & self.low
        self._prefix={}
        for name,mask in (("low",self.low),("sun",self.sun),("joint",self.joint)):
            self._prefix[name]=np.concatenate(([0.],
                np.cumsum(mask.astype(np.int64),dtype=np.int64)*600.)).astype(float)

    def _before_at(self,t,name):
        seconds=float(t.timestamp() if isinstance(t,datetime) else t)
        if not self.times[0]<=seconds<=self.times[-1]:
            raise ValueError("SOURCE_STOP_V70_OUTSIDE_AUTHENTIC_RWS_GAUGE_TIME")
        j=bisect_right(self.times,seconds)-1
        if j>=len(self.times)-1:
            return float(self._prefix[name][-1])
        return float(self._prefix[name][j]+
                     (seconds-self.times[j])*float(
                         {"low":self.low,"sun":self.sun,"joint":self.joint}[name][j]))

    def history_hours(self,stamp,*,offset_hours=0):
        """Exactly observed past 12h; even ghost is shifted farther into past."""
        if offset_hours not in (0,-6):
            raise ValueError("SOURCE_STOP_V70_UNFROZEN_HISTORY_SHIFT")
        if stamp.tzinfo is None:
            raise ValueError("SOURCE_STOP_V70_ORIGINAL_GPS_CLOCK_NAIVE")
        end=stamp+timedelta(hours=offset_hours)
        start=end-timedelta(seconds=TWELVE_HOURS_SECONDS)
        a,b=map(lambda t:float(t.timestamp()),(start,end))
        vals={name:(self._before_at(b,name)-self._before_at(a,name))/3600.
              for name in ("low","sun","joint")}
        if (any(not(-1e-8<=v<=12.+1e-8) for v in vals.values()) or
                vals["joint"]-min(vals["low"],vals["sun"])>1e-8 or
                vals["joint"]+12.-vals["low"]-vals["sun"] < -1e-8):
            raise ValueError("ESTIMAND_STOP_V70_PHYSICAL_OVERLAP_GEOMETRY_INVALID")
        return vals

    def augmented_original_GPS_rows(self,rows):
        out=[]
        for row in rows:
            actual=self.history_hours(row["t"])
            ghost=self.history_hours(row["t"],offset_hours=-6)
            out.append({**row,"low12":actual["low"],"sun12":actual["sun"],
                        "joint12":actual["joint"],
                        "ghostjoint12":ghost["joint"]})
        return out

    def daily_original_gauge_opportunities(self,year):
        """One genuine local (+01 fixed) official gauge day has 144 source bins."""
        start=round(datetime(year,1,1,tzinfo=FIXED_SOURCE_CLOCK).timestamp())
        end=round(datetime(year+1,1,1,tzinfo=FIXED_SOURCE_CLOCK).timestamp())
        j=bisect_right(self.times,start)-1
        if self.times[j]!=start:
            raise ValueError("SOURCE_STOP_V70_ORIGINAL_PLUS01_YEAR_START_MISSING")
        if (end-start)//TEN_MIN_SECONDS!=365*144:
            raise ValueError("SOURCE_STOP_V70_UNEXPECTED_ORIGINAL_CALENDAR_DAY_COUNT")
        records=[]
        for d in range(365):
            lo=j+d*144;hi=lo+144
            if self.times[lo]!=start+d*86400 or self.times[hi]!=start+(d+1)*86400:
                raise ValueError("SOURCE_STOP_V70_NO_144_ACTUAL_SOURCE_SAMPLES_PER_DAY")
            local_day=date(year,1,1)+timedelta(days=d)
            rise=sunrise(self.observer,date=local_day,tzinfo=timezone.utc)
            set_=sunset(self.observer,date=local_day,tzinfo=timezone.utc)
            daylength=(set_-rise).total_seconds()/3600.
            records.append({"source_day":local_day,"daylength_h":daylength,
                            "low_h":float(np.sum(self.low[lo:hi])/6.),
                            "joint_light_h":float(np.sum(self.joint[lo:hi])/6.),
                            "joint_dark_h":float(np.sum(
                                self.low[lo:hi]&~self.sun[lo:hi])/6.)})
        return records

def _summary(values):
    a=np.asarray(values,dtype=float)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("SOURCE_STOP_V70_EMPTY_PHYSICAL_DAILY_VALUES")
    return {
        "n":len(a),"mean":float(a.mean()),"min":float(a.min()),
        "median":float(np.median(a)),"max":float(a.max()),
        "quartiles_25_75":[float(x) for x in np.quantile(a,[.25,.75])],
        "p05_p95":[float(x) for x in np.quantile(a,[.05,.95])]}

def match_same_astronomical_daylength(daily):
    """Greedy source date-only plus daylength matching; never look at joint_h."""
    if len(daily)!=365:
        raise ValueError("SOURCE_STOP_V70_EXPECT_EXACT_SOURCE_YEAR_DAILY")
    cutoff=date(daily[0]["source_day"].year,6,21)
    rising=[(i,d) for i,d in enumerate(daily) if d["source_day"]<cutoff]
    falling=[(i,d) for i,d in enumerate(daily) if d["source_day"]>cutoff]
    candidates=[]
    for i,a in rising:
        for j,b in falling:
            distance=abs((b["source_day"]-a["source_day"]).days)
            gap=abs(b["daylength_h"]-a["daylength_h"])
            if (distance>=MIN_DAYLENGTH_PAIR_DISTANCE_DAYS and
                gap<=MAX_PAIR_DAYLENGTH_DIFFERENCE_H):
                candidates.append((gap,a["source_day"],b["source_day"],i,j))
    candidates.sort()
    used=set();pairs=[]
    for gap,_,__,i,j in candidates:
        if i in used or j in used:
            continue
        pairs.append((i,j))
        used.update((i,j))
    return pairs

def summarize_real_annual_opportunity(opportunity,year):
    daily=opportunity.daily_original_gauge_opportunities(year)
    pairs=match_same_astronomical_daylength(daily)
    diffs=[abs(daily[i]["joint_light_h"]-daily[j]["joint_light_h"]) for i,j in pairs]
    paired_gaps=[abs(daily[i]["daylength_h"]-daily[j]["daylength_h"])*60 for i,j in pairs]
    return {
        "official_station_code":opportunity.site,
        "original_observed_year":year,
        "original_10minute_buckets_used":365*144,
        "original_physical_source_days":len(daily),
        "q25_from_original_2010_station_m_NAP":opportunity.cutoff,
        "astronomical_daylength_h":_summary([x["daylength_h"] for x in daily]),
        "source_low_water_h_per_day":_summary([x["low_h"] for x in daily]),
        "source_low_water_sunlit_h_per_day":_summary([x["joint_light_h"] for x in daily]),
        "source_low_water_dark_h_per_day":_summary([x["joint_dark_h"] for x in daily]),
        "predeclared_same_daylength_sun_branch_pairs":len(pairs),
        "daylength_source_pair_absolute_difference_minutes":_summary(paired_gaps) if pairs else None,
        "same_daylength_pair_absolute_sunlit_low_h_difference":_summary(diffs) if pairs else None,
        "same_daylength_pairs_difference_ge1_hour":sum(x>=1 for x in diffs),
        "same_daylength_pairs_fraction_difference_ge1_hour":
            sum(x>=1 for x in diffs)/len(diffs) if diffs else None,
        "nonindependent_days_from_same_station_year":True,
        "low_water_gauge_Q25_NOT_measured_exposed_mudflat":True}

def source_only_GPS_window_gate(train,test,*,strict=True):
    if strict:
        if ((len(train),len(test),
              len({r["id"] for r in train}),len({r["id"] for r in test})) !=
             (1508,4948,8,13)):
            raise ValueError("SOURCE_STOP_V70_YEAR_AND_UNSEEN_ID_COUNTS_DRIFT")
    if {r["id"] for r in train}&{r["id"] for r in test}:
        raise ValueError("SOURCE_STOP_V70_TRAIN_TEST_ID_SHARED")
    out={}
    for name,rows,required in (("train2010",train,100),("test2011",test,200)):
        groups=defaultdict(Counter)
        for row in rows:
            value=row["joint12"]
            if not 0<=value<=12:
                raise ValueError("SOURCE_STOP_V70_SOURCE_PHYSICAL_WINDOW_OUT_OF_BOUNDS")
            if value<=LOW_WINDOW_ZERO_H:groups[row["id"]]["low"]+=1
            if value>=LOW_WINDOW_HIGH_H:groups[row["id"]]["high"]+=1
        all_counts=Counter()
        both=0
        for counts in groups.values():
            all_counts.update(counts)
            if counts["low"]>=10 and counts["high"]>=10:both+=1
        out[name]={
            "original_source_triplets":len(rows),
            "original_individuals":len(groups),
            "source_join_low_le0p1h":all_counts["low"],
            "source_join_high_ge1h":all_counts["high"],
            "original_source_birds_at_least_10_each_class":both}
        if all_counts["low"]<required or all_counts["high"]<required or both<3:
            raise ValueError("SOURCE_NOT_ADMITTED_V70_PHYSICAL_LOW_WATER_DAYLIGHT_"+name)
    month=len({(r["t"].year,r["t"].month) for r in test})
    out["test2011"]["source_calendar_months"]=month
    if month!=12:
        raise ValueError("SOURCE_NOT_ADMITTED_V70_FULL_2011_CALENDAR_MONTH_COVERAGE")
    return out
