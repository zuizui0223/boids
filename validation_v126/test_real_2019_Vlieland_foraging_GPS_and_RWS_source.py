"""v126 synthetic known-truth tests only; none of these generated events enter
the actual 2019 publisher-source result or any real foraging×tide outcome.
"""
from __future__ import annotations
from datetime import datetime,timedelta
from unittest.mock import patch
from io import StringIO
import csv,gzip,unittest
import real_2019_Vlieland_foraging_GPS_source as g
import real_2019_RWS_Vlieland_Haven_source as t

def csv_gz(header,rows):
    f=StringIO()
    w=csv.writer(f);w.writerow(header);w.writerows(rows)
    return gzip.compress(f.getvalue().encode())

class NativeVlielandSourceTruth(unittest.TestCase):
    def test_source_fixed_label_and_2019_publisher_gps_checksum(self):
        self.assertEqual(g.GPS_MD5,'65426aedf6f48c36f81990268d267c7b')
        self.assertEqual(g.LABEL_FORAGE,'forage')
        self.assertEqual(g.LABEL_INACTIVE,'inactive')
        self.assertEqual(g.ORIGINAL_BEHAVIOUR_ROWS,1817033)
        self.assertEqual(g.ORIGINAL_SOURCE_BIRDS,43)
        self.assertEqual(g.JOIN_MAX_ABSOLUTE_SECS,900)
        self.assertEqual(g.DISTANCE_PRIMARY_KM,25.)
    def test_native_original_GPS_bird_clock_join_nearest_and_no_interpolation(self):
        dt=datetime(2019,5,1,12)
        positions={'ORIGINAL_TEST_BIRD':(
            [dt,dt+timedelta(minutes=50)],
            [(dt,53.30,5.09),(dt+timedelta(minutes=50),53.90,6.09)])}
        event=g._nearest_real_original_gps(positions,'ORIGINAL_TEST_BIRD',
              dt+timedelta(minutes=13))
        self.assertEqual(event[0][1:3],(53.30,5.09))
        self.assertIsNone(g._nearest_real_original_gps(positions,
              'ORIGINAL_TEST_BIRD',dt+timedelta(minutes=28)))
        self.assertIsNone(g._nearest_real_original_gps(positions,
              'DIFFERENT_BIRD',dt))
    def test_genuine_GPS_file_schema_and_source_year_scope(self):
        p=csv_gz(['timestamp','individual-local-identifier','visible',
                  'location-lat','location-long'],[
                     ['2019-06-01T12:00:00Z','BIRD1','TRUE',53.3,5.09],
                     ['2019-06-01T13:00:00Z','BIRD2','TRUE',53.3,5.09],
                     ['2018-06-01T13:00:00Z','BIRD1','TRUE',53.3,5.09],
                     ['2019-06-01T13:00:00Z','BIRD1','FALSE',53.3,5.09]])
        idx,census=g.original_2019_gps_source_index(p,{})
        self.assertEqual(census['native_original_2019_genuine_GPS_birds'],2)
        self.assertEqual(census['native_original_2019_valid_WGS84_fix_n'],2)
        self.assertEqual(census['native_original_2019_GPS_full_source_rows'],4)
    def test_source_true_foraging_label_vs_inactive_one_GPS_fix_not_2_birds(self):
        begin='2019-05-01T12:00:00Z'
        p=csv_gz(['timestamp','individual-local-identifier','visible',
                  'location-lat','location-long'],[
                     [begin,'BIRD1','TRUE',53.3,5.09],
                     [begin,'BIRD2','TRUE',53.99,7.01]])
        idx,proof=g.original_2019_gps_source_index(p,{})
        acc=csv_gz(['timestamp','individual-local-identifier','behavioural-classification','visible'],[
            ['2019-05-01T12:05:00Z','BIRD1','forage','TRUE'],
            ['2019-05-01T12:08:00Z','BIRD1','inactive','TRUE'],
            ['2019-05-01T12:08:00Z','BIRD2','inactive','TRUE']])
        with patch.object(g,'ORIGINAL_BEHAVIOUR_ROWS',3),patch.object(g,'ORIGINAL_SOURCE_BIRDS',2),patch.dict(
            g.LABELS_FIXED,{'forage':1,'inactive':2},clear=True):
            out=g.true_original_2019_behaviour_gps_join(acc,{},idx)
        r=out['original_2019_local_behavior_to_original_GPS_by_radii']['25.0']
        self.assertEqual(r['genuine_original_birds_with_2019_foraging_OR_inactive_GPS_matched_near_station'],1)
        self.assertEqual(r['native_original_month_source']['5']['original_foraging_class_records'],1)
        self.assertEqual(r['native_original_month_source']['5']['original_inactive_class_records'],1)
        self.assertEqual(out['source_original_2019_tagged_birds_source_exact_replayed'],2)
        self.assertTrue(out['NO_2019_TIDE_SOLAR_BEHAVIOUR_Y_ESTIMATED'])
    def test_official_RWS_exact_vlieland_station_not_nearest_source_fallback(self):
        cat={'LocatieLijst':[{'Code':str(i),'Naam':f'other place {i}'} for i in range(180)]}
        cat['LocatieLijst'].extend([
            {'Code':'vlieland.haven','Naam':'Vlieland haven'},
            {'Code':'vlieland.test','Naam':'Vlieland east'}])
        source=t.validate_original_vlieland_station_catalogue(cat)
        self.assertEqual(source['original_native_RWS_station_code'],'vlieland.haven')
        cat['LocatieLijst'][-2]['Code']='notfound'
        with self.assertRaisesRegex(t.SourceStop,'EXACT_CODE_NOT_FOUND'):
            t.validate_original_vlieland_station_catalogue(cat)
    def test_official_source_RWS_2019_true_NAP_10min_not_predicted_tide(self):
        base=datetime.fromisoformat('2019-06-01T00:00:00+01:00')
        records=[{'Tijdstip':(base+timedelta(minutes=10*i)).isoformat(),
                 'Meetwaarde':{'Waarde_Numeriek':float(i%70)-35.}} for i in range(288)]
        o={'Succesvol':True,'WaarnemingenLijst':[{
            'AquoMetadata':{'Grootheid':{'Code':'WATHTE'},
               'Eenheid':{'Code':'cm'},'Hoedanigheid':{'Code':'NAP'}},
            'MetingenLijst':records}]}
        with patch.object(t,'publisher_post',return_value=(o,'native_sha')):
            source=t.original_2019_vlieland_haven_gauge_48h()
        self.assertEqual(source['native_original_2019_waterheight_observed_10min_n'],288)
        self.assertEqual(source['source_original_10min_interval_max_gap_minutes'],10)
        self.assertTrue(source['NO_forage_OR_SUN_OR_INDIVIDUAL_GPS_effect_scored'])
if __name__=='__main__':unittest.main()
