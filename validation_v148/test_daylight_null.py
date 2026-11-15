"""Source-free exact arithmetic assertions: do not query actual fish outcomes."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from same_day_diel import overlap,add_group,fresh,score_pair
from collections import defaultdict

def filled(keys):
    groups=defaultdict(fresh)
    for key,typ in keys:
        add_group(groups,key,typ)
    return groups

class TestDailyDiel(unittest.TestCase):
    def test_group_conditioned_expected(self):
        g=filled([("d",("Bocaccio",)),("d",("UF440",))])
        self.assertEqual(overlap(g,"Bocaccio","UF440"),(0,0.5))
    def test_day_night_can_remove_false_overlap_expectation(self):
        days=filled([("date",("Bocaccio",)),("date",("UF440",))])
        light=filled([(("date","day"),("Bocaccio",)),(("date","night"),("UF440",))])
        self.assertEqual(overlap(days,"Bocaccio","UF440"),(0,0.5))
        self.assertEqual(overlap(light,"Bocaccio","UF440"),(0,0))
    def test_joint_overlap_agrees_despite_null_change(self):
        g1=filled([("d",("Bocaccio","UF440")),("d",()),("d",()),("d",())])
        g2=filled([("d1",("Bocaccio","UF440")),("d2",()),("d2",()),("d2",())])
        a=score_pair("Bocaccio","UF440",g1,g2,g2)
        self.assertEqual(a["same_hour_observed"],1)
        self.assertEqual(a["E_same_local_date"],0.25)
        self.assertEqual(a["E_same_local_date_and_astronomical_light"],1.0)
        self.assertEqual(a["O_over_E_date"],4.0)
    def test_bad_mismatched_observed_caught(self):
        g1=filled([("d",("Bocaccio","UF440"))])
        g2=filled([("d",("Bocaccio",))])
        with self.assertRaises(AssertionError):
            score_pair("Bocaccio","UF440",g1,g2,g1)

if __name__=="__main__":unittest.main()
