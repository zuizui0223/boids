"""v202 source-only TRUE original WFS line geometry in frozen Vlieland 10km ROI.

Original public vector data are parsed in Actions memory then discarded.
Only aggregate length/count and source byte SHA are committed, never raw coordinates.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request
from pathlib import Path
from shapely.geometry import box,shape
from original_BAW_year_NL_WFS_WCS_schema_envelope import (
    CAP_SHA, WFS_TYPES, native_metadata_gate,tag)
from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
    DESTINATIONS,verified_direct_baw_OGC_GET)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import NeverFollowHTTPRedirects
from true_BAW_WFS_Vlieland_2018_2019_highlow_boundary_HITS import (
    fixed_roi,SOURCE_WFS_NATIVE_CRS)

EXPECTED_ORIGINAL_HITS={
 "TrilaWatt_Wattflaechen:high_water_boundary_2018_nl":7,
 "TrilaWatt_Wattflaechen:low_water_boundary_2018_nl":52,
 "TrilaWatt_Wattflaechen:high_water_boundary_2019_nl":8,
 "TrilaWatt_Wattflaechen:low_water_boundary_2019_nl":50,
}
MAX_ORIGINAL_BYTES=8_000_000
MAX_NATIVE_FEATURES=100
OUT=Path(__file__).resolve().parent/"results/BAW_original_2018_2019_Vlieland_highlow_true_line_intersection_v202.json"

def get_exact_original_GeoJSON_request(name):
    if name not in EXPECTED_ORIGINAL_HITS:
        raise ValueError("SOURCE_STOP_NONFROZEN_HIGH_LOW_ORIGINAL_FEATURE")
    bbox=fixed_roi()
    query={"service":"WFS","version":"2.0.0","request":"GetFeature",
       "typeNames":name,
       "srsName":SOURCE_WFS_NATIVE_CRS,
       "bbox":",".join(f"{x:.3f}" for x in bbox)+","+SOURCE_WFS_NATIVE_CRS,
       "count":str(MAX_NATIVE_FEATURES),
       "outputFormat":"application/json"}
    base=urllib.parse.urlsplit(DESTINATIONS["WFS"])
    return urllib.parse.urlunsplit((base.scheme,base.netloc,base.path,
            urllib.parse.urlencode(query),""))

def is_exact_GeoJSON_source_request(url):
    parts=urllib.parse.urlsplit(url)
    q=dict(urllib.parse.parse_qsl(parts.query))
    return (parts.scheme=="https" and parts.hostname=="coast.baw.de"
       and parts.path=="/geoserver/TrilaWatt_Wattflaechen/wfs"
       and q.get("service")=="WFS" and q.get("version")=="2.0.0"
       and q.get("request")=="GetFeature"
       and q.get("typeNames") in EXPECTED_ORIGINAL_HITS
       and q.get("outputFormat")=="application/json"
       and q.get("srsName")==SOURCE_WFS_NATIVE_CRS
       and q.get("bbox")==",".join(f"{x:.3f}" for x in fixed_roi())+","+SOURCE_WFS_NATIVE_CRS
       and q.get("count")==str(MAX_NATIVE_FEATURES))

def extract_original_exact_geometrical_intersection(raw,name):
    obj=json.loads(raw)
    if obj.get("type")!="FeatureCollection" or not isinstance(obj.get("features"),list):
        raise ValueError("STOP_WFS_ORIGINAL_NOT_JSON_FEATURECOLLECTION")
    feat=obj["features"]
    if len(feat)!=EXPECTED_ORIGINAL_HITS[name]:
        raise ValueError("STOP_NATIVE_FEATURES_COUNT_DIFFERS_FROM_FROZEN_V201_HITS")
    returned=obj.get("numberReturned")
    if returned is not None and int(returned)!=len(feat):
        raise ValueError("STOP_NATIVE_RESPONSE_FEATURES_COUNT_MISMATCH")
    sourceid=[]
    roi=box(*fixed_roi())
    true_hits=0
    positive_length=0
    total_clip_length=0.
    original_line_total=0.
    feature_geometries=0
    for f in feat:
        if not isinstance(f,dict) or f.get("type")!="Feature":
            raise ValueError("STOP_NOT_NATIVE_WFS_FEATURE")
        if f.get("id"):
            sourceid.append(str(f["id"]))
        geom=f.get("geometry")
        if not isinstance(geom,dict):
            raise ValueError("STOP_MISSING_ORIGINAL_GEOMETRY")
        g=shape(geom)
        if g.geom_type not in ("LineString","MultiLineString"):
            raise ValueError("STOP_SOURCE_NOT_YEAR_BOUNDARY_LINE_GEOMETRY")
        if g.is_empty:continue
        minx,miny,maxx,maxy=g.bounds
        if not(100000<minx<800000 and 100000<maxx<800000 and
               5000000<miny<7000000 and 5000000<maxy<7000000):
            raise ValueError("STOP_WFS_GEOJSON_NOT_IN_EXPECTED_METRIC_EPSG25832")
        feature_geometries+=1
        original_line_total+=g.length
        if g.intersects(roi):
            true_hits+=1
            clip=g.intersection(roi)
            length=clip.length
            if length>0:positive_length+=1
            total_clip_length+=length
    if sourceid and len(set(sourceid))!=len(sourceid):
        raise ValueError("STOP_NONUNIQUE_NATIVE_ORIGINAL_FEATURE_IDS")
    return {"native_WFS2_original_source_count":len(feat),
      "n_native_nonempty_line_geometries":feature_geometries,
      "n_exact_curve_geometries_intersect_fixed_ROI":true_hits,
      "n_intersections_with_positive_line_length":positive_length,
      "n_WFS_BBOX_matched_but_no_true_curve_intersection":len(feat)-true_hits,
      "original_line_length_clipped_to_public_Vlieland10km_km":round(total_clip_length/1000,6),
      "source_true_length_is_NOT_intertidal_area_or_coast_retreat":True}

def fetch_and_score_one(name):
    url=get_exact_original_GeoJSON_request(name)
    if not is_exact_GeoJSON_source_request(url):
        raise ValueError("STOP_NONFROZEN_ORIGINAL_GETFEATURE_QUERY")
    op=urllib.request.build_opener(
       urllib.request.HTTPSHandler(context=ssl.create_default_context()),
       NeverFollowHTTPRedirects())
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v202-real-original-WFS-MultiCurve-clip-10km-source-only/1.0",
       "Accept":"application/json"})
    with op.open(req,timeout=60) as r:
        raw=r.read(MAX_ORIGINAL_BYTES+1)
        status=r.status
        final=r.geturl()
        ct=r.headers.get("Content-Type")
    if status!=200 or final!=url or len(raw)>MAX_ORIGINAL_BYTES or not raw or "json" not in str(ct).lower():
        raise ValueError("STOP_NATIVE_WFS_RAW_FEATURE_TOO_LARGE_OR_RESPONSE_NOT_ORIGINAL_JSON")
    stat=extract_original_exact_geometrical_intersection(raw,name)
    return {"native_original_GeoJSON_payload_SHA256":hashlib.sha256(raw).hexdigest(),
      "native_original_source_HTTP_status":status,
      "native_original_GeoJSON_bytes_only_in_runner":len(raw),
      "original_raw_curve_coordinates_NOT_in_public_artifacts":True,
      **stat}

def run(out=OUT):
    data={"version":"v202-true-original-BAW-2018-2019-high-low-curves-geometric-clip",
       "original_WFS_capabilities_source_exact_SHA":CAP_SHA["WFS"],
       "original_v201_fixed_HITS_counts":EXPECTED_ORIGINAL_HITS,
       "fixed_original_public_reference_ROI_EPSG25832":[round(x,3) for x in fixed_roi()],
       "no_GPS_or_annual_intertidal_polygon_or_original_water_heights":True,
       "status":"SOURCE_STOP"}
    records={}
    try:
        raw,receipt=verified_direct_baw_OGC_GET(DESTINATIONS["WFS"],"WFS")
        if raw is None:raise ValueError("SOURCE_STOP_CAPABILITIES_NOT_RETRIEVED")
        root,originals,ops=native_metadata_gate(raw,"WFS")
        if receipt["original_XML_SHA256"]!=CAP_SHA["WFS"] or "GetFeature" not in ops:
            raise ValueError("SOURCE_STOP_NATIVE_WFS_CAPABILITIES_SHA_OR_OPERATION")
        for name in EXPECTED_ORIGINAL_HITS:
            crs=next((ch.text for ch in originals[name] if tag(ch.tag)=="DefaultCRS"),None)
            if crs!=SOURCE_WFS_NATIVE_CRS:
                raise ValueError("SOURCE_STOP_ORIGINAL_MULTI_CURVE_EXPECTED_CRS_MISMATCH")
            try:
                records[name]={"status":"ORIGINAL_YEAR_HIGHLOW_TRUE_ROI_CURVE_INTERSECTION_AUDITED",
                               **fetch_and_score_one(name)}
            except Exception as exc:
                records[name]={"status":"SOURCE_STOP_EXACT_ORIGINAL_HIGHLOW_CURVE_INTERSECTION",
                    "error_type":type(exc).__name__,"error_summary":str(exc)[:230]}
    except Exception as exc:
        data["source_error_type"]=type(exc).__name__
        data["source_error_summary"]=str(exc)[:230]
    data["four_source_original_curve_aggregate_results"]=records
    n_ok=sum(v["status"]=="ORIGINAL_YEAR_HIGHLOW_TRUE_ROI_CURVE_INTERSECTION_AUDITED"
             for v in records.values())
    n_positive=sum(v.get("n_intersections_with_positive_line_length",0)>0 for v in records.values())
    data["scientific_gates"]={
       "all_four_original_year_highlow_curve_geometry_source_QA_passed":n_ok==4,
       "n_native_four_types_verified":n_ok,
       "n_types_with_positive_original_curve_length_inside_public_ROI":n_positive,
       "all_four_types_truly_have_positive_line_length_in_ROI":n_ok==4 and n_positive==4,
       "original_raw_geometry_vertices_published":False,
       "annual_intertidal_polygon_area_or_timed_exposure_admitted":False,
       "tagged_bird_true_GPS_behavior_and_social_Boids_not_scored":True}
    data["status"]="ORIGINAL_FOUR_YEAR_BOUNDARY_TRUE_LINE_CLIPPING_AGGREGATED_NO_BIOLOGY" if n_ok==4 else "SOURCE_STOP_ORIGINAL_SOURCE_LINE_INTERSECTION_INCOMPLETE"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V202_EXACT_BAW_YEAR_BOUNDARY_CURVES="+json.dumps({
       "status":data["status"],"gates":data["scientific_gates"],
       "lines_by_source":{n:{"status":v["status"],
         "n_original":v.get("native_WFS2_original_source_count"),
         "n_true_intersections":v.get("n_exact_curve_geometries_intersect_fixed_ROI"),
         "n_false_bbox_only":v.get("n_WFS_BBOX_matched_but_no_true_curve_intersection"),
         "clipped_length_km":v.get("original_line_length_clipped_to_public_Vlieland10km_km"),
         "error":v.get("error_summary")} for n,v in records.items()},
       "source_error":data.get("source_error_summary"),"not_an_area_or_behavior":True},sort_keys=True))
    return data

if __name__=="__main__":
    run()
