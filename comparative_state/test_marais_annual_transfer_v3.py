"""Synthetic known-truth verification; not original ecological outcomes."""
import math, unittest
import numpy as np
from .marais_annual_transfer_v3 import (column_index,score_models,build_transitions,
                                         WATER,VEG,YEARS)

class MaraisKnownTruth(unittest.TestCase):
 def test_excel_col_refs(self):
  self.assertEqual(column_index('BJ92'),61)
  self.assertEqual(column_index('BF30'),57)
  self.assertEqual(column_index('A2'),0)
 def test_empty_annum_no_transition(self):
  z={k:0 for k in WATER+VEG}
  a={(1,2018):{'site':1,'year':2018,'environment':z,'total':0,'abund':np.zeros(48)},
     (1,2019):{'site':1,'year':2019,'environment':z,'total':8,'abund':np.ones(48)}}
  self.assertEqual(build_transitions(a),[])
 def test_site_gate(self):
  t=[{'site':i,'year':2019,'prev':np.ones(48),'nprev':48,'next':np.ones(48),
      'nnext':48,'change':{k:0. for k in WATER+VEG}} for i in range(11)]
  self.assertEqual(score_models(t)['status'],'PRIMARY_NOT_ADMITTED')
 def test_known_truth_water_signal(self):
  rng=np.random.default_rng(77)
  tr=[]
  for site in range(18):
   for yr in YEARS:
    x=float(rng.uniform(-1.,1.))
    # Last year's class probabilities uniform; next year favors species 0 or 1
    p=np.zeros(48)+.002
    if x>0:p[0]=.75
    else:p[1]=.75
    p/=p.sum()
    y=rng.multinomial(120,p)
    prev=np.zeros(48)+2.;prev[0]=10;prev[1]=10
    tr.append({'site':site,'year':yr,'prev':prev,'nprev':int(prev.sum()),
         'next':y.astype(float),'nnext':int(y.sum()),
         'change':{k: (x if k=='WA.mean' else 0.) for k in WATER+VEG}})
  v=score_models(tr)
  self.assertEqual(v['status'],'VALID_ORIGINAL_SITE_HELDOUT_ASSEMBLAGE_RESULTS')
  self.assertGreater(sum(r['gain_M1_water'] for r in v['site_results']),0)

if __name__=='__main__':unittest.main()
