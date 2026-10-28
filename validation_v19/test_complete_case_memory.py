"""v19 pre-real-GPS tests for fourteen-to-thirteen source-only fixed cohort."""
import math
import unittest
import numpy as np
import complete_case_memory as v19
import slow_pair_memory as v18


class ExploratorySourceAdmission(unittest.TestCase):
    def test_exclusion_is_fixed_and_old_fourteen_pair_result_frozen(self):
        self.assertEqual(v19.EXCLUDED_SOURCE_NO_CM_PAIR,"O19")
        self.assertEqual(v19.EXPECTED_EVALUATED_PAIRS,13)
        self.assertEqual(v19.ORIGINAL_FULL_PAIR_STOP,
                         "NOT_ADMITTED_ORIGINAL_FILENAME_STAGE_SITE_GATE")
        self.assertEqual(v19.EXPECTED_original_pairs,14)
        self.assertEqual(v18.ORIGINAL_PAIRS,14)
        self.assertEqual(v18.SHELLS,(250,500,750,1000,1250,1500,1750,2000))

    def _generated(self):
        world={}
        pairs=[f"O{i}" for i in range(1,20) if i<=16 or i==19][:14]
        # Real original pairs: O1,O2,O4,O5,O6,O7,O8,O9,
        # O10,O12,O14,O15,O16,O19 = fourteen.
        pairs=["O1","O2","O4","O5","O6","O7","O8","O9",
               "O10","O12","O14","O15","O16","O19"]
        for idx,pair in enumerate(pairs):
            for site in ("LH","SH"):
                main=.3*idx+(0.7 if site=="LH" else -.7)
                for b in (0,1):
                    bird=f"synthetic-{pair}-{b}"
                    for i in range(3):
                        world[(pair,bird,site,"solo","TR",f"TR-{pair}-{site}-{bird}-{i}")]={
                          shell:main+b*.01 for shell in v18.SHELLS}
                    if pair=="O19":
                        continue
                    for i in range(2):
                        world[(pair,bird,site,("pair" if i else "solo"),"CM",
                               f"CM-{pair}-{site}-{bird}-{i}")]={
                            shell:main+b*.01+.001 for shell in v18.SHELLS}
        return world,pairs

    def test_fourteen_train_thirteen_test_known_truth(self):
        world,pairs=self._generated()
        target_pairs=sorted(set(pairs)-{"O19"})
        r=v18.score(world,target_pairs)
        self.assertEqual(r["status"],"EXPLORATORY_14_PAIR_FUTURE_CM_ROUTE_MEMORY_FORECAST")
        self.assertEqual(len(r["per_pair"]),13)
        self.assertNotIn("O19",r["per_pair"])
        self.assertEqual(r["primary_pair_history"]["n_independent_pairs"],13)
        self.assertTrue(np.isfinite(r["primary_pair_history"]["equal_pair_mean_gain_rad2"]))
        # The 14th pair's TR history remains available for the population.
        person,group=v18.build_historic_templates(world)
        base=v18.population_without_pair(group,"O1","LH",250)
        altered={k:x for k,x in world.items() if k[0]!="O19"}
        nextbase=v18.population_without_pair(
            v18.build_historic_templates(altered)[1],"O1","LH",250)
        self.assertNotAlmostEqual(base,nextbase,places=5)

    def test_future_cm_target_change_never_changes_historical_template(self):
        world,_=self._generated()
        before=v18.build_historic_templates(world)
        revised={key:({k:-2. for k in angle} if key[4]=="CM" else angle)
                 for key,angle in world.items()}
        self.assertEqual(before,v18.build_historic_templates(revised))

    def test_missing_second_pair_stops_rather_than_drop(self):
        world,pairs=self._generated()
        later={k:r for k,r in world.items() if not(
            k[0]=="O1" and k[4]=="CM")}
        out=v18.score(later,sorted(set(pairs)-{"O19"}))
        self.assertEqual(out["status"],"NOT_ADMITTED_FROZEN_CM_ROUTE_SUPPORT")
        self.assertFalse(out["any_prediction_score_exported"])

    def test_pair_site_categorical_source_stays_identical_to_v18(self):
        line="18-C46_Site_SH_pair*_Checked_TR_2024-06-16 13:05:07.csv"
        self.assertEqual(v18.file_identity(line)[2:4],("pair","TR"))


if __name__=="__main__":
    unittest.main()
