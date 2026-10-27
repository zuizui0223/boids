import unittest
import json
from pathlib import Path
import audit_v12 as a

ROOT=Path(__file__).resolve().parent/'results'
class TestAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=json.loads((ROOT/'endogenous_policy_v12.json').read_text())
        cls.null=json.loads((ROOT/'guild_relabel_null_v12.json').read_text())
        cls.family=json.loads((ROOT/'force_family_sensitivity_v12.json').read_text())
    def test_audit_run_has_paired_seeds(self):
        x=a.paired_seed_contrasts(self.main,self.null,self.family,boot_b=500)
        self.assertEqual(x['species_orientation']['n_positive_signed_x_separation']+
                         x['species_orientation']['n_negative_signed_x_separation'],30)
    def test_forged_seed_list_fails(self):
        d=dict(self.main,seeds=list(self.main['seeds'][:-1]))
        with self.assertRaisesRegex(ValueError,'Seed mismatch'):
            a.paired_seed_contrasts(d,self.null,self.family,boot_b=100)
    def test_group_heldout_positive_and_social_effect_not_boids_effect(self):
        x=a.paired_seed_contrasts(self.main,self.null,self.family,boot_b=500)
        k='learning_plus_social__minus__private_learning_plus_boids__guild_patch_gain_nats'
        self.assertGreater(x['paired_differences'][k]['mean_paired_seed_change'],.25)
        null=x['guild_relabel_excess']['learning_plus_social']
        self.assertGreater(null['mean_excess_horizontal_info_over_pair_label_null'],.1)
    def test_report_contains_no_claim_about_wild_flight(self):
        x=a.paired_seed_contrasts(self.main,self.null,self.family,boot_b=500)
        self.assertIn('SYNTHETIC',x['status'])

if __name__=='__main__':unittest.main()
