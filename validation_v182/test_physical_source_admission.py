import unittest
from validation_v182.physical_source_admission import PhysicalSourceEvidence, physical_admission

class AdmissionTests(unittest.TestCase):
    def test_default_is_stop(self):
        self.assertEqual(physical_admission(PhysicalSourceEvidence())["stop_reason"],
                         ["vertical_datum", "local_tide_transfer", "actual_survey_day"])
    def test_horizontal_crs_not_a_vertical_datum(self):
        self.assertFalse(physical_admission(PhysicalSourceEvidence(
            dem_vertical_datum="EPSG:28992", gauge_vertical_datum="NAP",
            dem_datum_original_source_url="source", gauge_datum_original_source_url="source"
        ))["common_vertical_datum_source_verified"])
    def test_harbor_is_not_local_tide(self):
        self.assertFalse(physical_admission(PhysicalSourceEvidence(
            dem_vertical_datum="NAP", gauge_vertical_datum="NAP",
            dem_datum_original_source_url="source", gauge_datum_original_source_url="source",
            source_survey_day_verified=True, survey_day_original_source_url="source"
        ))["local_water_depth_or_exposure_admitted"])
    def test_source_year_is_not_survey_day(self):
        self.assertFalse(physical_admission(PhysicalSourceEvidence(
            dem_vertical_datum="NAP", gauge_vertical_datum="NAP",
            dem_datum_original_source_url="source", gauge_datum_original_source_url="source",
            gauge_to_gps_tidal_transfer_verified=True,
            gauge_to_gps_tidal_transfer_source_url="source"
        ))["local_water_depth_or_exposure_admitted"])

if __name__ == "__main__":
    unittest.main()
