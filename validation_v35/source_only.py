#!/usr/bin/env python3
"""v35-A: source-only Wadden Sea ecotope map catalog and version gate.

NO animal GPS, RWS tide heights, original individual IDs, or habitat labels
at GPS locations are ever opened by this script. Never persist signed URLs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

MENDELEY_ID="27mysx289g"
VERSION=2
ZIP_NAME="EctpWZ3L_gpkg.zip"
MENDELEY="https://api.data.mendeley.com"
WMR="https://opengeodata.wmr.wur.nl/geoserver/ows"
LAYER_IDS=(
 "WS3shp:ws3_ecotope_mp_basic",
 "WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics",
 "WS3shp:ws3_bivbeds_focc",
)
META_MAX_BYTES=15_000_000
USER_AGENT="boids-v35-original-wadden-ecotope-metadata/1.0"

def url_for_wfs(operation,layer=None):
    if operation not in ("GetCapabilities","DescribeFeatureType"):
        raise ValueError("Unapproved source-only WFS operation")
    params={"service":"WFS","version":"2.0.0","request":operation}
    if layer is not None:
        if operation!="DescribeFeatureType" or layer not in LAYER_IDS:
            raise ValueError("Original ecotope layer unregistered")
        params["typeNames"]=layer
    return WMR+"?"+urllib.parse.urlencode(params)

def mendeley_urls():
    return (
      f"{MENDELEY}/datasets/{MENDELEY_ID}?version={VERSION}",
      f"{MENDELEY}/datasets/{MENDELEY_ID}/files?version={VERSION}",
      f"{MENDELEY}/datasets/publics/{MENDELEY_ID}/files?version={VERSION}",
    )

def fetch_metadata(url,maxbytes=META_MAX_BYTES):
    allowed=(MENDELEY+"/",WMR+"?")
    if not url.startswith(allowed):raise ValueError("Source URL not approved")
    req=urllib.request.Request(url,headers={
       "Accept":"application/json, application/xml, text/xml, */*",
       "User-Agent":USER_AGENT})
    with urllib.request.urlopen(req,timeout=40) as r:
        effective=r.geturl()
        # Prevent side-channel reads from arbitrary redirects during a source-only audit.
        if not effective.startswith((MENDELEY+"/","https://opengeodata.wmr.wur.nl/geoserver/")):
            raise ValueError("Unexpected off-provider metadata redirect")
        raw=r.read(maxbytes+1)
        content_type=r.headers.get("Content-Type","")
    if len(raw)>maxbytes: raise ValueError("Source metadata payload too large")
    return raw,{"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                "content_type":content_type}

def mendeley_safelist(obj):
    """Leave signed URLs, personal contacts, tokens, and license irrelevant data out."""
    if isinstance(obj,list):
        return {"file_count":len(obj),"files":[file_entry(x) for x in obj[:300]]}
    if isinstance(obj,dict):
        if "results" in obj and isinstance(obj["results"],list):
            return mendeley_safelist(obj["results"])
        if "files" in obj and isinstance(obj["files"],list):
            base={"file_count":len(obj["files"]),"files":[file_entry(x) for x in obj["files"]]}
        else:base={}
        doi=obj.get("doi")
        if isinstance(doi,dict): doi=doi.get("id")
        base.update({"dataset_id":obj.get("id"),"published_version":obj.get("version"),
              "dataset_doi":doi,"dataset_name":obj.get("name"),
              "dataset_state":obj.get("status"),
              "top_level_metadata_keys":sorted(obj.keys())})
        if "filename" in obj or "content_details" in obj:
            base["single_file"]=file_entry(obj)
        return base
    raise ValueError("Unrecognized source manifest JSON type")

def file_entry(x):
    if not isinstance(x,dict):return {"unrecognized":True}
    content=x.get("content_details") or {}
    return {"name":x.get("filename") or x.get("name"),
            "file_id":x.get("id"),
            "size_bytes":x.get("size") or content.get("size"),
            "published_sha256":content.get("sha256_hash") or x.get("sha256_hash"),
            "content_type":content.get("content_type"),
            "file_status":x.get("status")}

def _bare(tag):
    return tag.rsplit("}",1)[-1]

def wfs_capabilities(xml):
    root=ET.fromstring(xml)
    if _bare(root.tag)!="WFS_Capabilities":
        raise ValueError("Official WFS returned non-capabilities XML")
    out={}
    for f in root.iter():
        if _bare(f.tag)!="FeatureType":continue
        fields={_bare(c.tag):(c.text or "").strip() for c in f
                if _bare(c.tag) in ("Name","Title","Abstract","DefaultCRS")}
        name=fields.get("Name")
        if name not in LAYER_IDS:continue
        box={}
        for node in f.iter():
            if _bare(node.tag) in ("LowerCorner","UpperCorner"):
                box[_bare(node.tag)]=(node.text or "").strip()
        out[name]={"name":name,"title":fields.get("Title"),
          "public_abstract":(fields.get("Abstract") or "")[:800],
          "original_advertised_default_CRS":fields.get("DefaultCRS"),
          "original_advertised_WGS84_bbox":box}
    return {"root_schema":_bare(root.tag),
            "three_frozen_ecotope_layers":out,"matched_layers":len(out),
            "all_required_present":len(out)==len(LAYER_IDS)}

def wfs_schema(xml,layer):
    if layer not in LAYER_IDS:raise ValueError("Not a frozen ecotope layer")
    root=ET.fromstring(xml)
    if _bare(root.tag)!="schema":raise ValueError("WFS DescribeFeatureType was not XSD")
    fields=[]
    for f in root.iter():
        if _bare(f.tag)!="element":continue
        name=f.get("name")
        typ=f.get("type")
        if name and typ:
            fields.append({"name":name,"type":typ,
                            "minimum_occurrences":f.get("minOccurs")})
    return {"original_layer":layer,"all_explicit_XSD_fields":fields,
       "field_count":len(fields),
       "possible_classification_fields":[f["name"] for f in fields if
           any(q in f["name"].casefold() for q in ("ecotope","code","litora","exposure","sediment","dynami","habitat","class","zes"))]}

def error_receipt(e):
    item={"request_status":"HTTP_OR_PARSE_STOP","error_type":type(e).__name__,
          "error_status":getattr(e,"code",None),"message":str(e)[:280]}
    if isinstance(e,urllib.error.HTTPError):
        # Do not store arbitrary response data / signed URLs.
        item["provider_error_excerpt"]=e.read(500).decode("utf-8",errors="replace")[:150]
    return item

def run():
    out={"source_stage":"V35_A_SOURCE_ONLY",
         "dataset":"Baptist et al. historical Wadden Sea ecotope map corrected v2",
         "source_DOI":"10.17632/27mysx289g.2",
         "representative_years":[2008,2009,2010,2011,2012],
         "original_ZIP_name":ZIP_NAME,
         "prior_bird_GPS_and_tide_outcomes_already_known":True,
         "original_animal_GPS_or_habitat_spatial_join_scored":False,
         "mendeley_public_api":{},"WMR_original_WFS":{}}
    for url in mendeley_urls():
        desc=url.split(MENDELEY,1)[-1]
        try:
            b,meta=fetch_metadata(url)
            data=json.loads(b)
            out["mendeley_public_api"][desc]={"status":"PUBLIC_HTTP_OK",
                "provider_metadata":meta,
                "safe_json_fields":mendeley_safelist(data)}
        except (urllib.error.URLError,ValueError,TimeoutError,ET.ParseError) as e:
            out["mendeley_public_api"][desc]=error_receipt(e)
    try:
        b,meta=fetch_metadata(url_for_wfs("GetCapabilities"))
        catalog=wfs_capabilities(b)
        out["WMR_original_WFS"]["get_capabilities"]={
           "status":"PUBLIC_HTTP_OK","provider_metadata":meta,**catalog}
    except (urllib.error.URLError,ValueError,TimeoutError,ET.ParseError) as e:
        out["WMR_original_WFS"]["get_capabilities"]=error_receipt(e)
    for layer in LAYER_IDS:
        try:
            b,meta=fetch_metadata(url_for_wfs("DescribeFeatureType",layer))
            parsed=wfs_schema(b,layer)
            out["WMR_original_WFS"][layer]={
                "status":"PUBLIC_HTTP_OK","provider_metadata":meta,**parsed}
        except (urllib.error.URLError,ValueError,TimeoutError,ET.ParseError) as e:
            out["WMR_original_WFS"][layer]=error_receipt(e)
    mendeley_items=[]
    for row in out["mendeley_public_api"].values():
        sf=row.get("safe_json_fields") or {}
        mendeley_items.extend(sf.get("files") or [])
    published=[f for f in mendeley_items if f.get("name")==ZIP_NAME]
    mendeley_pass=bool(published) and all(
       f.get("published_sha256") and f.get("size_bytes") for f in published)
    wfs=out["WMR_original_WFS"]
    layerpass=(wfs.get("get_capabilities",{}).get("all_required_present") and
       all(wfs.get(layer,{}).get("status")=="PUBLIC_HTTP_OK"
           for layer in LAYER_IDS))
    out["source_evidence"]={
      "mendeley_corrected_v2_original_file_with_verifiable_SHA_manifest":mendeley_pass,
      "WMR_exact_three_named_layer_schemas_available":bool(layerpass),
      "WMR_layer_version_corrected_v2_independently_verified":False,
      "no_GPS_positions_or_GIS_feature_geometries_read":True,
      "no_animal_habitat_association_or_ecological_score_computed":True}
    if mendeley_pass:out["status"]="MENDELEY_CORRECTED_V2_FILE_MANIFEST_ADMITTED_DOWNLOAD_UNVERIFIED"
    elif layerpass:out["status"]="WMR_GEOMETRY_SCHEMA_AVAILABLE_CORRECTED_VERSION_UNVERIFIED"
    else:out["status"]="V35_PUBLIC_HABITAT_SOURCE_NOT_ADMITTED"
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v35/results/wadden_ecotope_source_only_v35.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("V35_ECOTOPE_SOURCE_STATUS",out["status"])
    print("V35_ECOTOPE_SOURCE_ONLY_AGGREGATE",json.dumps(out,sort_keys=True,separators=(",",":")))
    print("V35_NO_GPS_HABITAT_ASSOCIATION_ANALYZED")
if __name__=="__main__":
    main()
