import unittest
from urllib.error import URLError
from source_fetch_resilience import (ALLOWED_STATIONS, observed_rws_year,
                                     retry_transport_only)
from tide_phase_yearago_placebo import SITES

class OriginalRWSResilienceTests(unittest.TestCase):
    def fake(self,path,query,max_bytes=15_000_000):
        name=query["Locatie"]["Code"]
        self.assertIn(name,ALLOWED_STATIONS)
        start=query["Periode"]["Begindatumtijd"]
        self.assertTrue(start.endswith("+01:00"))
        # Three distinct 10-minute samples per synthetic source month.
        base=start[:10]
        return {"Succesvol":True,"WaarnemingenLijst":[{
            "AquoMetadata":{"Grootheid":{"Code":"WATHTE"},
                            "Einheit":{},"Eenheid":{"Code":"cm"},
                            "Hoedanigheid":{"Code":"NAP"}},
            "MetingenLijst":[{"Tijdstip":f"{base}T00:{k*10:02d}:00+01:00",
                              "Meetwaarde":{"Waarde_Numeriek":float(k*20)}}
                             for k in range(3)]}]}
    def test_transport_retry_does_not_change_source_body(self):
        failures=[];calls=[]
        def flaky(path,query,max_bytes):
            calls.append((path,query))
            if len(calls)==1:raise URLError("temporary network outage")
            return self.fake(path,query,max_bytes)
        dummy={"Locatie":{"Code":"ameland.nes"},"Periode":{"Begindatumtijd":"2010-01-01T00:00:00.000+01:00"}}
        val=retry_transport_only("/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen",
                 dummy,request_fn=flaky,sleeper=lambda _:None)
        self.assertTrue(val["Succesvol"])
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[0],calls[1])
    def test_gauge_same_year_12_original_months_and_nap_gate(self):
        t,meta=observed_rws_year("ameland.nes",2009,request_fn=self.fake,
                                  sleeper=lambda _:None,min_values=36)
        self.assertEqual(meta["gauge_rows"],36)
        self.assertEqual(t.heights[:3],[0.0,0.2,0.4])
        self.assertEqual(len(meta["monthly_counts"]),12)
        with self.assertRaises(ValueError):
            observed_rws_year("unverified.station",2009,request_fn=self.fake)
    def test_reject_wrong_original_datum_without_retry(self):
        def bad(path,query,max_bytes=15_000_000):
            x=self.fake(path,query,max_bytes)
            x["WaarnemingenLijst"][0]["AquoMetadata"]["Hoedanigheid"]={"Code":"LAT"}
            return x
        with self.assertRaisesRegex(ValueError,"DATUM"):
            observed_rws_year("schiermonnikoog.waddenzee",2009,
                              request_fn=bad,sleeper=lambda _:None,min_values=36)
    def test_only_two_original_study_sites(self):
        self.assertEqual(SITES,("schiermonnikoog","ameland"))

if __name__=="__main__":
    unittest.main()
