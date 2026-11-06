"""Known-truth tests; these are not field evidence."""
import unittest
from datetime import datetime, timedelta, timezone
import numpy as np
from bearing_decomposition import decompose_predictions, summarize_rows, UndefinedBearing

def polar(angle_degrees, radius=1.):
    a = np.deg2rad(np.asarray(angle_degrees, dtype=float))
    return np.column_stack((np.cos(a), np.sin(a))) * np.asarray(radius)[..., None]

class BearingDecompositionTests(unittest.TestCase):
    def test_length_only_improvement_is_not_bearing_improvement(self):
        d = decompose_predictions(polar([0]), polar([0], .4), polar([0], .9))
        self.assertAlmostEqual(d['vector_loss0'][0] - d['vector_loss1'][0], .175)
        self.assertAlmostEqual(d['bearing_component'][0], 0.)
        self.assertAlmostEqual(d['magnitude_component'][0], .175)
        self.assertAlmostEqual(d['cosine_loss0'][0] - d['cosine_loss1'][0], 0.)
        self.assertAlmostEqual(d['angle_degrees0'][0] - d['angle_degrees1'][0], 0.)

    def test_bearing_only_improvement_and_exact_symmetric_allocation(self):
        y, a, b = polar([0, 0]), polar([60, -80], .6), polar([20, -30], .6)
        d = decompose_predictions(y, a, b)
        np.testing.assert_allclose(d['magnitude_component'], 0., atol=1e-14)
        np.testing.assert_allclose(d['bearing_component'], d['vector_loss0']-d['vector_loss1'], atol=1e-14)
        np.testing.assert_allclose(d['angle_degrees0']-d['angle_degrees1'], [40, 50])

    def test_exact_identity_matches_explicit_four_hybrids(self):
        rng = np.random.default_rng(7)
        y = polar(rng.uniform(-180, 180, 250))
        a = polar(rng.uniform(-180, 180, 250), rng.uniform(.02, 1.8, 250))
        b = polar(rng.uniform(-180, 180, 250), rng.uniform(.02, 1.8, 250))
        d = decompose_predictions(y, a, b)
        r0, r1 = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1)
        u0, u1 = a/r0[:,None], b/r1[:,None]
        L = lambda r,u: .5*np.sum((y-r[:,None]*u)**2, axis=1)
        expected_bearing=.5*((L(r0,u0)-L(r0,u1))+(L(r1,u0)-L(r1,u1)))
        expected_magnitude=.5*((L(r0,u0)-L(r1,u0))+(L(r0,u1)-L(r1,u1)))
        np.testing.assert_allclose(d['bearing_component'], expected_bearing, atol=1e-13)
        np.testing.assert_allclose(d['magnitude_component'], expected_magnitude, atol=1e-13)
        np.testing.assert_allclose(d['bearing_component']+d['magnitude_component'], d['vector_loss0']-d['vector_loss1'], atol=1e-13)
        self.assertTrue(np.any(d['radius0']>1))

    def test_direction_only_metrics_invariant_to_prediction_lengths(self):
        y=polar([10, 179, -170]); a=polar([40,-170,10]); b=polar([15,175,5])
        d=decompose_predictions(y,a,b)
        e=decompose_predictions(y,a*np.array([.02,2.,.4])[:,None],b*.71)
        for name in ('cosine_loss0','cosine_loss1','angle_degrees0','angle_degrees1'):
            np.testing.assert_allclose(d[name], e[name], atol=1e-12)
        self.assertAlmostEqual(d['angle_degrees0'][1],11.)
        self.assertAlmostEqual(d['angle_degrees0'][2],180.)

    def test_zero_vector_does_not_invent_a_direction(self):
        with self.assertRaises(UndefinedBearing):
            decompose_predictions(polar([0]), np.zeros((1,2)), polar([0]))
        with self.assertRaises(UndefinedBearing):
            decompose_predictions(polar([0]), polar([0],1e-13), polar([0]))

    def test_invalid_truth_and_shapes_are_not_silently_repaired(self):
        for y,a,b in [(polar([0])*2,polar([0]),polar([0])),
                      (polar([0]), np.array([[np.nan,0.]]),polar([0])),
                      (polar([0]),polar([0,10]),polar([0])),
                      (np.empty((0,2)),np.empty((0,2)),np.empty((0,2)))]:
            with self.assertRaises(ValueError): decompose_predictions(y,a,b)

    def test_equal_bird_and_equal_week_estimands_use_their_own_means(self):
        rows=[]; yy=[]; aa=[]; bb=[]
        for bird, week, count, final_angle in [('A',0,3,0),('B',0,1,90),('A',1,1,90)]:
            for j in range(count):
                rows.append({'id':bird,'t':datetime(2011,1,3,tzinfo=timezone.utc)+timedelta(weeks=week,hours=j)})
                yy.append([1.,0.]); aa.append([0.,1.]); bb.append(polar([final_angle])[0])
        d=decompose_predictions(yy,aa,bb)
        r=summarize_rows(rows,d,bird_draws=100,week_draws=100)
        self.assertAlmostEqual(r['equal_bird']['cosine_loss_gain']['mean'],.375)
        self.assertAlmostEqual(r['equal_week_then_bird']['cosine_loss_gain']['mean'],.25)
        for target in ('equal_bird','equal_week_then_bird'):
            s=r[target]
            self.assertAlmostEqual(s['bearing_component']['mean']+s['magnitude_component']['mean'],s['vector_loss_gain']['mean'])
            self.assertEqual(len(s['cosine_loss_gain']['paired_bootstrap_CI95']),2)
        self.assertEqual(r['n_birds'],2)
        self.assertEqual(r['n_weeks'],2)

    def test_row_alignment_fails_loudly(self):
        d=decompose_predictions(polar([0]),polar([20]),polar([0]))
        with self.assertRaises(ValueError): summarize_rows([],d)

if __name__=='__main__': unittest.main()
