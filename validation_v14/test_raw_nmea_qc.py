"""v14 original-source GPS raw NMEA structural quality tests (no ecology fitting)."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

import raw_nmea_qc as m


def nmea(body: str) -> str:
    h = 0
    for c in body:
        h ^= ord(c)
    return "$"+body+"*"+f"{h:02X}"


class TestRawNMEA(unittest.TestCase):
    def test_valid_nmea_and_checksum(self):
        raw = nmea("GNRMC,120001.20,A,5120.1234,N,00010.0000,W,5.1,90.0,261026,,")
        state, result = m.parse_rmc("device-prefix,"+raw)
        self.assertEqual(state,"valid")
        self.assertTrue(m.nmea_checksum_valid(raw))
        self.assertAlmostEqual(result[1],51.33539,places=4)
        self.assertTrue(result[2]<0)

    def test_invalid_checksum_and_fix_status(self):
        raw=nmea("GNRMC,120001.20,A,5120.1234,N,00010.0000,W,5.1,90.0,261026,,")
        self.assertEqual(m.parse_rmc(raw[:-2]+"00")[0],"invalid_checksum")
        void=nmea("GNRMC,120001.20,V,5120.1234,N,00010.0000,W,5.1,90.0,261026,,")
        self.assertEqual(m.parse_rmc(void)[0],"invalid_status")
        self.assertEqual(m.parse_rmc("status text without RMC")[0],"non_rmc")

    def test_invalid_nmea_coords_or_time_do_not_count(self):
        broken=nmea("GPRMC,296001,A,9999.0000,N,00010.0000,W,0,0,261026,,")
        self.assertEqual(m.parse_rmc(broken)[0],"invalid_date_time_or_coordinates")

    def test_haversine_and_nearest_raw_utc_only(self):
        self.assertAlmostEqual(m.haversine_m(0,0,0,0),0.)
        a=[(1000000,0.,0.),(1000100,0.,0.)]
        b=[(1000050,0.,0.),(1000400,0.,1.)]
        r=m.raw_neighbor_coverage(a,b)
        self.assertEqual(r["lag_le_200ms"],2)
        self.assertEqual(r["lag_le_200ms_and_dist_le_10m"],2)
        self.assertEqual(r["lag_le_200ms_and_dist_le_100m"],2)

    def test_sha256_manifest_validation_and_no_coordinates_export(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"records.zip"
            files={
                "data/analysis_trial_01/raw_gps/SB1_GPS.txt":
                     (nmea("GNRMC,120001.00,A,5120.1234,N,00010.0000,W,5.1,90,261026,,")+"\n").encode(),
                "data/analysis_trial_01/raw_attitude/SB1_ZiTai.txt":b"0 0 0 0 0 0 0 0 0 1\n"
            }
            manifest="".join(hashlib.sha256(v).hexdigest()+"  "+k.removeprefix("data/")+"\n" for k,v in files.items())
            with zipfile.ZipFile(path,"w") as z:
                for k,v in files.items():z.writestr(k,v)
                z.writestr(m.ZIP_MANIFEST,manifest)
            with zipfile.ZipFile(path) as z:
                verified=m.verify_members(z)
            self.assertEqual(verified["status"],"all_sensor_members_verified")
            self.assertEqual(verified["sensor_files_verified"],2)
            r=m.inspect_gps_archive(path)
        self.assertEqual(r["status"],"source_only_no_prediction")
        self.assertEqual(r["gps_files"],1)
        self.assertEqual(r["trial_source_quality"]["analysis_trial_01"]["gps_unique_utc_fixes"],1)
        self.assertFalse(r["conditional_3D_niche_admitted"])
        self.assertNotIn("5120.1234",str(r))

    def test_bad_manifest_blocks_original_source(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"bad.zip"
            with zipfile.ZipFile(path,"w") as arc:
                arc.writestr("data/analysis_trial_01/raw_gps/SB1_GPS.txt",b"$GNRMC,invalid\n")
                arc.writestr(m.ZIP_MANIFEST,"0"*64+"  analysis_trial_01/raw_gps/SB1_GPS.txt\n")
            result=m.inspect_gps_archive(path)
        self.assertEqual(result["status"],"STOP_source_member_verification")

    def test_no_guess_if_manifest_format_unknown(self):
        with self.assertRaisesRegex(ValueError,"Unknown checksum"):
            m.parse_manifest("abc,filename.csv")

if __name__=="__main__":
    unittest.main()
