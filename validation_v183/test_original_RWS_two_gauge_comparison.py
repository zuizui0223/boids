import unittest
from datetime import datetime,timedelta,timezone
from validation_v183.original_RWS_two_gauge_comparison import freeze_sites,original_nap_series,physical_gauge_contrast,SourceStop

class TrueSourceGates(unittest.TestCase):
    def test_unique_fixed_stations(self):
        rows=[{"Naam":f"Other {i}","Code":f"other{i}"} for i in range(50)]
        rows.extend([{"Naam":"Vlieland haven","Code":"vlieland.haven"},
                    {"Naam":"West-Terschelling","Code":"west.terschelling"}])
        self.assertEqual(freeze_sites({"LocatieLijst":rows})[1]["code"],"west.terschelling")
        rows.append({"Naam":"West Terschelling","Code":"duplicate"})
        with self.assertRaises(SourceStop):freeze_sites({"LocatieLijst":rows})
    def test_reject_LAT_not_NAP(self):
        bad={"Succesvol":True,"WaarnemingenLijst":[{"AquoMetadata":{
            "Grootheid":{"Code":"WATHTE"},"Eenheid":{"Code":"cm"},"Hoedanigheid":{"Code":"LAT"}
        },"MetingenLijst":[]} ]}
        with self.assertRaises(SourceStop):original_nap_series(bad)
    def test_contemporaneous_difference(self):
        zero=datetime(2018,6,1,tzinfo=timezone.utc)
        a={zero+timedelta(minutes=10*i):math.sin(i*.03) for i in range(288)}
        b={t:x+0.3 for t,x in a.items()}
        r=physical_gauge_contrast(a,b)
        self.assertEqual(r["exact_original_UTC_timestamps_both"],288)
        self.assertAlmostEqual(r["absolute_height_difference_m_median"],.3,places=6)

import math
if __name__=="__main__":
    unittest.main()
