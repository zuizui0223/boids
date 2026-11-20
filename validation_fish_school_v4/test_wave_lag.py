import unittest, numpy as np
from wave_lag_observability import decode24,lag_corr,AudioStop
class TestAudioLag(unittest.TestCase):
 def test_signed_24bit(self):
  raw=bytes([0,0,0,255,255,127,0,0,128,255,255,255])
  x=decode24(raw)
  self.assertAlmostEqual(x[0],0)
  self.assertGreater(x[1],.99)
  self.assertEqual(x[2],-1)
  self.assertLess(x[3],0)
 def test_known_truth_shift(self):
  rng=np.random.default_rng(10);x=rng.normal(size=4096);y=np.roll(x,20)
  lag,correlation=lag_corr(x,y)
  self.assertLess(abs(abs(lag)-.625),.033)
  self.assertGreater(correlation,.6)
 def test_unmatched_windows(self):
  with self.assertRaises(AudioStop):lag_corr(np.ones(100),np.ones(90))
if __name__=="__main__":unittest.main()
