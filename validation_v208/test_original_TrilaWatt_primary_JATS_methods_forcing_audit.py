import unittest
import xml.etree.ElementTree as ET
from validation_v208.original_TrilaWatt_primary_JATS_methods_forcing_audit import (
    ORIGINAL_DOI, ORIGINAL_PMCID, EXPECTED_TITLE,
    strictly_original_XML, validate_identity, original_method_gates,
    source_only_conclusion_gates, fetch_true_open_access_JATS
)

def synthetic_paper():
    paragraphs=[
      "Some relevant review research statements no false scores." for _ in range(70)
    ]
    paragraphs[0]="Hydrodynamic data were gridded to approximately 500 m and stored in a netCDF format in 20-minute intervals."
    paragraphs[1]="The provided coordinates are longitude and latitude, the height reference system is NHN (German chart datum), which is equivalent to NAP."
    paragraphs[2]="Sea surface elevations at the open boundary were reconstructed from global FES 2014b tidal constituents."
    paragraphs[3]="Observational sea surface elevations of gauges Helgoland and Roscoff were used to match regional water level bias."
    paragraphs[4]="We compared the simulated sea surface elevation against observations at tide gauges."
    paragraphs[5]="Modeled extreme tidal high water events improved after the switch in atmospheric forcing to ICON-EU in the year 2019."
    return (
      '<article><front><article-meta>'
       f'<article-id pub-id-type="doi">{ORIGINAL_DOI}</article-id>'
       f'<article-id pub-id-type="pmcid">{ORIGINAL_PMCID}</article-id>'
       f'<title-group><article-title>{EXPECTED_TITLE}</article-title></title-group>'
      '</article-meta></front><body><sec>'+
      ''.join('<p>'+p+'</p>' for p in paragraphs)+
      '</sec></body></article>'
    ).encode()

class OriginalPrimarySourceGates(unittest.TestCase):
    def test_synthetic_source_original_identity_and_six_source_methods(self):
        root=strictly_original_XML(synthetic_paper())
        ident=validate_identity(root)
        self.assertEqual(ident["original_DOI"],ORIGINAL_DOI)
        parsed=original_method_gates(root)
        self.assertTrue(parsed["all_six_methods_documented_in_primary_text"])
        self.assertEqual(len(parsed["facts"]),6)
        conclusion=source_only_conclusion_gates({
          "primary_publication_identity":ident,
          "primary_source_methods":parsed})
        self.assertTrue(conclusion["published_product_reference_NHN_equivalent_NAP"])
        self.assertTrue(conclusion["published_model_atmospheric_forcing_break_in_2019"])
        self.assertTrue(conclusion["published_observational_gauge_dependencies_exist"])
        self.assertFalse(conclusion["native_WMS_Wasserstand_units_and_original_FillValue_verified"])
        self.assertFalse(conclusion["three_specific_RWS_gauges_excluded_from_model_calibration_and_validation"])
        self.assertFalse(conclusion["source_applicable_bird_tide_solar_causal_mechanism_estimated"])

    def test_open_access_source_url_must_be_exact_frozen_DOI(self):
        with self.assertRaisesRegex(ValueError,"UNFROZEN"):
            fetch_true_open_access_JATS("https://example.org/any-source")
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            validate_identity(strictly_original_XML(synthetic_paper().replace(
                ORIGINAL_DOI.encode(),b"10.1038/nontrilawatt")))

    def test_reject_untrusted_HTML_or_entity_payload(self):
        with self.assertRaisesRegex(ValueError,"NOT_JATS"):
            strictly_original_XML(b"<html><head></head><body></body></html>")
        with self.assertRaisesRegex(ValueError,"DTD"):
            strictly_original_XML(b'<!DOCTYPE p [ <!ENTITY xx SYSTEM "file:///etc/passwd">]><article>&xx;</article>')

    def test_missing_model_transition_is_explicitly_failed_not_filled(self):
        root=strictly_original_XML(synthetic_paper().replace(b"ICON-EU",b"no-model-name"))
        parsed=original_method_gates(root)
        self.assertFalse(parsed["all_six_methods_documented_in_primary_text"])
        self.assertFalse(parsed["facts"]["2019_atmospheric_forcing_ICON_EU_switch"][
            "at_least_one_true_primary_original_paragraph"])

if __name__=="__main__":
    unittest.main()
