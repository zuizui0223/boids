import csv,io,unittest
from watlas_published_pair_source import heading,source_observability,NEEDED

class WATLASOriginalSourceTests(unittest.TestCase):
    def make_csv(self):
        output=io.StringIO()
        w=csv.DictWriter(output,fieldnames=['TAG','TIME','X','Y','NBS','VARX','VARY','COVXY'])
        w.writeheader()
        for bird,ydiff in [('A',0),('B',10)]:
            for k in range(3):
                w.writerow({'TAG':bird,'TIME':1535700000+30*k,'X':640000+30*k,
                            'Y':5900000+ydiff,'NBS':4,'VARX':16,'VARY':24,'COVXY':0})
        return output.getvalue().encode()
    def test_original_source_schema_and_30second_history(self):
        r=source_observability(self.make_csv())
        self.assertEqual(r['number_original_source_rows'],6)
        self.assertEqual(r['source_unique_tag_count'],2)
        self.assertEqual(r['different_tag_near_pair_30sec_bin_within_50m'],3)
        self.assertEqual(r['qualifying_directed_prior_heading_and_future_outcome_pairs'],2)
        self.assertEqual(r['unique_qualifying_dyads'],1)
        self.assertFalse(r['within_tide_exploratory_source_eligible'])
        self.assertEqual(r['independent_multitide_social_force_admission'],
                         'NOT_ADMITTED_ONE_PUBLISHED_NONRANDOM_TIDE')
    def test_original_localization_rate_eligibility(self):
        self.assertIsNotNone(heading((0,0,0),(30,15,0)))
        self.assertIsNone(heading((0,0,0),(0,15,0)))
        self.assertIsNone(heading((0,0,0),(120,15,0)))
    def test_source_column_contract_required(self):
        self.assertEqual(len(NEEDED),8)
        with self.assertRaises(ValueError):
            source_observability(b'TAG,TIME,X,Y\nA,1535700000,100,200\n')

if __name__=="__main__":unittest.main()
