"""v26b source-header fixtures, artificial only."""
import unittest
from validation_fish_school_v26.source_semantics import semantics,SourceStop


def synthetic(n=3200,nonfinite=0,duplicate=False):
    heads=["frame"]+[f"{p}{i}" for i in range(1,9) for p in ("x","y")]
    if duplicate:heads[-1]=heads[-2]
    lines=[" ".join(heads)]
    for j in range(n):
        tokens=[str(j)]
        for col in range(16):
            tokens.append("NA" if nonfinite and j%nonfinite==0 and col==0 else str(j/10+col))
        lines.append(" ".join(tokens))
    return ("\n".join(lines)+"\n").encode()


class FrozenSourceSemanticFixtures(unittest.TestCase):
    def test_17_columns_8_individuals(self):
        out=semantics(synthetic())
        self.assertEqual(out["n_observation_rows"],3200)
        self.assertEqual(out["native_column_count"],17)
        self.assertEqual(out["complete_eight_fish_coordinate_rows"],3200)
        self.assertEqual(out["original_frame_step_plus_one_fraction"],1.)
        self.assertFalse(out["raw_position_values_exported"])

    def test_original_missingness_kept_not_interpolated(self):
        out=semantics(synthetic(nonfinite=7))
        self.assertLess(out["complete_eight_fish_fraction"],1.)
        self.assertGreater(out["n_missing_fish_coordinate_tokens"],0)
        self.assertEqual(out["original_school_mapping"],"UNVERIFIED")

    def test_duplicate_header_stops(self):
        with self.assertRaises(SourceStop):semantics(synthetic(duplicate=True))

    def test_zero_usable_rows_stops(self):
        with self.assertRaises(SourceStop):semantics(b"frame x1\n1 2\n")

    def test_bad_shape_source_gate(self):
        b=synthetic()
        h,r=b.split(b"\n",1)
        fields=h.split()
        with self.assertRaises(SourceStop):
            semantics(b" ".join(fields[:-1])+b"\n"+r)


if __name__=="__main__":
    unittest.main()
