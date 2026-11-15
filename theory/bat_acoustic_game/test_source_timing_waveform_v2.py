"""Source timing, physics and no-new-measurement boundaries for v2."""
from __future__ import annotations
import math
import unittest
import numpy as np
from source_timing_waveform_v2 import (
 SOURCE_RESPONSE_PULSE_MS,SOURCE_SOUND_MS,SOURCE_IPI_MEAN,SOURCE_IPI_SD,
 SOURCE_IPI_GAMMA_SHAPE,SOURCE_IPI_GAMMA_SCALE,GROUP_BEGIN_MS,
 GROUP_END_MS,CURVES,SOURCE_SPEED_MS,FREQ_BIN_KHZ,
 initial_tf,source_schedules,source_receiver_drive,source_leaky_slope,
 source_rk4,source_tf_traces,normalized_wave,exact_correlations,
 get_correlations,quantization_audit,evaluate_world
)

class SourceTimingTests(unittest.TestCase):
 def test_source_pulse_lengths_are_separate(self):
  self.assertEqual(SOURCE_RESPONSE_PULSE_MS,5)
  self.assertEqual(SOURCE_SOUND_MS,3)
  self.assertEqual(GROUP_END_MS-GROUP_BEGIN_MS,5000)
 def test_gamma_source_parameters(self):
  self.assertAlmostEqual(SOURCE_IPI_GAMMA_SHAPE*SOURCE_IPI_GAMMA_SCALE,SOURCE_IPI_MEAN,places=12)
  self.assertAlmostEqual(math.sqrt(SOURCE_IPI_GAMMA_SHAPE)*SOURCE_IPI_GAMMA_SCALE,SOURCE_IPI_SD,places=12)
 def test_seeded_schedules_and_positive_spacing(self):
  for n in (4,8):
   x=source_schedules(n,.7)
   self.assertEqual(x,source_schedules(n,.7))
   self.assertEqual(len(x),n)
   for a in x:
    self.assertTrue(len(a)>100)
    self.assertTrue(all(t2-t1>=10 for t1,t2 in zip(a,a[1:])))
 def test_scale_change_does_not_change_seed_branch_convention(self):
  self.assertNotEqual(source_schedules(4,.7),source_schedules(4,3.))
 def test_recv_delay_positive_and_matches_source_c(self):
  n=4;scale=3.
  seq=source_schedules(n,scale)
  d,arr=source_receiver_drive(n,scale,seq)
  self.assertTrue(np.all(d[:GROUP_BEGIN_MS]==0))
  self.assertTrue(np.all(d[GROUP_END_MS:]==0))
  i,j=0,1
  self.assertTrue(arr[i,j] if False else arr[(i,j)])
  self.assertTrue(arr[(i,j)][0]>=seq[j][0])
  self.assertTrue(np.max(d[GROUP_BEGIN_MS:GROUP_END_MS])>0)
 def test_5ms_rectangular_input_occurs_within_window(self):
  n=4;s=.7;seq=source_schedules(n,s)
  drive,arr=source_receiver_drive(n,s,seq)
  i,j=0,1
  a=next(x for x in arr[(i,j)] if x>=GROUP_BEGIN_MS+20)
  self.assertTrue(np.all(drive[a:a+SOURCE_RESPONSE_PULSE_MS,i,j]>0))
  self.assertEqual(float(drive[a+SOURCE_RESPONSE_PULSE_MS,i,j]),0.)
 def test_source_law_rest(self):
  f0=np.asarray(initial_tf(4));d=np.zeros((4,4))
  y=source_rk4(f0,f0,d)
  self.assertTrue(np.allclose(y,f0,atol=1e-12))
 def test_asymmetric_response_source_sign(self):
  f0=np.asarray(initial_tf(4))
  r=np.zeros((4,4));r[0,1]=1;r[1,0]=1
  d=source_leaky_slope(f0,f0,r)
  self.assertLess(d[0],0)
  self.assertGreater(d[1],0)
 def test_no_jar_exact_source_baseline_trace(self):
  n=4;s=.7;seq=source_schedules(n,s)
  t=source_tf_traces(n,s,seq,jar=False)
  self.assertEqual(t.shape,(15001,n))
  self.assertTrue(np.allclose(t,np.asarray(initial_tf(n)),atol=1e-12))
 def test_nonzero_jar_and_post_group_recovery(self):
  n=4;s=.7;seq=source_schedules(n,s)
  t=source_tf_traces(n,s,seq,jar=True)
  f0=np.asarray(initial_tf(n))
  self.assertGreater(np.max(np.abs(t[6000]-f0)),1e-4)
  self.assertLess(np.max(np.abs(t[-1]-f0)),1e-7)
 def test_waveform_width_normalization(self):
  for curve in CURVES:
   x=normalized_wave(48.,curve)
   self.assertEqual(len(x),750)
   self.assertAlmostEqual(np.linalg.norm(x),1,places=10)
 def test_curvatures_are_distinct_models_not_claimed_source(self):
  a=normalized_wave(48.,"linear")
  b=normalized_wave(48.,"power_0p6")
  c=normalized_wave(48.,"power_2p0")
  self.assertLess(abs(np.dot(a,b)),.99)
  self.assertLess(abs(np.dot(a,c)),.99)
 def test_full_lag_crosscorrelation_bounds(self):
  for shape in CURVES:
   for d in (0,1.,3.):
    z,lag=exact_correlations(shape,48.,48.+d)
    self.assertTrue(0<=z<=lag+1e-10)
    self.assertTrue(lag<=1.000001)
    if d==0:self.assertAlmostEqual(lag,1,places=8)
 def test_lookup_exact_near_threshold_fallback(self):
  for shape in CURVES:
   z,l=get_correlations(shape,48.,49.5)
   self.assertGreaterEqual(l,z)
 def test_bounded_cache_preoutput_audit(self):
  err,rows=quantization_audit()
  self.assertEqual(len(rows),3*3*7)
  self.assertTrue(np.isfinite(err))
  self.assertGreaterEqual(err,0)
 def test_world_pairwise_opportunity_is_same_under_jar(self):
  n=4;s=.7;seq=source_schedules(n,s)
  _,arrival=source_receiver_drive(n,s,seq)
  no=source_tf_traces(n,s,seq,False)
  yes=source_tf_traces(n,s,seq,True)
  a=evaluate_world(n,s,"linear",seq,arrival,no,True)
  b=evaluate_world(n,s,"linear",seq,arrival,yes,True)
  self.assertEqual(a["focal_emissions"],b["focal_emissions"])
  self.assertEqual(a["eligible_other_bat_pulses"],b["eligible_other_bat_pulses"])
  for x in (a,b):
   self.assertTrue(x["focal_emissions"]>0)
   self.assertLessEqual(x["zero_count"],x["lag_count"])
   self.assertLessEqual(x["lag_count"],x["eligible_other_bat_pulses"])
 def test_bat_3d_geometry_is_source_extrapolation(self):
  self.assertEqual(len(CURVES),3)
  self.assertEqual(FREQ_BIN_KHZ,.02)
  self.assertGreater(SOURCE_SPEED_MS,300)

if __name__=="__main__":unittest.main()
