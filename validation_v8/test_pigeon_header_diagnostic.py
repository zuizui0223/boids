import io,unittest,zipfile
from pigeon_header_diagnostic import probe
from pigeon_timing_gate import PHASE
class TestHeaderOnly(unittest.TestCase):
 def test_detects_nonstandard_pair_headers_without_numeric_rows(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:
   z.writestr('GPS_tracks/Site1/'+PHASE+'/H02S27_1.csv','Date,Time,Latitude,Longitude,Altitude\nSECRET,SECRET,0,0,0\n')
   z.writestr('GPS_tracks/Site1/'+PHASE+'/S27H02_1.csv','bad,header\rPRIVATE,DATA\r')
  r=probe(b.getvalue(),skip_verify=True)
  self.assertEqual(r['header_variant_count'],2)
  self.assertEqual(len(r['nonconforming_examples']),1)
  self.assertEqual(r['nonconforming_examples'][0]['missing'],['Altitude','Date','Latitude','Longitude','Time'])
  self.assertNotIn('SECRET',str(r));self.assertNotIn('PRIVATE',str(r))
if __name__=='__main__':unittest.main()
