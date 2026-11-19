"""Offline known-truth structural tests; never opens real bat outcomes."""
import unittest
from dryad_original_source_gate import audit_structure, download_original, run, REQUIRED

class DryadStructureTests(unittest.TestCase):
    def synth(self,nsite=8,nrows=48,duplicate=False):
        headers=list(REQUIRED)
        out=[",".join(headers)]
        for i in range(nsite):
            for k in range(nrows):
                d={c:"1" for c in headers}
                d.update({
                    "id_site":str(i),
                    "IdTraj":str(k if not (duplicate and k==nrows-1) else k-1),
                    "Species_corrected":"sp"+str(i%4),
                    "guild":"g"+str(i%2),
                    "meanBuzz":"0.8","meanVfinal":"4.4",
                    "Conspecific_sp":str(k%2),
                    "Heterospecific_intraMRE":str(k%3==0).lower(),
                    "Heterospecific_inter_nonMRE":str(k%3==1).lower(),
                })
                out.append(",".join(d[c] for c in headers))
        return {"data":"\n".join(out),"delimiter":","}
    def test_fixed_nonoutcome_structure(self):
        r=audit_structure(self.synth())
        self.assertEqual(r["status"],"STRUCTURAL_PASS_ONLY")
        self.assertEqual(r["source_row_count"],384)
        self.assertEqual(r["site_count"],8)
        self.assertEqual(r["focal_species_count"],4)
        self.assertFalse(r["source_data_outcome_numeric_values_accessed"])
    def test_trajectory_duplicates_stop_without_deleting(self):
        r=audit_structure(self.synth(duplicate=True))
        self.assertEqual(r["status"],"GRAIN_STOP")
        self.assertGreater(r["duplicate_site_trajectory_id_n"],0)
    def test_no_favorable_threshold_relaxation(self):
        r=audit_structure(self.synth(nsite=4))
        self.assertEqual(r["status"],"SUPPORT_STOP")
        self.assertFalse(r["frozen_structure_gate_conditions"]["at_least_8_sites"])
    def test_unavailable_source_is_not_ecological_negative(self):
        def bad(url):raise ConnectionError("blocked")
        r=run(bad)
        self.assertEqual(r["status"],"SOURCE_ACCESS_STOP")
        self.assertTrue(r["no_universality_claim"])
        self.assertFalse(r["source_data_outcome_numeric_values_accessed"])
    def test_download_uses_only_known_official_endpoint_and_csv(self):
        original=self.synth()
        text=original["data"].replace(",",";")
        def fetch(url):
            self.assertIn("datadryad.org",url)
            return 200,"text/plain",text.encode("utf-8")
        z=download_original(fetch)
        self.assertEqual(z["status"],"ORIGINAL_CSV_RETRIEVED")
        self.assertEqual(z["delimiter"],";")
        self.assertEqual(len(z["sha256"]),64)

if __name__=="__main__":
    unittest.main()
