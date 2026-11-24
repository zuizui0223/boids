"""Original v23 fish source schema tests use constructed MAT objects only."""
import io
import unittest
from unittest.mock import patch
import numpy as np
from scipy.io import savemat
from validation_fish_school_v23 import source_metadata as m


def fixture(var, fish=15):
    a=np.empty((1,10),dtype=object)
    for i in range(10):a[0,i]=np.ones((12,fish))*i
    buf=io.BytesIO()
    savemat(buf,{var:a})
    return buf.getvalue()


class MatSourceGateTests(unittest.TestCase):
    def test_original_git_object_sha_exact(self):
        self.assertEqual(m.gitsha(b"abc"),"f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")

    def test_valid_xy_metadata_only(self):
        b=fixture("some_original")
        with patch.dict(m.FILES,{"test.mat":(len(b),m.gitsha(b),"some_original")},clear=True):
            x=m.inspect_blob("test.mat",b)
        self.assertEqual(x["curated_example"]["source_position_matrix_shape"],[12,15])
        self.assertFalse(x["curated_example"]["individual_positions_read_for_analysis"])
        self.assertEqual(len(x["observed_sha256"]),64)

    def test_changed_byte_blocked_by_git_sha(self):
        b=fixture("some_original")
        with patch.dict(m.FILES,{"test.mat":(len(b),m.gitsha(b),"some_original")},clear=True):
            with self.assertRaises(m.SourceStop):
                m.inspect_blob("test.mat",b[:-1]+bytes([b[-1]^1]))

    def test_missing_xy_cell_is_source_stop(self):
        b=fixture("different")
        with patch.dict(m.FILES,{"test.mat":(len(b),m.gitsha(b),"expected")},clear=True):
            with self.assertRaises(m.SourceStop):
                m.inspect_blob("test.mat",b)

    def test_wrong_fish_count_is_source_stop(self):
        b=fixture("some_original",fish=7)
        with patch.dict(m.FILES,{"test.mat":(len(b),m.gitsha(b),"some_original")},clear=True):
            with self.assertRaises(m.SourceStop):
                m.inspect_blob("test.mat",b)

    def test_all_source_fixtures_never_emit_species_score(self):
        b1=fixture("high")
        b2=fixture("low")
        z=io.BytesIO();savemat(z,{"summary":np.ones((2,4))});b3=z.getvalue()
        files={
            "high.mat":(len(b1),m.gitsha(b1),"high"),
            "low.mat":(len(b2),m.gitsha(b2),"low"),
            "summary.mat":(len(b3),m.gitsha(b3),None)
        }
        blobs={"high.mat":b1,"low.mat":b2,"summary.mat":b3}
        def open_fixture(req,timeout=25):
            return io.BytesIO(blobs[req.full_url.split("/")[-1]])
        with patch.dict(m.FILES,files,clear=True):
            x=m.run(open_fixture)
        self.assertEqual(x["status"],"TWO_CURATED_EXEMPLARS_METADATA_ADMITTED")
        self.assertIsNone(x["observed_third_species_predictive_score"])
        self.assertEqual(x["curated_15_fish_examples"],2)
        self.assertEqual(x["full_5_10_15_fish_study_cohorts"],"NOT_ADMITTED_AUTHOR_REQUEST_REQUIRED")

if __name__=="__main__":unittest.main()
