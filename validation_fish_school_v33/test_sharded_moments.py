"""v33b synthetic-only source serialization correctness, no original fish XY."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
import numpy as np
from validation_fish_school_v33.neighbor_panels import PANELS
from validation_fish_school_v33.aggregate_shoal_shards import restore_file_moments
from validation_fish_school_v33.neighbor_shoal_holdout import file_moments
from validation_fish_school_v30.harmonized_forecast import SourceStop


def artificial_moment_record():
    rng=np.random.default_rng(33077)
    n=1519
    y=rng.normal(size=(n,4))
    G=rng.normal(size=(n,14))
    glo=np.column_stack([G,rng.normal(size=(n,2))])
    panels={"G_geometry":G,"GLOBAL":glo}
    for name in PANELS[2:]:
        panels[name]=np.column_stack((glo,rng.normal(size=(n,2))))
    src={"X":panels,"Y":y}
    return file_moments(src)


def serializable(original):
    return {k:{field:(int(value) if field=="n" else np.asarray(value).tolist())
               for field,value in entry.items()}
            for k,entry in original.items()}


class OriginalShardingIsScientificIdentity(unittest.TestCase):
    def test_complete_serialized_moments_are_exactly_identical(self):
        original=artificial_moment_record()
        roundtripped=json.loads(json.dumps(serializable(original)))
        recreated=restore_file_moments(roundtripped)
        self.assertEqual(set(recreated),set(PANELS))
        for name in PANELS:
            for key in ("n","sx","sxx","sxy","sy","syy"):
                np.testing.assert_array_equal(original[name][key],recreated[name][key])

    def test_drop_a_source_panel_fails_closed(self):
        bad=serializable(artificial_moment_record())
        del bad["NEAR_ROT1"]
        with self.assertRaises(SourceStop):
            restore_file_moments(bad)

    def test_different_future_targets_between_panels_fails_closed(self):
        bad=serializable(artificial_moment_record())
        bad["FAR_TRUE"]["sy"][0]+=10
        with self.assertRaises(SourceStop):
            restore_file_moments(bad)

    def test_source_fish_frame_row_sample_count_inconsistent_fails_closed(self):
        bad=serializable(artificial_moment_record())
        bad["NEAR_TRUE"]["n"]+=1
        with self.assertRaises(SourceStop):
            restore_file_moments(bad)

    def test_non_finite_stats_are_rejected(self):
        bad=serializable(artificial_moment_record())
        bad["NEAR_TRUE"]["sx"][1]=float("nan")
        with self.assertRaises(SourceStop):
            restore_file_moments(bad)

if __name__=="__main__":
    unittest.main()
