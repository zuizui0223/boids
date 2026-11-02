"""Pure v34 original-source, clock, geography and unchanged predictor smoke tests."""
import csv,gzip,math,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from ameland_external_site import (GPS_MD5,STATION,BBOX,original_gps,
                                   measured_nes,ameland_original_steps)
from tidal_front import TideSeries
from observed_phase import make_x
from phase_rate_ablation import vector

class AmelandFrozenTests(unittest.TestCase):
    def test_source_pin_and_geo_bounds(self):
        self.assertEqual(GPS_MD5[2010],"71e0b66230b508873897c99464146167")
        self.assertEqual(GPS_MD5[2011],"ab74f7443bb09bd5be90bde69fc612eb")
        self.assertEqual(STATION,"ameland.nes")
        self.assertEqual(BBOX,(53.2,53.6,5.3,6.1))
        with self.assertRaises(ValueError):original_gps(2012,"/tmp/no-file")
    def test_ameland_original_fix_sampling_and_replay_features(self):
        start=datetime(2010,6,1,12,tzinfo=timezone.utc)
        gauge=TideSeries([(start-timedelta(hours=2)+timedelta(minutes=10*k),
                           .7*math.sin(k*.17)) for k in range(130)],
                         datum="NAP_m",provenance="synthetic")
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'GPS.csv.gz'
            with gzip.open(src,"wt",newline="") as handle:
                w=csv.writer(handle)
                w.writerow(['event-id','timestamp','location-lat','location-long',
                            'individual-local-identifier','visible'])
                i=0
                for bird in ('A','B'):
                    for k in range(10):
                        t=start+timedelta(hours=k,minutes=3)
                        i+=1
                        w.writerow([i,t.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f"),
                                   53.43,5.75+k*.001,bird,'TRUE'])
                    i+=1
                    w.writerow([i,'2010-06-01 13:01:00.000',54.0,7.3,bird,'TRUE'])
            rows,audit=ameland_original_steps(src,gauge,0)
            self.assertGreater(len(rows),10)
            self.assertEqual(audit['source_animals_in_region'],2)
            self.assertGreater(audit['drop_reasons']['outside_prefrozen_ameland_envelope'],0)
            self.assertEqual(len(make_x(rows[0],0)),9)
            self.assertEqual(len(vector(rows[0],"Mphase")),11)
            self.assertTrue(all(-1<=r['phase']<=1 for r in rows))
    def test_never_infer_from_non_nap_data(self):
        def wrong_datum(path,payload,max_bytes):
            self.assertEqual(payload['Locatie']['Code'],'ameland.nes')
            return {'Succesvol':True,'WaarnemingenLijst':[{
                'AquoMetadata':{'Grootheid':{'Code':'WATHTE'},
                                'Eenheid':{'Code':'cm'},
                                'Hoedanigheid':{'Code':'LAT'}},
                'MetingenLijst':[{'Tijdstip':'2010-01-01T00:00:00+01:00',
                                 'Meetwaarde':{'Waarde_Numeriek':70.}}]}]}
        with self.assertRaisesRegex(ValueError,"NAP"):
            measured_nes(2010,request=wrong_datum)

if __name__=="__main__":unittest.main()
