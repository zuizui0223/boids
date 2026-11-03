import unittest
from rws_source_probe import extract_station_catalog,describe_water_response
class RWSProbeTests(unittest.TestCase):
    def test_station_catalogue_case(self):
        c={"LocatieLijst":[{"Code":"schiermonnikoog","Naam":"Schiermonnikoog"},{"Code":"nes","Naam":"Nes"}]}
        self.assertEqual(extract_station_catalog(c),[{'code':'schiermonnikoog','name':'Schiermonnikoog'}])
    def test_datum_and_fixed_utc_offset_gate(self):
        inp={"Succesvol":True,"WaarnemingenLijst":[{"AquoMetadata":{"Eenheid":{"Code":"cm"},"Hoedanigheid":{"Code":"NAP"},"Grootheid":{"Code":"WATHTE"}},"MetingenLijst":[{"Tijdstip":"2008-08-14T12:00:00+01:00","Meetwaarde":{"Waarde_Numeriek":123.0}}]}]}
        r=describe_water_response(inp)
        self.assertTrue(r['field_tide_join_allowed'])
        self.assertEqual(r['series'][0]['reference_code'],'NAP')
        inp['WaarnemingenLijst'][0]['AquoMetadata']['Hoedanigheid']['Code']='LAT'
        self.assertFalse(describe_water_response(inp)['field_tide_join_allowed'])
        inp['WaarnemingenLijst'][0]['AquoMetadata']['Hoedanigheid']['Code']='NAP'
        inp['WaarnemingenLijst'][0]['MetingenLijst'][0]['Tijdstip']='2008-08-14T12:00:00+02:00'
        self.assertFalse(describe_water_response(inp)['field_tide_join_allowed'])
    def test_no_gauge_data_is_stop(self):
        self.assertEqual(describe_water_response({"Succesvol":True,"WaarnemingenLijst":[]})['status'],"NO_HISTORICAL_STATION_VALUES")
if __name__=='__main__':unittest.main()
