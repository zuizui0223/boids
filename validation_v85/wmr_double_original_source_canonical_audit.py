"""v85D ONLY WMR source SHA serialization diagnosis after zero-bird-source stop.

Two independent official WMR WFS GetFeature full responses per site.
All true 0..6 native polygon geometries are Shapely-normalized, hashed
independently of WFS ordering. Compare authentic 2010 NIOZ 398520-grid
class vector bytewise hash; old v84C actual class counts stay immutable.
Absolutely NO original wild GPS or RWS tide or model used-value data.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json

from wmr_original_midhigh_native_nioz_grid_source import (
    _native_original_Jan2010_grid)
from wild_2010_modelled_tidal_exposure_rank import _locxy
from midhigh_intertidal_source_and_fourway import (
    classify_native_2010_model_sites)

def run(output):
    lat,lon,proof=_native_original_Jan2010_grid()
    source_xy=_locxy(lat,lon)
    sites={}
    for site in ("Schier","Ameland"):
        copies=[]
        for replica in (1,2):
            q=classify_native_2010_model_sites(
                source_xy,site,
                source_only_diagnostic_waive_RAW_sha=True)
            receipt=q["source_record"]
            copies.append(receipt)
            print("V85D_WMR_NATIVE_ORIGINAL_GEOSPATIAL_SOURCE_REPLICA "+
                  json.dumps({"site":site,"replica":replica,
                    "current_RAW_GeoJSON_SHA":receipt[
                      "source_current_original_WMR_RAW_GeoJSON_sha256"],
                    "original_v84C_RAW_SHA_equal":receipt[
                      "source_WMR_older_original_RAW_response_SHA_matches"],
                    "original_all_native_0_6_canonical_polygon_SHA":receipt[
                      "source_original_WMR_ALL_CODE0_TO6_canonical_geometry_SHA256"],
                    "native_2010_grid_class_array_SHA":receipt[
                      "source_true_native_2010_mid_high_class_grid_vector_SHA256"],
                    "source_mid_cells":receipt["native_model_center_count_mid3"],
                    "source_high_cells":receipt["native_model_center_count_high4"]},
                    sort_keys=True),flush=True)
        canon=[x["source_original_WMR_ALL_CODE0_TO6_canonical_geometry_SHA256"]
               for x in copies]
        native=[x["source_true_native_2010_mid_high_class_grid_vector_SHA256"]
                for x in copies]
        if len(set(canon))!=1 or len(set(native))!=1:
            raise ValueError("SOURCE_STOP_V85D_TWO_INDEPENDENT_ORIGINAL_WMR_GEOMETRIES_OR_NATIVE_MASK_DIFFER")
        sites[site]={
            "original_twice_publisher_full_GeoJSON_RAW_SHA256":
                [x["source_current_original_WMR_RAW_GeoJSON_sha256"] for x in copies],
            "original_twice_response_RAW_SHA_matches_previous_v84C":
                [x["source_WMR_older_original_RAW_response_SHA_matches"] for x in copies],
            "original_original_ALL_0_6_class_polygon_geometry_CANONICAL_SHA256":
                canon[0],
            "original_NIOZ_398520_model_native_CODE3_4_CLASS_GRID_SHA256":native[0],
            "original_true_WMR_polygons_full_count":copies[0][
                "original_WMR_publisher_polygon_count"],
            "genuine_NIOZ_WMR_mid_class3":copies[0]["native_model_center_count_mid3"],
            "genuine_NIOZ_WMR_high_class4":copies[0]["native_model_center_count_high4"],
            "two_source_retrievals_same_original_canonical_polygon_and_indexwise_class":True}
    result={
        "analysis":"V85D_PRE_BIRD_WMR_RAW_WFS_RESPONSE_DRIFT_2X_ORIGINAL_CANONICAL_GEOMETRY_CHECK",
        "frozen_protocol":"docs/V85D_FROZEN_WMR_TWO_INDEPENDENT_SOURCE_SHAPE_HASH_AUDIT.md",
        "original_NIOZ_publisher_source_jan2010":proof,
        "original_public_WMR_full_source_site_checksums":sites,
        "source_status":"SOURCE_AUTHENTICATED_SEMANTICALLY_IDENTICAL_TWO_INDEPENDENT_WMR_GETFEATURE_PER_ISLAND",
        "source_retrieval_0_original_bird_GPS_0_RWS_0_behavior_scores":True,
        "corrected_Mendeley_2021_v2_source_version_NOT_VERIFIED":True,
        "source_class2_low_littoral_excluded":True,
        "published_WMR_all_0_to6_polygon_SHAs_are_locally_computed_not_publisher_certified":True}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V85D_ORIGINAL_WMR_CANONICAL_SEMANTIC_SOURCE_DECISION "+
          json.dumps({"source":result["source_status"],
             "canonical_shape_by_site":{s:r[
                 "original_original_ALL_0_6_class_polygon_geometry_CANONICAL_SHA256"]
                      for s,r in sites.items()},
             "native_2010_indexed_3_4_class_by_site":{s:r[
                 "original_NIOZ_398520_model_native_CODE3_4_CLASS_GRID_SHA256"]
                      for s,r in sites.items()},
             "no_wild_animal_source_read":True},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    run(p.parse_args().output)
