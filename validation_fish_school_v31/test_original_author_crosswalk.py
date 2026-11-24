"""v31 source-only ORIGINAL author ID crosswalk fixtures, all synthetic only."""
import csv
import io
import json
import unittest

from validation_fish_school_v31.original_author_crosswalk import (
    SourceStop,decode_json,parse_csv_only,unique_table_report,run,URLS,index_filenames
)


def fake84():
    return [f"{i:02d}.txt" for i in range(1,85)]

def csv_fixture(contradictory=False,group_missing=False,trial_id=False):
    raw=io.StringIO()
    w=csv.writer(raw)
    w.writerow(["Video_ID" if not trial_id else "Trial","Group","Day","Polarization"])
    for i in range(1,85):
        w.writerow([i,("G"+str((i-1)%12+1)) if not group_missing else "",i//12,0.7])
    if contradictory:w.writerow([1,"G12",3,0.001])
    return raw.getvalue().encode()

def fake_directory():
    links="".join(f'<a href="{x}">{x}</a>\n' for x in fake84())
    return ('<html><title>Index of /datastore/eidchub/test/</title>'+links+'</html>').encode()

class CrosswalkKnownTruth(unittest.TestCase):
    def test_exact_84_original_source_and_12_author_group_ids(self):
        fields,rows=parse_csv_only(csv_fixture())
        out=unique_table_report(fields,rows,fake84())
        self.assertEqual(out["source_file_to_biological_shoal"],"EXPLICIT_ORIGINAL_AUTHOR_TABLE_JOIN")
        self.assertEqual(out["complete_author_verified_trial_to_group_map"]["n_distinct_original_group_labels"],12)
        self.assertEqual(len(out["complete_author_verified_trial_to_group_map"]["84_file_to_group_ID"]),84)

    def test_contradictory_group_id_same_trial_is_scientific_stop(self):
        fields,rows=parse_csv_only(csv_fixture(contradictory=True))
        out=unique_table_report(fields,rows,fake84())
        self.assertEqual(out["source_file_to_biological_shoal"],"UNVERIFIED")

    def test_84_files_and_12_group_count_alone_cannot_identify_mapping(self):
        fields,rows=parse_csv_only(csv_fixture(group_missing=True))
        out=unique_table_report(fields,rows,fake84())
        self.assertIsNone(out["complete_author_verified_trial_to_group_map"])

    def test_bad_trial_file_join_no_mapping(self):
        fields,rows=parse_csv_only(csv_fixture())
        raw=unique_table_report(fields,rows,[f"{i:02d}.txt" for i in range(30,114)])
        self.assertIsNone(raw["complete_author_verified_trial_to_group_map"])

    def test_invalid_error_html_not_a_source_dataset(self):
        with self.assertRaises(SourceStop):
            parse_csv_only(b"<html><title>access denied</title></html>")

    def test_200_response_json_error_envelope_is_not_fish_metadata(self):
        with self.assertRaises(SourceStop):
            decode_json(json.dumps({"id":123,"identifier":"doi:source",
                                    "message":"You lack permission"}).encode())

    def test_original_directory_names_require_true_84_distinct_and_exact_source_index(self):
        m=index_filenames(fake_directory())
        self.assertEqual(len(m),84)
        with self.assertRaises(SourceStop):
            index_filenames(fake_directory().replace(b"Index of /datastore/eidchub/",b"Data unavailable /"))

    def test_metadata_only_source_stop_no_fabricated_crosswalk(self):
        fake=lambda url,cap: (_ for _ in ()).throw(SourceStop("TEST_ONLY_ACCESS_STOP"))
        res=run(fake)
        self.assertEqual(res["status"],"SOURCE_IDENTITY_NOT_ADMITTED")
        self.assertFalse(res["new_fish_movement_forecast_scored"])
        self.assertFalse(res["original_fish_positions_or_outcome_columns_exported"])
        self.assertEqual(len(res["source_access"]),len(URLS))


if __name__=="__main__":
    unittest.main()
