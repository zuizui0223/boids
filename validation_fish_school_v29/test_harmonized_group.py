"""v29 source-free 0.2s speed calculation and native-v27 25Hz regression fixtures."""
import unittest
import numpy as np
from validation_fish_school_v29.harmonized_group import (
 harmonized_group_correlation,aggregate,SourceStop)
from validation_fish_school_v27.group_velocity_correlation import exact_group_correlation

def positions(n=4000,num=8):
    t=np.arange(n)
    p=np.zeros((n,num,2))
    for j in range(num):
        p[:,j,0]=10+j*2+.1*t+2*np.sin(t/(15+j))
        p[:,j,1]=20+j*3+.03*t+3*np.cos(t/(17+j))
    return p

class HarmonizedSpeedChecks(unittest.TestCase):
    def test_200ms_native_frame_windows_all_sources(self):
        pos=positions()
        for fps,step in [(25.,5),(30.,6),(50.,10)]:
            start=int(2*fps)+step
            i=np.arange(start,3900,5,dtype=int)
            obs=harmonized_group_correlation(pos,i,fps)
            self.assertEqual(obs["speed_window_native_frames"],step)
            self.assertEqual(obs["speed_window_seconds"],.2)
            self.assertEqual(len(obs["correlations"]),3)

    def test_25Hz_exactly_replays_unchanged_original_v27(self):
        p=positions()
        ids=np.arange(60,3900,5,dtype=int)
        new=harmonized_group_correlation(p,ids,25.)
        old=exact_group_correlation(p,ids,25.,5)
        for age in (".2","1","2"):
            # using string names as produced by :g format
            x= "age_0.2s" if age==".2" else f"age_{age}s"
            self.assertAlmostEqual(new["correlations"][x],old["correlations"][x],places=12)

    def test_future_source_never_used(self):
        p=positions()
        ids=np.arange(110,3800,5,dtype=int)
        base=harmonized_group_correlation(p,ids,50.)
        b=p.copy();b[3900:]+=100000
        self.assertEqual(base["correlations"],harmonized_group_correlation(b,ids,50.)["correlations"])

    def test_nonfinite_exact_stale_source_stops(self):
        p=positions();ids=np.arange(110,3800,5,dtype=int)
        p[ids[0]-100-10,0,0]=np.nan
        with self.assertRaises(SourceStop):
            harmonized_group_correlation(p,ids,50.)

    def test_constant_group_speed_not_claimed_as_persistent(self):
        p=np.zeros((4000,8,2))
        t=np.arange(4000)
        p[:,:,0]=t[:,None]
        p[:,:,1]=t[:,None]*3
        with self.assertRaises(SourceStop):
            harmonized_group_correlation(p,np.arange(110,3800,5),50.)

    def test_equal_file_source_weighting(self):
        a={"correlations":{"age_0.2s":.1,"age_1s":.2,"age_2s":.3}}
        b={"correlations":{"age_0.2s":.9,"age_1s":.4,"age_2s":.1}}
        y=aggregate("test",[a,b],2,{"test":True})
        self.assertAlmostEqual(y["equal_original_file_mean_C"]["age_0.2s"],.5)
        self.assertFalse(y["original_fish_future_velocity_model_refitted"])

if __name__=="__main__": unittest.main()
