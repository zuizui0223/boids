"""Synthetic archive and source-range admission tests; no real bat records."""
from __future__ import annotations
import io,zipfile,hashlib,unittest
from external_2026_EEG_and_3D_ERTF_source_gate_v1 import (
  central_zip_names,eocd_info,TAIL_BYTES,MAX_CENTRAL,ZIP_NAME,XLSX_NAME
)

def artificial_zip():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",compression=zipfile.ZIP_STORED) as z:
        z.writestr("bat3d/code.zip",b"test fake code")
        z.writestr("bat3d/worlds.zip",b"test fake world")
        z.writestr("bat3d/runs/E1/metrics.json",b"test fake metrics")
        z.writestr("bat3d/source_data/run_table.json",b"test fake data")
    return b.getvalue()

class TestSourceAdmissionBounds(unittest.TestCase):
    def test_zenodo_zip_central_dir_parses_without_data(self):
        archive=artificial_zip()
        meta=eocd_info(archive[-TAIL_BYTES:],len(archive))
        central=archive[meta["directory_offset"]:meta["directory_offset"]+meta["directory_size"]]
        names=central_zip_names(central)
        self.assertEqual(len(names),meta["member_count"])
        self.assertEqual(len(names),4)
        self.assertIn("bat3d/source_data/run_table.json",[x["path"] for x in names])
    def test_source_archive_is_not_unpacked_to_model_results(self):
        archive=artificial_zip()
        meta=eocd_info(archive[-TAIL_BYTES:],len(archive))
        central=archive[meta["directory_offset"]:meta["directory_offset"]+meta["directory_size"]]
        names=central_zip_names(central)
        self.assertEqual(names[0]["uncompressed_bytes"],len(b"test fake code"))
        self.assertNotIn("test fake",str(names))
    def test_strict_no_zip_central_missing_eocd(self):
        with self.assertRaisesRegex(ValueError,"END_OF_CENTRAL"):
            eocd_info(b"no eocd",100)
    def test_corrupted_zip_directory_entry_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_MAGIC"):
            central_zip_names(b"not a zip directory")
    def test_no_gigabyte_download_cap(self):
        self.assertEqual(TAIL_BYTES,131072)
        self.assertEqual(MAX_CENTRAL,2097152)
    def test_sources_are_named_literally(self):
        self.assertEqual(XLSX_NAME,"in_flight_bat_eeg_echolocation_combined_table.xlsx")
        self.assertEqual(ZIP_NAME,"2026 - Steckel - Bats Learn Echolocation.zip")
if __name__=="__main__":
    unittest.main()
