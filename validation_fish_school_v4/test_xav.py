import io,unittest,wave
from xav_source_gate import BLOBS,PIN,blob_sha
class XAVTests(unittest.TestCase):
 def test_git_blob_known_truth(self):
  self.assertEqual(blob_sha(b"abc"),"f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
 def test_six_files_pinned(self):
  self.assertEqual(len(BLOBS),6)
  self.assertEqual(len({x[0] for x in BLOBS}),6)
  self.assertEqual(len(PIN),40)
 def test_wave_header_fixture(self):
  z=io.BytesIO()
  with wave.open(z,"wb") as f:
   f.setnchannels(1);f.setframerate(32000);f.setsampwidth(2);f.writeframes(b"\0\0"*320)
  with wave.open(io.BytesIO(z.getvalue()),"rb") as f:
   self.assertEqual(f.getnframes(),320)
   self.assertEqual(f.getframerate(),32000)
if __name__=="__main__":unittest.main()
