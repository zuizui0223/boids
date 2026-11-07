"""Resumable delivery of EXACT original RWS WATHTE meting cm/NAP observations.

A successful quarter and three successful months represent the same
half-open calendar span with inclusive 10-minute boundary samples.
Transport/cache changes only. The unchanged v39 observed_rws_year parser
still builds the physical TideSeries and checks annual values.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
from datetime import datetime,timedelta,timezone
from pathlib import Path

from source_fetch_resilience import (ALLOWED_STATIONS,original_month_request,
                                      observed_rws_year,retry_transport_only)
from rws_source_probe import WATHTE

PATH="/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
START_YEAR=2009
END_YEAR=2011
MAX_COMPRESSED_BYTES=20_000_000
CACHE_VERSION="rws-original-v57-same-measurement-v1"

class SourceStop(ValueError):
    pass

def _parse(text):
    if not isinstance(text,str):raise SourceStop("SOURCE_STOP_INVALID_FIXED_OFFSET_TIME")
    t=datetime.fromisoformat(text)
    if t.tzinfo is None or t.utcoffset()!=timedelta(hours=1):
        raise SourceStop("SOURCE_STOP_RWS_TIME_NOT_FIXED_PLUS01")
    if (t.hour,t.minute,t.second,t.microsecond)!=(0,0,0,0):
        raise SourceStop("SOURCE_STOP_ORIGINAL_SOURCE_DAY_BOUNDARY")
    return t

def validate_request(path,payload):
    if path!=PATH:raise SourceStop("SOURCE_STOP_UNFROZEN_ORIGINAL_ENDPOINT")
    if not isinstance(payload,dict):raise SourceStop("SOURCE_STOP_ORIGINAL_REQUEST_NOT_DICT")
    station=(payload.get("Locatie") or {}).get("Code")
    if station not in ALLOWED_STATIONS:
        raise SourceStop("SOURCE_STOP_ORIGINAL_STATION")
    meta=((payload.get("AquoPlusWaarnemingMetadata") or {}).get("AquoMetadata") or {})
    expected={**WATHTE,"ProcesType":"meting"}
    if meta!=expected:raise SourceStop("SOURCE_STOP_REQUEST_NOT_WATHTE_METING")
    period=payload.get("Periode") or {}
    first=_parse(period.get("Begindatumtijd"))
    last=_parse(period.get("Einddatumtijd"))
    if not(START_YEAR<=first.year<=END_YEAR and first.day==1 and first.month in range(1,13)):
        raise SourceStop("SOURCE_STOP_YEAR_OR_MONTH_OUTSIDE_FROZEN_SOURCE")
    months=(last.year-first.year)*12+last.month-first.month
    if last.day!=1 or months not in (1,3) or last<=first:
        raise SourceStop("SOURCE_STOP_ORIGINAL_SOURCE_MONTH_OR_QUARTER_ONLY")
    if months==3 and first.month not in (1,4,7,10):
        raise SourceStop("SOURCE_STOP_UNFROZEN_QUARTER_START")
    if first.year==END_YEAR and last.year>END_YEAR+1:
        raise SourceStop("SOURCE_STOP_UNFROZEN_ORIGINAL_SOURCE_END")
    return station,first,last,months

def _request_key(path,payload):
    data=json.dumps({"v":CACHE_VERSION,"endpoint":path,
                     "payload":payload},sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(data).hexdigest()

def validate_source_response(response,payload):
    """Validate metadata, coverage and original distinct ten-minute times.

    Do not filter or invent a missing observation. A hole hard-stops before
    any downstream GPS/tidal forecast can be calculated.
    """
    _,first,last,_=validate_request(PATH,payload)
    if not isinstance(response,dict) or response.get("Succesvol") is not True:
        raise SourceStop("SOURCE_STOP_RWS_OFFICIAL_RESPONSE_FAILED")
    values={}
    seen_good=0
    for series in response.get("WaarnemingenLijst") or []:
        meta=series.get("AquoMetadata") or {}
        if (meta.get("Grootheid") or {}).get("Code")!="WATHTE":
            raise SourceStop("SOURCE_STOP_RWS_ALTERNATIVE_PARAMETER")
        if (meta.get("Eenheid") or {}).get("Code")!="cm":
            raise SourceStop("SOURCE_STOP_ORIGINAL_UNIT_NOT_CM")
        if (meta.get("Hoedanigheid") or {}).get("Code")!="NAP":
            raise SourceStop("SOURCE_STOP_ORIGINAL_DATUM_NOT_NAP")
        for r in series.get("MetingenLijst") or []:
            stamp=datetime.fromisoformat(r["Tijdstip"].replace("Z","+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset()!=timedelta(hours=1):
                raise SourceStop("SOURCE_STOP_RWS_SAMPLE_CLOCK_NOT_PLUS01")
            if not first<=stamp<=last:
                raise SourceStop("SOURCE_STOP_ORIGINAL_MEASUREMENT_OUTSIDE_REQUEST")
            raw=(r.get("Meetwaarde") or {}).get("Waarde_Numeriek")
            try: val=float(raw)
            except (ValueError,TypeError):
                raise SourceStop("SOURCE_STOP_ORIGINAL_MISSING_MEASUREMENT")
            if not math.isfinite(val) or abs(val)>500:
                raise SourceStop("SOURCE_STOP_ORIGINAL_NONPHYSICAL_MEASUREMENT")
            if stamp in values and abs(values[stamp]-val)>1e-5:
                raise SourceStop("SOURCE_STOP_ORIGINAL_CONFLICTING_DUPLICATE")
            values[stamp]=val;seen_good+=1
    expected=int((last-first).total_seconds()//600)+1
    if len(values)!=expected:
        raise SourceStop(f"SOURCE_STOP_ORIGINAL_TEN_MINUTE_COVERAGE_{len(values)}_expected_{expected}")
    if min(values)!=first or max(values)!=last or any(
            t.second!=0 or t.microsecond!=0 or ((t-first).total_seconds()%600)!=0
            for t in values):
        raise SourceStop("SOURCE_STOP_RWS_NOT_REGULAR_TEN_MINUTE_COVERAGE")
    return {"distinct_original_ten_minute_samples":len(values),
            "raw_matched_original_source_records":seen_good,
            "source_original_start":first.isoformat(),
            "source_original_end":last.isoformat()}

def _monthly_payload(quarter_payload,first,last):
    out=json.loads(json.dumps(quarter_payload))
    out["Periode"]["Begindatumtijd"]=first.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")
    out["Periode"]["Einddatumtijd"]=last.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")
    validate_request(PATH,out)
    return out

class OriginalRwsCache:
    def __init__(self,directory,*,request_fn=original_month_request,sleeper=lambda seconds:None):
        self.dir=Path(directory);self.dir.mkdir(parents=True,exist_ok=True)
        self.request_fn=request_fn
        self.sleeper=sleeper
        self.hits=0;self.quarters_fetched=0;self.months_fetched=0
        self.quarter_fallbacks=0
        self.diagnostics=[]

    def _paths(self,key):
        return self.dir/(key+".json.gz"),self.dir/(key+".sha256")

    def _cached(self,path,payload):
        key=_request_key(path,payload)
        gz,check=self._paths(key)
        if not gz.exists() and not check.exists():return None
        if not gz.is_file() or not check.is_file():
            raise SourceStop("SOURCE_STOP_PARTIAL_SOURCE_CACHE_ENTRY")
        data=gz.read_bytes()
        if len(data)>MAX_COMPRESSED_BYTES:
            raise SourceStop("SOURCE_STOP_CACHE_BLOB_TOO_LARGE")
        if hashlib.sha256(data).hexdigest()!=check.read_text().strip():
            raise SourceStop("SOURCE_STOP_CACHE_SHA256_MISMATCH")
        try:result=json.loads(gzip.decompress(data))
        except (OSError,ValueError) as error:
            raise SourceStop("SOURCE_STOP_CACHE_NOT_AUTHENTIC_JSON") from error
        qa=validate_source_response(result,payload)
        self.hits+=1
        self.diagnostics.append({"source_cache_hit":True,"request_digest":key,
                                 **qa})
        return result

    def _save(self,path,payload,result):
        qa=validate_source_response(result,payload)
        key=_request_key(path,payload)
        gz,check=self._paths(key)
        raw=json.dumps(result,sort_keys=True,separators=(",",":")).encode("utf-8")
        data=gzip.compress(raw,compresslevel=6,mtime=0)
        if len(data)>MAX_COMPRESSED_BYTES:raise SourceStop("SOURCE_STOP_CACHE_BLOB_TOO_LARGE")
        scratch=gz.with_suffix(".pending")
        scratch.write_bytes(data)
        os.replace(scratch,gz)
        check.write_text(hashlib.sha256(data).hexdigest()+"\n")
        self.diagnostics.append({"source_cache_hit":False,"request_digest":key,**qa})
        return result

    def _fetch(self,path,payload):
        return retry_transport_only(path,payload,request_fn=self.request_fn,
                                    sleeper=self.sleeper)

    def _month(self,path,payload):
        hit=self._cached(path,payload)
        if hit is not None:return hit
        source=self._fetch(path,payload)
        self.months_fetched+=1
        return self._save(path,payload,source)

    def request(self,path,payload,max_bytes=20_000_000):
        # Signature strictly compatible with original v39 request_fn.
        _,first,last,months=validate_request(path,payload)
        hit=self._cached(path,payload)
        if hit is not None:return hit
        if months==1:return self._month(path,payload)
        try:
            direct=self._fetch(path,payload)
            self.quarters_fetched+=1
            return self._save(path,payload,direct)
        except RuntimeError as e:
            if str(e)!="SOURCE_STOP_RWS_TRANSPORT_RETRY_EXHAUSTED":
                raise
            self.quarter_fallbacks+=1
        # Only a transport failure permits the EXACT same-quarter month split.
        # The original monthly source returns inclusive 00:00 boundaries.
        chunks=[]
        for m in range(first.month,first.month+3):
            a=datetime(first.year,m,1,tzinfo=timezone(timedelta(hours=1)))
            b=(datetime(first.year+1,1,1,tzinfo=a.tzinfo) if m==12 else
               datetime(first.year,m+1,1,tzinfo=a.tzinfo))
            month_payload=_monthly_payload(payload,a,b)
            chunks.append(self._month(path,month_payload))
        result={"Succesvol":True,
                "WaarnemingenLijst":[series for chunk in chunks
                                     for series in chunk["WaarnemingenLijst"]]}
        return self._save(path,payload,result)

    def snapshot(self):
        return {"cache_version":CACHE_VERSION,
                "cached_response_hits":self.hits,
                "new_original_quarter_requests":self.quarters_fetched,
                "new_original_month_requests":self.months_fetched,
                "transport_fallback_quarters":self.quarter_fallbacks,
                "cached_request_files":len(list(self.dir.glob("*.json.gz"))),
                "no_original_GPS_source_or_model_changed":True}

def observed_original_rws_year_cached(cache,station,year):
    if station not in ALLOWED_STATIONS or year not in range(START_YEAR,END_YEAR+1):
        raise SourceStop("SOURCE_STOP_STATION_YEAR_OUTSIDE_ORIGINAL")
    return observed_rws_year(station,year,request_fn=cache.request,sleeper=cache.sleeper)
