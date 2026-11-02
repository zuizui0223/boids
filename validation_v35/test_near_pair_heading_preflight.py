import csv,gzip,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path
from near_pair_heading_preflight import heading,audit

class PairHeadings(unittest.TestCase):
    def test_real_past_is_distinct_from_next_target(self):
        a={"time":datetime(2010,1,1,12,0),"lat":53.45,"lon":6.2}
        b={"time":datetime(2010,1,1,12,10),"lat":53.45,"lon":6.201}
        z=heading(a,b)
        self.assertIsNotNone(z)
        self.assertGreater(z[0],.999)
        self.assertAlmostEqual(z[1],0.,places=6)
        self.assertIsNone(heading(a,{**b,"time":a["time"]}))
        self.assertIsNone(heading(a,{**b,"lon":a["lon"],"lat":a["lat"]}))
    def test_source_unique_dyad_day_not_duplicate_fix_pairs(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"test.csv.gz"
            with gzip.open(path,"wt",newline="") as f:
                writer=csv.writer(f)
                writer.writerow(["event-id","timestamp","location-lat","location-long","individual-local-identifier","visible"])
                k=1
                for bird,shift in (("A",0.),("B",.0002)):
                    for m in (0,10,20):
                        t=datetime(2010,6,1,12,0)+timedelta(minutes=m)
                        writer.writerow([k,t.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                         53.45,6.2+shift+(m/10)*.001,bird,"TRUE"])
                        k+=1
            result=audit(path,2010)
            self.assertEqual(result["nearby_raw_different_bird_pairs_5s_100m"],3)
            self.assertEqual(result["qualifying_directed_neighbor_prior_to_focal_next_pairs"],2)
            self.assertEqual(result["unique_day_dyad_replicates"],1)
            self.assertEqual(result["unique_calendar_days"],1)
            self.assertEqual(result["unique_qualifying_birds"],2)
            self.assertEqual(result["status"],"NOT_ADMITTED_SOCIAL_MOVEMENT_FORECAST")
            self.assertEqual(result["social_alignment_or_causal_boids"],"NOT_ESTIMATED")

if __name__=="__main__":unittest.main()
