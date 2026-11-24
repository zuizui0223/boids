"""v33 entirely synthetic original-source topological positive/negative controls."""
from __future__ import annotations
import unittest
import numpy as np

from validation_fish_school_v30.harmonized_forecast import build_original_recording
from validation_fish_school_v33.neighbor_panels import (
    original_panels,frozen_original_source_clock_and_cohort,PANELS
)
from validation_fish_school_v33.neighbor_shoal_holdout import (
    file_moments,summaries_from_mse,EXPECTED_V32,BASELINE_ABS_MAX_ERROR
)

def fake_source(n=4200,nfish=8):
    rng=np.random.default_rng(42042)
    t=np.arange(n,dtype=float)
    out=np.zeros((n,nfish,2))
    drift=np.zeros((n,nfish,2))
    for j in range(nfish):
        drift[:,j,0]=.2*np.sin(t/(20+j*3))+.015*j*t/n
        drift[:,j,1]=.16*np.cos(t/(16+j))+.025*j*t/n
        out[:,j,0]=50+5*j+.03*t+drift[:,j,0]
        out[:,j,1]=20+6*j+.02*t+drift[:,j,1]
    return np.arange(n,dtype=float),out

class GenuineOriginalSourceGeometryFixtures(unittest.TestCase):
    def test_all_six_frozen_panels_same_source_and_future_response(self):
        f,p=fake_source()
        prior=build_original_recording(f,p,25)
        case=original_panels(f,p)
        self.assertEqual(tuple(case["X"]),PANELS)
        self.assertEqual(len(case["Y"]),len(prior["Y"]))
        np.testing.assert_array_equal(case["Y"],prior["Y"])
        np.testing.assert_array_equal(case["X"]["GLOBAL"],prior["X"]["age_0s"])
        for panel in PANELS[2:]:
            np.testing.assert_array_equal(case["X"][panel][:,:16],prior["X"]["age_0s"])
        self.assertTrue(case["same_source_frozen_Y_and_G14_and_GLOBAL"])

    def test_near_far_and_fixed_rotation_are_same_size_but_different_assignment(self):
        f,p=fake_source()
        case=original_panels(f,p)
        n=case["X"]["NEAR_TRUE"]
        far=case["X"]["FAR_TRUE"]
        rot=case["X"]["NEAR_ROT1"]
        self.assertEqual(n.shape,far.shape)
        self.assertEqual(n.shape,rot.shape)
        self.assertEqual(n.shape[1],18)
        self.assertGreater(np.max(np.abs(n[:,-2:]-far[:,-2:])),1e-10)
        self.assertGreater(np.max(np.abs(n[:,-2:]-rot[:,-2:])),1e-10)

    def test_stale_velocity_uses_same_current_global_and_focal_geometry(self):
        f,p=fake_source()
        x=original_panels(f,p)["X"]
        self.assertEqual(len(x["NEAR_STALE_0.2S"]),len(x["NEAR_TRUE"]))
        np.testing.assert_array_equal(x["NEAR_STALE_0.2S"][:,:16],x["NEAR_TRUE"][:,:16])
        self.assertGreater(np.mean(np.abs(x["NEAR_STALE_0.2S"][:,-2:]-x["NEAR_TRUE"][:,-2:])),0)

    def test_native_original_frame_missing_invalid_clock_fails_closed(self):
        f,p=fake_source()
        f[40]+=2
        with self.assertRaises(Exception):
            original_panels(f,p)

    def test_original_source_NA_admission_matches_v30_unmodified(self):
        f,p=fake_source()
        p[500:580,2,1]=np.nan
        prior=build_original_recording(f,p,25)
        case=original_panels(f,p)
        self.assertEqual(case["n_original_eligible_group_times"],prior["n_original_eligible_group_times"])
        np.testing.assert_array_equal(case["Y"],prior["Y"])
        self.assertTrue(all(np.isfinite(x).all() for x in case["X"].values()))

    def test_source_moments_same_four_response_columns(self):
        f,p=fake_source()
        case=original_panels(f,p)
        mom=file_moments(case)
        self.assertEqual(tuple(mom),PANELS)
        self.assertEqual(len({z["n"] for z in mom.values()}),1)
        self.assertEqual(mom["NEAR_TRUE"]["sxy"].shape,(18,4))

    def test_prespecified_comparisons_use_conventional_signed_deltas(self):
        x={"GLOBAL":10,"NEAR_TRUE":8,"FAR_TRUE":9,"NEAR_ROT1":11,"NEAR_STALE_0.2S":9.5,"G_geometry":12}
        c=summaries_from_mse(x)
        self.assertEqual(c["NEAR_ADDITIONAL_BEYOND_GLOBAL"],2)
        self.assertEqual(c["TRUE_NEAR_VERSUS_ROTATED_ONE"],3)
        self.assertEqual(c["TRUE_NEAR_VERSUS_FAR3"],1)
        self.assertEqual(c["CURRENT_NEAR_VERSUS_AGE02_NEAR"],1.5)
        self.assertEqual(c["FAR3_ADDITIONAL_BEYOND_GLOBAL"],1)
        self.assertEqual(BASELINE_ABS_MAX_ERROR,.02)

    def test_exact_2021_source_source_roster_no_future_leakage(self):
        f,p=fake_source()
        cohort=frozen_original_source_clock_and_cohort(f,p)
        self.assertGreater(len(cohort),300)
        cur=original_panels(f,p)
        changed=p.copy()
        changed[-4:,:,0]+=1e4
        after=original_panels(f,changed)
        for k in PANELS:
            np.testing.assert_array_equal(cur["X"][k],after["X"][k])
        self.assertEqual(set(EXPECTED_V32),{"short","delayed"})

if __name__=="__main__":unittest.main()
