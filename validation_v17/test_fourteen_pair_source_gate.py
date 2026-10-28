"""v17-D source-only original 2026 pigeon pair GPS known-truth tests."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

import fourteen_pair_source_gate as m


class FourteenPairsSource(unittest.TestCase):
    def test_pinned_author_commit_and_two_git_blob_hashes(self):
        self.assertEqual(m.REV,"8e4f7e48abfa57212c5207c28580003f0ef14210")
        self.assertEqual(m.PAIR_BLOB_SHA1,"8c607d535e549fb72f0863b616e28cac24d031f7")
        self.assertEqual(m.ZIP_BLOB_SHA1,"0b1bd66f08c1cac5f8ca582f289d49c43f553bfa")
        self.assertEqual(m.ZIP_BYTES,21425810)

    def test_git_blob_digest_is_not_plain_file_sha1(self):
        v=b"hello world\n"
        self.assertEqual(m.git_blob_digest(v),
            hashlib.sha1(f"blob {len(v)}\0".encode()+v).hexdigest())
        self.assertNotEqual(m.git_blob_digest(v),hashlib.sha1(v).hexdigest())

    def test_published_fourteen_pair_identity_graph_no_shared_birds(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"pair.csv"
            p.write_text(
                "Bird,Partner,Pair_ID,Additional_training_site\n"+
                "".join(f"B{i:02d},S{i:02d},O{i},{'SH' if i%2 else 'LH'}\n"
                        for i in range(1,15)),encoding="utf-8")
            g=m.independent_pair_assignments(p)
        self.assertEqual(g["original_published_pair_ID_count"],14)
        self.assertEqual(g["distinct_individual_IDs"],28)
        self.assertTrue(g["passes_pair_component_source_gate"])
        self.assertTrue(g["source_pairs_have_no_shared_individuals"])
        self.assertEqual(g["individual_GPS_rows_analyzed"],0)

    def test_reusing_partner_across_pairs_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"pair.csv"
            p.write_text("Bird,Partner,Pair_ID,Additional_training_site\n"+
                         "".join(f"B{i:02d},{'S01' if i==14 else 'S'+str(i).zfill(2)},O{i},SH\n"
                                 for i in range(1,15)))
            with self.assertRaisesRegex(ValueError,"Duplicate/missing"):
                m.independent_pair_assignments(p)

    def test_zip_headers_are_not_animal_trajectories(self):
        with tempfile.TemporaryDirectory() as root:
            z=Path(root)/"gps.zip"
            with zipfile.ZipFile(z,"w") as f:
                f.writestr("CM_trimmed/bird01_siteLH_train_2024.csv",
                           "DT,Latitude,Longitude,Course,Speed.km.h.,DistRS,DistHome\n"+
                           "2024-06-01T13:01:02,51.31,-1.42,280,40,200,2000\n")
                f.writestr("CM_trimmed/bird02_siteLH_train_2024.csv",
                           "DT,Latitude,Longitude,Course,Speed.km.h.,DistRS,DistHome\n"+
                           "2024-06-01T13:01:03,51.32,-1.41,280,41,220,1980\n")
            q=m.archive_inventory(z)
        self.assertTrue(q["GPS_DT_column_listed"])
        self.assertTrue(q["GPS_lat_lon_course_columns_listed"])
        self.assertEqual(q["physical_csv_files"],2)
        self.assertFalse(q["raw_positions_or_courses_read"])
        self.assertFalse(q["observed_route_memory_scores_computed"])


if __name__=="__main__":
    unittest.main()
