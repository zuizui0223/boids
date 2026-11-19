"""v200: original BAW year-NL Wattflächen WFS schema + WCS coverage metadata only.
No WFS GetFeature, no WCS GetCoverage, no raw pixels/polygons, no bird GPS.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request,urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from pyproj import Transformer
from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
    DESTINATIONS,verified_direct_baw_OGC_GET
)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import NeverFollowHTTPRedirects

CAP_SHA={
"WFS":"ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5",
"WCS":"55e531bbe17f8720b5b1aecc82130c1d8a29adb10738fe727ac3d4869f2afeec",
}
YEARS=("2018","2019")
WFS_TYPES=tuple(
 f"TrilaWatt_Wattflaechen:{kind}_water_boundary_{year}_nl"
 for year in YEARS for kind in ("high","low"))
WCS_IDS=tuple(
 f"TrilaWatt_Wattflaechen__{kind}_{year}_nl"
 for year in YEARS for kind in ("topography_inter_supratidal",
     "high_water_boundary_confidence","low_water_boundary_confidence"))
PUBLISHED_VLIE_RD=(135280,590000)
OUT=Path(__file__).resolve().parent/"results/BAW_original_2018_2019_NL_WFS_WCS_schema_bbox_v200.json"

def tag(t):
    return t.rsplit("}",1)[-1].split(":")[-1]

def child_text(node,name):
    for c in node:
        if tag(c.tag)==name:return (c.text or "").strip()
    return None

def source_xml(raw,expected_root=None):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_ORIGINAL_XML_DTD_ENTITY")
    root=ET.fromstring(raw)
    if expected_root and tag(root.tag).lower()!=expected_root.lower():
        raise ValueError("STOP_ORIGINAL_GML_OR_OGC_DOCUMENT_TYPE_MISMATCH")
    return root

def parsed_corner_pair(node):
    for x in node.iter():
        if tag(x.tag)!="WGS84BoundingBox":continue
        a=child_text(x,"LowerCorner")
        b=child_text(x,"UpperCorner")
        if a and b:
            lo=list(map(float,a.split()));hi=list(map(float,b.split()))
            if len(lo)==2 and len(hi)==2 and lo[0]<=hi[0] and lo[1]<=hi[1]:
                return [lo[0],lo[1],hi[0],hi[1]]
    return None

def metadata_named_original(root,tag_name,key,required_names):
    entries={}
    for n in root.iter():
        if tag(n.tag)!=tag_name:continue
        name=child_text(n,key)
        if name is None or name not in required_names:continue
        if name in entries:raise ValueError("SOURCE_STOP_DUPLICATE_NATIVE_NAMED_COVERAGE_FEATURE")
        entries[name]=n
    if set(entries)!=set(required_names):
        raise ValueError("SOURCE_STOP_NATIVE_ORIGINAL_NL_YEAR_NAMES_MISSING_OR_AMBIGUOUS")
    return entries

def declared_ops(root):
    return {n.attrib.get("name") for n in root.iter()
            if tag(n.tag)=="Operation" and n.attrib.get("name")}

def native_metadata_gate(orig_bytes,service):
    if hashlib.sha256(orig_bytes).hexdigest()!=CAP_SHA[service]:
        raise ValueError("SOURCE_STOP_BAW_NATIVE_2018_2019_WFS_WCS_SOURCE_SHA_CHANGED")
    root=source_xml(orig_bytes)
    if service=="WFS":
        if tag(root.tag)!="WFS_Capabilities" or root.attrib.get("version")!="2.0.0":
            raise ValueError("SOURCE_STOP_NOT_ORIGINAL_WFS2")
        entries=metadata_named_original(root,"FeatureType","Name",WFS_TYPES)
    else:
        if tag(root.tag) not in ("Capabilities","WCS_Capabilities") or root.attrib.get("version")!="2.0.1":
            raise ValueError("SOURCE_STOP_NOT_ORIGINAL_WCS2_0_1")
        entries=metadata_named_original(root,"CoverageSummary","CoverageId",WCS_IDS)
    return root,entries,declared_ops(root)

def only_native_query(service,operation,name):
    if service=="WFS":
        if operation!="DescribeFeatureType" or name not in WFS_TYPES:raise ValueError("UNFROZEN_WFS_SCHEMA")
        params={"service":"WFS","version":"2.0.0","request":"DescribeFeatureType","typeNames":name}
    elif service=="WCS":
        if operation!="DescribeCoverage" or name not in WCS_IDS:raise ValueError("UNFROZEN_WCS_COVERAGE")
        params={"service":"WCS","version":"2.0.1","request":"DescribeCoverage","coverageId":name}
    else:raise ValueError("UNFROZEN_OGC_SERVICE")
    root=urllib.parse.urlsplit(DESTINATIONS[service])
    return urllib.parse.urlunsplit((root.scheme,root.netloc,root.path,
               urllib.parse.urlencode(params),""))

def original_secure_describe(service,operation,name,limit=800_000):
    url=only_native_query(service,operation,name)
    req=urllib.request.Request(url,headers={
      "User-Agent":"boids-v200-source-schema-only-original-BAW/1.0",
      "Accept":"application/xml,text/xml"},method="GET")
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NeverFollowHTTPRedirects())
    with op.open(req,timeout=30) as response:
        raw=response.read(limit+1)
        status=response.status
        url_final=response.geturl()
    if len(raw)>limit or not raw or status!=200 or url_final!=url:
        raise ValueError("STOP_ORIGINAL_BAW_DESCRIBE_HTTP_OR_SIZE_OR_REDIRECT")
    native=source_xml(raw)
    if operation=="DescribeFeatureType":
        if tag(native.tag)!="schema":raise ValueError("SOURCE_STOP_NOT_GENUINE_XSD_SCHEMA")
    elif tag(native.tag)!="CoverageDescriptions":
        raise ValueError("SOURCE_STOP_NOT_GENUINE_GML_COVERAGE_DESCRIPTIONS")
    return native,{"native_original_XML_SHA256":hashlib.sha256(raw).hexdigest(),
        "native_response_bytes":len(raw),"HTTPS_CA_verified":True,
        "no_raw_raster_or_geometry_feature_downloaded":True}

def summarize_xsd(root):
    out=[]
    for elem in root.iter():
        if tag(elem.tag)!="element":continue
        nm=elem.attrib.get("name")
        if nm and len(out)<30:
            out.append({"original_element_name":nm[:100],
                "declared_type":elem.attrib.get("type","")[:150],
                "substitutionGroup":elem.attrib.get("substitutionGroup","")[:120]})
    return {"original_XSD_elements_capped30":out,
        "n_native_element_declarations":sum(tag(n.tag)=="element" for n in root.iter()),
        "no_polygon_geometries_downloaded":True}

def summarize_coverage(root):
    srs=[]
    fields=[]
    nill=[]
    bounds=[]
    for item in root.iter():
        t=tag(item.tag)
        if t=="Envelope" and len(bounds)<3:
            bounds.append({"source_srsName":item.attrib.get("srsName"),
                "source_axisLabels":item.attrib.get("axisLabels"),
                "lower":child_text(item,"lowerCorner"),
                "upper":child_text(item,"upperCorner")})
        elif t=="field" and len(fields)<20:
            fields.append({"field_name":item.attrib.get("name")})
        elif t=="NilValue" and len(nill)<20:
            nill.append((item.text or "").strip()[:80])
    return {"original_coverage_envelopes":bounds,
      "native_rangeType_fields":fields,
      "native_nilvalue_literals":nill,
      "no_original_coverage_pixels_downloaded":True}

def run(out=OUT):
    transform=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True)
    lon,lat=transform.transform(*PUBLISHED_VLIE_RD)
    result={"analysis":"v200-original-WFS2-WCS2-NL-2018-2019-boundary-schema-bbox-only",
        "v199_authentic_original_308_destinations_source_runs":[44429739018,44429768184],
        "pinned_original_capability_SHA256":CAP_SHA,
        "public_2011_reference_VlielandHaven_RD":PUBLISHED_VLIE_RD,
        "public_2011_reference_reprojected_WGS84_lonlat":[round(lon,6),round(lat,6)],
        "not_original_tagged_bird_GPS":True,
        "no_original_OGC_GetFeature_or_GetCoverage_used":True,
        "status":"SOURCE_STOP"}
    by_service={}
    for service,names in (("WFS",WFS_TYPES),("WCS",WCS_IDS)):
        record={"status":"SOURCE_STOP", "source_names":list(names),"layers":{}}
        try:
            raw,receipt=verified_direct_baw_OGC_GET(DESTINATIONS[service],service)
            if raw is None:raise ValueError("SOURCE_STOP_ORIGINAL_BAW_CAP_NOT_HTTP200")
            orig,entries,operations=native_metadata_gate(raw,service)
            record["original_capabilities_SHA256"]=receipt["original_XML_SHA256"]
            record["native_operations"]=sorted(x for x in operations if x)
            expected_op="DescribeFeatureType" if service=="WFS" else "DescribeCoverage"
            record["native_operation_advertised"]=expected_op in operations
            for name in names:
                entry=entries[name]
                bounds=parsed_corner_pair(entry)
                source={"native_original_metadata_WGS84_BBox":bounds,
                    "2011_public_Vlie_reference_within_source_metadata_bbox":(
                        bounds[0]<=lon<=bounds[2] and bounds[1]<=lat<=bounds[3]) if bounds else None,
                    "original_native_CRS_declared":child_text(entry,"DefaultCRS")
                         or child_text(entry,"DefaultSRS") or child_text(entry,"SupportedCRS"),
                    "source_metadata_no_geometry_data":True}
                if record["native_operation_advertised"]:
                    try:
                        schema,provenance=original_secure_describe(service,expected_op,name)
                        source["native_original_describe_response_SHA256"]=provenance["native_original_XML_SHA256"]
                        source["description_status"]="ORIGINAL_DESCRIBE_SCHEMA_ONLY_ADMITTED"
                        source["original_describe_source_fields"]=(
                            summarize_xsd(schema) if service=="WFS" else summarize_coverage(schema))
                    except Exception as e:
                        source["description_status"]="SOURCE_STOP_NATIVE_DESCRIBE"
                        source["describe_error_kind"]=type(e).__name__
                        source["describe_error_summary"]=str(e)[:180]
                else:
                    source["description_status"]="SOURCE_STOP_NATIVE_DESCRIBE_OPERATION_NOT_ADVERTISED"
                record["layers"][name]=source
            record["status"]="ORIGINAL_YEAR_NL_LAYER_SOURCE_BBOX_AND_DESCRIBE_AUDITED_NO_GEOMETRY"
        except Exception as e:
            record["status"]="SOURCE_STOP_NATIVE_YEAR_NL_CAPABILITIES_OR_BBOX"
            record["error_kind"]=type(e).__name__
            record["error_summary"]=str(e)[:220]
        by_service[service]=record
    result["services"]=by_service
    result["scientific_gates"]={
        "both_original_WFS_WCS_frozen_SHA_and_native_all_year_NL_layer_names":all(
           v["status"]=="ORIGINAL_YEAR_NL_LAYER_SOURCE_BBOX_AND_DESCRIBE_AUDITED_NO_GEOMETRY"
           for v in by_service.values()),
        "all_4_WFS_year_NL_boundary_schemas_original_checked":all(
           v.get("description_status")=="ORIGINAL_DESCRIBE_SCHEMA_ONLY_ADMITTED"
           for v in by_service["WFS"]["layers"].values()),
        "all_6_WCS_NL_raster_metadata_original_checked":all(
           v.get("description_status")=="ORIGINAL_DESCRIBE_SCHEMA_ONLY_ADMITTED"
           for v in by_service["WCS"]["layers"].values()),
        "2011_published_Vlie_reference_metadata_bbox_covered_by_all_WFS_year_NL":all(
           v.get("2011_public_Vlie_reference_within_source_metadata_bbox") is True
           for v in by_service["WFS"]["layers"].values()),
        "native_year_2018_2019_genuine_intertidal_polygon_geometry_verified":False,
        "bird_GPS_true_local_dryflat_and_Wasserstand_NAP_calibrated":False,
        "animal_foraging_sun_tide_or_social_Boids_effect_estimated":False}
    result["status"]="ORIGINAL_TWO_SERVICE_YEAR_NL_SCHEMA_METADATA_AUDITED_GEOMETRIES_STILL_STOP" if (
      result["scientific_gates"]["both_original_WFS_WCS_frozen_SHA_and_native_all_year_NL_layer_names"]
    ) else "SOURCE_STOP_ORIGINAL_WFS_WCS_YEAR_NL_SCHEMA_METADATA"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V200_BAW_ORIGINAL_NL_INTERTIDAL_SOURCE="+json.dumps({
       "status":result["status"],"gates":result["scientific_gates"],
       "by_service":{k:{"status":v["status"],
          "operations":v.get("native_operations"),
          "layers":{n:{"native_WGS84_BBox":x["native_original_metadata_WGS84_BBox"],
                       "2011_Vlie_within_provider_bbox":x["2011_public_Vlie_reference_within_source_metadata_bbox"],
                       "native_CRS":x.get("original_native_CRS_declared"),
                       "describe_status":x["description_status"],
                       "source_fields":x.get("original_describe_source_fields"),
                       "error":x.get("describe_error_summary")}
                      for n,x in v["layers"].items()},
          "error":v.get("error_summary")} for k,v in by_service.items()},
       "no_GPS_local_tide_or_animal_behavior_used":True},sort_keys=True))
    return result

if __name__=="__main__":
    run()
