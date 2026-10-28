"""v16 data-format probe only, no animal movement outcomes."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import format_gate as m


class FormatContract(unittest.TestCase):
    def test_mask_eliminates_literal_source_timestamps(self):
        self.assertEqual(m.mask_format("2016/08/05"),"DDDD/DD/DD")
        self.assertEqual(m.mask_format("14:02:33.200"),"DD:DD:DD.DDD")
        self.assertNotIn("14:02",m.mask_format("14:02:33.200"))

    def test_exact_18_original_column_names_locked(self):
        self.assertEqual(len(m.SOURCE_COLUMNS),18)
        self.assertEqual(m.SOURCE_COLUMNS[7],"MS")
        self.assertEqual(m.SOURCE_COLUMNS[12],"ALTITUDE")

    def test_synthetic_source_schema_profile_is_aggregate_only(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"fixture.zip"
            with zipfile.ZipFile(path,"w") as z:
                for f in range(1,9):
                    for release in (1,2,3):
                        row=["1","test","SPS","2016/08/05","14:02:33",
                             "2016/08/05","15:02:33","200",
                             "51.8051","N","1.3551","W","30.2",
                             "30","120","0","0","0"]
                        content=",".join(m.SOURCE_COLUMNS)+"\n"+(",".join(row)+"\n")*4
                        z.writestr(f"01_{f:02d}_A21_{release:02d}.csv",content)
            result=m.inspect_schema(path)
        self.assertEqual(result["sampled_files"],24)
        self.assertEqual(result["sampled_rows"],96)
        self.assertEqual(result["numeric_parsability_counts"]["ALTITUDE"]["finite"],96)
        self.assertEqual(result["duplicate_raw_utc_tokens_in_sample"],72)
        self.assertFalse(result["movement_outcomes_read"])
        self.assertFalse(result["GPS_altitude_error_calibrated"])
        self.assertNotIn("51.8051",json.dumps(result))
        self.assertNotIn("14:02:33",json.dumps(result))


if __name__=="__main__":
    unittest.main()
