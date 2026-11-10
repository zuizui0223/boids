"""Known truths: v102 only re-shards transport by immutable original UHSLC site ID."""
import unittest
import shard_fixed_original_2018_N00 as s
import merge_2018_original_eight_bands as m
class ExactOriginalSourceShardTruth(unittest.TestCase):
    def test_UID_modulo_three_exhaustive_original_22_no_source_selection(self):
        frame=[{'uid':i,'record_id':100+i} for i in range(1,23)]
        shards=[s.subset_by_source_only_uid(frame,j) for j in range(3)]
        self.assertEqual(sum(len(x) for x in shards),22)
        self.assertEqual({x['uid'] for row in shards for x in row},set(range(1,23)))
        self.assertTrue(all(x['uid']%3==j for j,row in enumerate(shards) for x in row))
    def test_uid_frame_duplicate_refused(self):
        frame=[{'uid':1} for _ in range(22)]
        with self.assertRaisesRegex(ValueError,'FRAME_CHANGED'):
            s.subset_by_source_only_uid(frame,1)
    def test_original_source_biological_missing_must_not_be_zero(self):
        d={'site_outputs':[],
           'source_quality_not_admitted':[{'id':2}],
           'source_failures':[{'id':1,'attempts':[{'code':429}]}]}
        self.assertEqual(sorted(m.counted_ids(d)),[1,2])
        d['site_outputs']=[{'uid':1,'2018_physical':{}}]
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            m.counted_ids(d)
    def test_strict_8_preexisting_authentic_source_files(self):
        with self.assertRaisesRegex(ValueError,'COUNT_NOT_3_PLUS_7'):
            m.merge([],[], 'unused','unused')
    def test_no_year_or_identity_switch(self):
        self.assertEqual(s.ORIGINAL_2019_SOURCE_N,22)
        self.assertEqual(s.N_SHARDS,3)
        self.assertEqual(m.EXPECTED_OTHER,
          {'N_15_30','N_30_45','N_45_60','N_60_75','S_00_15','S_30_45','S_45_60'})
if __name__=="__main__":unittest.main()
