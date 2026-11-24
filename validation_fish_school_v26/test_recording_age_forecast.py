"""v26d source-free original-source-schema and prediction support known-truth."""
from __future__ import annotations
import io,unittest
import numpy as np
import pandas as pd
from validation_fish_school_v26.recording_age_forecast import (
    read_source,build,assess,SOURCE_IDS,AGES,FRAME_LAGS,COLUMN_NAMES,SourceStop
)

def make_xy(n=4000):
    times=np.arange(n,dtype=float)
    arr=np.empty((n,8,2))
    for i in range(8):
        arr[:,i,0]=10+2*i+.05*times+2*np.sin(times/(10+i))
        arr[:,i,1]=40+3*i+.04*times+3*np.cos(times/(12+i))
    return arr

def bytes_file(pos):
    m=pos.reshape(len(pos),16)
    d=pd.DataFrame(np.column_stack((m,np.arange(len(pos)))),columns=COLUMN_NAMES)
    return d.to_csv(index=False,sep=" ",na_rep="NA").encode()

class OriginalCaseFixture(unittest.TestCase):
    def test_exact_17column_position_clock_semantics(self):
        d=make_xy(3500)
        frame,pos=read_source(bytes_file(d))
        self.assertEqual(pos.shape,d.shape)
        self.assertEqual(len(frame),3500)

    def test_source_missing_rows_removed_without_imputation(self):
        d=make_xy(3500)
        d[300:420,:,0]=np.nan
        _,src=read_source(bytes_file(d))
        case=build(src)
        self.assertGreater(case["n_tracking_rows_missing_any_XY"],0)
        self.assertLess(case["n_complete_source_frames"],(3500-55-21)//5)
        self.assertTrue(case["all_models_same_target_cohort"])
        self.assertEqual(set(case["Y"]),{"short","delayed"})
        self.assertEqual(len(case["Y"]["short"]),len(case["Y"]["delayed"]))

    def test_age_vectors_keep_own_and_geometry_identical(self):
        x=build(make_xy(3500))
        g=x["X"]["G_geometry"]
        self.assertEqual(FRAME_LAGS,(0,5,10,25,50))
        self.assertEqual(AGES,(0.,.2,.4,1.,2.))
        for age in AGES:
            z=x["X"][f"age_{age:g}s"]
            np.testing.assert_array_equal(g,z[:,:g.shape[1]])
        self.assertFalse(np.array_equal(x["X"]["age_0s"][:,-2:],x["X"]["age_2s"][:,-2:]))

    def test_wrong_clock_is_source_stop(self):
        d=pd.read_csv(io.BytesIO(bytes_file(make_xy(3500))),sep=r"\s+")
        d.loc[100,"frame"]=d.loc[100,"frame"]+3
        with self.assertRaises(SourceStop):
            read_source(d.to_csv(index=False,sep=" ").encode())

    def test_wrong_original_coordinate_order_blocks(self):
        d=pd.read_csv(io.BytesIO(bytes_file(make_xy(3500))),sep=r"\s+")
        cols=list(d.columns)
        cols[0],cols[1]=cols[1],cols[0]
        d=d[cols]
        with self.assertRaises(SourceStop):
            read_source(d.to_csv(index=False,sep=" ").encode())

    def test_three_files_not_three_known_shoals(self):
        with self.assertRaises(SourceStop):
            assess({})
        self.assertEqual(len(SOURCE_IDS),3)

if __name__=="__main__":unittest.main()
