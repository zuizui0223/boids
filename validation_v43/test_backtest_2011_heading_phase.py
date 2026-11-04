import unittest,math
from datetime import datetime,timedelta,timezone
from original_heading_tide import forecast,directional_half_mse
from backtest_2011_heading_phase import (score,TRAIN_YEAR,TEST_YEAR,
                                        SOURCE_QA_MIN,TEST_MIN_BIRDS,TEST_MIN_WEEKS)

class V43FrozenHeadingBacktestTests(unittest.TestCase):
    def row(self,k,b,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=k*4)
        phase=1 if k%3 else -1
        e=phase*.7+.01*math.sin(k+b)
        n=math.sqrt(1-e*e)
        return {"id":str(b),"t":t,"h":math.sin(k*.12),"phase":phase,
                "lat":53.43+b*.01,"lon":5.87+b*.001,
                "clocksin":math.sin(2*math.pi*t.hour/24),
                "clockcos":math.cos(2*math.pi*t.hour/24),
                "yearsin":math.sin(2*math.pi*t.timetuple().tm_yday/365.25),
                "yearcos":math.cos(2*math.pi*t.timetuple().tm_yday/365.25),
                "previous_e":.6,"previous_n":.8,
                "previous_speed_log":math.log1p(2.),
                "target_e":e,"target_n":n}
    def test_immutable_v41_source_thresholds(self):
        self.assertEqual(TRAIN_YEAR,2010)
        self.assertEqual(TEST_YEAR,2011)
        self.assertEqual(SOURCE_QA_MIN,1000)
        self.assertEqual(TEST_MIN_BIRDS,3)
        self.assertEqual(TEST_MIN_WEEKS,4)
    def test_directional_phase_known_truth_heldout_2011(self):
        train=[self.row(k,b,2010) for b in range(4) for k in range(380)]
        test=[self.row(k,b,2011) for b in range(4) for k in range(380)]
        out=score(train,test,bird_draws=120,week_draws=120)
        self.assertEqual(out["n_heldout_source_birds"],4)
        self.assertEqual(out["status"],"2011_REAL_DIRECTIONAL_BACKTEST_POST_V41_EXPLORATORY")
        self.assertGreater(out["tidal_phase_gain_pooled_equal_bird_half_MSE"],0)
        self.assertTrue(out["v41_frozen_heading_model_imported_unchanged"])
        self.assertEqual(len(out["pooled_bird_bootstrap95"]),2)
        self.assertEqual(len(out["separate_week_bootstrap95"]),2)
    def test_test_year_must_be_2011(self):
        train=[self.row(k,0,2010) for k in range(20)]
        test=[self.row(k,0,2012) for k in range(20)]
        with self.assertRaisesRegex(ValueError,"fully withheld 2011"):
            score(train,test)
    def test_low_independent_birds_gives_source_stop(self):
        train=[self.row(k,0,2010) for k in range(1100)]
        test=[self.row(k,0,2011) for k in range(1100)]
        out=score(train,test)
        self.assertEqual(out["status"],"NOT_ADMITTED_INSUFFICIENT_ORIGINAL_2011_DIRECTION_SOURCE")

if __name__=="__main__":unittest.main()
