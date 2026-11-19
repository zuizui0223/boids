"""v34 original published file source-structure tests; synthetic, no wild values."""
import io,zipfile,unittest
from original_dryad_source_gate import signature,inspect_zip,acquire,run

def fake_zip(kind):
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        site=("Hormiguero","Okolhuitz","Corriental")
        for i in range(3):
            for j in range(8):
                if kind=="raw":
                    body="ID,timestamp,lat,long\n"+"\n".join(f"bat{j},2021-10-11 21:00:{k:02d},12,13" for k in range(100))
                else:
                    body="sensor,timestamps,coords.x1,coords.x2\n"+"\n".join(f"interpolateTime,2021-10-11 21:00:{k:02d},12,13" for k in range(100))
                z.writestr(f"{site[i]}/track{j}.csv",body)
    return b.getvalue()

class SourceGateTests(unittest.TestCase):
    def test_html_200_does_not_qualify_as_zip(self):
        self.assertEqual(signature(b"<!DOCTYPE html><html>Validating...</html>"),"HTML_NOT_ZIP")
    def test_fake_original_schema_without_numeric_outcomes(self):
        r=inspect_zip(fake_zip("raw"),"raw_original")
        self.assertEqual(r["status"],"STRUCTURE_CHECKED")
        self.assertEqual(r["csv_file_count"],24)
        self.assertEqual(r["source_row_count"],2400)
        self.assertEqual(r["original_fix_schema_csv_count"],24)
        self.assertEqual(len(r["site_tokens_in_original_filenames"]),3)
        self.assertFalse(r["numeric_movement_coordinate_or_HMM_values_interpreted"])
    def test_processed_is_not_raw_independent_positions(self):
        r=inspect_zip(fake_zip("processed"),"processed_interpolated")
        self.assertEqual(r["processed_interpolation_schema_csv_count"],24)
        self.assertEqual(r["original_fix_schema_csv_count"],0)
    def test_official_source_gate_requires_both_files(self):
        def f(url):
            if "5036051" in url:return 200,"application/zip",fake_zip("processed")
            return 200,"application/zip",fake_zip("raw")
        d=run(f)
        self.assertEqual(d["admission"],"SCHEMA_READY_NEEDS_BAT_ID_MAPPING")
        self.assertFalse(d["behavior_model_fitted"])
        self.assertFalse(d["source_animal_movement_outcomes_opened"])
    def test_all_blocked_is_transport_not_biology(self):
        d=run(lambda url:(200,"text/html",b"<html>Validating...</html>"))
        self.assertEqual(d["admission"],"SOURCE_ACCESS_OR_STRUCTURE_STOP")
        self.assertEqual(d["sources"]["raw_original"]["status"],"ORIGINAL_ZIP_ACCESS_STOP")

if __name__=="__main__":
    unittest.main()
