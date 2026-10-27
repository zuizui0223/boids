"""No-network tests for v14 DOI metadata, observational grain, and no-leakage."""
import csv
import zipfile
import tempfile
import unittest
from pathlib import Path

import source_preflight as v14


class TestFieldPreflight(unittest.TestCase):
    def test_predefined_source_identifiers(self):
        self.assertEqual(v14.ZENODO_ID, "21092705")
        self.assertEqual(v14.DRYAD_DOI, "doi:10.5061/dryad.4tmpg4fp6")
        self.assertIn("Bird", v14.NECESSARY)
        self.assertNotIn("Altitude", v14.NECESSARY)

    def test_extract_version_ids_from_nested_api_links(self):
        source = {"_links": {"stash:versions": {"href":
                  "https://datadryad.org/api/v2/versions/14121"}}}
        self.assertEqual(v14.public_version_ids(source), [14121])

    def test_reject_wrong_digests(self):
        actual = {"md5":"a"*32, "sha256":"b"*64}
        self.assertTrue(v14.compare_source_digest(
            {"digest":"md5:"+"a"*32},actual)["match"])
        self.assertFalse(v14.compare_source_digest(
            {"digest":"md5:"+"c"*32},actual)["match"])
        self.assertIsNone(v14.compare_source_digest({},actual)["match"])

    def _csv(self, root, duplicate=False, bad_time=False, include_extra=False):
        path = Path(root)/"toy.csv"
        with path.open("w",encoding="utf-8",newline="") as f:
            writer = csv.DictWriter(f,fieldnames=list(v14.NECESSARY))
            writer.writeheader()
            for flight in range(1,4):
                for bird in range(6):
                    for counter in range(1,6):
                        row={"Bird":f"B{bird}","Loft":"N","Iteration":str(flight),
                             "Counter":str(counter),
                             "Latitude":"51.2","Longitude":"-0.5",
                             "Time":f"11:00:{(counter-1)//5:02d}",
                             "Date":f"2025-01-0{flight}","Layer":"Open"}
                        if bad_time and bird == 0:
                            row["Time"]=""
                        writer.writerow(row)
                        if duplicate and flight==1 and bird==1 and counter==3:
                            writer.writerow(row)
        return path

    def test_many_repeated_birds_admitted_only_for_future_horizontal_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._csv(tmp)
            d = v14.profile_csv(p)
        self.assertEqual(d["rows"],90)
        self.assertEqual(d["number_distinct_loft_birds"],6)
        self.assertEqual(d["number_bird_flight_trials"],18)
        self.assertEqual(d["birds_with_at_least_3_flights"],6)
        self.assertTrue(d["repeated_horizontal_candidate_admitted_for_next_protocol"])
        self.assertTrue(d["no_altitude"])
        self.assertFalse(d["synchronous_social_steering_admitted"])
        self.assertFalse(d["exact_altitude_niche_admitted"])
        self.assertNotIn("B0",str(d))
        self.assertGreater(d["time_string_repetition_keys"],0)

    def test_duplicate_key_fails_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self._csv(tmp,duplicate=True)
            d=v14.profile_csv(p)
        self.assertEqual(d["duplicate_composite_keys"],1)
        self.assertFalse(d["repeated_horizontal_candidate_admitted_for_next_protocol"])

    def test_rounded_or_missing_times_not_treated_as_high_freq_synchrony(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self._csv(tmp,bad_time=True)
            d=v14.profile_csv(p)
        self.assertEqual(d["missing_field_counts"]["Time"],15)
        self.assertFalse(d["clock_synchronicity_assessed"])
        self.assertFalse(d["synchronous_social_steering_admitted"])

    def test_zip_manifest_is_structural_and_never_reads_animal_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fixture.zip"
            with zipfile.ZipFile(path,"w") as ar:
                ar.writestr("README.md", "Sensors: GPS, IMU. No inference.")
                ar.writestr("flight_001/raw.csv", "Lat,Lon\n12,20\n")
            result=v14.profile_zip_manifest(path)
        self.assertEqual(result["regular_files"],2)
        self.assertEqual(result["observation_rows_processed"],0)
        self.assertEqual(result["forecast_scores_computed"],0)
        self.assertEqual(result["file_extensions"][".csv"],1)
        self.assertIn("Sensors: GPS",result["readme_documents"][0]["readme_excerpt"])
        self.assertNotIn("12,20",str(result))

    def test_zip_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"malicious.zip"
            with zipfile.ZipFile(path,"w") as ar:
                ar.writestr("../outside.csv","a,b\n1,2\n")
            with self.assertRaisesRegex(ValueError,"unsafe member"):
                v14.profile_zip_manifest(path)

    def test_missing_header_blocks_model_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"missing.csv"
            p.write_text("Bird,Loft\n1,L\n",encoding="utf-8")
            d=v14.profile_csv(p)
        self.assertEqual(d["status"],"missing_required_columns")
        self.assertIn("Latitude",d["missing"])


if __name__=="__main__":
    unittest.main()
