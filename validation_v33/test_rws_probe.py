"""No tide or animal movement data: source-only request fixtures."""
import unittest
import rws_probe as m
class SourceProbe(unittest.TestCase):
    def test_only_rws_source_and_fixed_three_queries(self):
        self.assertEqual(len(m.PROBES),3)
        self.assertEqual(m.PROBES[0][0],"schiermonnikoog.waddenzee")
        self.assertEqual(m.PROBES[0][1],"astronomisch")
        self.assertEqual(m.PROBES[1][1],"meting")
        self.assertEqual(m.PROBES[2][0],"lauwersoog.waddenzee")
    def test_fixed_winter_timezone_and_aquo_codes(self):
        p=m.payload(*m.PROBES[0])
        self.assertEqual(p["Locatie"]["Code"],"schiermonnikoog.waddenzee")
        self.assertEqual(p["AquoPlusWaarnemingMetadata"]["AquoMetadata"]["Grootheid"]["Code"],"WATHTE")
        self.assertTrue(p["Periode"]["Begindatumtijd"].endswith("+01:00"))
    def test_source_shape_no_tide_values(self):
        shape=m.inspect_shape({"WaarnemingenLijst":[{
            "Locatie":{"Code":"schiermonnikoog.waddenzee","Naam":"Schiermonnikoog"},
            "MetingenLijst":[{"Tijdstip":"2010-05-11T23:10:00Z","Meetwaarde":{"Waarde_Numeriek":99999}},
                             {"Tijdstip":"2010-05-11T23:20:00Z","Meetwaarde":{"Waarde_Numeriek":100}}]}]})
        self.assertEqual(shape["lists"][0]["measurement_count"],2)
        self.assertNotIn("99999",str(shape))
        self.assertNotIn("Waarde_Numeriek",str(shape.get("values","")))
    def test_reject_unfrozen_requests(self):
        with self.assertRaises(ValueError):
            m.payload("random_spot","meting","a","b")

if __name__=="__main__":unittest.main()
