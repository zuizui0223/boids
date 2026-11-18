import unittest
from validation_v187.original_RWS_15_fixed_seaward_sites import CODE,freeze_selected,SourceStop
from validation_v185.original_fifteen_wadden_gauge_inventory import ATLAS
class FrozenSourceCodes(unittest.TestCase):
    def test_no_data_driven_site_switch(self):
        self.assertEqual(len(CODE),15)
        self.assertEqual(len(set(CODE.values())),15)
        self.assertEqual(CODE["WestTerschelling"],"terschelling.west")
        self.assertEqual(CODE["VlielandHaven"],"vlieland.haven")
        self.assertIn("buiten",CODE["DenOever"])
        self.assertIn("waddenzee",CODE["Kornwerderzand"])
    def test_all_fixed_codes_present_behind_native_names(self):
        fake=[{"Naam":f"Other {i}","Code":f"other{i}"} for i in range(50)]
        fake.extend([{"Code":CODE["DenOever"],"Naam":"Den Oever spuisluis buiten",
                      "Coordinatenstelsel":"ETRS89","X":None,"Y":None}])
        selected=freeze_selected({"LocatieLijst":fake})
        self.assertEqual(len(selected),15)
        self.assertEqual(next(x for x in selected if x["reference_2011_station"]=="DenOever")["status"],
                         "NAME_ONLY_SOURCE_CODE_MATCH")
        self.assertEqual(next(x for x in selected if x["reference_2011_station"]=="Harlingen")["status"],
                         "STOP_FIXED_ORIGINAL_CODE_NOT_UNIQUE_OR_MISSING")
    def test_duplicate_provider_code_stops(self):
        fake=[{"Naam":f"Other {i}","Code":f"other{i}"} for i in range(50)]
        fake.extend([{"Code":CODE["DenHelder"],"Naam":"Den Helder Marsdiep"}]*2)
        selected=freeze_selected({"LocatieLijst":fake})
        self.assertEqual(selected[0]["status"],"STOP_FIXED_ORIGINAL_CODE_NOT_UNIQUE_OR_MISSING")
if __name__=="__main__":unittest.main()
