"""Known-truth fixtures only: original Leizhou outcomes NEVER used for test tuning."""
import io
import json
import math
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from .leizhou_v2 import (
    boot_ci, choose_required_files, great_circle_m, local_day, map_sample,
    prepare_tracking, radial_endpoints, read_tagmap, secure_zip, source_only_manifest,
    summarize, fit_holdout, DOI,
)

class LeizhouKnownTruthTests(unittest.TestCase):
    def test_geo_endpoints_and_circle(self):
        xs, ys = radial_endpoints(110.1,20.5,500)
        self.assertEqual(len(xs),32)
        d=[great_circle_m(20.5,110.1,float(y),float(x)) for x,y in zip(xs,ys)]
        self.assertLess(max(abs(a-500) for a in d),0.001)

    def test_raster_class_and_nodata(self):
        v = np.zeros((100,100),dtype="uint8")
        v[:,:50]=1
        v[:,50:]=2
        with MemoryFile() as mem:
            with mem.open(driver="GTiff",count=1,width=100,height=100,dtype="uint8",crs="EPSG:4326",transform=from_origin(110.,20.6,.001,.001),nodata=0) as dst:
                dst.write(v,1)
            with mem.open() as src:
                z=map_sample(src,src.read(1),[110.02,110.09,109.0],[20.55,20.55,20.55])
        self.assertEqual(z[:2].tolist(),[1,2])
        self.assertTrue(math.isnan(z[2]))

    def test_static_source_manifest_without_outcome(self):
        gps=b'S/N,Collecting time,Longitude,Latitude,HorAccuracy\n6710,2020-11-20T00:00:00Z,110.02,20.55,3\n'
        scheme=b'1: tidal flat; 2: aquaculture pond'
        tag=b'6710\tCORE_01\tCommon redshank\n'
        arr=np.ones((10,10),dtype="uint8")
        with MemoryFile() as mem:
            with mem.open(driver="GTiff",width=10,height=10,count=1,dtype="uint8",crs="EPSG:4326",transform=from_origin(110,20.6,.01,.01)) as dst:
                dst.write(arr,1)
            tif=mem.read()
        files={"tracking data/sample.csv":gps,"SN to id.txt":tag,"Habitat mapping scheme.txt":scheme,"Habitat map.tif":tif}
        roles=choose_required_files(files)
        m=source_only_manifest(files,roles,{"outer_zip_sha256":"abcd"})
        self.assertEqual(m["source_doi"],DOI)
        self.assertFalse(m["original_habitat_use_or_effects_scored"])
        self.assertEqual(read_tagmap(tag),{"6710":"CORE_01"})
        d, qc=prepare_tracking(gps,{"6710":"CORE_01"})
        self.assertEqual(qc["distinct_focal_birds"],1)
        self.assertEqual(d.loc[d.index[0],"species"],"CORE")

    def test_source_zip_path_traversal_fails(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z: z.writestr("../escape.txt", "no")
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            secure_zip(b.getvalue())

    def test_nonadmission_under_five_core_birds(self):
        examples=[]
        for i in range(5):
            for j in range(25):
                examples.append({"individual":f"CORE_{i}","species":"CORE","Y":j%2,"R":0.2 if i%2 else -0.1,
                                 "origin_cls":1,"dest_cls":1,"day":j%2,"C_distance":.5,"C_500":.4,"C_1500":.3})
        receipt=summarize(examples,source_manifest={"outer_archive":{"outer_zip_sha256":"abc"},"raster_metadata":{}},qc={},crosswalk={},max_accuracy=50)
        self.assertEqual(receipt["status"],"PRIMARY_NOT_ADMITTED")
        self.assertEqual(receipt["eligible_CORE_birds_ge20"],5)
        self.assertEqual(fit_holdout(examples,receipt)["status"],"FORECAST_NOT_ESTIMABLE_PRIMARY_GATE")

    def test_independent_bird_groups_and_prediction_sign(self):
        examples=[]
        for i in range(7):
            for j in range(100):
                c=.05+.9*(j%10)/9
                y=int(c>.5)
                examples.append({"individual":f"CORE_{i}","species":"CORE","Y":y,"R":y-c,
                    "origin_cls":j%2+1,"dest_cls":j%2+1 if y else 3,"day":j%2,
                    "C_distance":c,"C_500":c,"C_1500":c})
        receipt=summarize(examples,source_manifest={"outer_archive":{"outer_zip_sha256":"abc"},"raster_metadata":{}},qc={},crosswalk={},max_accuracy=50)
        self.assertTrue(receipt["status"].startswith("PRIMARY_ADMITTED"))
        predicted=fit_holdout(examples,receipt)
        self.assertEqual(len(predicted["bird_level_scores"]),7)
        self.assertGreater(predicted["M1_minus_M0_equal_bird_log_loss_gain"],.1)
        self.assertTrue(all(x["gain_nats_per_step"]>0 for x in predicted["bird_level_scores"]))

if __name__=="__main__":
    unittest.main()
