import unittest
from validation_v186.original_RWS_catalogue_alias_probe import candidates_for_target,report_candidates
from validation_v185.original_fifteen_wadden_gauge_inventory import ATLAS
class ProbeTests(unittest.TestCase):
    def test_alias_detects_suffixed_station_but_does_not_auto_choose(self):
        r=[{"Naam":"Harlingen Haven","Code":"h1","Coordinatenstelsel":"EPSG:28992","X":156480,"Y":576550},
           {"Naam":"Harlingen outer","Code":"h2"}]
        h=next(x for x in ATLAS if x[0]=="Harlingen")
        c=candidates_for_target(r,h)
        self.assertEqual(len(c),2)
        self.assertTrue(all(k["match_kind"].startswith("ALIAS") for k in c))
    def test_nes_requires_word(self):
        r=[{"Naam":"Nieuw-Nes","Code":"n1"},{"Naam":"Vanessa","Code":"n2"},
           {"Naam":"Nes","Code":"n3"}]
        c=candidates_for_target(r,next(s for s in ATLAS if s[0]=="Nes"))
        self.assertEqual(len(c),2)
    def test_all_atlas_slots_even_if_unavailable(self):
        x=report_candidates({"LocatieLijst":[{"Naam":f"Other {i}","Code":str(i)} for i in range(60)]})
        self.assertEqual(len(x),15)
        self.assertTrue(all(r["n_original_catalogue_name_candidates"]==0 for r in x))
if __name__=="__main__":unittest.main()
