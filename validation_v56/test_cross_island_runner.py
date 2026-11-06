import unittest
from run_cross_island_transfer import gauge_count,compact_metrics,transfer_pairs

class RunnerTests(unittest.TestCase):
    def test_both_reciprocal_pairs_fixed(self):
        self.assertEqual(transfer_pairs(),(('schiermonnikoog','ameland'),('ameland','schiermonnikoog')))
    def test_source_counts_exact_and_only_2009_2011(self):
        for year in (2009,2010,2011):self.assertEqual(gauge_count(year,{'gauge_rows':52561}),52561)
        with self.assertRaises(ValueError):gauge_count(2012,{'gauge_rows':52705})
        with self.assertRaises(ValueError):gauge_count(2011,{'gauge_rows':50000})
    def test_compact_receipt_keeps_all_axes_contrasts_and_estimands(self):
        metric={'n_rows':1001,'n_birds':3,'n_weeks':8,
                'equal_bird':{'model_mean_losses':{'M0':{'absolute_angle_degrees':60}},
                              'contrasts':{'M365_minus_Mactual':{'cosine_loss_gain':{'mean':-.1}}}},
                'equal_week_then_bird':{'contrasts':{'M365_minus_Mactual':{'cosine_loss_gain':{'mean':.2}}}}}
        r=compact_metrics(metric)
        self.assertEqual(r,metric)
        self.assertIsNot(r,metric)
if __name__=='__main__':unittest.main()
