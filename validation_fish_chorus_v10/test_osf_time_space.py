import unittest,math
from datetime import datetime,timezone
from osf_time_space import parse_events,pair_indices,meddist,shuffled,test,parse_time,FILE_IDS,SHA
import random
class OriginalSoundTests(unittest.TestCase):
 def test_six_existing_original_shas_locked(self):
    self.assertEqual(len(SHA),6)
    self.assertEqual(set(SHA),set(FILE_IDS))
    self.assertTrue(all(len(x)==64 for x in SHA.values()))
 def test_event_iso_time(self):
    self.assertEqual(parse_time("2019-09-20T16:38:58Z"),
                     datetime(2019,9,20,16,38,58,tzinfo=timezone.utc).timestamp())
 def test_same_label_shuffling_preserves_multiset(self):
    ev=[{"label":"fish","xyz":(float(i),0.,0.),"t":float(i),
         "uncert":[.2,.3,.4],"uid":str(i)} for i in range(9)]
    a=shuffled(ev,random.Random(4),True)
    self.assertEqual(sorted(a),sorted(e["xyz"] for e in ev))
 def test_consecutive_expected_distance(self):
    e=[{"t":i*10.,"xyz":(float(i),0,0),"label":"fish",
         "uncert":[.1,.1,.1],"uid":str(i)} for i in range(8)]
    self.assertEqual(meddist([q["xyz"] for q in e],pair_indices(e)),1.)
    self.assertEqual(test(e,10)["status"],"EXPLORATORY_EVENT_TIME_SPACE_TESTED")
 def test_large_gap_dropped(self):
    e=[{"t":i*200.,"xyz":(float(i),0,0),"label":"fish",
         "uncert":[.1,.1,.1],"uid":str(i)} for i in range(8)]
    self.assertEqual(test(e,10)["status"],"STOP_INSUFFICIENT_NEAR_TIME_AUDIO_LOCALIZATIONS")
 def test_source_dates_without_coordinates_stop_eligibility(self):
    b=b"uuid,time_min_date,x,y,z,label_class,x_err_span,y_err_span,z_err_span\nA,2019-01-01T00:00:00Z,1,2,3,fish,0.1,0.2,0.3\n"
    ev,bad=parse_events(b)
    self.assertEqual(len(ev),1)
    self.assertFalse(bad)
if __name__=="__main__":unittest.main()
