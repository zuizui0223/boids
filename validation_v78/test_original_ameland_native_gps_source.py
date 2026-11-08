"""v78 original Ameland island source boundary tests, no animal field effects."""
import csv
import gzip
import io
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.spatial import cKDTree

import original_ameland_native_gps_source as a
from matched_tide_state_day_night_native_ranks import tide_light_source_groups
from wild_2010_modelled_tidal_exposure_rank import _locxy

def fixture_native_model():
    lat=np.linspace(53.41,53.47,101)
    lon=np.linspace(5.70,5.80,101)
    la,lo=np.meshgrid(lat,lon,indexing="ij")
    xy=_locxy(la.ravel(),lo.ravel())
    return {"xy":xy,"index":np.linspace(0,1,len(xy)),
            "n_native":len(xy),"tree":cKDTree(xy)}

def original_shaped_fixes(*,birds=8,n_each=35,month=8):
    positions=[]
    for i in range(birds):
        for k in range(n_each):
            positions.append((f"SYNTHETIC_AMELAND_{i}",
                datetime(2010,month,3)+timedelta(hours=k),
                53.44+0.00002*k,5.75+0.00002*i))
    return positions

class AmelandOutOfIslandSourceSafety(unittest.TestCase):
    def test_original_field_identity_prior_documented_hashes(self):
        self.assertEqual(a.AMELAND_RAW_2010,119507)
        self.assertEqual(a.AMELAND_MD5_2010,
                         "71e0b66230b508873897c99464146167")
        self.assertEqual(a.AMELAND_SHA_2010,
            "c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c")
        self.assertEqual(a.AMELAND_STATUS,
                         "SOURCE_ADMITTED_V78_AMELAND_2010_GPS_ORIGINAL_NIOZ_MONTH_1KM")

    def test_native_original_earliest_bird_hour_am_land_and_2010_only(self):
        output=io.StringIO()
        writer=csv.DictWriter(output,fieldnames=[
            "event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible","target_future_ignore"])
        writer.writeheader()
        for idx,minu in enumerate((50,10,22)):
            writer.writerow({"event-id":str(idx),
                "timestamp":f"2010-08-12 07:{minu:02d}:00",
                "location-lat":53.44,"location-long":5.75,
                "individual-local-identifier":"SYNTHETIC_TEST_BIRD_A",
                "visible":"TRUE","target_future_ignore":9999+idx})
        writer.writerow({"event-id":"3",
            "timestamp":"2011-08-12 07:03:00",
            "location-lat":53.44,"location-long":5.75,
            "individual-local-identifier":"SYNTHETIC_TEST_BIRD_A",
            "visible":"TRUE","target_future_ignore":0})
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"test.gz"
            with gzip.open(p,"wt",encoding="utf-8",newline="") as f:
                f.write(output.getvalue())
            by_month,source=a.original_ameland_2010_hourly(p,expected=4)
        self.assertEqual(by_month[8][0][1].minute,10)
        self.assertEqual(len(by_month[8]),1)
        self.assertEqual(source["source_fixed_2010_Aug_to_Dec_hourly_bird_fixes"]["8"][
            "original_Ameland_native_hourly_locations"],1)
        self.assertNotIn("SYNTHETIC_TEST_BIRD_A",str(source))
        self.assertNotIn("target_future_ignore",str(source))

    def test_Ameland_has_independent_source_admission_and_index_not_read(self):
        model=fixture_native_model()
        fixes=original_shaped_fixes()
        with patch.object(a,"NATIVE_EXPECTED",model["n_native"]):
            source=a.original_ameland_month_native_source_gate(8,fixes,model)
        receipt=source["source_receipt"]
        self.assertEqual(receipt["source_original_distinct_birds"],8)
        self.assertEqual(receipt["original_GPS_nearest_NIOZ_grid_within_300m"],280)
        self.assertEqual(receipt["original_birds_with_20plus_source_locations_and_1km_background"],8)
        self.assertEqual(receipt["fixed_source_admission"],a.AMELAND_STATUS)
        self.assertTrue(receipt["original_NIOZ_time_expo_used_location_values_not_read"])
        self.assertNotIn("SYNTHETIC_AMELAND",str(receipt))

    def test_Ameland_underfive_month_source_will_not_qualify(self):
        model=fixture_native_model()
        with patch.object(a,"NATIVE_EXPECTED",model["n_native"]):
            r=a.original_ameland_month_native_source_gate(8,
                original_shaped_fixes(birds=3,n_each=80),model)
        self.assertIn("NOT_ADMITTED",r["source_receipt"]["fixed_source_admission"])

    def test_existing_Schier_original_matcher_default_stays_intact(self):
        model=fixture_native_model()
        with patch.object(a,"NATIVE_EXPECTED",model["n_native"]):
            source=a.original_ameland_month_native_source_gate(8,
                original_shaped_fixes(),model)
        preflight={m:{**source,
            "fixes":original_shaped_fixes(month=m)}
            for m in (8,9,10,11,12)}
        def label(bird,month,i):
            return (.2,1 if (i%4<2) else -1,
                    "DAY" if i%2==0 else "NIGHT")
        _,old=tide_light_source_groups(preflight,None,
            synthetic_labels=label)
        self.assertEqual(old["admission"],"NOT_ADMITTED_V76_PRIOR_SPATIAL_SOURCE")
        _,new=tide_light_source_groups(preflight,None,
            synthetic_labels=label,required_geo_status=a.AMELAND_STATUS)
        self.assertNotEqual(new["admission"],"NOT_ADMITTED_V76_PRIOR_SPATIAL_SOURCE")
        self.assertTrue(new["no_model_index_or_next_heading_used_in_pair_matching"])

if __name__=="__main__":
    unittest.main()
