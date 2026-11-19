"""v48 known-truth official README/CSV header-only and no effort claims."""
import json
import unittest
from nabat_readme_manifest_header_gate import audit,source_field_names,ITEM_ID

def fake_item():
    return {"id":ITEM_ID,"files":[
        {"name":"README.md","size":150,"downloadUri":"https://www.sciencebase.gov/catalog/file/get/abc?f=README.md"},
        {"name":"nabat-acoustic-data-manifest-20261015.csv","size":50000,
         "downloadUri":"https://www.sciencebase.gov/catalog/file/get/abc?f=manifest.csv"},
    ]}

def source_reader(url,cap,method_range=None):
    if "format=json" in url:
        return 200,"application/json","",json.dumps(fake_item()).encode(),"https://www.sciencebase.gov/catalog/item/abc"
    if "README.md" in url:
        return 200,"text/plain","",b"Acoustic recorder survey start and end times; detector site metadata.",url
    assert method_range==16384
    header=b"site_id,survey_start,survey_end,auto_species,manual_species,audio_filename\n"
    body=header+b"\x00"*(16384-len(header))
    return 206,"text/csv","bytes 0-49999/50000",body,url

class V48SourceTests(unittest.TestCase):
    def test_semantic_original_header_fields_only(self):
        d=source_field_names(b"site_id,survey_start,recording_time,species_label,source_project\n123,2021-01-01,test\n")
        self.assertEqual(d["status"],"SOURCE_FIRST_LINE_HEADERS_ONLY")
        self.assertEqual(d["header_field_count"],5)
        self.assertGreater(d["semantic_field_category_counts"]["survey"],0)
        self.assertFalse(d["original_record_values_opened"])
        self.assertNotIn("2021-01-01",str(d))
    def test_original_docs_and_bounded_manifest_header_is_not_effort(self):
        d=audit(source_reader)
        self.assertEqual(d["status"],"README_AND_MANIFEST_HEADERS_SOURCE_ONLY")
        self.assertFalse(d["true_zero_detector_nights_or_effort_denominators_verified"])
        self.assertTrue(d["USFWS_2010_2018_record_overlap_unresolved"])
        self.assertFalse(d["animal_audio_or_numeric_species_values_read"])
    def test_ignore_range_200_rejected(self):
        def no_range(url,cap,method_range=None):
            if method_range is None:return source_reader(url,cap,method_range)
            return 200,"text/csv","",b"site,date\nA,2021\n",url
        d=audit(no_range)
        self.assertEqual(d["status"],"README_OR_MANIFEST_SOURCE_FILE_ACCESS_STOP")
        self.assertEqual(d["source_file_schema_receipts"]["manifest_1"]["status"],"MANIFEST_RANGE_UNVERIFIED_STOP")
    def test_non_usgs_download_uri_never_fetches(self):
        source=fake_item()
        source["files"][0]["downloadUri"]="https://evil.test/roost"
        def proxy(url,cap,method_range=None):
            if "format=json" in url:return 200,"application/json","",json.dumps(source).encode(),url
            if "evil.test" in url:raise AssertionError("should never be called")
            return source_reader(url,cap,method_range)
        d=audit(proxy)
        self.assertEqual(d["source_file_schema_receipts"]["readme"]["status"],"PUBLISHED_URL_OUTSIDE_OFFICIAL_SOURCE_STOP")
        self.assertFalse(d["bat_behavior_prediction_fitted"])
    def test_wrong_source_item_is_access_stop(self):
        def wrong(url,cap,method_range=None):
            return 200,"application/json","",b'{"id":"wrong","files":[]}',url
        d=audit(wrong)
        self.assertEqual(d["status"],"OFFICIAL_ITEM_JSON_SOURCE_ACCESS_STOP")

if __name__=="__main__":
    unittest.main()
