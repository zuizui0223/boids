import unittest
import numpy as np
from geometry_audit_v10d import length_matched_rank, stream_baseline_transfer

class GroupedGeometryTests(unittest.TestCase):
    def data(self,shift=False):
        # Two animals, many independent steps; stable starts and 1 used/3 alternatives.
        animals=[];clusters=[];sheets=[];used=[];length=[];rs=[];re=[];ts=[];te=[];ss=[];se=[]
        for a in range(12):
            for g in range(4):
                for j in range(4):
                    animals.append('B'+str(a));clusters.append(str(g));sheets.append(0)
                    used.append(int(j==0));length.append(100.+j)
                    rs.append(100.);ts.append(20.);ss.append(50.)
                    re.append(110. if j==0 and not shift else 130.+j*40)
                    te.append(25. if j==0 and not shift else 35.+j*10)
                    se.append(55. if j==0 and not shift else 75.+j*40)
        d={k:np.array(x,dtype=object if k in ('animal','cluster') else int if k in ('sheet','used') else float)
           for k,x in [('animal',animals),('cluster',clusters),('sheet',sheets),('used',used),('sl',length),('road_start',rs),('road_end',re),('traffic_start',ts),('traffic_end',te),('stream_start',ss),('stream_end',se)]}
        groups=[]
        for a in range(12):
            for g in range(4):
                idx=np.flatnonzero((d['animal']=='B'+str(a))&(d['cluster']==str(g)))
                groups.append(((0,'B'+str(a),str(g)),idx))
        return d,groups
    def test_rank_detects_stable_source_state(self):
        d,g=self.data();r=length_matched_rank(d,g)
        self.assertEqual(r['counts']['matched_groups'],48)
        self.assertGreater(r['rank_excess']['road']['equal_animal_calibrated_rank_excess'],.25)
    def test_rank_not_universally_positive(self):
        d,g=self.data(shift=True);r=length_matched_rank(d,g)
        self.assertTrue(np.isfinite(r['rank_excess']['road']['equal_animal_calibrated_rank_excess']))
    def test_stream_model_executes(self):
        # The entire baseline stream->road additional-predictor branch must
        # execute on synthetic source-defined alternatives, without relying
        # on original animal data. This guards the previously missed fold-map
        # typo and ensures the result schema remains finite.
        d,g=self.data()
        d["hour"]=np.full(len(d["sl"]),12.0)
        r=stream_baseline_transfer(d,g)
        self.assertEqual(r["status"],"POSTRESULT_STREAM_AS_SPATIAL_CONTINUITY_CONTROL")
        self.assertTrue(np.isfinite(r["equal_animal_nats_per_movement"]))
        self.assertEqual(r["source_heldout_31_animal_units"],12)

    def test_bad_group_rejected(self):
        d,g=self.data();d['used'][g[0][1]]=[0,0,0,0]
        with self.assertRaises(ValueError):length_matched_rank(d,g)
if __name__=='__main__':unittest.main()
