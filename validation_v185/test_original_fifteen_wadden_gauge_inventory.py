import unittest
from validation_v185.original_fifteen_wadden_gauge_inventory import ATLAS,select_fixed_catalogue

class AtlasContracts(unittest.TestCase):
    def test_reference_15_predeclared_unique_rd(self):
        self.assertEqual(len(ATLAS),15)
        self.assertEqual(len({r[0] for r in ATLAS}),15)
        self.assertEqual(len({(r[1],r[2]) for r in ATLAS}),15)
        self.assertTrue(all(100000<r[1]<300000 and 540000<r[2]<630000 for r in ATLAS))
    def test_no_outcome_guided_rescue_of_duplicate_names(self):
        fake=[{"Naam":f"Other {i}","Code":f"other{i}"} for i in range(50)]
        fake +=[{"Naam":"Vlieland haven","Code":"vlieland.haven"},
                {"Naam":"West Terschelling","Code":"wt"}]
        d=select_fixed_catalogue({"LocatieLijst":fake})
        self.assertEqual(next(x for x in d if x["webtics_2011_station_name"]=="VlielandHaven")["match_status"],
                         "SINGLE_NATIVE_RWS_NAME")
        fake +=[{"Naam":"West-Terschelling","Code":"wt2"}]
        d=select_fixed_catalogue({"LocatieLijst":fake})
        self.assertEqual(next(x for x in d if x["webtics_2011_station_name"]=="WestTerschelling")["match_status"],
                         "AMBIGUOUS_MATCH_STOP")
    def test_missing_does_not_create_station(self):
        fake=[{"Naam":f"Other {i}","Code":f"other{i}"} for i in range(50)]
        d=select_fixed_catalogue({"LocatieLijst":fake})
        self.assertEqual(sum(x["match_status"]=="SINGLE_NATIVE_RWS_NAME" for x in d),0)

if __name__=="__main__":unittest.main()
