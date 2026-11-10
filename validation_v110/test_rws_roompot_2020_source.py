import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import rws_roompot_2020_source as r
class OriginalRWS2020SourceTruth(unittest.TestCase):
    def test_freeze_year_station_and_tide_level_metadata(self):
        self.assertEqual(r.PERIOD[0],'2020-06-01T00:00:00.000+01:00')
        self.assertEqual(r.NATIVE_META['Grootheid']['Code'],'WATHTE')
        self.assertEqual(r.NATIVE_META['ProcesType'],'meting')
        self.assertEqual(r.MIN_MEASUREMENTS_48H,200)
    def test_catalogue_prior_to_measured_outcome_selects_outside_inside(self):
        cat={'LocatieLijst':[{'Code':str(i),'Naam':f'other location {i}'} for i in range(180)]}
        cat['LocatieLijst'].extend([
            {'Code':'roompot.buiten','Naam':'Roompot buiten'},
            {'Code':'roompot.binnen','Naam':'Roompot binnen'}])
        a=r.native_roompot_stations(cat)
        selected=r.prespecified_probes(a)
        self.assertEqual(len(selected['primary_outside_station_source_candidates']),1)
        self.assertEqual(len(selected['secondary_inside_station_source_candidates']),1)
    def test_true_original_10min_time_unit_cm_NAP(self):
        t=datetime(2020,6,1,tzinfo=timezone(timedelta(hours=1)))
        native=[]
        for h in range(288):
            stamp=(t+timedelta(minutes=10*h)).isoformat()
            native.append({'Tijdstip':stamp,'Meetwaarde':{'Waarde_Numeriek':float(h%100)}})
        o={'Succesvol':True,'WaarnemingenLijst':[{
            'AquoMetadata':{'Grootheid':{'Code':'WATHTE'},
                'Eenheid':{'Code':'cm'},'Hoedanigheid':{'Code':'NAP'}},
            'MetingenLijst':native}]}
        with patch.object(r,'publisher_post',return_value=(o,'sourceSHA')):
            result=r.probe_original_gauge('roompot.buiten')
        self.assertEqual(result['source_status'],'ORIGINAL_2020_RWS_ROOMPO_GAUGE_10MIN_NAP_MEASURED_SOURCE_ADMITTED')
        self.assertEqual(result['original_n_unique_true_observed_timestamps'],288)
        self.assertEqual(result['original_gauge_time_gap_minutes_max'],10)
        self.assertTrue(result['no_original_tide_array_or_bird_positions_exported'])
    def test_no_time_zone_shift_and_source_not_biological_evidence(self):
        self.assertIn('No behavior',r.__doc__)
        self.assertNotIn('GULL_SCIENTIFIC_OUTCOME',r.__dict__)
if __name__=='__main__':unittest.main()
