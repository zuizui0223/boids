"""v216: year-specific BAW ncHydro WCS *candidate* metadata-only audit.
The official WMS endpoint is published; the sibling WCS endpoint is unverified
until its actual HTTPS OGC response succeeds. WCS NilValue != NetCDF _FillValue.
NO model water-level binaries, actual NetCDF, GPS, DEM, RWS or animal data.
"""
from __future__ import annotations
import hashlib,json,re,ssl,urllib.error,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from original_BAW_2018_2019_verified_WMS_capabilities import (
 OFFICIAL_YEAR_WMS, fetch_verified_original_WMS, inspect_WMS_xml)
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
 FIXED_CAPABILITIES_SHA256,NATIVE_HEIGHT_LAYERS)

CANDIDATE={
 "2018":"https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wcs?service=WCS&version=2.0.1&request=GetCapabilities",
 "2019":"https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2019/wcs?service=WCS&version=2.0.1&request=GetCapabilities"}
OUT=Path(__file__).resolve().parent/"results/BAW_timed_ncHydro_2018_2019_WCS_native_description_v216.json"

class NeverRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def tag(node):
    return node.tag.rsplit("}",1)[-1] if isinstance(node.tag,str) else ""

def text_child(node,field):
    for x in node:
        if tag(x).lower()==field.lower():
            return " ".join(" ".join(x.itertext()).split())
    return ""

def safe_xml(raw,expected):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_NATIVE_WCS_UNTRUSTED_XML_ENTITY")
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:raise ValueError("STOP_NATIVE_WCS_UNPARSABLE_XML") from e
    if tag(root).lower()!=expected.lower():
        raise ValueError("STOP_NOT_ORIGINAL_WCS_"+expected.upper())
    return root

def fixed_wcs_authorized(url,year,operation,cover=None):
    if year not in CANDIDATE:
        return False
    u=urllib.parse.urlsplit(url)
    if not (u.scheme=="https" and u.hostname=="coast.baw.de" and u.port is None and
       u.username is None and u.password is None and not u.fragment and
       u.path==f"/geoserver/TrilaWatt_ncHydro_{year}/wcs"):
        return False
    pairs=urllib.parse.parse_qsl(u.query)
    d=dict(pairs)
    if len(d)!=len(pairs) or d.get("service")!="WCS" or d.get("version")!="2.0.1" or d.get("request")!=operation:
        return False
    if operation=="GetCapabilities":
        return url==CANDIDATE[year] and set(d)=={"service","version","request"}
    if operation=="DescribeCoverage":
        return cover and d.get("coverageId")==cover and set(d)=={"service","version","request","coverageId"}
    return False

def original_GET(year,url,operation,cover=None,max_bytes=4000000):
    if not fixed_wcs_authorized(url,year,operation,cover):
        raise ValueError("STOP_NOT_FROZEN_BAW_YEAR_WCS_QUERY")
    op=urllib.request.build_opener(
       urllib.request.HTTPSHandler(context=ssl.create_default_context()),NeverRedirect())
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v216-original-BAW-yearly-ncHydro-WCS-metadata-only/1.0",
       "Accept":"text/xml,application/xml"})
    try:
        with op.open(req,timeout=35) as r:
            blob=r.read(max_bytes+1)
            code=r.status
            final=r.geturl()
            ct=r.headers.get("Content-Type")
        if code!=200 or final!=url or not blob or len(blob)>max_bytes or not blob.lstrip().startswith(b"<"):
            raise ValueError("STOP_NATIVE_WCS_NOT_HTTPS200_BOUNDED_XML")
        return blob,{"status":"BAW_CANDIDATE_WCS_HTTPS200_XML",
          "native_http_code":code,"original_SHA256":hashlib.sha256(blob).hexdigest(),
          "original_bytes":len(blob),"original_content_type":ct,
          "default_CA_validation_ON":True,"no_redirect_followed":True}
    except urllib.error.HTTPError as e:
        return None,{"status":"SOURCE_STOP_CANDIDATE_BAW_WCS_HTTP",
          "native_http_code":e.code,"unfollowed_Location":e.headers.get("Location"),
          "no_redirect_followed":True}

def parse_native_WCS_capabilities(blob,year):
    root=safe_xml(blob,"Capabilities")
    if root.attrib.get("version")!="2.0.1":
        raise ValueError("STOP_WCS_NOT_NATIVE_VERSION2_0_1")
    ops=set()
    cover=[]
    for node in root.iter():
        if tag(node)=="Operation" and node.attrib.get("name"):
            ops.add(node.attrib["name"])
        if tag(node)=="CoverageSummary":
            cid=text_child(node,"CoverageId")
            if cid:
                cover.append({"native_CoverageId":cid[:300],
                              "native_Title":text_child(node,"Title")[:150]})
    if len(cover)==0 or len(cover)>1000:
        raise ValueError("STOP_WCS_NO_COVERAGE_OR_UNBOUNDED")
    matches=[]
    for row in cover:
        s=(row["native_CoverageId"]+" "+row["native_Title"]).lower()
        height=any(t in s for t in ("sea_surface_height_2d","sea_surface_height",
                                     "wasserstand","water_level","sea surface height"))
        nl=bool(re.search(r"(^|[^a-z])nl([^a-z]|$)",s))
        if height and str(year) in s and nl:
            matches.append(row)
    return {
      "native_year_WCS2_version":root.attrib["version"],
      "native_number_of_CoverageIds":len(cover),
      "native_advertised_operations":sorted(ops),
      "source_CoverageId_sample_up_to80":cover[:80],
      "native_2018_2019_NL_SSH_CoverageId_candidates":matches[:25],
      "candidate_count":len(matches),
      "not_NetCDF_original_variable_attrs":True}

def describe_URL(year,cid):
    if year not in CANDIDATE or not isinstance(cid,str) or not(1<=len(cid)<=300):
        raise ValueError("STOP_WRONG_WCS_COVERAGE")
    b=urllib.parse.urlsplit(CANDIDATE[year])
    q=urllib.parse.urlencode([("service","WCS"),("version","2.0.1"),
          ("request","DescribeCoverage"),("coverageId",cid)])
    url=urllib.parse.urlunsplit((b.scheme,b.netloc,b.path,q,""))
    if not fixed_wcs_authorized(url,year,"DescribeCoverage",cid):
        raise ValueError("STOP_UNAUTHORIZED_NATIVE_COVERAGE")
    return url

def parse_native_WCS_desc(blob,cid):
    root=safe_xml(blob,"CoverageDescriptions")
    d=[n for n in root if tag(n)=="CoverageDescription"]
    if len(d)!=1:
        raise ValueError("STOP_WRONG_NATIVE_DESCRIPTION_COUNT")
    ids=[(n.text or "").strip() for n in d[0].iter() if tag(n)=="CoverageId"]
    if ids!=[cid]:
        raise ValueError("STOP_NATIVE_DESCRIPTION_COVERAGE_ID_MISMATCH")
    env=[];fields=[];nils=[]
    for n in d[0].iter():
        if tag(n)=="Envelope" and len(env)<4:
            env.append({"srsName":n.attrib.get("srsName"),
               "axisLabels":n.attrib.get("axisLabels"),
               "uomLabels":n.attrib.get("uomLabels"),
               "lowerCorner":text_child(n,"lowerCorner"),
               "upperCorner":text_child(n,"upperCorner")})
        if tag(n)=="field" and len(fields)<25:
            fields.append({"name":n.attrib.get("name"),
                "native_WCS_uom":[z.attrib.get("code") for z in n.iter() if tag(z)=="uom"][:8]})
        if tag(n).lower()=="nilvalue" and len(nils)<25:
            nils.append({"value":(n.text or "").strip()[:120],
                         "reason":n.attrib.get("reason")})
    return {"native_original_CoverageId":cid,
       "native_WCS_envelopes":env,
       "native_WCS_range_fields":fields,
       "native_WCS_nil_values":nils,
       "OGC_service_nil_is_not_original_NetCDF__FillValue":True,
       "original_NetCDF_units_FillValue_datum_verified":False}

def run(out=OUT):
    result={"version":"v216-Baw-timed-ncHydro-2018-2019-WCS-candidate-source-preflight",
       "WCS_candidates_NOT_registered_official_BAW_WCS_source":CANDIDATE,
       "published_official_year_WMS_source":OFFICIAL_YEAR_WMS,
       "frozen_WMS_XML_SHA256":FIXED_CAPABILITIES_SHA256,
       "no_NetCDF_annual_binary_or_GetCoverage_or_bird_GPS":True,
       "status":"SOURCE_STOP"}
    results={}
    for year in ("2018","2019"):
        item={"status":"SOURCE_STOP_WCS_YEAR_UNVERIFIED"}
        try:
            wms,wr=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            if wr["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year]:
                raise ValueError("STOP_ORIGINAL_WMS_SOURCE_SHA_CHANGED")
            w=inspect_WMS_xml(wms,target_year=year)
            if not any(x["name"]==NATIVE_HEIGHT_LAYERS[year] for x in
                       w["source_tide_water_height_named_layers_cap45"]):
                raise ValueError("STOP_ORIGINAL_NL_WMS_HEIGHT_LAYER_NOT_FOUND")
            item["published_WMS_original_SHA_reverified"]=wr["original_WMS_xml_SHA256"]
            cap,receipt=original_GET(year,CANDIDATE[year],"GetCapabilities")
            item["candidate_WCS_http_receipt"]=receipt
            if cap is None:
                item["status"]="SOURCE_STOP_WCS_CANDIDATE_NOT_BAW_AVAILABLE_OGC"
            else:
                native=parse_native_WCS_capabilities(cap,year)
                item["actual_native_WCS_metadata"]=native
                item["status"]="TRUE_WCS2_NATIVE_CAPABILITIES_OBTAINED"
                matches=native["native_2018_2019_NL_SSH_CoverageId_candidates"]
                if len(matches)!=1:
                    item["status"]="SOURCE_STOP_NATIVE_NL_SEA_HEIGHT_COVERAGE_NOT_UNIQUE"
                elif "DescribeCoverage" not in native["native_advertised_operations"]:
                    item["status"]="SOURCE_STOP_WCS_NO_ADVERTISED_DESCRIBE"
                else:
                    cid=matches[0]["native_CoverageId"]
                    raw,dr=original_GET(year,describe_URL(year,cid),"DescribeCoverage",
                                        cid,max_bytes=2000000)
                    item["WCS_DescribeCoverage_http_receipt"]=dr
                    if raw is not None:
                        item["native_WCS_DescribeCoverage_metadata"]=parse_native_WCS_desc(raw,cid)
                        item["status"]="TRUE_NATIVE_WCS_NL_HEIGHT_DESCRIBECOVERAGE_OBTAINED"
                    else:
                        item["status"]="SOURCE_STOP_NATIVE_WCS_DESCRIBE_HTTP_ERROR"
        except Exception as exc:
            item["status"]="SOURCE_STOP_YEAR_SOURCE_OR_PARSE_INVALID"
            item["error_kind"]=type(exc).__name__
            item["error_summary"]=str(exc)[:230]
        results[year]=item
    result["year_results"]=results
    result["source_gates"]={
       "both_years_authentic_published_BAW_WMS_reverified":all(
            x.get("published_WMS_original_SHA_reverified")==FIXED_CAPABILITIES_SHA256[y]
            for y,x in results.items()),
       "both_years_native_WCS2_Capabilities_retrieved":all(
            bool(x.get("actual_native_WCS_metadata")) for x in results.values()),
       "both_years_NL_height_native_WCS_DescribeCoverage_retrieved":all(
            x["status"]=="TRUE_NATIVE_WCS_NL_HEIGHT_DESCRIBECOVERAGE_OBTAINED"
            for x in results.values()),
       "native_NetCDF_original__FillValue_directly_verified":False,
       "native_NetCDF_original_units_and_vertical_datum_directly_verified":False,
       "year_model_WMS_1e31_established_physically_dry_cell":False,
       "bird_GPS_tide_sun_social_Boids_causal_effect_estimated":False}
    result["status"]="BAW_ORIGINAL_TWO_YEAR_TIMED_NCHYDRO_WCS2_DESCRIPTIONS_SOURCE_ONLY" if (
        result["source_gates"]["both_years_NL_height_native_WCS_DescribeCoverage_retrieved"]
    ) else "SOURCE_STOP_NATIVE_TIMED_NCHYDRO_WCS2_HEIGHT_NOT_ADMITTED_BOTH_YEARS"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V216_ORIGINAL_TIMED_NCHYDRO_WCS="+json.dumps({
       "status":result["status"],"gates":result["source_gates"],
       "by_year":{y:{"status":x["status"],
          "http":x.get("candidate_WCS_http_receipt",{}).get("native_http_code"),
          "n_coverages":x.get("actual_native_WCS_metadata",{}).get("native_number_of_CoverageIds"),
          "height_candidates":x.get("actual_native_WCS_metadata",{}).get("native_2018_2019_NL_SSH_CoverageId_candidates"),
          "OGC_nil":x.get("native_WCS_DescribeCoverage_metadata",{}).get("native_WCS_nil_values"),
          "OGC_uom":x.get("native_WCS_DescribeCoverage_metadata",{}).get("native_WCS_range_fields"),
          "error":x.get("error_summary")}
          for y,x in results.items()},
       "no_NetCDF_binary_or_behavior_used":True
    },sort_keys=True))
    return result

if __name__=="__main__":
    run()
