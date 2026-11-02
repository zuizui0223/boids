"""Scientific invariants for the novel synthetic proxy, not animal validation."""
import math
import unittest
import numpy as np
from common_physics_v1 import (
    FS,CHIRP_S,BANDWIDTH_HZ,TAU_S,DT_S,CORRELATION_CUTOFF,
    RECEIVER_THRESHOLD_DB,PULSE_IPI_MS,ECHO_MARGINS_DB,
    initial_tf,points,receiver_powers,aij,pulse_flags,drift,rk4,
    time_series,chirp,correlations,group_summary,run)

class TestSourceBoundProxy(unittest.TestCase):
    def test_source_fixed_constants(self):
        self.assertEqual(FS,250_000)
        self.assertEqual(CHIRP_S,.003)
        self.assertEqual(BANDWIDTH_HZ,40_000)
        self.assertEqual(TAU_S,.200)
        self.assertEqual(DT_S,.001)
        self.assertEqual(CORRELATION_CUTOFF,.5)
    def test_source_frequency_overlap(self):
        self.assertEqual(aij(48,48),1)
        self.assertAlmostEqual(aij(48,49.5),.5)
        self.assertEqual(aij(48,51),0)
        self.assertEqual(aij(48,60),0)
        self.assertEqual(aij(48,46),aij(46,48))
    def test_pulse_window(self):
        self.assertFalse(any(pulse_flags(4999,4)))
        self.assertFalse(any(pulse_flags(10000,4)))
        self.assertTrue(pulse_flags(5040,4)[0])
        self.assertFalse(pulse_flags(5044,4)[0])
    def test_initial_frequency_centred(self):
        for n in (4,8):
            self.assertAlmostEqual(sum(initial_tf(n))/n,48)
    def test_disallowed_group(self):
        with self.assertRaises(ValueError):initial_tf(6)
        with self.assertRaises(ValueError):points(4,1.0)
    def test_power_has_physical_ordering(self):
        a=receiver_powers(points(4,.7))
        b=receiver_powers(points(4,3.))
        for i in range(4):
            self.assertEqual(a[i][i],0)
            for j in range(i+1,4):
                self.assertGreater(a[i][j],b[i][j])
                self.assertAlmostEqual(a[i][j],a[j][i])
    def test_rk4_no_forcing_preserves_baseline(self):
        f0=initial_tf(4)
        x=rk4(list(f0),f0,receiver_powers(points(4,.7)),(False,)*4)
        self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(x,f0)))
    def test_forced_source_frequency_nonzero(self):
        f0=initial_tf(4)
        g=receiver_powers(points(4,.7))
        x=drift(f0,f0,g,(True,)*4)
        self.assertGreater(max(abs(t) for t in x),0)
    def test_base_nojar_is_identity(self):
        for n in (4,8):
            x=time_series(n,.7,False)
            self.assertTrue(all(abs(a-b)<1e-10 for a,b in zip(x["late_tf_khz"],x["initial_tf_khz"])))
    def test_end_of_five_second_rest_returns_baseline(self):
        x=time_series(4,.7,True)
        for y,b in zip(x["last_tf_khz"],x["initial_tf_khz"]):
            self.assertLess(abs(y-b),1e-7)
    def test_fm_waveform_normalized(self):
        x=chirp(48)
        self.assertEqual(len(x),round(FS*CHIRP_S))
        self.assertAlmostEqual(float(np.linalg.norm(x)),1,places=12)
        self.assertLess((48_000+BANDWIDTH_HZ),FS/2)
    def test_waveform_correlations_are_symmetric_and_bounded(self):
        c=correlations((47.5,48.,48.8))
        for key in ("zero","lag"):
            self.assertTrue(np.allclose(c[key],c[key].T))
            self.assertTrue(np.all(c[key]>=0))
            self.assertTrue(np.all(c[key]<=1+1e-8))
        self.assertTrue(np.all(c["lag"]+1e-10>=c["zero"]))
    def test_linear_fm_time_frequency_shift_recoverable(self):
        c=correlations((48.,51.))
        self.assertLess(c["zero"][0,1],.5)
        self.assertGreater(c["lag"][0,1],.5)
    def test_large_delta_outside_lag_window(self):
        c=correlations((48.,56.))
        self.assertLess(c["lag"][0,1],.5)
    def test_time_frequency_ambiguity_delay_fixture(self):
        a,b=chirp(48.),chirp(51.)
        cc=np.correlate(a,b,"full")
        lags=np.arange(-len(a)+1,len(a))
        best=abs(float(lags[int(np.argmax(np.abs(cc)))]))/FS
        expected=(3000*CHIRP_S/BANDWIDTH_HZ)
        self.assertLess(abs(best-expected),.00002)
        self.assertGreater(expected*343/2,.03) # 3kHz shift could mimic >3cm range offset
    def test_monotone_prey_margin_under_fixed_receiver(self):
        power=receiver_powers(points(4,.7))
        x=group_summary((47.4,47.8,48.2,48.6),power)
        for mode in ("zero","lag"):
            d=[r["detected_fraction"] for r in x[mode]["echo_detection_by_margin"]]
            self.assertEqual(d,sorted(d))
    def test_no_data_and_no_full_replay_markers(self):
        x=run()
        self.assertFalse(x["source2020_numeric_reproduction"])
        self.assertFalse(x["source2026_group_numeric_reproduction"])
        self.assertFalse(x["added_bat_measurements"])
        self.assertEqual(len(x["worlds"]),4)
        self.assertEqual(len(x["pure_FM_frequency_ambiguity_fixture"]),8)
    def test_both_modes_held_to_same_threshold(self):
        x=run()
        for w in x["worlds"]:
            for tag in ("assay_noJAR","assay_JAR"):
                for mode in ("zero","lag"):
                    d=w[tag][mode]
                    self.assertGreaterEqual(d["confusable_pair_fraction"],0)
                    self.assertLessEqual(d["confusable_pair_fraction"],1)
                    self.assertLessEqual(d["mean_echo_detection_across_margins"],1)

if __name__=="__main__":
    unittest.main()
