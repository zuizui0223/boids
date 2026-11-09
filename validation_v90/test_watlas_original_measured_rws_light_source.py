"""v90 synthetic known-truth two-taxon actual gauge-source matching ONLY.

All tags, coordinates, tide/source levels, solar labels below are synthetic.
No signed original animal behavior effect or cross-species interaction.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import unittest

import numpy as np
from pyproj import Transformer

import watlas_original_measured_rws_light_source as v

def fake_source_csv():
    proj=Transformer.from_crs("EPSG:4326","EPSG:32631",always_xy=True)
    x,y=proj.transform(5.25,53.25)
    original=["TAG,TIME,X,Y,NBS,tideID,tidaltime,waterlevel"]
    base=datetime(2018,8,12,0,0,tzinfo=timezone.utc).timestamp()
    for i in range(5):
        for j in range(3):
            source=base+3*3600*(i*3+j)
            original.append(f"T_SYNTHETIC_{i},{source},{x},{y},4,TIDE_{j},-120,0")
    return ("\n".join(original)+"\n").encode()

def prepared_fake_source(*,height_bins=2,species=("Red_knot","Sanderling"),
                          tags_per_species=5,values_per_cell=3):
    clock=datetime(2018,8,12,0,0,tzinfo=timezone.utc).timestamp()
    # A real measured 10-minute height series, assembled synthetically to
    # test the *geometry of source matching* only. RWS original is separate.
    official={}
    source={}
    daynight={}
    index=0
    for specie in species:
        original=[]
        light={}
        for bird in range(tags_per_species):
            for height in range(height_bins):
                for phase,a in (("FLOOD","DAY"),("FLOOD","NIGHT"),
                                ("EBB","DAY"),("EBB","NIGHT")):
                    for j in range(values_per_cell):
                        sec=int(clock+10800*index)
                        index+=1
                        gaugetime=sec-30*60
                        h=height*25+5
                        slope=+15 if phase=="FLOOD" else -15
                        official[gaugetime]=float(h)
                        official[gaugetime-1800]=h-slope
                        official[gaugetime+1800]=h+slope
                        tag=f"SYNTH_{specie}_{bird}"
                        original.append((sec,tag,f"TID_{j}",5.25,53.25,
                                         float(h),-120.))
                        light[(tag,sec)]=a
        source[specie]=original
        daynight[specie]=light
    return source,daynight,official

class OriginalWATLAS2018RwsSourceFalsifiers(unittest.TestCase):
    def test_genuine_source_year_taxa_original_figshare_PINNED(self):
        self.assertEqual(v.TAXA,("Red_knot","Sanderling"))
        self.assertEqual(v.TRACK_ORIGINAL_FIG9_TOTAL,
            {"Red_knot":7595,"Sanderling":6509})
        self.assertEqual(v.SOURCE_PRIOR_PHYSICAL_LAG_MIN,-30)
        self.assertEqual(v.SOURCE_COMPANION_LAG_MIN,0)
        self.assertEqual(v.WATER_HEIGHT_BIN_CM,25)
        self.assertEqual(v.SOURCE_MIN_COMPLETE_TAGS_EACH_SPECIES,3)
        self.assertEqual(v.RWS_EXPECTED,4465)

    def test_original_UTM31N_UNIX_source_15min_not_tag_observations(self):
        actual=fake_source_csv()
        # Synthetic example has 5 source tags, 15 rows (all in 15-min bins).
        with patch.dict(v.TRACK_ORIGINAL_FIG9_TOTAL,{"Red_knot":15}):
            rows,clock,qa=v._original_source_windows(actual,"Red_knot",
                              transformer=None)
        self.assertEqual(qa["source_original_genuine_radio_rows"],15)
        self.assertEqual(qa["source_distinct_original_TAGs"],5)
        self.assertEqual(qa["source_valid_actual_TAG_15min_windows"],15)
        self.assertNotIn("T_SYNTHETIC_",str(qa))
        self.assertTrue(qa["no_animal_movement_or_velocity_scored"])

    def test_source_admits_known_truth_two_height_bands_and_all_four_categories(self):
        data,solar,official=prepared_fake_source(height_bins=2)
        q=v._source_one_gauge_alignment(
            data,solar,official,shift=-30)
        self.assertEqual(q["original_complete_same_TAG_measured_25cm_all4_tide_solar_bins"],20)
        self.assertEqual(q["source_complete_mapped_TAGs_by_species"],
                         {"Red_knot":5,"Sanderling":5})
        self.assertEqual(sum(q[
            "source_TRUE_measured_RWS_height25cm_complete_4cell_tag_windows_by_species"].values()),240)
        self.assertEqual(q["source_distinct_original_tide_cycles_eligible_bins_by_species"],
                         {"Red_knot":3,"Sanderling":3})
        self.assertTrue(q["SOURCE_ADMISSION"].startswith("SOURCE_ADMITTED"))

    def test_one_height_band_not_false_support_diluted_species(self):
        data,solar,official=prepared_fake_source(height_bins=1)
        q=v._source_one_gauge_alignment(data,solar,official,shift=-30)
        self.assertEqual(q["original_complete_same_TAG_measured_25cm_all4_tide_solar_bins"],10)
        self.assertTrue(q["SOURCE_ADMISSION"].startswith("NOT_ADMITTED"))

    def test_no_night_or_missing_physical_ebb_cannot_bypass_fourcell(self):
        data,solar,official=prepared_fake_source(height_bins=2)
        for spec in data:
            for key in list(solar[spec]):
                if solar[spec][key]=="NIGHT":solar[spec][key]="DAY"
        q=v._source_one_gauge_alignment(data,solar,official,shift=-30)
        self.assertEqual(q["original_complete_same_TAG_measured_25cm_all4_tide_solar_bins"],0)
        self.assertTrue(q["SOURCE_ADMISSION"].startswith("NOT_ADMITTED"))
        with self.assertRaisesRegex(ValueError,"UNREGISTERED"):
            v._source_one_gauge_alignment(data,solar,official,shift=60)

    def test_cross_species_tag_counts_do_not_create_fake_species_8birds(self):
        data,solar,official=prepared_fake_source(
            height_bins=2,tags_per_species=2)
        q=v._source_one_gauge_alignment(data,solar,official,shift=-30)
        self.assertEqual(q["source_complete_mapped_TAGs_by_species"],
                         {"Red_knot":2,"Sanderling":2})
        self.assertTrue(q["SOURCE_ADMISSION"].startswith("NOT_ADMITTED"))

if __name__=="__main__":
    unittest.main()
