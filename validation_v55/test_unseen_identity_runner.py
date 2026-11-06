import unittest
from copy import deepcopy
from run_unseen_identity_transfer import source_years,check_fixed2012_replay,check_gauge_count

class SourceRunnerTests(unittest.TestCase):
    def test_only_fixed_site_years(self):
        self.assertEqual(source_years('ameland'),(2010,2011,2012))
        self.assertEqual(source_years('schiermonnikoog'),(2010,2011))
        with self.assertRaises(ValueError):source_years('new-site')

    def test_2012_full_fixed_policy_replay_exact(self):
        s={'n_rows':1186,'n_birds':3,'equal_bird':{'model_mean_losses':{
            'M0':{'absolute_angle_degrees':69.62997611500825},
            'Mactual':{'absolute_angle_degrees':59.66726851878847},
            'M365':{'absolute_angle_degrees':67.34326266351121}}}}
        self.assertTrue(check_fixed2012_replay(s))
        for alteration in ('rows','angles','nan'):
            bad=deepcopy(s)
            if alteration=='rows':bad['n_rows']=1187
            else:bad['equal_bird']['model_mean_losses']['Mactual']['absolute_angle_degrees']=float('nan') if alteration=='nan' else 61
            with self.assertRaises(ValueError):check_fixed2012_replay(bad)

    def test_original_water_counts_not_current_or_sparse(self):
        for y in (2009,2010,2011):self.assertEqual(check_gauge_count(y,{'gauge_rows':52561}),52561)
        self.assertEqual(check_gauge_count(2012,{'gauge_rows':52705}),52705)
        with self.assertRaises(ValueError):check_gauge_count(2011,{'gauge_rows':50000})
        with self.assertRaises(ValueError):check_gauge_count(2013,{'gauge_rows':52561})

if __name__=='__main__':unittest.main()
