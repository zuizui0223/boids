import unittest
try:
    from run_fixed_policy_years import check_known_angular
except ImportError:
    check_known_angular=None

class OriginalScalarReplayTests(unittest.TestCase):
    def fake(self,year):
        values={2011:(75.22439202732221,62.009059594352095,72.64143235714869),
                2012:(59.86051001221907,59.8033309479592,58.90134102050317)}[year]
        return {'equal_bird':{'model_mean_losses':{k:{'absolute_angle_degrees':v}
                     for k,v in zip(('M0','Mactual','M365'),values)}}}
    def test_known_2011_and_updated2012_angles_replay(self):
        self.assertIsNotNone(check_known_angular,'source runner replay helper missing')
        for year in (2011,2012):self.assertTrue(check_known_angular(self.fake(year),year))
    def test_score_drift_cannot_be_called_exact_replay(self):
        self.assertIsNotNone(check_known_angular,'source runner replay helper missing')
        wrong=self.fake(2011);wrong['equal_bird']['model_mean_losses']['Mactual']['absolute_angle_degrees']+=.01
        with self.assertRaisesRegex(ValueError,'V53_ANGULAR'):check_known_angular(wrong,2011)
    def test_unexpected_year_rejected(self):
        self.assertIsNotNone(check_known_angular,'source runner replay helper missing')
        with self.assertRaises(ValueError):check_known_angular(self.fake(2011),2013)
if __name__=='__main__':unittest.main()
