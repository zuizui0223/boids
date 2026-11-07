"""v58 runner invariants: preserve complete prior v57 original field result."""
import unittest
from copy import deepcopy
from run_phase_sign_switch_field import EXPECTED_V57_TRANSLATED,check_prior_cross_site_replay

class PriorFieldReplay(unittest.TestCase):
    def make(self,route):
        ref=EXPECTED_V57_TRANSLATED[route]
        return {"status":"OBSERVED_CROSS_ISLAND_YEAR_TRANSFER",
                "source_gate":{"training_rows":ref["source_train"],
                               "test_rows":ref["target_test"],
                               "test_birds":ref["target_birds"]},
                "conditions":{"translated":{
                    "status":"OBSERVED_CROSS_ISLAND_ANGULAR_TRANSFER",
                    "metrics":{"equal_bird":{"model_mean_losses":{
                        key:{"absolute_angle_degrees":val}
                        for key,val in ref["angles"].items()}}}}}}
    def test_replay_both_exact_original_site_direction_forecasts(self):
        for route in EXPECTED_V57_TRANSLATED:
            audit=check_prior_cross_site_replay(route,self.make(route))
            self.assertTrue(audit["prior_v57_translated_angles_exactly_replayed"])

    def test_original_old_cohort_and_angle_drifts_stop_before_phase_switch(self):
        for route in EXPECTED_V57_TRANSLATED:
            ref=self.make(route)
            ref["source_gate"]["test_rows"]+=1
            with self.assertRaisesRegex(ValueError,"COUNTS_DRIFT"):
                check_prior_cross_site_replay(route,ref)
            changed=self.make(route)
            changed["conditions"]["translated"]["metrics"]["equal_bird"][
                "model_mean_losses"]["Mactual"]["absolute_angle_degrees"]+=.00001
            with self.assertRaisesRegex(ValueError,"ANGLE_CHANGED"):
                check_prior_cross_site_replay(route,changed)

    def test_old_transfer_fitted_model_must_be_admitted(self):
        x=self.make("schiermonnikoog_to_ameland")
        x["status"]="NOT_ADMITTED"
        with self.assertRaisesRegex(ValueError,"NO_LONGER_ADMITTED"):
            check_prior_cross_site_replay("schiermonnikoog_to_ameland",x)
        with self.assertRaises(ValueError):
            check_prior_cross_site_replay("unregistered_transfer",x)
if __name__=="__main__":unittest.main()
