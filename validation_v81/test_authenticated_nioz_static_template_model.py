"""v81 synthetic known truth for explicitly inferred NIOZ *model mesh* geography.

Synthetic images/files and animals are NOT actual original NIOZ or bird effects.
Preserve older native-coordinate source failures and v78 late-month no score.
"""
from __future__ import annotations
import hashlib
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
import numpy as np
from netCDF4 import Dataset

import authenticated_nioz_static_template_model as source
from original_ameland_native_gps_source import (
    original_ameland_month_native_source_gate,AMELAND_STATUS)
from matched_tide_state_day_night_native_ranks import tide_light_source_groups

def model_bytes(*,missing_lat=False,lon_changed=False,lat_changed=False):
    with tempfile.TemporaryDirectory() as td:
        file=Path(td)/"synthetic.nc"
        with Dataset(file,"w") as d:
            d.createDimension("y",486)
            d.createDimension("x",820)
            lat=np.broadcast_to(
                np.linspace(53.1,53.9,486,dtype=np.float32)[:,None],
                (486,820)).copy()
            lon=np.broadcast_to(
                np.linspace(5.3,6.7,820,dtype=np.float32)[None,:],
                (486,820)).copy()
            expo=np.broadcast_to(np.linspace(0,1,820,dtype=np.float32)[None,:],
                                 (486,820)).copy()
            if missing_lat:lat[:]=np.nan
            if lat_changed:lat[4,4]+=.0004
            if lon_changed:lon[4,4]+=.0004
            for name,arr in (("lat",lat),("lon",lon),("time_expo",expo)):
                var=d.createVariable(name,"f4",("y","x"),fill_value=-9999.)
                var[:]=arr
        return file.read_bytes()

def fixture_provider(*,july_lat_present=False,July_lon_changed=False,
                     august_lat_changed=False,bad_2009=False):
    real=model_bytes()
    missing=model_bytes(missing_lat=True)
    july_other=model_bytes(missing_lat=True,lon_changed=True)
    aug_other=model_bytes(lat_changed=True)
    outside=model_bytes(lon_changed=True)
    data={}
    for name in source.EXACT_MODEL_SHAS:
        if name=="README.txt":raw=b"Original fake README synthetic source"
        elif name in ("eco_av.201006.nc","eco_av.201007.nc"):
            raw=missing
        else:raw=real
        data[name]=raw
    if july_lat_present:data["eco_av.201007.nc"]=real
    if July_lon_changed:data["eco_av.201007.nc"]=july_other
    if august_lat_changed:data["eco_av.201008.nc"]=aug_other
    if bad_2009:data["eco_av.200908.nc"]=outside
    hashes={k:hashlib.sha256(v).hexdigest() for k,v in data.items()}
    provider={name:{"name":name} for name in data}
    def loader(entry):
        b=data[entry["name"]]
        return b,{
            "original_computed_sha256":hashlib.sha256(b).hexdigest(),
            "original_bytes":len(b)}
    return provider,loader,hashes

class ModelNativeTemplateExplicitOnly(unittest.TestCase):
    def test_original_fixed_source_months_and_SHA_pin_list(self):
        self.assertEqual(source.MONTHS_V81,(6,7,8,9,10,11,12))
        self.assertEqual(source.ORIGINAL_INFERRED_MONTHS,(6,7))
        self.assertEqual(source.TOTAL_NATIVE_CELLS,398520)
        self.assertEqual(len(source.EXACT_MODEL_SHAS),11)
        self.assertEqual(source.EXACT_MODEL_SHAS["eco_av.201006.nc"],
                         "9d32caeda98fb5be6096b60ada49fd4109b9cf076f406451ffbe5ff3899ef952")

    def test_exact_two_other_year_original_model_source_and_only_missing_lat_inferred(self):
        provider,loader,hashes=fixture_provider()
        with patch.dict(source.EXACT_MODEL_SHAS,hashes,clear=True):
            native,metadata=source.authenticated_template_and_model_months(
                provider,loader=loader)
        self.assertEqual(sorted(native),list(range(6,13)))
        self.assertTrue(metadata[
            "original_2010_Jan_and_2009_Jan_Aug_exact_grid_provenance_verified"])
        for m in (6,7):
            self.assertTrue(metadata["original_month_specific_spatial_source"][m][
                "2010_static_model_template_lat_explictly_inferred_not_measured"])
            self.assertTrue(metadata["original_month_specific_spatial_source"][m][
                "original_jun_jul_native_lat_was_not_observed"])
        for m in range(8,13):
            self.assertFalse(metadata["original_month_specific_spatial_source"][m][
                "2010_static_model_template_lat_explictly_inferred_not_measured"])
        self.assertTrue(metadata["original_month_2010_JunJul_lat_remains_missing_and_is_only_INFERRED"])
        self.assertEqual(native[6]["n_native"],398520)
        self.assertNotIn("53.46894",str(metadata))

    def test_original_july_source_lon_changed_hard_source_stops(self):
        publisher,loader,sha=fixture_provider(July_lon_changed=True)
        with patch.dict(source.EXACT_MODEL_SHAS,sha,clear=True):
            with self.assertRaisesRegex(ValueError,"NATIVE_LON_INDEX_NOT_STATIC"):
                source.authenticated_template_and_model_months(
                    publisher,loader=loader)

    def test_original_july_lat_present_is_not_silently_marked_as_missing(self):
        publisher,loader,sha=fixture_provider(july_lat_present=True)
        with patch.dict(source.EXACT_MODEL_SHAS,sha,clear=True):
            with self.assertRaisesRegex(ValueError,"EXPECTED_ORIGINAL_JUNE_JULY_MASK_CHANGED"):
                source.authenticated_template_and_model_months(
                    publisher,loader=loader)

    def test_native_original_august_lat_not_equal_hard_stop(self):
        publisher,loader,sha=fixture_provider(august_lat_changed=True)
        with patch.dict(source.EXACT_MODEL_SHAS,sha,clear=True):
            with self.assertRaisesRegex(ValueError,"NATIVE_AUG_DEC_LAT_GRID_NOT_EXACT"):
                source.authenticated_template_and_model_months(
                    publisher,loader=loader)

    def test_independent_original_2009_model_grid_not_identical_hard_stop(self):
        publisher,loader,sha=fixture_provider(bad_2009=True)
        with patch.dict(source.EXACT_MODEL_SHAS,sha,clear=True):
            with self.assertRaisesRegex(ValueError,"INDEPENDENT_2009_GRID_NOT_EXACT"):
                source.authenticated_template_and_model_months(
                    publisher,loader=loader)

    def test_old_Ameland_source_and_tide_match_default_untouched_new_June_months_explicit(self):
        publisher,loader,sha=fixture_provider()
        with patch.dict(source.EXACT_MODEL_SHAS,sha,clear=True):
            native,_=source.authenticated_template_and_model_months(
                publisher,loader=loader)
        months={}
        for m in source.MONTHS_V81:
            fixes=[]
            for bird in range(5):
                for hour in range(45):
                    fixes.append((
                        f"SYNTHETIC_{bird}",
                        datetime(2010,m,3)+timedelta(hours=hour),
                        53.44+hour*.00001,5.75+bird*.00001))
            q=original_ameland_month_native_source_gate(
                m,fixes,native[m],allowed_months=source.MONTHS_V81)
            self.assertEqual(q["source_receipt"]["fixed_source_admission"],
                             AMELAND_STATUS)
            months[m]=q
        with self.assertRaisesRegex(ValueError,"UNFROZEN_MONTH"):
            tide_light_source_groups(months,None)
        def labels(bird,month,idx):
            return (.1,(-1 if idx%4<2 else 1),
                    ("DAY" if idx%2 else "NIGHT"))
        _,qa=tide_light_source_groups(
            months,None,required_months=source.MONTHS_V81,
            required_geo_status=AMELAND_STATUS,synthetic_labels=labels)
        self.assertEqual(qa["original_distinct_months_in_paired_conditions"],0)
        self.assertIn("NOT_ADMITTED",qa["admission"])
        self.assertTrue(qa["no_model_index_or_next_heading_used_in_pair_matching"])

if __name__=="__main__":
    unittest.main()
