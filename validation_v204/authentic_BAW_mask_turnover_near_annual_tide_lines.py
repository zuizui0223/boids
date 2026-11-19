"""v204 source-only: is BAW 2018->19 native topography mask turnover near
the same model product's original annual high/low boundary MultiCurves?

This is an explicitly post-v203 EXPLORATORY source diagnostic, not true
field-measured erosion, intertidal area, bird access, or causal ecology.
Raw original WCS rasters and WFS curves are held in Actions RAM only.
"""
from __future__ import annotations
import hashlib
import json
import math
import ssl
import urllib.request
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt
from rasterio.features import rasterize
from shapely.geometry import box, shape

from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
    DESTINATIONS, verified_direct_baw_OGC_GET
)
from original_BAW_year_NL_WFS_WCS_schema_envelope import (
    CAP_SHA, native_metadata_gate, tag
)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import (
    NeverFollowHTTPRedirects
)
from authentic_BAW_WFS_year_highlow_exact_curve_ROI_source import (
    EXPECTED_ORIGINAL_HITS,
    MAX_ORIGINAL_BYTES,
    get_exact_original_GeoJSON_request,
    is_exact_GeoJSON_source_request,
    extract_original_exact_geometrical_intersection
)
from original_BAW_WCS_2018_2019_NL_topography_Vlieland_ROI import (
    COVERS,
    make_native_original_WCS_ROI_request,
    original_secure_WCS_data_bytes,
    parse_original_NL_grid
)
from true_BAW_WFS_Vlieland_2018_2019_highlow_boundary_HITS import fixed_roi

PRIOR_V202_HTTP_CURVE_SHA256_RECEIPT = {
    "TrilaWatt_Wattflaechen:high_water_boundary_2018_nl":
        "4f3d9911234641d846ad43c5adc9e311b4fc48303580583b35baae6d6227c847",
    "TrilaWatt_Wattflaechen:low_water_boundary_2018_nl":
        "084e654278b56976097570879505d5b5c9b204b6a7fd856ecb67b349",
    "TrilaWatt_Wattflaechen:high_water_boundary_2019_nl":
        "b0ed2e8fab7fd1ece9a09678ebf5a921208c8ed34852e30651115b613ca52d23",
    "TrilaWatt_Wattflaechen:low_water_boundary_2019_nl":
        "c68a7332afc497e57753f7ecb3b32726db76d77d8ef902e102d",
}
# Frozen from v202 original two source-success runs BEFORE v204 retrieves any data.
# Raw GeoJSON bytes vary across successful v202 runs even when counts/length match.
# The old hashes are receipts only, not an immutable-content success gate.
FIXED_CURVE_CLIPPED_LENGTH_KM = {
    "TrilaWatt_Wattflaechen:high_water_boundary_2018_nl":30.715113,
    "TrilaWatt_Wattflaechen:low_water_boundary_2018_nl":131.948330,
    "TrilaWatt_Wattflaechen:high_water_boundary_2019_nl":28.668077,
    "TrilaWatt_Wattflaechen:low_water_boundary_2019_nl":127.491236,
}
FIXED_TOPO_SHA256 = {
    "2018": "3630b3a732efb79bc5a85a6d1c8bc0c63cff992783ca86142360837cd318ba4f",
    "2019": "e666c271b3d3cab98aaa8d0ca7ba3c076b7bd363036f9a15e58593ffa8994e37",
}
FIXED_MASK_COUNTS = {
    "2018_valid": 247437,
    "2019_valid": 219396,
    "both": 215587,
    "2018_only": 31850,
    "2019_only": 3809,
    "neither": 748754,
}
BINS_METERS = (0,50,100,250,500,1000,float("inf"))
BIN_NAMES = ("0-50m","50-100m","100-250m","250-500m",
             "500-1000m","1000m_plus")
GRID_SHAPE = (1000,1000)
OUT = Path(__file__).resolve().parent / "results/original_2018_2019_mask_turnover_near_annual_watertide_boundary_v204.json"

def source_stop_if_mismatch(actual,expected,code):
    if actual != expected:
        raise ValueError(code)

def original_WFS_curve_source_with_pinned_sha(name: str):
    if name not in EXPECTED_ORIGINAL_HITS or name not in PRIOR_V202_HTTP_CURVE_SHA256_RECEIPT:
        raise ValueError("SOURCE_STOP_UNFROZEN_WFS_NAME")
    url = get_exact_original_GeoJSON_request(name)
    if not is_exact_GeoJSON_source_request(url):
        raise ValueError("SOURCE_STOP_WFS_UNFROZEN_REQUEST")
    op = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NeverFollowHTTPRedirects())
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent":"boids-v204-original-BAW-source-boundary-mask-distance/1.0",
        "Accept":"application/json"})
    with op.open(req,timeout=65) as response:
        raw = response.read(MAX_ORIGINAL_BYTES+1)
        status, final = response.status,response.geturl()
    if status != 200 or final != url or not raw or len(raw)>MAX_ORIGINAL_BYTES:
        raise ValueError("SOURCE_STOP_GENUINE_GEOJSON_WFS_HTTP_OR_SIZE")
    origsha = hashlib.sha256(raw).hexdigest()
    # Original HTTP raw bytes differ between the two earlier v202 source-success
    # runs. Record SHA as a receipt, not evidence of immutable geometry.
    # Exclude ONLY top-level response timeStamp from the stable semantic digest.
    content=json.loads(raw)
    if content.get("type") != "FeatureCollection" or not isinstance(content.get("features"),list):
        raise ValueError("SOURCE_STOP_ORIGINAL_GEOJSON_NOT_FEATURECOLLECTION")
    frozen_content={k:v for k,v in content.items() if k!="timeStamp"}
    semantic_sha=hashlib.sha256(json.dumps(frozen_content,sort_keys=True,
       separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")).hexdigest()
    # Reuse v202 source gate: count==v201 hits, original projected
    # native MULTICURVE, no duplicated features, true ROI intersections.
    native = extract_original_exact_geometrical_intersection(raw,name)
    if (native["n_exact_curve_geometries_intersect_fixed_ROI"] !=
          EXPECTED_ORIGINAL_HITS[name] or
        native["n_WFS_BBOX_matched_but_no_true_curve_intersection"]!=0):
        raise ValueError("SOURCE_STOP_GENUINE_GEOJSON_GEOMETRY_COUNTS_CHANGED")
    if abs(native["original_line_length_clipped_to_public_Vlieland10km_km"]-
           FIXED_CURVE_CLIPPED_LENGTH_KM[name])>0.00001:
        raise ValueError("SOURCE_STOP_V202_ORIGINAL_LINE_LENGTH_NOT_REPRODUCED")
    roi=box(*fixed_roi())
    lines=[]
    for feature in content["features"]:
        g = shape(feature["geometry"])
        intersection=g.intersection(roi)
        if not intersection.is_empty and intersection.length>0:
            lines.append(intersection)
    return lines,{"source_actual_HTTP_GeoJSON_byte_SHA256":origsha,
                  "source_geometry_semantic_JSON_SHA256_excluding_top_level_timestamp":semantic_sha,
                  "source_original_v202_earlier_raw_HTTP_SHA_receipt":PRIOR_V202_HTTP_CURVE_SHA256_RECEIPT[name],
                  "native_clipped_length_km_rechecked":native["original_line_length_clipped_to_public_Vlieland10km_km"],
                  "n_original_WFS_MultiCurve_features":len(content["features"]),
                  "source_raw_curves_saved_to_artifact":False}

def fetch_original_two_year_tiff():
    grids={}
    receipts={}
    for year in ("2018","2019"):
        raw,receipt=original_secure_WCS_data_bytes(
            make_native_original_WCS_ROI_request(year))
        source_stop_if_mismatch(receipt["original_WCS_GeoTIFF_bytes_SHA256"],
            FIXED_TOPO_SHA256[year],"SOURCE_STOP_NATIVE_TOPO_TIFF_SHA_CHANGED")
        stat,mask,values,affine=parse_original_NL_grid(raw)
        if stat["n_plausible_numeric_topography_pixels_NOT_surveyday_calibrated"] != (
              FIXED_MASK_COUNTS[f"{year}_valid"]):
            raise ValueError("SOURCE_STOP_V203_FROZEN_NATIVE_NUMERIC_SUPPORT_CHANGED")
        if mask.shape!=GRID_SHAPE:
            raise ValueError("SOURCE_STOP_UNEXPECTED_10M_GRID_SHAPE")
        grids[year]=(mask,affine)
        receipts[year]={"native_original_GeoTIFF_SHA256":
               receipt["original_WCS_GeoTIFF_bytes_SHA256"],
            "native_original_valid_pixels":int(mask.sum()),
            "native_original_width_height":list(mask.shape),
            "native_original_no_raw_elevation_export":True}
    if grids["2018"][1]!=grids["2019"][1]:
        raise ValueError("SOURCE_STOP_NATIVE_YEAR_GRIDS_NOT_IDENTICAL")
    return grids,receipts

def canonical_classes(mask18,mask19):
    if mask18.shape!=mask19.shape or mask18.dtype!=np.bool_ or mask19.dtype!=np.bool_:
        raise ValueError("SOURCE_STOP_INVALID_YEAR_BOOLEAN_MASKS")
    classes={
        "2018_only":mask18&~mask19,
        "2019_only":~mask18&mask19,
        "both":mask18&mask19,
        "neither":~mask18&~mask19,
    }
    if sum(int(x.sum()) for x in classes.values()) != mask18.size:
        raise ValueError("SOURCE_STOP_PIXEL_CLASSES_NOT_DISJOINT_EXHAUSTIVE")
    return classes

def bin_source_masks(classes, distance):
    if set(classes)!={"2018_only","2019_only","both","neither"}:
        raise ValueError("SOURCE_STOP_SOURCE_CLASS_NAMES_INVALID")
    if distance.shape!=classes["both"].shape or not np.all(np.isfinite(distance)):
        raise ValueError("SOURCE_STOP_INVALID_BOUNDARY_DISTANCE_RASTER")
    bins = np.digitize(distance, [50,100,250,500,1000],right=False)
    ret={}
    for i,bname in enumerate(BIN_NAMES):
        band=bins==i
        nums={c:int(np.sum(m&band)) for c,m in classes.items()}
        n18=nums["2018_only"]+nums["both"]
        nums["original_year2018_valid_pixel_n"]=n18
        nums["probability_2018_valid_becomes_2019_invalid"]=(
            round(nums["2018_only"]/n18,8) if n18 else None)
        nums["all_native_grid_pixels_in_band"]=int(np.sum(band))
        ret[bname]=nums
    if sum(r["all_native_grid_pixels_in_band"] for r in ret.values()) != distance.size:
        raise ValueError("SOURCE_STOP_DISTANCE_BIN_ASSIGNMENT_NOT_EXHAUSTIVE")
    return ret

def risk_ratio_near_far(classes,distance):
    original2018=classes["2018_only"]|classes["both"]
    lost=classes["2018_only"]
    bands={"near_lt100m":distance<100,"far_gte500m":distance>=500}
    counts={}
    for label,region in bands.items():
        eligible=int(np.sum(original2018&region))
        disappeared=int(np.sum(lost&region))
        counts[label]={"native_2018_valid_eligible":eligible,
                       "native_2018_to_2019_invalid":disappeared,
                       "conditional_loss_rate":round(disappeared/eligible,8)
                          if eligible else None}
    n=counts["near_lt100m"]
    f=counts["far_gte500m"]
    if n["native_2018_valid_eligible"]==0 or f["native_2018_valid_eligible"]==0:
        ratio=None
    elif f["native_2018_to_2019_invalid"]==0:
        ratio=None
    else:
        ratio=round((n["native_2018_to_2019_invalid"]/n["native_2018_valid_eligible"])/
           (f["native_2018_to_2019_invalid"]/f["native_2018_valid_eligible"]),8)
    return {"source_near_vs_far_counts":counts,
        "loss_risk_ratio_near100m_to_far500m":ratio,
        "posthoc_descriptive_not_an_independent_ecological_effect":True}

def quadrants(classes):
    out={}
    N,M=classes["both"].shape
    for name,ys,xs in (("NW",slice(None,N//2),slice(None,M//2)),
                        ("NE",slice(None,N//2),slice(M//2,None)),
                        ("SW",slice(N//2,None),slice(None,M//2)),
                        ("SE",slice(N//2,None),slice(M//2,None))):
        out[name]={k:int(v[ys,xs].sum()) for k,v in classes.items()}
    return out

def analyze_masks_against_lines(mask18,mask19,lines,affine):
    classes=canonical_classes(mask18,mask19)
    bitmap=rasterize(((curve,1) for curve in lines),
                     out_shape=mask18.shape,transform=affine,fill=0,
                     all_touched=True,dtype="uint8")
    n_line=int(np.sum(bitmap==1))
    if n_line<100:raise ValueError("SOURCE_STOP_SOURCE_LINES_DID_NOT_RASTERIZE")
    distance=distance_transform_edt(bitmap==0,sampling=(abs(affine.e),abs(affine.a)))
    totals={key:int(value.sum()) for key,value in classes.items()}
    for name,expected in (("both",215587),("2018_only",31850),("2019_only",3809)):
        source_stop_if_mismatch(totals[name],FIXED_MASK_COUNTS[name],
            "SOURCE_STOP_SOURCE_V203_PIXEL_TRANSITION_COUNTS_NOT_EQUAL")
    return {
        "source_total_native_grid_pixels":int(mask18.size),
        "source_native_2018_2019_classes":totals,
        "n_source_line_raster_pixels_alltouched":n_line,
        "source_distance_method":"EPSG25832 10m rasterized four original year high/low MultiCurves, scipy Euclidean distance_transform_edt",
        "native_distance_bin_classes":bin_source_masks(classes,distance),
        "frozen_near_far_mask_loss_contrast":risk_ratio_near_far(classes,distance),
        "native_quadrant_mask_change_all_classes":quadrants(classes),
        "native_boundary_distance_is_approx_not_exact_curve_distance":True,
        "source_mask_change_not_necessarily_real_intertidal_area_or_erosion":True}

def run(out=OUT):
    record={"version":"v204-original-BAW-WCS2018-2019-numeric-mask-transition-vs-WFS-water-boundary",
      "post_v203_exploratory_not_biology":True,
      "original_WFS_v202_prior_HTTP_SHA_receipts_not_stable":PRIOR_V202_HTTP_CURVE_SHA256_RECEIPT,
      "original_WFS_v202_clipped_length_km_frozen":FIXED_CURVE_CLIPPED_LENGTH_KM,
      "original_WCS_TIFF_binary_SHA256_frozen":FIXED_TOPO_SHA256,
      "frozen_2018_and_2019_original_valid_support_counts":FIXED_MASK_COUNTS,
      "frozen_source_distance_bins_m":list(BIN_NAMES),
      "original_source_use_only_10km_published_Vlieland_ROI":True,
      "raw_source_curves_or_TIFF_never_persisted":True,
      "status":"SOURCE_STOP"}
    try:
        for service in ("WFS","WCS"):
            xml,receipt=verified_direct_baw_OGC_GET(DESTINATIONS[service],service)
            if xml is None or receipt.get("original_XML_SHA256")!=CAP_SHA[service]:
                raise ValueError("SOURCE_STOP_ORIGINAL_BAW_OGC_CAPABILITIES_SHA_CHANGED")
            native,entries,ops=native_metadata_gate(xml,service)
            required_operation="GetFeature" if service=="WFS" else "GetCoverage"
            if required_operation not in ops:
                raise ValueError("SOURCE_STOP_NO_AUTHENTIC_NATIVE_OGC_OPERATION")
        grids,tiff_receipts=fetch_original_two_year_tiff()
        line_geometries=[]
        curve_receipts={}
        for name in PRIOR_V202_HTTP_CURVE_SHA256_RECEIPT:
            curves,provenance=original_WFS_curve_source_with_pinned_sha(name)
            line_geometries.extend(curves)
            curve_receipts[name]=provenance
        if len(line_geometries)!=sum(EXPECTED_ORIGINAL_HITS.values()):
            raise ValueError("SOURCE_STOP_ORIGINAL_GEOJSON_FOUR_LAYER_LINE_COUNT")
        record["original_native_WFS_curve_source_receipts"]=curve_receipts
        record["original_native_WCS_10m_TIFF_source_receipts"]=tiff_receipts
        record["original_bounded_mask_vs_boundary_distance_audit"] = (
           analyze_masks_against_lines(grids["2018"][0],grids["2019"][0],
                                      line_geometries,grids["2018"][1]))
        record["status"]="ORIGINAL_BAW_BOUNDARY_DISTANCE_VS_YEARLY_SUPPORT_MASK_AUDITED_EXPLORATORY"
    except Exception as e:
        record["source_stop_error_kind"]=type(e).__name__
        record["source_stop_reason"]=str(e)[:240]
    record["scientific_gates"]={
        "all_original_raw_WCS_WFS_binary_SHAs_and_geographies_verified":
            record["status"]=="ORIGINAL_BAW_BOUNDARY_DISTANCE_VS_YEARLY_SUPPORT_MASK_AUDITED_EXPLORATORY",
        "real_2018_2019_intertidal_habitat_area_loss_inferred":False,
        "original_field_survey_year_days_verified":False,
        "original_local_GPS_h_s_t_and_datum_reconciled":False,
        "bird_ACC_tide_solar_or_social_Boids_effect_estimated":False}
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    physical=record.get("original_bounded_mask_vs_boundary_distance_audit",{})
    print("V204_ORIGINAL_WATT_BOUNDARY_MASK_SCOPE="+json.dumps({
      "status":record["status"],
      "source_stop_reason":record.get("source_stop_reason"),
      "native_mask_classes":physical.get("source_native_2018_2019_classes"),
      "distance_bins":physical.get("native_distance_bin_classes"),
      "near_far_loss":physical.get("frozen_near_far_mask_loss_contrast"),
      "quadrants":physical.get("native_quadrant_mask_change_all_classes"),
      "n_line_mask_pixels":physical.get("n_source_line_raster_pixels_alltouched"),
      "no_new_bird_or_true_intertidal_area":True
    },sort_keys=True),flush=True)
    return record

if __name__=="__main__":
    run()
