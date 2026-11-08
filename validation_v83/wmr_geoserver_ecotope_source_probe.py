"""v83B direct original Wageningen Marine Research ecotope WFS source audit.

The publisher's public WMR GeoServer may serve the trilateral ecotope
layers even when corrected Mendeley 2021 v2 archive requires API auth.
A WS3 layer name is NOT proof that 2021 v2 4% low-littoral boundary
was corrected. Output first the true VERSION gate before any GPS use.
No original animal GPS, RWS series or NIOZ model rank evaluated.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
import re
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from xml.etree import ElementTree as ET

BASE="https://opengeodata.wmr.wur.nl/geoserver/WS3shp/ows"
PUBLISHER_HOST="opengeodata.wmr.wur.nl"
EXPECTED_LAYERS=(
    "WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics",
    "WS3shp:ws3_ecotope_mp_basic",
    "WS3shp:ws3_ecotope_mp_zessmpl",
    "WS3shp:ws3_bivbeds_focc")
MAIN="WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics"
STATION_BBOX={
    "Schiermonnikoog":(6.00,53.35,6.32,53.53),
    "Ameland_Nes":(5.58,53.34,5.96,53.51)}
MAX_CAPABILITIES_BYTES=4_000_000
MAX_DESCRIPTION_BYTES=1_000_000
MAX_SAMPLE_BYTES=3_000_000
MAX_GEO_FEATURES=10
EXPECTED_CORRECTED_DOI="10.17632/27mysx289g.2"
VERSION_STRICT_SOURCE="WMR_WFS_ORIGINAL_ECOTOPE_VERSION_NOT_VERIFIED"

class SourceUnavailable(Exception):pass

def bounded_request(params,*,limit):
    fields={"service":"WFS","version":"2.0.0",**params}
    url=BASE+"?"+urlencode(fields)
    p=urlparse(url)
    if p.hostname!=PUBLISHER_HOST or p.scheme!="https":
        raise SourceUnavailable("SOURCE_STOP_V83B_NOT_WMR_ORIGINAL_HOST")
    try:
        with urlopen(Request(url,headers={
            "User-Agent":"boids-v83b-original-WMR-WS3-ecotope-source-audit/1.0",
            "Accept":"application/xml,application/json,*/*"}),timeout=60) as stream:
            data=stream.read(limit+1)
            if len(data)>limit:
                raise SourceUnavailable("SOURCE_STOP_V83B_TOO_MUCH_SOURCE_DATA")
            if urlparse(stream.geturl()).scheme!="https":
                raise SourceUnavailable("SOURCE_STOP_V83B_INSECURE_REDIRECT")
            return data
    except (HTTPError,URLError,TimeoutError) as e:
        raise SourceUnavailable("SOURCE_UNAVAILABLE_V83B_PUBLIC_WMR_WFS "+str(e)[:150]) from e

def native_capabilities(raw):
    try:xml=ET.fromstring(raw)
    except ET.ParseError as e:
        raise SourceUnavailable("SOURCE_STOP_V83B_NOT_ORIGINAL_WFS_XML") from e
    if xml.tag.endswith("ExceptionReport"):
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_EXCEPTION_REPORT")
    features={}
    for layer in xml.findall(".//{*}FeatureType"):
        def a(name):
            v=layer.findtext("{*}"+name)
            return " ".join((v or "").split())[:350]
        name=a("Name")
        if name not in EXPECTED_LAYERS:continue
        bbox=layer.find(".//{*}WGS84BoundingBox")
        coord={}
        if bbox is not None:
            coord={
                "lower":(bbox.findtext("{*}LowerCorner") or "")[:90],
                "upper":(bbox.findtext("{*}UpperCorner") or "")[:90]}
        urls=[]
        for m in layer.findall(".//{*}MetadataURL"):
            href=next((str(value) for key,value in m.attrib.items()
                       if key.endswith("href")),None)
            if href and href.startswith("https://"):
                urls.append(href[:250])
        features[name]={
            "title":a("Title"),
            "abstract":a("Abstract"),
            "wgs84_bbox_source":coord,
            "source_metadata_links":urls,
            "native_name":name}
    return {
        "original_WFS_capabilities_SHA256_locally_computed_not_publisher_hash":
            sha256(raw).hexdigest(),
        "source_original_relevant_layers":features,
        "original_main_ecotope_layer_present":MAIN in features,
        "original_relevant_layers_count":len(features)}

def native_schema(raw):
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_SCHEMA_XML_INVALID") from e
    if root.tag.endswith("ExceptionReport"):
        raise SourceUnavailable("SOURCE_STOP_V83B_GEOSERVER_SCHEMA_EXCEPTION")
    fields=[]
    for element in root.iter():
        if element.tag.endswith("element"):
            name=element.attrib.get("name")
            if name:
                fields.append({
                    "source_field":name[:90],
                    "source_type":str(element.attrib.get("type",""))[:90]})
    if not fields:
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_FIELDS_NOT_RETURNED")
    return {"source_original_schema_fields":fields[:100],
            "original_native_litoral_or_depth_fields":[f["source_field"]
                 for f in fields if re.search(
                     "litor|literal|expos|class|depth|dynamic|zes",
                     f["source_field"],re.I)],
            "source_schema_XML_SHA256_local_not_publisher_digest":
                sha256(raw).hexdigest()}

def native_sample(raw,station):
    try:geo=json.loads(raw)
    except (ValueError,TypeError) as e:
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_SAMPLE_NOT_GEOJSON") from e
    if not isinstance(geo,dict) or not isinstance(geo.get("features"),list):
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_NO_GEOJSON_FEATURES")
    features=geo["features"]
    if len(features)>MAX_GEO_FEATURES:
        raise SourceUnavailable("SOURCE_STOP_V83B_WFS_RETURNED_MORE_THAN_10")
    classes=Counter()
    geometry=Counter()
    props=set()
    for f in features:
        properties=f.get("properties") or {}
        props|=set(properties)
        geom=f.get("geometry") or {}
        geometry[str(geom.get("type"))[:45]]+=1
        for key,value in properties.items():
            if re.search("litor|literal|expos|class|depth|dynamic|zes",
                         str(key),re.I):
                if isinstance(value,(int,float,str)) and len(str(value))<75:
                    classes[str(key)[:60]+":"+str(value)[:75]]+=1
    return {
        "original_public_station_region":station,
        "original_WFS_polygon_geojson_samples":len(features),
        "original_native_source_property_field_names":sorted(
            [str(k)[:90] for k in props]),
        "original_native_relevant_class_code_sample_counts":dict(classes),
        "original_geometries_only_type_counts_not_original_coordinates":
            dict(geometry),
        "source_sample_SHA256_local_not_publisher_digest":
            sha256(raw).hexdigest(),
        "sample_is_not_estimate_of_all_polygon_class_abundance":True}

def version_strict_from_publisher_meta(cap,schema):
    """Never treat WS3 name as the corrected 2021 v2 DOI."""
    text=" ".join([
        x.get("title","")+" "+x.get("abstract","")+" "+
        " ".join(x.get("source_metadata_links",[]))
        for x in cap["source_original_relevant_layers"].values()])
    text+=" "+json.dumps(schema["source_original_schema_fields"])
    x=text.lower()
    has_v2_doi=EXPECTED_CORRECTED_DOI in x
    has_explicit_correction=(
        "2021" in x and
        ("4%" in x or "4 percent" in x or "0.04" in x) and
        ("correc" in x or "corrigen" in x or "revised" in x))
    return {
        "source_version_2021_v2_DOI_in_WMR_original_native_metadata":
            has_v2_doi,
        "source_corrected_boundary_4percent_explicit_in_original_metadata":
            has_explicit_correction,
        "corrected_2021_v2_SOURCE_status":
            ("CORRECTED_2021_V2_PROVENANCE_VERIFIED"
             if has_v2_doi or has_explicit_correction
             else VERSION_STRICT_SOURCE),
        "underlying_published_map_v1_correction_not_assumed_from_WS3_name":True}

def run(output):
    report={
        "analysis":"V83B_PUBLISHER_WMR_WFS_WS3_TIDAL_ECOTOPE_NATIVE_CLASS_AND_VERSION_SOURCE",
        "source_original_WMR_public_base":BASE,
        "fixed_corrected_Mendeley_V2_DOI":EXPECTED_CORRECTED_DOI,
        "original_corrected_GPKG_API_previous_status":"SOURCE_UNAVAILABLE_HTTP_401",
        "is_source_only_no_wild_bird_GPS_modelled_index_or_RWS_data":True}
    try:
        cap=native_capabilities(bounded_request(
            {"request":"GetCapabilities"},limit=MAX_CAPABILITIES_BYTES))
        report["original_publisher_WMR_WFS_metadata"]=cap
        if not cap["original_main_ecotope_layer_present"]:
            raise SourceUnavailable("SOURCE_NOT_ADMITTED_V83B_MAIN_WS3_PUBLISHER_LAYER_ABSENT")
        schema=native_schema(bounded_request(
            {"request":"DescribeFeatureType","typeNames":MAIN},
            limit=MAX_DESCRIPTION_BYTES))
        report["original_WMR_polygon_source_field_schema"]=schema
        samples={}
        for site,bbox in STATION_BBOX.items():
            fmt=",".join(f"{x:.5f}" for x in bbox)+",CRS:84"
            x=bounded_request({
                "request":"GetFeature","typeNames":MAIN,
                "count":str(MAX_GEO_FEATURES),
                "srsName":"CRS:84",
                "bbox":fmt,
                "outputFormat":"application/json"},
                limit=MAX_SAMPLE_BYTES)
            samples[site]=native_sample(x,site)
        report["original_OGC_WFS_bounded_source_samples"]=samples
        version=version_strict_from_publisher_meta(cap,schema)
        report["original_ecotope_native_corrected_version_evidence"]=version
        report["source_geographic_class_source_status"]=(
            "PUBLISHER_WFS_ORIGINAL_ECOTOPE_FIELDS_FOUND"
            if all(s["original_WFS_polygon_geojson_samples"]>=1 for s in
                   samples.values()) and
               schema["original_native_litoral_or_depth_fields"]
            else "SOURCE_NOT_ADMITTED_V83B_NO_BOTH_STATION_CLASS_FEATURES")
        report["corrected_v2_habitat_mask_SOURCE_ADMISSION"]=(
            "ADMITTED_SOURCE_CORRECTED_2021_V2_PUBLISHER_GEOSERVICE"
            if report["source_geographic_class_source_status"]==
                "PUBLISHER_WFS_ORIGINAL_ECOTOPE_FIELDS_FOUND"
            and version["corrected_2021_v2_SOURCE_status"]==
                "CORRECTED_2021_V2_PROVENANCE_VERIFIED"
            else "NOT_ADMITTED_VERSION_UNVERIFIED_OR_SOURCE_INCOMPLETE")
    except SourceUnavailable as exc:
        report["source_geographic_class_source_status"]="SOURCE_UNAVAILABLE_V83B_WMR_PUBLISHER"
        report["corrected_v2_habitat_mask_SOURCE_ADMISSION"] = (
            "NOT_ADMITTED_VERSION_UNVERIFIED_OR_SOURCE_INCOMPLETE")
        report["public_WMR_original_source_error"]=str(exc)[:350]
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V83B_WMR_OFFICIAL_WFS_NATIVE_ECOTOPE_SOURCE_RESULT "+json.dumps({
        "WFS_source_status":report["source_geographic_class_source_status"],
        "corrected_2021_v2_source_status":
            report["corrected_v2_habitat_mask_SOURCE_ADMISSION"],
        "observed_WMR_layer_names":list(report.get(
            "original_publisher_WMR_WFS_metadata",{}).get(
            "source_original_relevant_layers",{})),
        "original_http_or_source_issue":report.get(
            "public_WMR_original_source_error")
    },sort_keys=True,ensure_ascii=False),flush=True)
    print("V83B_WMR_GEOSERVER_ECOTOPE_SOURCE_AUDIT_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--output",required=True)
    run(ap.parse_args().output)
