"""v73 synthetic known-truth gate and ecological-index null/positive tests.

No synthetic animal outputs can be represented as real Dutch shorebirds.
"""
from __future__ import annotations
import gzip
import io
import csv
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path

import numpy as np

from wild_gps_native_month_exposure import (
    _locxy,_cluster_bootstrap,model_used_vs_local,map_geo_source_only,
    original_visible_january_2010_fixes,grid_source,MIN_HOURLY_FIXES)

def known_truth_grid(*,used_high=True,uniform=False):
    lat=np.linspace(53.4,53.5,101)
    lon=np.linspace(5.95,6.05,101)
    source_lat,source_lon=np.meshgrid(lat,lon,indexing="ij")
    xyz=_locxy(source_lat.ravel(),source_lon.ravel())
    grid=np.full(101*101,.05 if used_high else .95)
    # 25 source model cells, with all fixed original source-quality support
    # and distinct numeric index values. Critically not true bird behavior.
    cells=[(38+(i*7)%25,40+(i*11)%25) for i in range(25)]
    for i,(y,x) in enumerate(cells):
        grid[y*101+x]=(.52+.017*i if used_high else .45-.017*i)
    if uniform:
        grid[:]=.5
    fixes=[]
    for bird in range(5):
        for k in range(60):
            y,x=cells[(k+bird)%len(cells)]
            t=datetime(2010,1,2)+timedelta(hours=bird*70+k)
            fixes.append({"id":f"TEST_ONLY_{bird}",
                "t":t,"lat":float(source_lat[y,x]),
                "lon":float(source_lon[y,x])})
    return {"xy":xyz,"exposure":grid,"n_source_cells":len(grid)},fixes

class AuthenticSourceFieldLogicTests(unittest.TestCase):
    def test_known_positive_local_model_index_comparison_and_independent_bird_bootstrap(self):
        grid,fixes=known_truth_grid(used_high=True)
        mapped,src=map_geo_source_only(fixes,grid)
        self.assertEqual(len(mapped),5*60)
        self.assertEqual(src["source_bird_count"],5)
        self.assertEqual(src["source_birds_with_at_least_20_mapped_original_fixes"],5)
        q=model_used_vs_local(fixes,grid)
        self.assertEqual(q["source_gate"]["source_admission"],
            "ORIGINAL_WILD_JANUARY_POSITION_NIOZ_MODEL_1KM_LOCAL_COMPARISON")
        m=q["original_field_primary"]
        self.assertEqual(m["source_original_detected_2010_bird_count"],5)
        self.assertEqual(m["source_original_January_positions_with_1km_native_model_reference"],300)
        self.assertGreater(m["source_bird_equal_model_numeric_index_used_minus_nearby"],.3)
        self.assertGreater(m["whole_bird_cluster_bootstrap_95"][0],0)
        self.assertEqual(m["source_birds_positive_local_index_contrast"],5)
        self.assertEqual(m["source_field_status"],
            "EXPLORATORY_POSITIVE_LOCAL_NATIVE_MODELED_EXPOSURE_INDEX_ASSOCIATION")
        self.assertNotIn("TEST_ONLY_",str(q))

    def test_known_negative_local_model_index_does_not_become_positive(self):
        model,fixes=known_truth_grid(used_high=False)
        report=model_used_vs_local(fixes,model)
        contrast=report["original_field_primary"]
        self.assertLess(contrast["source_bird_equal_model_numeric_index_used_minus_nearby"],-.2)
        self.assertLess(contrast["whole_bird_cluster_bootstrap_95"][1],0)
        self.assertEqual(contrast["source_field_status"],
                         "LOCAL_MODELED_EXPOSURE_ASSOCIATION_NOT_ESTABLISHED")

    def test_uniform_monthly_exposure_has_no_source_variation_for_identification(self):
        model,fixes=known_truth_grid(uniform=True)
        r=model_used_vs_local(fixes,model)
        self.assertEqual(r["original_field_exposure_index_contrast"],
                         "NOT_ESTIMATED_SOURCE_GATE")
        self.assertIn("TOO_FEW_DISTINCT",r["source_gate"]["source_admission"])

    def test_underpowered_source_stops_without_exposure_contrast(self):
        model,fixes=known_truth_grid()
        r=model_used_vs_local(fixes[:100],model)
        self.assertEqual(r["original_field_exposure_index_contrast"],
                         "NOT_ESTIMATED_SOURCE_GATE")
        self.assertIn("INSUFFICIENT",r["source_gate"]["source_admission"])
        self.assertEqual(MIN_HOURLY_FIXES,200)

    def test_2010_field_native_earliest_hour_and_no_hidden_target_filter(self):
        fd=io.StringIO()
        keys=["event-id","timestamp","location-lat","location-long",
              "individual-local-identifier","visible","FUTURE_HEADING_IGNORE"]
        wr=csv.DictWriter(fd,fieldnames=keys)
        wr.writeheader()
        for i,minute in enumerate((45,20,55)):
            wr.writerow({"event-id":str(i),"timestamp":
                          f"2010-01-02 04:{minute:02d}:00",
                          "location-lat":53.45,
                          "location-long":6.07,
                          "individual-local-identifier":"PRIVATE_TEST",
                          "visible":"TRUE","FUTURE_HEADING_IGNORE":9999-i})
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.gz"
            with gzip.open(path,"wt",encoding="utf-8",newline="") as gz:
                gz.write(fd.getvalue())
            rows,qa=original_visible_january_2010_fixes(path)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["t"].minute,20)
        self.assertNotIn("FUTURE_HEADING_IGNORE",str(rows))
        self.assertEqual(qa["original_valid_visible_January_distinct_bird_hour_fixes"],1)

    def test_bootstrap_source_bird_only_and_original_native_grid_fixed(self):
        for q in _cluster_bootstrap([.11]*5,20261108):
            self.assertAlmostEqual(q,.11,places=12)
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
            _cluster_bootstrap([np.nan],20261108)
        lat=np.full((486,820),53.45)
        lon=np.full((486,820),6.)
        expo=np.full((486,820),.5)
        g=grid_source((lat,lon,expo))
        self.assertEqual(g["n_source_cells"],398520)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            grid_source((lat,lon,np.full((486,820),2.)))

if __name__=="__main__":
    unittest.main()
