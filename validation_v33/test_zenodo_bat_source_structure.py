"""Known-truth original bat source structure: no behavioral numerical values."""
import io
import unittest
from zenodo_bat_source_structure import analyze_structure, parse_timestamp, original_source, run, REQ


class ZenodoBatOriginalSourceTests(unittest.TestCase):
    def sample(self):
        # Exactly fixed source schema, two track IDs in each of nine site/date recordings.
        lines=[";".join(REQ)]
        for s in range(9):
            for tr in (1,2):
                for k in range(12):
                    vals={x:"1,5" for x in REQ}
                    vals.update({
                        "id_site":f"20220921_site{s}_C_control",
                        "typeSite":"C","date":"2022:09:21",
                        "time":f"20:09:{k:02d}+02:00",
                        "Trajectory_identifier":str(tr),
                        "Species_corrected":"Pipkuh" if tr==1 else "Pipnat",
                        "guild":"MRE","x (m)":"2,3", "y (m)":"4,5",
                        "z (m)":"0,3","Speed":"999",
                        "Imprecision":"0,2","buzz_proba":"999",
                        "mean_buzz_proba":"0,5",
                    })
                    lines.append(";".join(vals[k] for k in REQ))
        return "\n".join(lines)
    def test_source_timestamp_timezone(self):
        t=parse_timestamp("2022:09:21","20:09:01+02:00")
        self.assertEqual(t.hour,20)
        self.assertEqual(t.utcoffset().total_seconds(),7200)
    def test_timing_overlap_is_only_possibility_not_annotated_interaction(self):
        r=analyze_structure(self.sample())
        self.assertEqual(r["possible_different_trajectory_interval_overlap_pairs"],9)
        self.assertEqual(r["site_date_type_recordings_with_possible_overlap"],9)
        self.assertFalse(r["social_interaction_or_continuous_time_overlap_established"])
        self.assertEqual(r["source_structure_status"],"SOURCE_FEASIBILITY_STOP")
        self.assertFalse(r["3d_coordinates_speed_buzz_numeric_values_read"])
    def test_source_metadata_no_numeric_behavior_access(self):
        r=analyze_structure(self.sample())
        self.assertEqual(r["source_raw_event_row_count"],216)
        self.assertEqual(r["source_trajectory_key_count"],18)
        self.assertEqual(r["source_species_labels_n"],2)
        self.assertEqual(r["date_stripped_nominal_locality_n"],9)
        self.assertEqual(r["source_raw_event_row_count"],216)
        self.assertTrue(r["no_biological_effect_or_prediction_computed"])
    def test_fake_zip_or_html_is_md5_stop(self):
        r=original_source(lambda url:(200,"text/html",b"<html>captcha</html>"))
        self.assertEqual(r["status"],"SOURCE_MD5_MISMATCH_STOP")
    def test_error_response_cannot_be_translated_into_ecological_negative(self):
        r=run(lambda url: (_ for _ in ()).throw(OSError("source blocked")))
        self.assertEqual(r["status"],"SOURCE_ACCESS_OR_INTEGRITY_STOP")
        self.assertTrue(r["source_is_not_independent_of_Delmotte_2025"])
        self.assertTrue(r["no_biological_effect_or_prediction_computed"])

if __name__=="__main__":
    unittest.main()
