"""Network-free known truths for v92 ORIGINAL world-source physical pipeline."""
import io,csv,math,unittest
from datetime import datetime,timezone
import numpy as np
import original_UHSLC_2019_tide_solar as q

class PhysicalPilot(unittest.TestCase):
    def test_original_rows_duplicate_version_excluded_and_year_coverage(self):
        f=io.StringIO();w=csv.writer(f)
        w.writerow(['uhslc_id','record_id','time','sea_level','quality'])
        w.writerow(['','', 'UTC','millimeters',''])
        for i in range(8760):
            t=(q.START+q.timedelta(hours=i)).isoformat().replace('+00:00','Z')
            w.writerow([3,10,t,round(1000*math.sin(2*math.pi*i/12.4206012)),4])
            if i<200:w.writerow([3,11,t,2000,4])
        by=q.parse_native(f.getvalue().encode(),3)
        self.assertEqual(len(by[10]),8760)
        self.assertEqual(len(by[11]),200)
        rec,actual,gap=q.choose_original_segment(by,{10,11})
        self.assertEqual((rec,len(actual),gap),(10,8760,0))
    def test_harmonic_and_real_sun_physical_known_truths(self):
        d={i:1000*math.sin(2*math.pi*i/12.4206012) for i in range(8760)}
        harmonic=q.harmonic_form(d)
        self.assertEqual(harmonic['regime'],'semidiurnal')
        self.assertGreater(harmonic['four_constituent_R2'],.99)
        res=q.opportunity(d,0.,0.)
        self.assertEqual(res['source_hours'],8760)
        self.assertGreater(res['n_valid_days'],300)
        self.assertGreater(res['daily_mean_abs_M'],0)
        self.assertGreater(res['annual_A'],.45)
        self.assertLess(res['annual_A'],.55)
        self.assertIn('2019-01-01',res['daily'][0]['date'])
    def test_source_failures_and_no_pseudoreplication(self):
        self.assertIsNone(q.choose_original_segment({1:{0:1,1:2}},{1}))
        self.assertEqual(q.YEAR,2019)
        self.assertEqual(q.MAX_CANDIDATES,8)
        self.assertNotEqual(q.PERIODS['M2'],q.PERIODS['S2'])
if __name__=='__main__':unittest.main()
