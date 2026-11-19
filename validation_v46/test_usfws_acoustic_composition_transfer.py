"""v46 known-truth seasonal composition, no future-site leakage or false zeros."""
import unittest
import numpy as np
from usfws_acoustic_composition_transfer import (
    date_from_cell,count_int,season_x,predict,model_loss,sign_p,summarize,evaluate,
    CODES
)

def item(site,year,doy,c):
    vec=np.asarray(c,float)
    return {"site":site,"year":year,"doy":doy,"counts":vec,"share":vec/vec.sum()}

class USFWSSourceCompositionTests(unittest.TestCase):
    def test_source_date_serial_and_text(self):
        self.assertEqual(date_from_cell("2015-06-01").year,2015)
        self.assertEqual(date_from_cell("42005").year,2014)
        self.assertIsNone(date_from_cell("unverifiable date"))
    def test_invalid_counts_and_valid_zero(self):
        self.assertEqual(count_int("0"),0)
        self.assertEqual(count_int("24"),24)
        self.assertIsNone(count_int("-1"))
        self.assertIsNone(count_int("1.3"))
        self.assertIsNone(count_int("nan"))
    def test_predictor_never_reads_test_species_response(self):
        train=[]
        for k in range(60):
            species=[0]*14
            species[(k//3)%14]=20
            train.append(item("Train",2015,1+k*5,species))
        test=[item("Held",2016,99,[1]*14)]
        pred0=predict(train,test,"M0")
        pred1=predict(train,test,"M1")
        changed=[item("Held",2016,99,[0]*13+[100])]
        np.testing.assert_allclose(pred0,predict(train,changed,"M0"))
        np.testing.assert_allclose(pred1,predict(train,changed,"M1"))
        self.assertAlmostEqual(float(pred1.sum()),1.0)
        self.assertEqual(pred1.shape,(1,len(CODES)))
    def test_exact_sign_is_whole_site_not_per_night(self):
        self.assertEqual(sign_p(8,8),1/256)
        r=summarize([.1]*8,[1.2]*8,[1.1]*8)
        self.assertEqual(r["positive_heldout_group_n"],8)
        self.assertTrue(r["frozen_primary_positive_gate"])
    def test_missing_source_support_is_not_biological_zero(self):
        r=evaluate([],{"original_classifier_labels_positive_n":0})
        self.assertEqual(r["status"],"SOURCE_RESPONSE_SUPPORT_STOP")
        self.assertTrue(r["no_full_recording_effort_or_species_absence_inferred"])
        self.assertTrue(r["original_source_original_v45_effort_stop_retained"])

if __name__=="__main__":
    unittest.main()
