import unittest
import rws_catalog as m
class CatalogKnownTruth(unittest.TestCase):
 def test_catalog_filters_source_names_only(self):
  x=m.scrutinize({"LocatieLijst":[
   {"Code":"schiermonnikoog.waddenzee","Naam":"Schiermonnikoog, Waddenzee"},
   {"Code":"lauwersoog.waddenzee","Naam":"Lauwersoog, Waddenzee"},
   {"Code":"unrelated","Naam":"Somewhere Else"}],
   "AquoMetadataLijst":[],"AquoMetadataLocatieLijst":[]})
  self.assertEqual(len(x["filtered_original_source_locations"]),2)
  self.assertTrue(x["no_tide_numeric_value_or_bird_position_read"])
 def test_wrong_metadata_stops(self):
  with self.assertRaises(ValueError):m.scrutinize({})
if __name__=="__main__":unittest.main()
