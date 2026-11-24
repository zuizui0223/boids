"""v32 known-truth source-free exact sufficient moments and 12-group leakage gates."""
from __future__ import annotations
import unittest
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from validation_fish_school_v32.moment_loo import (
    file_moment,sum_moments,train_only_standardized_ridge,score_file_moment,
    group_heldout,bootstrap_group_differences,spearman_descriptive,SourceStop
)
from validation_fish_school_v30.harmonized_forecast import MODEL_NAMES


def synthetic(seed=42,n=2000,p=16):
    rng=np.random.default_rng(seed)
    x=rng.normal(0,1,(n,p))
    x[:,0]*=50
    x[:,1]+=1200
    x[:,2]=1.       # train-constant / StandardScaler 1 convention
    a=rng.normal(size=(p,4))
    y=x@a+rng.normal(0,2,(n,4))+np.array([200,10,-20,7])
    return x,y


class MomentBackendTruth(unittest.TestCase):
    def test_exact_train_only_std_ridge_and_heldout_file_mse(self):
        for p in (14,16):
            X,Y=synthetic(n=5500,p=p)
            train=file_moment(X[:4000],Y[:4000])
            held=file_moment(X[4000:],Y[4000:])
            B,a=train_only_standardized_ridge(train)
            numerical=score_file_moment(held,B,a)
            s=StandardScaler().fit(X[:4000])
            m=Ridge(alpha=10.).fit(s.transform(X[:4000]),Y[:4000])
            pred=m.predict(s.transform(X[4000:]))
            target={
                "short":np.mean((pred[:,:2]-Y[4000:,:2])**2),
                "delayed":np.mean((pred[:,2:]-Y[4000:,2:])**2)}
            for h in target:
                self.assertAlmostEqual(numerical[h]/target[h],1.,delta=1e-6)

    def test_sum_moments_reproduces_direct_two_recording_source(self):
        X,Y=synthetic(n=6000)
        m1=file_moment(X[:3000],Y[:3000])
        m2=file_moment(X[3000:],Y[3000:])
        pooled=sum_moments([m1,m2])
        raw=file_moment(X,Y)
        self.assertEqual(pooled["n"],raw["n"])
        np.testing.assert_allclose(pooled["sx"],raw["sx"],rtol=1e-10)
        np.testing.assert_allclose(pooled["sxx"],raw["sxx"],rtol=1e-10)
        np.testing.assert_allclose(pooled["sxy"],raw["sxy"],rtol=1e-10)

    def test_no_source_file_left_in_train_shoals(self):
        groups={}
        files={}
        for group in range(1,13):
            for j in range(7):
                name=f"{(group-1)*7+j+1:02d}.txt"
                groups[name]=str(group)
                fake={}
                for k in MODEL_NAMES:
                    dim=14 if k=="G_geometry" else 16
                    x,y=synthetic(seed=100+group*7+j,n=1200,p=dim)
                    fake[k]=file_moment(x,y)
                files[name]=fake
        report=group_heldout(files,groups,{"source":"synthetic-only"})
        self.assertEqual(report["n_original_trial_files"],84)
        self.assertEqual(report["n_original_heldout_biological_shoals"],12)
        for r in report["source_group_holdout_results"]:
            self.assertFalse(r["train_test_shoal_overlap"])
            self.assertNotIn(r["original_heldout_shoal_ID"],r["train_shoal_IDs"])
            self.assertEqual(r["n_source_train_shoals"],11)
            self.assertEqual(r["n_original_trial_files_heldout"],7)
        self.assertFalse(report["fish_acoustic_calls_or_causal_social_transfer_observed"])

    def test_any_incomplete_84_or_group_not_admitted(self):
        with self.assertRaises(SourceStop):
            group_heldout({}, {}, {"fixture":True})

    def test_negative_or_perfect_signed_spearman_not_relabelled(self):
        self.assertAlmostEqual(spearman_descriptive([1,2,3,4,5,6,7,8],
                          [8,7,6,5,4,3,2,1]),-1)
        self.assertAlmostEqual(spearman_descriptive([1,2,3,4,5,6,7,8],
                          [1,2,3,4,5,6,7,8]),1)

    def test_bootstrap_resamples_exactly_twelve_real_group_scores(self):
        data=np.arange(12,dtype=float)
        c=bootstrap_group_differences(data)
        self.assertLess(c[0],c[1])
        with self.assertRaises(SourceStop):
            bootstrap_group_differences(np.arange(84))

    def test_future_coordinates_not_required_from_new_source(self):
        x,y=synthetic()
        x[25,3]=np.nan
        with self.assertRaises(SourceStop):
            file_moment(x,y)

    def test_source_recording_with_too_few_fish_frames_stops(self):
        x,y=synthetic(n=500)
        with self.assertRaises(SourceStop):
            file_moment(x,y)


if __name__=="__main__":unittest.main()
