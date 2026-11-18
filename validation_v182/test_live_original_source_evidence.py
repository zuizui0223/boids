import json
import unittest
from validation_v182.live_original_source_evidence import build_report, verify_v174_das

def make_manifest():
    tiles=[]
    for i in range(10):
        tiles.append({"tile": f"T{i}", "das": {"original_provider_provenance": {
            "source_uri_requested": f"https://opendap.deltares.nl/thredds/dodsC/original/T{i}.nc.das",
            "source_metadata_content_SHA256": __import__("hashlib").sha256(b"units m EPSG:28992").hexdigest()
        }}})
    return {"all_original_tile_source_schema_or_STOP": tiles}

class SourceAudit(unittest.TestCase):
    def test_das_horizontal_crs_no_vertical(self):
        out=verify_v174_das(make_manifest(), lambda url: (
            b"units m EPSG:28992",
            {"url":url, "sha256":__import__("hashlib").sha256(b"units m EPSG:28992").hexdigest(),
             "downloaded":True, "bytes":22}
        ))
        self.assertEqual(out["original_DAS_exact_SHA_rechecked"], 10)
        self.assertEqual(out["native_DAS_explicit_NAP_count_verified"], 0)
    def test_missing_source_stops(self):
        def offline(url):
            return None, {"url": url, "sha256": None, "downloaded": False, "error_kind": "offline"}
        report=build_report(make_manifest(), offline)
        self.assertFalse(report["scientific_gates"]["local_water_depth_exposure_or_foraging_mechanism_admitted"])
        self.assertEqual(report["native"]["original_DAS_exact_SHA_rechecked"],0)
        self.assertEqual(report["status"],"STOP_LOCAL_EXPOSURE_AND_BIOLOGICAL_FIT")
    def test_website_class_evidence_never_opens_exposure(self):
        def all_pages(url):
            if url.endswith(".nc.das"):
                data=b"units m EPSG:28992"
            else:
                data=b"Vaklodingen 20x20 NAP waterhoogte_nap Vlieland haven propagation amplitudes phases"
            import hashlib
            return data, {"url":url, "sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"downloaded":True}
        report=build_report(make_manifest(), all_pages)
        self.assertTrue(report["scientific_gates"]["datum_source_class_plausible_NOT_native_cell_calibration"])
        self.assertFalse(report["scientific_gates"]["vertical_datum_at_original_native_z_grid_proven"])
        self.assertFalse(report["scientific_gates"]["local_water_depth_exposure_or_foraging_mechanism_admitted"])

if __name__=="__main__":
    unittest.main()
