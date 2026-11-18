import unittest
from validation_v193.original_BAW_TrilaWatt_2018_2019_source_index import (
    OFFICIAL_ROOT,original_links,approved_original_url,
    original_filename_year_candidate,discover_original_files,source_gate
)
class BAWLiveSourceContracts(unittest.TestCase):
    def test_no_filename_invention_source_href_only(self):
        d1=OFFICIAL_ROOT+"2018/"
        d2=OFFICIAL_ROOT+"2019/"
        a=(
            '<html><a href="2018/">2018</a><a href="2019/">2019</a>'
            '<a href="https://evil.example/tides_2018_nl.nc">malicious</a></html>'
        ).encode()
        data={OFFICIAL_ROOT:a,
              d1:b'<a href="tides_2018_nl.nc">original model</a><a href="tides_2018_ger.nc">not Dutch</a>',
              d2:b'<a href="tides_2019_nl.nc">original model</a>'}
        def fake(url):
            return data[url],{"url":url,"source_HTML_SHA256":"test"}
        found=discover_original_files(fake)
        self.assertEqual(found["2018_candidates"],[d1+"tides_2018_nl.nc"])
        self.assertEqual(found["2019_candidates"],[d2+"tides_2019_nl.nc"])
        self.assertTrue(found["index_root_reachable"])
        self.assertTrue(found["all_candidate_files_from_actual_source_href_not_generated"])
    def test_unreachable_index_has_explicit_stop(self):
        def offline(url):
            raise TimeoutError("original host temporarily not responding")
        result=discover_original_files(offline)
        self.assertFalse(result["index_root_reachable"])
        self.assertEqual(result["2018_candidates"],[])
        gate=source_gate(result,{})
        self.assertFalse(gate["original_2018_and_2019_HEAD_metadata_verified"])
        self.assertFalse(gate["local_model_h_at_bird_GPS_source_admitted"])
    def test_strict_link_host_and_no_user_query(self):
        self.assertFalse(approved_original_url("https://evil.example/whatever.nc"))
        self.assertFalse(approved_original_url(OFFICIAL_ROOT+"tides_2018_nl.nc?danger=1"))
        self.assertFalse(original_filename_year_candidate(OFFICIAL_ROOT+"tides_2020_ger.nc",2018))
        self.assertTrue(original_filename_year_candidate(OFFICIAL_ROOT+"tides_2018_nl.nc",2018))
    def test_two_HEAD_years_still_not_admit_native_tide_values(self):
        names={f"{y}_candidates":[OFFICIAL_ROOT+f"tides_{y}_nl.nc"] for y in (2018,2019)}
        names["index_root_reachable"]=True
        heads={str(y):{"http_status":200,
            "final_approved_original_source_url":OFFICIAL_ROOT+f"tides_{y}_nl.nc",
            "Content-Length":1_000_000} for y in (2018,2019)}
        gate=source_gate(names,heads)
        self.assertTrue(gate["original_2018_and_2019_HEAD_metadata_verified"])
        self.assertFalse(gate["native_netCDF_dimensions_time_bbox_and_units_verified"])
        self.assertFalse(gate["original_20m_DEM_z_survey_day_and_datum_verified"])
        self.assertFalse(gate["2019_as_real_time_forecast_available_in_2018"])
if __name__=="__main__":
    unittest.main()
