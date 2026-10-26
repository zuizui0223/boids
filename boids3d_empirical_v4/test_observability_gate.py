import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from boids_observability_gate import assess

class TestGate(unittest.TestCase):
    def test_together_and_far(self):
        with TemporaryDirectory() as td:
            p=Path(td)/'obs.csv'
            with p.open('w') as f:
                w=csv.writer(f);w.writerow(['animal-id','timestamp','location-long','location-lat','height-above-msl'])
                for i in range(20):
                    t=f'2026-01-01 00:{i//6:02}:{(i%6)*10:02}'
                    for animal,lon in [('a',0),('b',.00001),('c',1)]:w.writerow([animal,t,lon,0,100])
            v=assess(p)
            self.assertEqual(v['individuals'],3)
            self.assertGreater(v['near_5sec_100m'],0)
            self.assertGreater(v['near_15sec_500m'],0)
            self.assertFalse(v['illustrative_fast_social_boids_gate_pass']) # median 10s, but only one near pair
if __name__=='__main__':unittest.main()
