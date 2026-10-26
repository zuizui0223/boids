import io,zipfile,unittest
from pigeon_timing_gate import evaluate,time_value,pair_match,PHASE

def build_zip(n=8,offset=0.,missing_reverse=False,cr=False):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:
  for k in range(n):
   for ab in (['H32H79'] if missing_reverse else ['H32H79','H79H32']):
    linebreak='\r' if cr else '\n'
    lines=['Date,Time,Latitude,Longitude,Altitude,Speed,Course,Type,Distance,Essential']
    for j in range(45):
     # UTC-ish form, 5 Hz with exact double-tracker alignment
     sec=j/5+ (offset if ab=='H79H32' else 0.)
     lines.append(f'2016-01-01,12:00:{sec:06.3f},51.0,{-.01+j*0.00001:.6f},20,0,0,0,0,0')
    z.writestr(f'GPS_tracks/Site1/{PHASE}/{ab}_{k+1}.csv',linebreak.join(lines)+linebreak)
 return b.getvalue()

class TestGate(unittest.TestCase):
 def test_datetime_parser(self):
  t=time_value('2016-01-01','12:00:00.200')
  self.assertAlmostEqual(time_value('2016-01-01','12:00:00.400')-t,.2,places=5)
  self.assertIsNone(time_value('junk','now'))
 def test_nearest_unique(self):
  a=[(0,50,0,0),(.2,50,0,0),(.4,50,0,0)]
  b=[(.05,50,0,0),(.25,50,0,0),(.45,50,0,0)]
  self.assertEqual(len(pair_match(a,b)),3)
 def test_real_pair_status(self):
  r=evaluate(build_zip(n=8),skip_checksum=True)
  self.assertEqual(r['eligible_synchronized_flights'],8)
  self.assertEqual(r['eligible_site_dyads'],1)
  self.assertEqual(r['gate'],'STOP') # independent replicate requirement
 def test_header_whitespace_matches_audited_header_semantics(self):
  # Only header labels change, not numeric track contents.
  import zipfile,io
  b=io.BytesIO()
  from pigeon_timing_gate import PHASE
  with zipfile.ZipFile(b,'w') as z:
   for ab in ('H32H79','H79H32'):
    h=' Date , Time , Latitude , Longitude , Altitude ,Speed,Course,Type,Distance,Essential\r'
    rows=''.join(f'2016-01-01,12:00:{i/5:06.3f},51.0,-0.01,20,0,0,0,0,0\r' for i in range(45))
    z.writestr(f'GPS_tracks/Site1/{PHASE}/{ab}_1.csv',h+rows)
  r=evaluate(b.getvalue(),skip_checksum=True)
  self.assertEqual(r['eligible_synchronized_flights'],1)
 def test_missing_reverse(self):
  r=evaluate(build_zip(missing_reverse=True),skip_checksum=True)
  self.assertEqual(r['candidate_named_pairs'],0)
 def test_cr_only(self):
  r=evaluate(build_zip(cr=True),skip_checksum=True)
  self.assertEqual(r['eligible_synchronized_flights'],8)
 def test_no_sync(self):
  r=evaluate(build_zip(offset=.12),skip_checksum=True)
  self.assertLess(r['total_matched_fix_pairs'],8*45)
if __name__=='__main__':unittest.main()
