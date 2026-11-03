import csv, gzip, math, random, tempfile, unittest
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tidal_observed_2009 import (get_gauge, read_gps, make_steps, split_rows,
                                  score, ONE_HOUR, STATION)
from tidal_front import TideSeries

class V31OriginalSourceTests(unittest.TestCase):
    def test_rws_real_datum_hour_and_unit_gate(self):
        begin=datetime(2009,5,20,tzinfo=ONE_HOUR)
        end=begin+timedelta(minutes=20)
        def fake_req(path,payload):
            self.assertIn('OphalenWaarnemingen',path)
            self.assertEqual(payload['Locatie']['Code'],STATION)
            self.assertEqual(payload['Periode']['Begindatumtijd'],'2009-05-20T00:00:00.000+01:00')
            return {"Succesvol":True,"WaarnemingenLijst":[{
                "AquoMetadata":{"Eenheid":{"Code":"cm"},"Hoedanigheid":{"Code":"NAP"},
                                "Grootheid":{"Code":"WATHTE"}},
                "MetingenLijst":[
                    {"Tijdstip":(begin+timedelta(minutes=10*i)).isoformat(),
                     "Meetwaarde":{"Waarde_Numeriek":float(i*20)}} for i in range(3)]}]}
        gauge,audit=get_gauge(start=begin,end=end,request=fake_req,min_obs=3)
        self.assertEqual(audit['unique_valid_water_observations'],3)
        self.assertEqual(gauge.heights,[0.,.2,.4])
        self.assertEqual(gauge.times[0].hour,23) # fixed +01:00 implies UTC previous day
        def bad_unit(path,payload):
            r=fake_req(path,payload)
            r['WaarnemingenLijst'][0]['AquoMetadata']['Eenheid']['Code']='m'
            return r
        with self.assertRaises(ValueError):
            get_gauge(start=begin,end=end,request=bad_unit,min_obs=3)

    def test_source_step_without_unverified_real_tide(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.csv.gz'
            with gzip.open(source,'wt',newline='') as f:
                w=csv.writer(f)
                w.writerow(['event-id','timestamp','location-lat','location-long',
                            'individual-local-identifier','visible'])
                for i in range(12):
                    w.writerow([i+1,f'2009-05-20 04:{i*5:02d}:00.000',53.48,
                                6.2+i*.00001,'A','TRUE'])
            fixes,audit=read_gps(source)
            self.assertEqual(audit['n_original_birds'],1)
            start=datetime(2009,5,20,2,tzinfo=timezone.utc)
            gauge=TideSeries([(start+timedelta(minutes=10*k),
                               math.cos(2*math.pi*k/60)) for k in range(48)],
                             datum='NAP_m',provenance='synthetic')
            steps,stats=make_steps(fixes,gauge)
            self.assertEqual(len(steps),11)
            self.assertEqual(stats['n_eligible_steps'],11)
            self.assertTrue(all(s['y']>=0 for s in steps))

    def test_known_truth_phase_is_predictive_on_untouched_weeks(self):
        rng=random.Random(32)
        start=datetime(2009,5,25,tzinfo=timezone.utc)
        rows=[]
        for week in range(22):
            for bird in ['A','B','C','D']:
                for k in range(48):
                    phase=1 if k%2 else -1
                    time=start+timedelta(weeks=week,hours=k*3)
                    rows.append({'bird':bird,'stamp':time,'week':time.isocalendar()[:2],
                        'y':0.8+0.23*phase+rng.gauss(0,.12),
                        'height':rng.uniform(-1,1),'phase':phase,'lat':53.45,
                        'lon':6.2,'dt_s':600,'hour':time.hour,
                        'day':time.timetuple().tm_yday})
        train,test,split=split_rows(rows)
        out=score(train,test,split,B=200)
        self.assertEqual(out['admission'],'OBSERVED_EXPLORATORY_CLOCK_UNVERIFIED')
        self.assertGreater(out['gain_M0_minus_M1_MSE'],0)
        self.assertEqual(out['n_heldout_birds'],4)
        self.assertGreaterEqual(split['n_test_weeks'],4)

    def test_insufficient_holdout_stops(self):
        train=[{'bird':'a','y':1.}]*1200
        test=[{'bird':'a','y':1.}]*1200
        info={'n_shared_test_birds':1,'n_test_weeks':7}
        self.assertTrue(score(train,test,info)['admission'].startswith('NOT_ADMITTED'))

if __name__=='__main__':unittest.main()
