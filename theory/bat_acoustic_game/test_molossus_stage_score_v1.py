import hashlib, io, math, unittest, zipfile
import molossus_stage_score_v1 as model

class TestStageScoring(unittest.TestCase):
    def test_binomial_score_uses_attacks_not_rows(self):
        self.assertAlmostEqual(model.conditional_nll([1,0],[2,0],[.5,.01]), math.log(2))
    def test_no_attack_is_missing_not_zero(self):
        self.assertIsNone(model.conditional_nll([0,0],[0,0],[.2,.8]))
    def test_success_exceeds_attacks_rejected(self):
        with self.assertRaises(ValueError): model.conditional_nll([3],[2],[.5])
    def test_better_success_predictions_lower_loss(self):
        self.assertLess(model.conditional_nll([9],[10],[.9]),model.conditional_nll([9],[10],[.5]))
    def test_package_change_does_not_change_member_identity(self):
        def archive(year):
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w') as z:
                info=zipfile.ZipInfo('pnas.2321724121.sd01.xlsx',(year,1,1,0,0,0))
                z.writestr(info,b'fake xlsx bytes')
            return stream.getvalue()
        a,b=archive(2020),archive(2022)
        sha=hashlib.sha256(b'fake xlsx bytes').hexdigest()
        ra,_=model.inspect_bundle(a,sha);rb,_=model.inspect_bundle(b,sha)
        self.assertNotEqual(ra['zip_sha256'],rb['zip_sha256'])
        self.assertEqual(ra['members'],rb['members'])
    def test_modified_source_workbook_fails_closed(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:z.writestr('pnas.2321724121.sd01.xlsx',b'changed')
        with self.assertRaises(ValueError):model.inspect_bundle(stream.getvalue(),'0'*64)
    def test_equal_bat_summary_not_window_weighted(self):
        out=model.summarize_pairs([(1.,.5),(3.,4.)])
        self.assertEqual(out['baseline_mean'],2.)
        self.assertEqual(out['density_mean'],2.25)
        self.assertEqual(out['difference_mean'],.25)
        self.assertEqual(out['bats_improved'],1)

if __name__=='__main__':unittest.main()
