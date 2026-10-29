"""v23 ERA5 prior-time original weather provider schema synthetic tests only."""
import datetime as dt
import json
import unittest
import weather_source_gate as w

class OriginalERASourceOnly(unittest.TestCase):
    def test_exact_register_and_bounded_reference_points(self):
        self.assertEqual(w.MODEL,"era5")
        self.assertEqual(w.START,"2019-01-01")
        self.assertEqual(w.END,"2023-12-31")
        self.assertEqual(w.REGION_POINTS["baikka_beel"],(24.3503,91.6995))
        self.assertEqual(w.REGION_POINTS["tanguar_haor"],(25.15,91.0667))
        self.assertEqual(w.N_DAYS,1826)
        url=w.request_url(25.15,91.0667)
        self.assertIn("models=era5",url)
        self.assertIn("timezone=UTC",url)

    def fixture(self):
        days=[str(dt.date(2019,1,1)+dt.timedelta(days=i)) for i in range(w.N_DAYS)]
        return {"latitude":24.25,"longitude":91.75,
            "utc_offset_seconds":0,"timezone":"UTC",
            "daily":{"time":days,
                     "temperature_2m_mean":[24.]*len(days),
                     "precipitation_sum":[0.]*len(days),
                     "wind_speed_10m_max":[5.]*len(days)},
            "daily_units":{"temperature_2m_mean":"°C",
                           "precipitation_sum":"mm",
                           "wind_speed_10m_max":"km/h"}}

    def test_full_two_wetland_daily_support_and_no_weather_values_export(self):
        d=self.fixture();raw=json.dumps(d).encode()
        q=w.validate_weather_json(d,raw,"baikka_beel","https://archive-api.open-meteo.com")
        self.assertEqual(q["status"],"ERA5_ORIGINAL_SOURCE_ONLY_VERIFIED")
        self.assertEqual(q["days"],1826)
        self.assertFalse(q["numeric_daily_weather_values_exported"])
        self.assertFalse(q["animal_GPS_or_movement_outcomes_processed"])
        self.assertNotIn("[24.0,",json.dumps(q))

    def test_weather_utc_off_by_hour_fails(self):
        d=self.fixture();d["utc_offset_seconds"]=3600
        with self.assertRaisesRegex(ValueError,"UTC"):
            w.validate_weather_json(d,b"{}", "baikka_beel","x")

    def test_missing_current_day_data_and_broken_unit_fail(self):
        d=self.fixture();d["daily"]["precipitation_sum"]=[None]*w.N_DAYS
        with self.assertRaisesRegex(ValueError,"missingness"):
            w.validate_weather_json(d,b"{}", "tanguar_haor","x")
        d=self.fixture();d["daily_units"]["temperature_2m_mean"]="fahrenheit"
        with self.assertRaisesRegex(ValueError,"temperature"):
            w.validate_weather_json(d,b"{}","baikka_beel","x")

    def test_no_location_selection_from_animal_movement(self):
        with self.assertRaisesRegex(ValueError,"registered"):
            w.validate_weather_json(self.fixture(),b"{}","posthoc_gps_hotspot","x")

if __name__=="__main__":
    unittest.main()
