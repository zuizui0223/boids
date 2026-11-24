"""v27 all synthetic known-truth group correlation and cohort-stop fixtures."""
import unittest
import numpy as np
from validation_fish_school_v27.group_velocity_correlation import (
    exact_group_correlation,record_result,AGES,SourceStop
)

def fixture(n=3500,N=8):
    t=np.arange(n,dtype=float)
    z=np.zeros((n,N,2))
    for i in range(N):
        z[:,i,0]=10+i*3+.12*t+np.sin(t/(15+i))
        z[:,i,1]=20+i*5+.15*t+np.cos(t/(21+i))
    return z,np.arange(75,n-30,5)

class KnownTruthGroupCorrelation(unittest.TestCase):
    def test_original_velocity_group_state_time_lag_grid(self):
        p,i=fixture()
        r=exact_group_correlation(p,i,25.,5)
        self.assertEqual(set(r["correlations"]),{"age_0.2s","age_1s","age_2s"})
        self.assertEqual(r["original_fps"],25.)
        self.assertTrue(all(-1<=x<=1 for x in r["correlations"].values()))
        self.assertFalse(r["new_fish_movement_prediction_computed"])

    def test_source_disallowed_age_fps_stop(self):
        p,i=fixture()
        with self.assertRaises(SourceStop):
            exact_group_correlation(p,i,17.,5)

    def test_missing_original_source_position_fails_not_cohort_resampled(self):
        p,i=fixture()
        p[i[0]-5,:,0]=np.nan
        with self.assertRaises(SourceStop):
            exact_group_correlation(p,i,25.,5)

    def test_wrong_or_empty_time_ids_source_stop(self):
        p,i=fixture()
        with self.assertRaises(SourceStop):
            exact_group_correlation(p,i[::-1],25.,5)
        with self.assertRaises(SourceStop):
            exact_group_correlation(p,i[:20],25.,5)

    def test_no_variable_school_motion_cannot_create_information(self):
        p=np.zeros((3500,8,2))
        t=np.arange(3500,dtype=float)
        p[:,:,0]=t[:,None]
        p[:,:,1]=t[:,None]*2
        with self.assertRaises(SourceStop):
            exact_group_correlation(p,np.arange(75,3000,5),25.,5)

    def test_equal_recording_not_frame_average(self):
        a={"correlations":{"age_0.2s":.4,"age_1s":.1,"age_2s":0}}
        b={"correlations":{"age_0.2s":.8,"age_1s":.3,"age_2s":.2}}
        z=record_result("knowntruth",[a,b],{"source":"synthetic"})
        self.assertAlmostEqual(z["equal_file_mean_correlation"]["age_0.2s"],.6)
        self.assertFalse(z["new_fish_future_velocity_fit"])

if __name__=="__main__":unittest.main()
