"""Synthetic only, zero original bat source row content embedded."""
import unittest,math
from molossus_2024_source_capture_LOBO_corrected_v2 import (
 admit_corrected_source
)
def fake_original():
    rows=[]
    # Nine original-source-style, consecutive source 5s group series,
    # one deliberately gapped source series. All invented identities/values.
    for i in range(9):
        for n in range(1,433):
            c=[0,5,40,100][n%4]
            rows.append([f"FAKE-BAT-{i}",str(n),str(41),str(1),
                         str(n%2),str(c),0,0])
    skip=set(range(70,77))
    for n in range(1,419):
        if n in skip:continue
        rows.append(["FAKE-BAT-9",str(n),str(41),str(1),str(n%2),str([0,5,40,100][n%4]),0,0])
    assert len(rows)==4299
    return rows

class TestCorrectedMolossusInterval(unittest.TestCase):
 def test_predeclared_source_row_support(self):
    records,clean,meta=admit_corrected_source(fake_original())
    self.assertEqual(len(records),4299)
    self.assertEqual(len(clean),9)
    self.assertEqual(meta["original_source_biological_bats"],10)
    self.assertEqual(meta["source_bats_with_one_seven_group_gap"],1)
    self.assertEqual(meta["source_anomaly_metadata_only"][0]["original_sec_group_missing_indices"],7)
 def test_correct_5s_exposure_is_1_not_original_numel_field(self):
    rows,clean,meta=admit_corrected_source(fake_original())
    self.assertTrue(all(x["E"]==1 for x in rows))
    self.assertEqual(meta["corrected_observed_5s_exposures_all_ten_bats"],4299)
    self.assertGreater(meta["invalid_previous_source_estimated_exposures"],4299)
 def test_source_conspecific_density_not_divided_by_numel(self):
    rows,_,_=admit_corrected_source(fake_original())
    r=next(x for x in rows if x["C"]==100)
    self.assertEqual(r["density"],100)
    self.assertAlmostEqual(r["z"],1,places=13)
 def test_source_ids_not_serialized_in_summary(self):
    _,_,meta=admit_corrected_source(fake_original())
    self.assertNotIn("FAKE-BAT",str(meta))
    self.assertFalse(meta["original_source_bat_IDs_or_5s_rows_released"])
 def test_source_no_more_than_original_captures(self):
    rows,_,_=admit_corrected_source(fake_original())
    self.assertTrue(all(r["Y"]<=r["A"] for r in rows))
 def test_bad_source_duplicate_group_requires_stop(self):
    rows=fake_original()
    rows[1][1]=rows[0][1]
    with self.assertRaisesRegex(ValueError,"SOURCE_CLEAN_NINE_BAT"):
      admit_corrected_source(rows)
 def test_extra_missing_group_requires_stop(self):
    rows=fake_original()
    key="FAKE-BAT-9"
    i=next(j for j,r in enumerate(rows) if r[0]==key and r[1]=="99")
    rows[i][1]="999"
    with self.assertRaisesRegex(ValueError,"SOURCE_ANOMALY_NO_LONGER_SEVEN_MISSING"):
      admit_corrected_source(rows)

if __name__=="__main__":
 unittest.main()
