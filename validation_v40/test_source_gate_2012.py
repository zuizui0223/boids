import csv,gzip,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path
from source_gate_2012 import (AMELAND_2012_MD5,SCHIER_2012_MD5,
                              REGIONS,eligible_source_steps)

class V40SourceOnly(unittest.TestCase):
    def test_original_pinned_source_and_scopes(self):
        self.assertEqual(AMELAND_2012_MD5,"12d5d3045578538f6a6ac9f8e78766df")
        self.assertEqual(SCHIER_2012_MD5,"a2ccce5afe2a6cad09a27e2957beacaf")
        self.assertEqual(REGIONS["ameland"],(53.2,53.6,5.3,6.1))
    def test_one_first_fix_per_hour_bird_unjoined(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"test.csv.gz"
            with gzip.open(f,"wt",newline="") as output:
                w=csv.writer(output)
                w.writerow(["event-id","timestamp","location-lat","location-long",
                            "individual-local-identifier","visible"])
                event=0
                for bird in ("a","b","c"):
                    for k in range(10):
                        event+=1
                        t=datetime(2012,6,4,0,2)+timedelta(hours=k)
                        w.writerow([event,t.isoformat(" ")+".000",53.4,
                                    5.75+(k*.001),bird,"TRUE"])
                event+=1
                w.writerow([event,"2012-06-04 10:02:00.000",54.3,7.7,"a","TRUE"])
            quality=eligible_source_steps(f,"ameland")
            self.assertEqual(quality["source_individuals_in_geographic_gate"],3)
            self.assertEqual(quality["candidate_individuals_with_2012_steps"],3)
            self.assertEqual(quality["candidate_2012_hourly_step_count"],27)
            self.assertEqual(quality["tide_test_admission"],"NOT_ADMITTED_INSUFFICIENT_2012_SOURCE")
            self.assertFalse(quality["source_tide_joined"])
            self.assertEqual(quality["biological_tide_effect"],"NOT_ESTIMATED")
    def test_original_absent_fields_stops(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"broken.csv.gz"
            with gzip.open(f,"wt") as output:
                output.write("timestamp,location-lat\n2012-01-01 00:00:00.000,53.4\n")
            with self.assertRaisesRegex(ValueError,"columns mismatch"):
                eligible_source_steps(f,"schiermonnikoog")

if __name__=="__main__":
    unittest.main()
