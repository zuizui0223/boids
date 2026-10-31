"""Invented polygons only; no original animal GPS positions."""
import unittest
from shapely.geometry import Point,Polygon
import geometry_semantics as m

class KnownTruth(unittest.TestCase):
 def test_fixed_provider_sha_and_expected_source_units(self):
  self.assertEqual(m.PIN_SHA,"2cc448f22730ebcc751d51eba68c61d13be435479abbfd7ab483bc3f77d95856")
  self.assertEqual(m.PIN_BYTES,194382)
  self.assertEqual(m.ZIP_ELEV,"QuantileRegressionbased_ElevationChangesInTheWaddenSea.zip")
 def test_public_station_and_buffer_source_not_animal(self):
  square=Polygon([(0,0),(10,0),(10,10),(0,10)])
  x=m.source_geometry(square,Point(5,5),5)
  self.assertTrue(x["covers_original_station"])
  self.assertTrue(x["intersects_fixed_buffer"])
  self.assertAlmostEqual(x["distance_km"],0.)
  far=m.source_geometry(square,Point(100,100),5)
  self.assertFalse(far["covers_original_station"])
  self.assertFalse(far["intersects_fixed_buffer"])
 def test_source_polygons_invalid_not_repaired_silently(self):
  bowtie=Polygon([(0,0),(5,5),(0,5),(5,0),(0,0)])
  a=m.source_geometry(bowtie,Point(2,2))
  self.assertFalse(a["valid"])
  self.assertTrue(a["repair_needed"])
 def test_no_false_elevation_or_GPS_in_source_join(self):
  import inspect
  t=inspect.getsource(m.run)
  self.assertIn("NO_animal_GPS_or_original_RWS_tide_time_series_read",t)
  self.assertIn("not",m.__doc__.lower())
if __name__=="__main__":unittest.main()
