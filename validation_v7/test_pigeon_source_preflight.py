import unittest
from pathlib import PurePosixPath
from zipfile import ZipFile
from io import BytesIO
from unittest.mock import patch
import csv
import json
from pigeon_source_preflight import inspect,verify,PAIR_PHASE,MIN_MATCHED_PAIR_EPISODES


def fakezip(n=10,unmatched=False):
    b=BytesIO()
    with ZipFile(b,'w') as z:
        for i in range(n):
            name=f'GPS_tracks/Site_1/{PAIR_PHASE}/H32H79_{i+1}.csv'
            z.writestr(name,'timestamp,lat,lon,height\nPRIVATE_PAYLOAD_SHOULD_NOT_APPEAR,0,0,0\n')
            if not unmatched:
                z.writestr(name.replace('H32H79','H79H32'),'timestamp,lat,lon,height\nSECRET_SOURCE_ROWS,0,0,0\n')
    return b.getvalue()

class Preflight(unittest.TestCase):
    def test_bad_checksum_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'STOP_SOURCE_SIZE_CHANGED'):
            verify(b'fake')
    def test_matching_bidirectional_pairs(self):
        x=inspect(fakezip(),require_source_verification=False)
        self.assertEqual(x['paired_phase']['matched_dual_tracker_episodes'],10)
        self.assertEqual(x['status'],'PASS_HEADER_AND_PAIR_NAMES_ONLY')
        self.assertEqual(x['archive']['csv_files'],20)
    def test_single_track_per_episode_not_two_independent_units(self):
        x=inspect(fakezip(unmatched=True),require_source_verification=False)
        self.assertEqual(x['paired_phase']['matched_dual_tracker_episodes'],0)
        self.assertEqual(x['status'],'STOP_INSUFFICIENT_MATCHED_PAIRED_FILES')
    def test_no_coordinate_disclosure(self):
        s=json.dumps(inspect(fakezip(),require_source_verification=False))
        self.assertNotIn('PRIVATE_PAYLOAD_SHOULD_NOT_APPEAR',s)
        self.assertNotIn('SECRET_SOURCE_ROWS',s)
    def test_empty_headers_do_not_generate_data_rows(self):
        b=BytesIO()
        with ZipFile(b,'w') as z:
            z.writestr(f'Site_1/{PAIR_PHASE}/H32H79_1.csv','')
        x=inspect(b.getvalue(),require_source_verification=False)
        self.assertEqual(x['archive']['csv_files'],1)
        self.assertEqual(x['archive']['phase_header_examples'][PAIR_PHASE],[])
if __name__=='__main__':unittest.main()
