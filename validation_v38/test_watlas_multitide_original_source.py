import csv,io,unittest
from watlas_multitide_original_source import NEEDED,source_quality

class PublishedMultiTideSource(unittest.TestCase):
    def make(self):
        out=io.StringIO()
        w=csv.DictWriter(out,fieldnames=['TAG','TIME','X','Y','NBS','VARX','VARY',
                                        'COVXY','tideID','tidaltime','waterlevel'])
        w.writeheader()
        for tide in range(4):
            for bird in range(5):
                for k in range(3):
                    w.writerow({'TAG':f'b{bird}',"TIME":1535700000+tide*86400+k*30,
                                'X':650000+k*30,'Y':5900000+bird*6,
                                'NBS':4,'VARX':10,'VARY':12,'COVXY':0,
                                'tideID':str(tide),'tidaltime':k*.5,
                                'waterlevel':80+k})
        return out.getvalue().encode()
    def test_four_source_tide_cycles_not_four_independent_social_results(self):
        s=source_quality(self.make())
        self.assertEqual(s['original_unique_tideID'],4)
        self.assertEqual(s['original_unique_tags'],5)
        self.assertEqual(s['unique_tag_30s_position_bins'],60)
        self.assertEqual(s['near_tag_position_pairs_30s_50m'],120)
        self.assertEqual(s['directed_prior_headings_and_future_target_eligible'],80)
        self.assertEqual(s['tide_cycles_meeting_10pairs_2dyads'],4)
        self.assertEqual(s['status'],'NOT_ADMITTED_MULTITIDE_SOCIAL')
        self.assertEqual(s['biological_social_cohesion_or_alignment_effect'],'NOT_ESTIMATED')
    def test_tide_identifier_required_as_original_source(self):
        self.assertEqual(len(NEEDED),11)
        with self.assertRaisesRegex(ValueError,"field dictionary"):
            source_quality(b'TAG,TIME,X,Y\nA,1535700000,650000,5900000\n')

if __name__=="__main__":unittest.main()
