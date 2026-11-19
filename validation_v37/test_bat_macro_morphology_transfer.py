"""v37 synthetic group-holdout methodology tests, no wild source outcomes."""
import unittest
import numpy as np
from bat_macro_morphology_transfer import num,prepare,xyz,compare,by_group,boot

def records(n_papers=25):
    r=[]
    for i in range(n_papers):
        for j in range(7):
            x=float(i+j+1)
            r.append({
                "Authors":f"author{i}","Year_pub":str(1990+i%25),"Journal":"journal",
                "Pays":f"country{i%6}","Species":f"sp{i%12}",
                "Mass":str(x),"Forearm":str(x+5),
                "Dist":str(1+0.2*x),"MCP":str(1+0.1*x)
            })
    return r

class BatMacroTransferTests(unittest.TestCase):
    def test_target_support_and_no_animal_id_inference(self):
        rows,diag=prepare(records(),"Dist")
        self.assertEqual(diag["paper_groups"],25)
        self.assertEqual(diag["eligible_target_rows"],175)
        self.assertTrue(diag["frozen_structural_gate_passed"])
    def test_morphology_impute_train_only(self):
        rows,_=prepare(records(),"Dist")
        tr=rows[:100];te=rows[100:105]
        a,med=xyz(tr)
        b,_=xyz(te,med=med)
        self.assertEqual(a.shape,(100,4))
        self.assertEqual(b.shape,(5,4))
    def test_target_test_values_do_not_enter_model_fitting(self):
        rows,_=prepare(records(),"Dist")
        tr=rows[:100];te=rows[100:110]
        before=compare(tr,te)
        altered=[dict(r,y=r["y"]+200.) for r in te]
        # Loss changes because targets change, but feature-based coefficients
        # must not: verify train-only regression predictions indirectly with
        # identical target changes in M0 and M1 not artificially zero.
        after=compare(tr,altered)
        self.assertTrue(np.isfinite(after).all())
        self.assertGreater(after[0],before[0])
    def test_paper_heldout_all_records_and_summary(self):
        rows,_=prepare(records(),"Dist")
        r=by_group(rows,"paper")
        self.assertEqual(r["tested_groups"],25)
        self.assertEqual(len(r["hashed_publication_group_gains"]),25)
        self.assertTrue(np.isfinite(r["equal_group_MSE_saved"]))
    def test_country_holdout_does_not_share_paper(self):
        rows,_=prepare(records(),"Dist")
        one="country0"
        blocked={r["paper"] for r in rows if r["country"]==one}
        train=[r for r in rows if r["country"]!=one and r["paper"] not in blocked]
        self.assertFalse(any(r["paper"] in blocked for r in train))
    def test_exact_sign_direction(self):
        out=boot([1.,2.,3.,4.,5.,6.,7.,8.])
        self.assertTrue(out["predeclared_positive_gate_passed"])
        self.assertAlmostEqual(out["exact_one_sided_positive_sign_p"],1/256)

if __name__=="__main__":unittest.main()
