"""v26c fake source identities and missing sentinels."""
import unittest
from validation_fish_school_v26.source_column_diagnostic import schema_only,SourceStop


def make_firstcol(kind="partial",n=3100):
    hdr=["Frame"]+[f"{axis}_{i}" for i in range(8) for axis in ("X","Y")]
    records=[" ".join(hdr)]
    for i in range(n):
        frame=("NA" if kind=="allmissing" else "NaN" if kind=="partial" and i%2 else str(i))
        records.append(" ".join([frame]+[str(i+j) for j in range(16)]))
    return ("\n".join(records)+"\n").encode()


class Diagnostic(unittest.TestCase):
    def test_half_source_clock_missing_wont_be_false_pass(self):
        o=schema_only(make_firstcol())
        self.assertEqual(o["column_0_finite_fraction"],0.5)
        self.assertEqual(o["original_complete_eight_fish_XY_rows"],3100)
        self.assertEqual(o["frame_column_identity"],"NOT_VERIFIED")
        self.assertEqual(o["column_0_nonnumeric_string_frequencies"][0][0],"NaN")

    def test_allmissing_clock_keeps_source_schema_only(self):
        o=schema_only(make_firstcol("allmissing"))
        self.assertEqual(o["column_0_finite_count"],0)
        self.assertFalse(o["original_coordinates_or_model_effect_exported"])

    def test_missing_header_blocks_source(self):
        with self.assertRaises(SourceStop):schema_only(b"Frame X Y\n")


if __name__=="__main__":unittest.main()
