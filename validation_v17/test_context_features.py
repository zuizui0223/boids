"""v17 deterministic environmental geometry known-truth, NO field data."""
import datetime as dt
import math
import unittest

import context_features as m


class ContextGeometry(unittest.TestCase):
    def test_west_wind_tailwind_when_flying_east(self):
        w=m.wind_components(5.,270.,90.)
        self.assertAlmostEqual(w["tailwind_support_m_s"],5.)
        self.assertAlmostEqual(w["signed_crosswind_m_s"],0.,places=10)

    def test_east_wind_headwind_when_flying_east(self):
        w=m.wind_components(5.,90.,90.)
        self.assertAlmostEqual(w["tailwind_support_m_s"],-5.)
        self.assertAlmostEqual(w["crosswind_abs_m_s"],0.,places=10)

    def test_wind_to_left_has_negative_crosswind(self):
        w=m.wind_components(5.,90.,0.)
        self.assertAlmostEqual(w["signed_crosswind_m_s"],-5.)
        self.assertAlmostEqual(w["tailwind_support_m_s"],0.,places=10)

    def test_solar_noon_near_due_south_in_oxford_summer(self):
        z=m.solar_azimuth_elevation(
          dt.datetime(2015,6,21,12,tzinfo=dt.timezone.utc),51.8,-1.35)
        self.assertTrue(170<z["solar_azimuth_deg_north_clockwise"]<205)
        self.assertTrue(55<z["solar_elevation_deg"]<65)
        self.assertFalse(z["actual_cloud_visibility_known"])
        self.assertFalse(z["animal_circadian_phase_known"])

    def test_solar_sunrise_near_east_summer_and_before_noon(self):
        z=m.solar_azimuth_elevation(
          dt.datetime(2015,6,21,6,tzinfo=dt.timezone.utc),51.8,-1.35)
        self.assertTrue(40<z["solar_azimuth_deg_north_clockwise"]<130)
        self.assertTrue(0<z["solar_elevation_deg"]<50)

    def test_naive_local_datetime_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"timezone-aware"):
            m.solar_azimuth_elevation(dt.datetime(2015,7,1,12),51.8,-1.35)

    def test_longitude_and_tz_conversion_invariant(self):
        t=dt.datetime(2015,6,21,12,tzinfo=dt.timezone.utc)
        bst=dt.timezone(dt.timedelta(hours=1))
        s1=m.solar_azimuth_elevation(t,51.8,-1.35)
        s2=m.solar_azimuth_elevation(t.astimezone(bst),51.8,-1.35)
        self.assertAlmostEqual(s1["solar_elevation_deg"],s2["solar_elevation_deg"])
        self.assertAlmostEqual(s1["solar_azimuth_deg_north_clockwise"],s2["solar_azimuth_deg_north_clockwise"])

    def test_head_relative_sun_wrap_and_invalid_wind(self):
        self.assertAlmostEqual(m.relative_solar_bearing(5.,355.),10.)
        with self.assertRaisesRegex(ValueError,"Wind"):
            m.wind_components(-1.,90.,0.)


if __name__=="__main__":
    unittest.main()
