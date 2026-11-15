import unittest
from full9_temporal import conditional_overlap, TYPES, CUTS
class SourceDefinitionTests(unittest.TestCase):
    def test_null_equal_opportunity(self):
        h=set(range(10));a={0,1,2,3,4};b={0,1,5,6}
        obs,exp,n=conditional_overlap(h,a,b,lambda h:0)
        self.assertEqual(obs,2)
        self.assertAlmostEqual(exp,2)
        self.assertEqual(n,1)
    def test_condition_exact_hour(self):
        h=set(range(10));a={0,1,2,3,4};b={0,1,5,6}
        obs,exp,n=conditional_overlap(h,a,b,lambda h:h)
        self.assertEqual((obs,exp,n),(2,2,10))
    def test_same_observed_under_multiple_nulls(self):
        hours=set(range(100))
        a=set(range(30))
        b=set(range(0,30,2)) | set(range(40,60))
        ref=conditional_overlap(hours,a,b,lambda h:0)[0]
        conditional=conditional_overlap(hours,a,b,lambda h:(h//24,h%12))[0]
        self.assertEqual(ref,conditional)
    def test_empty_detection(self):
        obs,exp,n=conditional_overlap(set(range(10)),set(),set(),lambda h:h%2)
        self.assertEqual((obs,exp,n),(0,0,2))
    def test_original_spec(self):
        self.assertEqual(len(TYPES),5)
        self.assertEqual(CUTS,(-0.833,-6.0))
if __name__=="__main__":unittest.main()
