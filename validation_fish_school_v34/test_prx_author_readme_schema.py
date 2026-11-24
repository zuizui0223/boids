"""v34e artificial original source ZIP README-only safe inspection gates."""
import hashlib,io,zipfile,unittest
from validation_fish_school_v34.prx_author_readme_schema import (
  inspect_readme,one_zip_readmes,SourceStop,run)

def zipfake(rows):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for p,x in rows:z.writestr(p,x)
    return b.getvalue()

class OriginalReadmeOnlySource(unittest.TestCase):
    def test_original_PRX_fig_zip_ONLY_README_not_exp_or_sim_tracks(self):
        raw=zipfake([
            ("Figs/Fig2/README.txt",b"Experimental trajectories: traj_exp.dat\ncolumns: time real fish virtual fish\n"),
            ("Figs/Fig2/traj_exp.dat",b"FAKE REAL FISH POSITIONS NEVER READ"),
            ("Figs/FigS3/traj_sim.dat",b"FAKE SIMULATED NEVER READ"),
            ("Figs/FigS3/README.txt",b"Simulation, do not treat as experimental fish\n"),
        ])
        out=one_zip_readmes(raw,31378621)
        self.assertEqual(out["original_total_verified_README_only_members"],2)
        self.assertFalse(out["original_non_README_data_or_code_member_contents_read"])
        self.assertFalse(out["original_trajectory_exp_sim_and_figure_data_member_contents_read"])
        self.assertEqual(len(out["source_README_member_descriptors_only"]),2)
        self.assertEqual(out["source_README_member_descriptors_only"][0]["source_descriptor_term_occurrence_counts_only"]["experiment_trajectory_file"],1)

    def test_original_code_zip_only_two_exact_READMEs(self):
        raw=zipfake([
            ("Model code/Readme.txt",b"Original source schema only\n"),
            ("Model code/Parameters/README STEPHANE.txt",b"Input parameter metadata\n"),
            ("Model code/Model_3D_VR _SCAN.py",b"PY CODE MUST NOT LOAD"),
        ])
        out=one_zip_readmes(raw,31386349)
        self.assertEqual(out["original_total_verified_README_only_members"],2)
        self.assertFalse(out["original_non_README_data_or_code_member_contents_read"])

    def test_parent_directory_in_original_archive_stops(self):
        raw=zipfake([("../Figs/README.txt",b"TRAVERSAL")])
        with self.assertRaises(SourceStop):
            one_zip_readmes(raw,31378621)

    def test_no_readme_original_zip_stops(self):
        raw=zipfake([("Figs/Fig2/traj_exp.dat",b"DO NOT READ")])
        with self.assertRaises(SourceStop):
            one_zip_readmes(raw,31378621)

    def test_real_fish_clocks_conditions_are_descriptors_not_effect(self):
        x=inspect_readme(b"data columns: frame, real fish id, virtual fish id\n", "Figs/Fig2/README.txt")
        self.assertGreater(x["source_descriptor_term_occurrence_counts_only"]["source_column"],0)
        self.assertGreater(x["source_descriptor_term_occurrence_counts_only"]["physical_time"],0)
        self.assertFalse(x["original_source_readme_full_text_redistributed"])
        self.assertFalse(x["original_source_numerical_figure_or_trajectory_member_read"])

    def test_missing_both_original_provider_records_fails_closed(self):
        def inaccessible(article): raise SourceStop("TEST_ONLY_AUTHOR_SOURCE_STOP")
        d=run(fetchmeta=inaccessible)
        self.assertEqual(d["status"],"SOURCE_ACCESS_STOP")
        self.assertFalse(d["original_fish_trajectory_member_bodies_loaded"])
        self.assertFalse(d["real_fish_trial_or_virtual_controller_treatment_outcomes_fitted"])

if __name__=="__main__":unittest.main()
