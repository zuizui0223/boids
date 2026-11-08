"""v74 native 2010 model source and original GPS month known-truth tests.

All here are synthetic, never original animals, never model-selection effects.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from real_2010_monthly_nioz_gps_source_gate import (
    CKAN,PACKAGE,MONTH_NAMES,original_all_2010_manifest,
    parse_whole_2010_original_hourly,original_month_native_source,
    source_month_geo_fixes,EXPECTED_RAW_GPS)

def model_source(month=1,*,valid_lat=True):
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"synthetic.nc"
        with Dataset(path,"w") as net:
            net.createDimension("y",486);net.createDimension("x",820)
            yy=np.linspace(53.25,53.65,486,dtype=np.float32)
            xx=np.linspace(5.75,6.55,820,dtype=np.float32)
            lat=np.broadcast_to(yy[:,None],(486,820)).copy()
            lon=np.broadcast_to(xx[None,:],(486,820)).copy()
            expo=np.broadcast_to(np.linspace(0,1,820,dtype=np.float32),
                                 (486,820)).copy()
            if not valid_lat:lat[:]=np.nan
            for name,array in (("lat",lat),("lon",lon),("time_expo",expo)):
                var=net.createVariable(name,"f4",("y","x"),fill_value=-9999.)
                var[:]=array
        return path.read_bytes()

def synthetic_gps_source():
    buf=io.StringIO()
    keys=["event-id","timestamp","location-lat","location-long",
          "individual-local-identifier","visible"]
    wr=csv.DictWriter(buf,fieldnames=keys);wr.writeheader()
    for bird in range(5):
        for month in (1,2):
            for hour in range(40):
                wr.writerow({"event-id":f"{bird}-{month}-{hour}",
                    "timestamp":(datetime(2010,month,2)+timedelta(hours=hour)).strftime("%Y-%m-%d %H:%M:%S"),
                    "location-lat":53.45,"location-long":6.0+hour*.0001,
                    "individual-local-identifier":f"synthetic_{bird}","visible":"TRUE"})
    return buf.getvalue()

class OriginalWholeYearSourceAuditTests(unittest.TestCase):
    def test_12_months_original_provider_all_authenticated_and_frozen(self):
        self.assertEqual(len(MONTH_NAMES),12)
        self.assertEqual(MONTH_NAMES[0],"eco_av.201001.nc")
        self.assertEqual(MONTH_NAMES[-1],"eco_av.201012.nc")
        self.assertEqual(EXPECTED_RAW_GPS,282920)
        readme=b"source manifest synthetic"
        model=b"nc file fake bytes synthetic"
        resources=[]
        for y in (2009,2010,2011):
            for m in range(1,13):
                resources.append({
                    "name":f"eco_av.{y}{m:02d}.nc",
                    "size":len(model),"hash":hashlib.md5(model).hexdigest(),
                    "url":f"https://doi.nioz.nl/synthetic/{y}{m:02d}.nc"})
        resources.append({
            "name":"README.txt","size":len(readme),
            "hash":hashlib.md5(readme).hexdigest(),
            "url":"https://doi.nioz.nl/synthetic/README.txt"})
        def fetch(url,cap):
            if url!=CKAN:raise RuntimeError("no URLs beyond original publisher")
            return json.dumps({"success":True,"result":{
                "id":PACKAGE,"resources":resources}}).encode()
        names=original_all_2010_manifest(fetch=fetch)
        self.assertEqual(len(names),13)
        self.assertEqual(set(MONTH_NAMES),set(names)-{"README.txt"})
        resources[0]["hash"]="wrong_md5"
        # The wrong hash is for 2009 and out-of-month: no source
        # modification was used as a path through this 2010 source gate.
        names=original_all_2010_manifest(fetch=fetch)
        self.assertEqual(len(names),13)
        resources[12]["hash"]="wrong_md5"
        with self.assertRaisesRegex(ValueError,"MD5"):
            original_all_2010_manifest(fetch=fetch)

    def test_original_native_model_source_geographic_and_missing_2010_month(self):
        jan=original_month_native_source(model_source(),MONTH_NAMES[0])
        self.assertEqual(jan[1]["original_native_lat_lon_valid_geographic_cells"],398520)
        self.assertIsNotNone(jan[0])
        missing=original_month_native_source(
            model_source(month=6,valid_lat=False),MONTH_NAMES[5])
        self.assertEqual(missing[1]["original_native_lat_lon_valid_geographic_cells"],0)
        self.assertIsNone(missing[0])
        with self.assertRaisesRegex(ValueError,"OUTSIDE_FROZEN"):
            original_month_native_source(model_source(),"eco_av.201101.nc")

    def test_original_gps_earliest_native_hour_and_month_birds(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"original.csv.gz"
            with gzip.open(p,"wt",encoding="utf-8",newline="") as f:
                f.write(synthetic_gps_source())
            months,qa=parse_whole_2010_original_hourly(p,expected_raw=400)
        self.assertEqual(qa["original_hourly_visible_Schier_2010_positions"],400)
        self.assertEqual(qa["source_year_months"]["1"]["original_birds"],5)
        self.assertEqual(len(months[1]),200)
        self.assertEqual(len(months[2]),200)
        self.assertEqual(len(months[3]),0)
        self.assertNotIn("synthetic_1",str(qa))

    def test_original_all_2010_month_identical_admission_no_favorable_subset(self):
        a=np.linspace(53.25,53.65,486)
        b=np.linspace(5.75,6.55,820)
        yy,xx=np.meshgrid(a,b,indexing="ij")
        model={"xy":np.column_stack((xx.ravel()*.595*111195,yy.ravel()*111195)),
               "n":486*820}
        month=[(f"bird_{i}",53.45,6.0+((k%10)-5)*.0001)
               for i in range(5) for k in range(50)]
        qa={"original_native_grid_cells":398520}
        result=source_month_geo_fixes(month,model,qa)
        self.assertEqual(result["original_nearby_300m_source_fixes"],250)
        self.assertEqual(result["original_individuals_geocoded_at_least_20"],5)
        self.assertEqual(result["original_fixed_month_admission"],
            "SOURCE_ADMITTED_V74_FIXED_GPS_AND_MODELED_INDEX_GEOMETRY_ONLY")
        fail=source_month_geo_fixes(month[:100],model,qa)
        self.assertTrue(fail["original_fixed_month_admission"].startswith("NOT_ADMITTED"))
        source_missing=source_month_geo_fixes(month,None,qa)
        self.assertTrue(source_missing["original_fixed_month_admission"].startswith("NOT_ADMITTED"))

if __name__=="__main__":
    unittest.main()
