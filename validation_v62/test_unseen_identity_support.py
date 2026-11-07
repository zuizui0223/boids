"""v62 exact source-only identity-disjoint gates on synthetic observations."""
import unittest
from unseen_identity_support import (
    disjoint_2010_training,source_qualified_pair_subset,exact_prior_v61_replay,
    PRIOR_V61_T)

def synthetic_training_and_eval():
    full=[]
    for i in range(13):
        full.extend({"id":f"shared{i}"} for _ in range(493 if i<12 else 487))
    for j in range(8):
        full.extend({"id":f"sourceonly{j}"} for _ in range(188 if j<7 else 192))
    test=[]
    for i in range(13):
        test.extend({"id":f"shared{i}"} for _ in range(380 if i<12 else 388))
    return full,test

def synthetic_pairs():
    counts=[27]*7+[8,7,7]
    test=[]
    pairs=[]
    for i,n in enumerate(counts):
        for _ in range(n):
            a=len(test)
            test.extend(({"id":f"bird{i}"},{"id":f"bird{i}"}))
            pairs.append((a,a+1))
    return test,pairs

class UnseenSourceOnlyTests(unittest.TestCase):
    def test_exact_original_source_counts_and_identity_removal(self):
        full,test=synthetic_training_and_eval()
        kept,receipt=disjoint_2010_training(full,test)
        self.assertEqual((len(full),len(test),len(kept)),(7911,4948,1508))
        self.assertEqual(receipt["disjoint_training_birds"],8)
        self.assertEqual(receipt["literal_train_test_identity_overlap"],0)
        self.assertEqual(receipt["training_rows_removed_for_2011_overlap"],6403)
        for r in test:r.update(target_e=9999,target_n=-9999)
        self.assertEqual(receipt,disjoint_2010_training(full,test)[1])

    def test_too_few_train_rows_is_hard_source_stop(self):
        full,test=synthetic_training_and_eval()
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            disjoint_2010_training(full[:-1],test)
        # Identity filtering is still strict even when test has a new identity.
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            disjoint_2010_training(full,test[:-1])

    def test_qualified_source_only_pairs_are_no_outcome_selected(self):
        test,pairs=synthetic_pairs()
        sub,receipt=source_qualified_pair_subset(test,pairs)
        self.assertEqual(len(pairs),211)
        self.assertEqual(receipt["source_qualified_birds"],7)
        self.assertEqual(receipt["source_qualified_pairs"],189)
        for r in test:r.update(target_e=123456)
        self.assertEqual(sub,source_qualified_pair_subset(test,pairs)[0])

    def test_pair_source_gate_cannot_change_counts(self):
        test,pairs=synthetic_pairs()
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            source_qualified_pair_subset(test,pairs[:-1])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            source_qualified_pair_subset(test,[])
    
    def test_old_source_prediction_exact_replay_control(self):
        self.assertTrue(exact_prior_v61_replay(PRIOR_V61_T))
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            exact_prior_v61_replay(PRIOR_V61_T+.00001)

if __name__=="__main__":
    unittest.main()
