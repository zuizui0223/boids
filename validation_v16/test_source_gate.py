"""No-network, no-outcome source gate regression tests for v16."""
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import source_gate as m


class SourceContract(unittest.TestCase):
    def test_external_record_is_not_old_v8_or_v15(self):
        self.assertEqual(m.RECORD_ID,4943714)
        self.assertEqual(m.REQUIRED_MD5,"ab0950ffebd924950632f727cd487c27")
        self.assertEqual(m.EXPECTED_SOURCE_FLOCKS,8)
        self.assertNotIn(m.RECORD_ID,(5010830,21092705))

    def test_select_api_file_fail_closed(self):
        a={"id":4943714,"files":[{"key":"Data.zip",
            "size":272_300_000,"checksum":"md5:"+m.REQUIRED_MD5,
            "links":{"self":"https://zenodo.org/api/files/frozen"}}]}
        d=m.select_file(a)
        self.assertEqual(d["name"],"Data.zip")
        self.assertEqual(d["size"],272_300_000)
        with self.assertRaisesRegex(ValueError,"Wrong Zenodo"):
            m.select_file({**a,"id":21092705})
        with self.assertRaisesRegex(ValueError,"MD5"):
            m.select_file({"id":4943714,"files":[{**a["files"][0],"checksum":"md5:"+"0"*32}]})
        with self.assertRaisesRegex(ValueError,"non-Zenodo"):
            m.select_file({"id":4943714,"files":[{**a["files"][0],"links":{"self":"https://evil.example/file"}}]})

    def test_exact_public_example_filename(self):
        self.assertEqual(m.member_identity("Data/01_08_S01_12.csv"),("08","S01",12))
        self.assertEqual(m.member_identity("01_08_S05_08.CSV"),("08","S05",8))
        self.assertIsNone(m.member_identity("Data/undocumented.csv"))

    def _fixture(self, directory, flocks=8, releases=5, birds=3, extra=None):
        path=Path(directory)/"mock.zip"
        with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for f in range(1,flocks+1):
                for b in range(1,birds+1):
                    for rel in range(1,releases+1):
                        header="time,lat,lon\n"
                        data="".join("123,51.2,-1.3\n" for _ in range(11))
                        z.writestr(f"data/01_{f:02d}_S{b:02d}_{rel:02d}.csv",header+data)
            if extra:
                z.writestr(extra,"time,lat,lon\n100,52.2,-1.5\n")
        return path

    def test_eight_flocks_with_releases_are_structurally_admitted(self):
        with tempfile.TemporaryDirectory() as root:
            p=self._fixture(root)
            d=m.inspect_zip(p)
        self.assertEqual(d["csv_files"],120)
        self.assertEqual(d["header_variants"],1)
        self.assertEqual(d["flocks_meeting_repeated_design_gate"],8)
        self.assertTrue(d["all_8_flocks_admitted_for_future_schema_contract"])
        self.assertFalse(d["observed_treatment_schedule_verified"])
        self.assertFalse(d["fast_social_time_sync_admitted"])
        self.assertFalse(d["target_route_scores_computed"])
        self.assertNotIn("51.2",json.dumps(d))
        self.assertEqual(d["total_csv_physical_data_lines"],1320)

    def test_fewer_flocks_or_undocumented_header_stop(self):
        with tempfile.TemporaryDirectory() as root:
            p=self._fixture(root,flocks=7,extra="other.csv")
            d=m.inspect_zip(p)
        self.assertFalse(d["all_8_flocks_admitted_for_future_schema_contract"])
        self.assertEqual(d["unrecognized_csv_filename_count"],1)

    def test_malformed_archive_paths_fail(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("../source.csv","time,lat,lon\n1,2,3\n")
            with self.assertRaisesRegex(ValueError,"Unsafe"):
                m.inspect_zip(p)

    def test_duplicate_archive_member_names_fail(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("01_01_S01_01.csv","time,lat,lon\n1,2,3\n")
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore",UserWarning)
                    z.writestr("01_01_S01_01.csv","time,lat,lon\n1,2,3\n")
            with self.assertRaisesRegex(ValueError,"Duplicate ZIP"):
                m.inspect_zip(p)

    def test_unknown_header_is_not_recast_as_valid_time(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"bad_header.zip"
            with zipfile.ZipFile(p,"w") as z:
                for f in range(1,9):
                    for bird in range(1,4):
                        for release in range(1,6):
                            z.writestr(f"01_{f:02d}_S{bird:02d}_{release:02d}.csv",
                                       "alpha,beta,gamma\n"+("1,2,3\n"*12))
            d=m.inspect_zip(p)
        self.assertEqual(d["flocks_meeting_repeated_design_gate"],8)
        self.assertFalse(d["all_8_flocks_admitted_for_future_schema_contract"])
        self.assertFalse(d["measured_3D_altitude_admitted"])


if __name__=="__main__":
    unittest.main()
