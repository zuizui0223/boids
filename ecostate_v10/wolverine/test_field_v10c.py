import io,math,sys,unittest,zipfile,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import field_v10c as f

class FieldTests(unittest.TestCase):
 def test_pinned_source_and_columns(self):
  self.assertEqual(f.SOURCE_SHA256,'979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd')
  self.assertEqual(len(f.H),17)
 def test_flags(self):
  self.assertEqual([f.case_flag(x) for x in ['1','FALSE','True','2']],[1,0,1,-1])
 def test_xml_first_header_and_inline(self):
  xml='<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>cluster</t></is></c><c r="B1" t="inlineStr"><is><t>used</t></is></c></row><row r="2"><c r="A2"><v>3</v></c><c r="B2"><v>1</v></c></row></sheetData></worksheet>'
  with zipfile.ZipFile(io.BytesIO(),mode='w') as z:pass
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('xl/worksheets/sheet1.xml',xml)
  b.seek(0)
  with zipfile.ZipFile(b) as z:
   rr=list(f.rows_from_sheet(z,'xl/worksheets/sheet1.xml',[]))
  self.assertEqual(rr[0][:2],['cluster','used'])
  self.assertEqual(rr[1][:2],['3','1'])
 def test_softmax_gradient(self):
  x=np.array([[0,1],[1,2],[3,0],[1,0],[0,2]],dtype=float)
  sizes=np.array([3,2]);starts=np.array([0,3]);used=np.array([2,4]);w=np.array([.5,.5])
  theta=np.array([.1,-.3]);a,b=f.condloss(theta,x,sizes,starts,used,w,True)
  n=[]
  for i in range(2):
   v=theta.copy();v[i]+=1e-6
   u=theta.copy();u[i]-=1e-6
   n.append((f.condloss(v,x,sizes,starts,used,w)-f.condloss(u,x,sizes,starts,used,w))/2e-6)
  np.testing.assert_allclose(b,n,rtol=1e-5,atol=1e-6)
 def synthetic(self,n=10,g=60,c=6):
  rng=np.random.default_rng(63)
  d={k:[] for k in ('animal','cluster','sheet','used','hour','sl','road_end','road_start','traffic_end','traffic_start','stream_end','stream_start')}
  groups=[]
  for a in range(n):
   for j in range(g):
    start=np.exp(rng.uniform(0,8))-1
    ends=np.exp(rng.uniform(0,8,size=c))-1
    best=int(np.argmin(np.abs(np.log1p(ends)-np.log1p(start))))
    ids=[]
    for k in range(c):
     ids.append(len(d['animal']))
     d['animal'].append(str(a));d['cluster'].append(str(j));d['sheet'].append(j%2)
     d['used'].append(int(k==best));d['hour'].append(j%24)
     d['sl'].append(float(rng.uniform(5,2500)))
     d['road_end'].append(float(ends[k]));d['road_start'].append(float(start))
     t=float(rng.uniform(0,10));d['traffic_end'].append(t)
     d['traffic_start'].append(float(rng.uniform(0,10)))
     d['stream_end'].append(float(rng.uniform(0,1000)));d['stream_start'].append(float(rng.uniform(0,1000)))
    # time and all starting states must be common within the group
    base=d['traffic_start'][ids[0]];base2=d['stream_start'][ids[0]]
    for i in ids:d['traffic_start'][i]=base;d['stream_start'][i]=base2
    groups.append(((j%2,str(a),str(j)),ids))
  d={k:np.asarray(v,dtype=object if k in ('animal','cluster') else int if k in ('sheet','used') else float) for k,v in d.items()}
  return d,groups
 def test_source_matched_group_and_animal_balance(self):
  d,groups=self.synthetic()
  g,q=f.group_admit(d,{'source_rows':len(d['used'])})
  self.assertEqual(q['eligible_independent_animals'],10)
  self.assertEqual(q['eligible_strata'],600)
  self.assertEqual(len(g),600)
 def test_known_truth_origin_resemblance_can_transfer(self):
  d,groups=self.synthetic()
  v=f.fit_eval(d,groups,boot=150)
  self.assertGreater(v['primary_road_origin_vs_destination']['mean_nats_per_movement'],0)
  self.assertEqual(v['primary_road_origin_vs_destination']['source_state_coeff_negative_folds'],5)
if __name__=='__main__':unittest.main()
