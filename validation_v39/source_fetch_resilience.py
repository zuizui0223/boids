"""v39 source-delivery amendment. Original RWS WATHTE meting NAP only.

No changes to biological estimands. Retry bounded *transport* failures without
switching instruments, timestamps, datum, units, location, or ecological rows.
Original gauge positions/values remain on the ephemeral runner only.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timedelta, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen

from tidal_front import TideSeries
from rws_source_probe import ROOT, WATHTE

ALLOWED_STATIONS = ("schiermonnikoog.waddenzee", "ameland.nes")
ALLOWED_YEARS = (2009, 2010, 2011)
RETRIES = 3

def original_month_request(path, payload, max_bytes=15_000_000, timeout=25):
    if path != "/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen":
        raise ValueError("Only frozen RWS historical measurements endpoint")
    req = Request(ROOT + path, data=json.dumps(payload).encode(), method="POST",
                  headers={"Content-Type":"application/json","Accept":"application/json",
                           "User-Agent":"boids-v39-original-source-monthly-retry/1.0"})
    with urlopen(req, timeout=timeout) as response:
        data=response.read(max_bytes+1)
    if len(data)>max_bytes:
        raise ValueError("RWS source response exceeded predeclared memory cap")
    return json.loads(data)

def retry_transport_only(path, payload, *, request_fn=original_month_request,
                         attempts=RETRIES, sleeper=time.sleep):
    if attempts<1 or attempts>RETRIES:
        raise ValueError("Retry count must be from 1 to 3")
    for k in range(attempts):
        try:
            return request_fn(path,payload,max_bytes=15_000_000)
        except (TimeoutError,ConnectionError,URLError) as exc:
            if k == attempts-1:
                raise RuntimeError("SOURCE_STOP_RWS_TRANSPORT_RETRY_EXHAUSTED") from exc
            sleeper(2 ** k)
    raise AssertionError("Unexpected retry loop")

def observed_rws_year(station, year, *, request_fn=original_month_request,
                      sleeper=time.sleep, min_values=12000):
    if station not in ALLOWED_STATIONS or year not in ALLOWED_YEARS:
        raise ValueError("Unfrozen original historical RWS station or year")
    values={};monthly=[];clock_values=0
    for month in range(1,13):
        first=datetime(year,month,1)
        last=(datetime(year+1,1,1) if month==12 else datetime(year,month+1,1))
        args={"Locatie":{"Code":station},
              "AquoPlusWaarnemingMetadata":{"AquoMetadata":dict(WATHTE,ProcesType="meting")},
              "Periode":{"Begindatumtijd":first.strftime("%Y-%m-%dT%H:%M:%S.000+01:00"),
                         "Einddatumtijd":last.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")}}
        path="/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
        print(f"RWS original-month source request: {station} {year}-{month:02d}",flush=True)
        response=retry_transport_only(path,args,request_fn=request_fn,sleeper=sleeper)
        if response.get("Succesvol") is not True:
            raise ValueError(f"SOURCE_STOP_RWS_EXPLICIT_API_ERROR {station} {year}-{month:02d}")
        count=0
        for series in response.get("WaarnemingenLijst") or []:
            meta=series.get("AquoMetadata") or {}
            if (meta.get("Grootheid") or {}).get("Code")!="WATHTE":
                continue
            if (meta.get("Eenheid") or {}).get("Code")!="cm":
                raise ValueError("SOURCE_STOP_RWS_UNIT_NOT_CM")
            if (meta.get("Hoedanigheid") or {}).get("Code")!="NAP":
                raise ValueError("SOURCE_STOP_RWS_DATUM_NOT_NAP")
            for record in series.get("MetingenLijst") or []:
                stamp=datetime.fromisoformat(record["Tijdstip"].replace("Z","+00:00"))
                if stamp.utcoffset()!=timedelta(hours=1):
                    raise ValueError("SOURCE_STOP_RWS_NOT_FIXED_UTC_PLUS_ONE")
                value=(record.get("Meetwaarde") or {}).get("Waarde_Numeriek")
                if value is None:
                    continue
                numeric=float(value)
                if not math.isfinite(numeric) or abs(numeric)>500:
                    continue
                utc=stamp.astimezone(timezone.utc)
                if utc in values and abs(values[utc]-numeric/100)>1e-4:
                    raise ValueError("SOURCE_STOP_RWS_CONTRADICTORY_DUPLICATE")
                values[utc]=numeric/100
                count+=1
        monthly.append({"month":f"{year}-{month:02d}","original_finite_values":count})
        clock_values+=count
        print(f"RWS original-month admitted: {station} {year}-{month:02d} count={count}",flush=True)
    if len(values)<min_values:
        raise ValueError("SOURCE_STOP_INSUFFICIENT_ORIGINAL_NAP_GAUGE_VALUES")
    tide=TideSeries(sorted(values.items()),datum="NAP_m",provenance="observed")
    return tide,{"gauge_rows":len(values),"station":station,
                 "source":"RWS_DDAPI2_original_WATHTE_meting_cm_NAP",
                 "source_offset":"+01:00_fixed","monthly_counts":monthly,
                 "original_download_measurement_count":clock_values,
                 "original_year_data_type":"MEASURED_NOT_MODEL",
                 "source_values_saved_to_repository":False}
