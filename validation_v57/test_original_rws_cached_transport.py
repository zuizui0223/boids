"""Known-source-shape tests for v57 original RWS delivery, no animal GPS."""
import json,math,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path

from original_rws_cached_transport import (
    OriginalRwsCache,PATH,SourceStop,validate_request,
    validate_source_response,observed_original_rws_year_cached)

PLUS1=timezone(timedelta(hours=1))

def payload(year=2011,month=7,months=3,station="ameland.nes"):
    a=datetime(year,month,1,tzinfo=PLUS1)
    end_month=month+months
    b=datetime(year+(end_month-1)//12,(end_month-1)%12+1,1,tzinfo=PLUS1)
    return {"Locatie":{"Code":station},
            "AquoPlusWaarnemingMetadata":{"AquoMetadata":{
                "Compartiment":{"Code":"OW"},
                "Grootheid":{"Code":"WATHTE"},"ProcesType":"meting"}},
            "Periode":{"Begindatumtijd":a.strftime("%Y-%m-%dT%H:%M:%S.000+01:00"),
                       "Einddatumtijd":b.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")}}

def fake_response(p):
    _,first,last,_=validate_request(PATH,p)
    n=int((last-first).total_seconds()/600)+1
    meta={"Grootheid":{"Code":"WATHTE"},
          "Eenheid":{"Code":"cm"},"Hoedanigheid":{"Code":"NAP"}}
    # Samples have identical values at shared monthly boundaries.
    sample=[]
    for k in range(n):
        t=first+timedelta(minutes=10*k)
        ordinal=int((t-datetime(2009,1,1,tzinfo=PLUS1)).total_seconds()/600)
        sample.append({"Tijdstip":t.isoformat(),
                       "Meetwaarde":{"Waarde_Numeriek":float(50*math.sin(ordinal*.013))}})
    return {"Succesvol":True,"WaarnemingenLijst":[{"AquoMetadata":meta,"MetingenLijst":sample}]}

class OriginalRwsResumeTests(unittest.TestCase):
    def test_original_unmodified_request_contract(self):
        p=payload()
        self.assertEqual(validate_request(PATH,p)[3],3)
        self.assertEqual(validate_request(PATH,payload(month=2,months=1))[3],1)
        for bad in (
            {**p,"Locatie":{"Code":"another.station"}},
            {**p,"AquoPlusWaarnemingMetadata":{"AquoMetadata":{"Grootheid":{"Code":"WATHTE"}}}},
            payload(year=2024),
            payload(month=5,months=3),
            payload(month=1,months=2),
        ):
            with self.assertRaises(SourceStop):validate_request(PATH,bad)
        with self.assertRaises(SourceStop):validate_request("/unfrozen/endpoint",p)

    def test_same_original_quarter_cached_without_refetch(self):
        calls=[]
        def fetch(path,p,max_bytes):
            calls.append(p)
            return fake_response(p)
        with tempfile.TemporaryDirectory() as folder:
            c=OriginalRwsCache(folder,request_fn=fetch)
            p=payload()
            x=c.request(PATH,p)
            self.assertEqual(validate_source_response(x,p)["distinct_original_ten_minute_samples"],13249)
            self.assertEqual(len(calls),1)
            y=c.request(PATH,p)
            self.assertEqual(x,y)
            self.assertEqual(len(calls),1)
            self.assertEqual(c.snapshot()["cached_response_hits"],1)
            self.assertEqual(len(list(Path(folder).glob("*.sha256"))),1)
            # Source is not contaminated with any simulated animal ID/track fields.
            self.assertNotIn("bird",json.dumps(c.snapshot()))

    def test_month_fallback_and_exact_quarter_timestamp_coverage(self):
        calls=[]
        def fetch(path,p,max_bytes):
            months=validate_request(path,p)[3]
            calls.append(months)
            if months==3:raise TimeoutError("single original quarter transport outage")
            return fake_response(p)
        with tempfile.TemporaryDirectory() as folder:
            c=OriginalRwsCache(folder,request_fn=fetch)
            p=payload()
            x=c.request(PATH,p)
            qa=validate_source_response(x,p)
            self.assertEqual(qa["distinct_original_ten_minute_samples"],13249)
            self.assertEqual(c.snapshot()["transport_fallback_quarters"],1)
            self.assertEqual(c.snapshot()["new_original_month_requests"],3)
            self.assertEqual(len(x["WaarnemingenLijst"]),3)
            count=len(calls)
            self.assertEqual(c.request(PATH,p),x)
            self.assertEqual(len(calls),count)

    def test_checkpoint_first_month_after_second_month_timeout(self):
        attempts=[]
        stage={"fail":True}
        def fetch(path,p,max_bytes):
            station,first,last,months=validate_request(path,p)
            attempts.append((months,first.month))
            if months==3:raise TimeoutError("quarter down")
            if stage["fail"] and first.month==8:raise TimeoutError("August down")
            return fake_response(p)
        with tempfile.TemporaryDirectory() as folder:
            p=payload()
            c=OriginalRwsCache(folder,request_fn=fetch)
            with self.assertRaisesRegex(RuntimeError,"SOURCE_STOP_RWS_TRANSPORT_RETRY_EXHAUSTED"):
                c.request(PATH,p)
            self.assertTrue(len(list(Path(folder).glob("*.json.gz")))>=1)
            stage["fail"]=False
            previous_july_count=sum(1 for m,k in attempts if m==1 and k==7)
            c2=OriginalRwsCache(folder,request_fn=fetch)
            o=c2.request(PATH,p)
            self.assertEqual(sum(1 for m,k in attempts if m==1 and k==7),
                             previous_july_count)
            self.assertEqual(c2.snapshot()["cached_response_hits"],1)
            self.assertEqual(validate_source_response(o,p)["distinct_original_ten_minute_samples"],13249)

    def test_cache_tamper_or_missing_sidecar_hard_stops(self):
        with tempfile.TemporaryDirectory() as folder:
            p=payload()
            c=OriginalRwsCache(folder,request_fn=lambda path,p,max_bytes:fake_response(p))
            c.request(PATH,p)
            q=list(Path(folder).glob("*.json.gz"))[0]
            q.write_bytes(b"not original source bytes")
            with self.assertRaisesRegex(SourceStop,"SHA256_MISMATCH"):
                c.request(PATH,p)
            q.unlink()
            with self.assertRaisesRegex(SourceStop,"PARTIAL_SOURCE_CACHE_ENTRY"):
                c.request(PATH,p)

    def test_missing_or_wrong_source_is_not_cached(self):
        with tempfile.TemporaryDirectory() as folder:
            p=payload()
            broken=fake_response(p)
            broken["WaarnemingenLijst"][0]["AquoMetadata"]["Hoedanigheid"]["Code"]="LAT"
            c=OriginalRwsCache(folder,request_fn=lambda path,p,max_bytes:broken)
            with self.assertRaisesRegex(SourceStop,"DATUM_NOT_NAP"):c.request(PATH,p)
            self.assertFalse(list(Path(folder).glob("*.json.gz")))

            def incomplete(path,p,max_bytes):
                source=fake_response(p)
                source["WaarnemingenLijst"][0]["MetingenLijst"].pop(20)
                return source
            c=OriginalRwsCache(folder,request_fn=incomplete)
            with self.assertRaisesRegex(SourceStop,"TEN_MINUTE_COVERAGE"):
                c.request(PATH,p)
            self.assertFalse(list(Path(folder).glob("*.json.gz")))

    def test_original_parser_full_year_equivalence_monthly_vs_quarter(self):
        # Exercises unchanged v39 annual parser including redundant month boundaries.
        with tempfile.TemporaryDirectory() as root:
            direct=OriginalRwsCache(Path(root)/"direct",
                request_fn=lambda path,p,max_bytes:fake_response(p))
            def split(path,p,max_bytes):
                if validate_request(path,p)[3]==3:raise TimeoutError("quarter transport")
                return fake_response(p)
            monthly=OriginalRwsCache(Path(root)/"split",request_fn=split)
            a,ar=observed_original_rws_year_cached(direct,"ameland.nes",2011)
            b,br=observed_original_rws_year_cached(monthly,"ameland.nes",2011)
            self.assertEqual(ar["gauge_rows"],52561)
            self.assertEqual(br["gauge_rows"],52561)
            self.assertEqual(a.times,b.times)
            self.assertEqual(a.heights,b.heights)
            self.assertEqual(direct.snapshot()["new_original_quarter_requests"],4)
            self.assertEqual(monthly.snapshot()["new_original_month_requests"],12)

if __name__=="__main__":unittest.main()
