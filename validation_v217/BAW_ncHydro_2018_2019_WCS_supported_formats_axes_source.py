"""v217: original BAW ncHydro 2018/19 WCS2 native output formats and
DescribeCoverage space/time axis metadata; no actual WCS GetCoverage or NC.
Strict SHA lock both pre-verified authentic BAW Capabilities/Describe sources.
"""
from __future__ import annotations
import hashlib,json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
  CANDIDATE,original_GET,describe_URL,safe_xml,parse_native_WCS_capabilities,
  parse_native_WCS_desc
)
from original_BAW_2018_2019_verified_WMS_capabilities import (
  OFFICIAL_YEAR_WMS,fetch_verified_original_WMS,inspect_WMS_xml
)
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
  FIXED_CAPABILITIES_SHA256,NATIVE_HEIGHT_LAYERS
)

FROZEN_WCS_CAP_SHA={
 "2018":"7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388",
 "2019":"a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d"}
FROZEN_COVERAGE_IDS={
 "2018":"TrilaWatt_ncHydro_2018__sea_surface_height_2d_2018_NL",
 "2019":"TrilaWatt_ncHydro_2019__sea_surface_height_2d_2019_NL"}
FROZEN_DESCRIBE_SHA={
 "2018":"bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664",
 "2019":"9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91"}
FROZEN_NATIVE_NIL="9.999999848243207E30"
MAX_TEXT_CUE=220
MAX_NATIVE_ELEMENTS=250
OUT=Path(__file__).resolve().parent/"results/authentic_BAW_ncHydro_2018_2019_WCS2_formats_axes_native_v217.json"

def local(node):
    return node.tag.rsplit("}",1)[-1] if isinstance(node.tag,str) else ""

def compact_text(node):
    return " ".join(" ".join(node.itertext()).split())

def safe_info_slice(s,limit=MAX_TEXT_CUE):
    return str(s or "")[:limit]

def source_native_formats(raw):
    root=safe_xml(raw,"Capabilities")
    if root.attrib.get("version")!="2.0.1":
        raise ValueError("SOURCE_STOP_NCHYDRO_WCS_CAP_VERSION_DRIFT")
    format_tags={"formatSupported","SupportedFormat","nativeFormat","CoverageFormat",
                 "format","Format"}
    fmts=[]
    ops=[]
    root_names=Counter()
    service_info=[]
    for el in root.iter():
        key=local(el)
        root_names[key]+=1
        if key in format_tags and el.text:
            value=" ".join(el.text.split())
            if value and value not in fmts and len(fmts)<70:
                fmts.append(value[:160])
        if key=="Operation" and el.attrib.get("name"):
            ops.append(el.attrib.get("name"))
        if key in ("ServiceMetadata","Extension","Profile") and len(service_info)<15:
            service_info.append({"native_tag":key,"native_attrs":{
              k:safe_info_slice(v,90) for k,v in el.attrib.items()}})
    return {
       "native_WCS_version":root.attrib.get("version"),
       "native_declared_GetCoverage":("GetCoverage" in ops),
       "native_OGC_advertised_operations":sorted(set(ops)),
       "native_WCS_formatSupported_and_other_format_tags":fmts,
       "native_explicit_NetCDF_output_format_if_any":[x for x in fmts
           if any(t in x.lower() for t in ("netcdf","ncdf","x-netcdf"))],
       "native_explicit_GeoTIFF_output_format_if_any":[x for x in fmts
           if any(t in x.lower() for t in ("tiff","geotiff"))],
       "native_Capabilities_tag_counts_limited":{
           k:int(root_names[k]) for k in sorted(root_names)
           if k in ("CoverageSummary","formatSupported","ServiceMetadata","Operation",
              "Extension","Profile","GetCoverage","SupportedFormat")},
       "source_ServiceMetadata_tag_only":service_info,
       "supported_format_without_full_native_var_attributes":True,
    }

def source_native_description_axes(raw,expected_cover):
    doc=safe_xml(raw,"CoverageDescriptions")
    ids=[compact_text(el) for el in doc.iter() if local(el)=="CoverageId"]
    if ids!=[expected_cover]:
        raise ValueError("SOURCE_STOP_WRONG_OR_NONUNIQUE_DESCRIBE_YEAR_COVERAGE")
    counter=Counter()
    envelopes=[]
    rectified=[]
    grids=[]
    times=[]
    positions=[]
    uoms=[]
    native_nil=[]
    bounded_first=[]
    for n in doc.iter():
        t=local(n)
        counter[t]+=1
        if t in ("Envelope","EnvelopeWithTimePeriod") and len(envelopes)<8:
            envelopes.append({"native_tag":t,
                "native_srs":n.attrib.get("srsName"),
                "native_axisLabels":n.attrib.get("axisLabels"),
                "native_srsDimension":n.attrib.get("srsDimension"),
                "native_uomLabels":n.attrib.get("uomLabels"),
                "source_lowerCorner":next((safe_info_slice(compact_text(z)) for z in n if local(z)=="lowerCorner"),None),
                "source_upperCorner":next((safe_info_slice(compact_text(z)) for z in n if local(z)=="upperCorner"),None)})
        if t in ("RectifiedGrid","ReferenceableGrid","Grid") and len(grids)<8:
            grids.append({"native_tag":t,"native_dimension":n.attrib.get("dimension"),
                          "native_axisLabels":n.attrib.get("axisLabels")})
        if t in ("offsetVector","origin","low","high","axisName") and len(rectified)<32:
            rectified.append({"native_tag":t,"native_text":safe_info_slice(compact_text(n),140)})
        if t in ("timePosition","beginPosition","endPosition","begin","end") and len(times)<30:
            times.append({"native_tag":t,"source_time":safe_info_slice(compact_text(n),140)})
        if t in ("pos","posList","lowerCorner","upperCorner") and len(positions)<24:
            positions.append({"native_tag":t,"source_value_prefix":safe_info_slice(compact_text(n),140)})
        if t=="uom" and len(uoms)<20:
            uoms.append({"native_uom_code":n.attrib.get("code"),
                         "native_uom_text":safe_info_slice(compact_text(n),100)})
        if t.lower()=="nilvalue" and len(native_nil)<25:
            native_nil.append({"native_literal":safe_info_slice(compact_text(n),100),
               "source_reason":n.attrib.get("reason")})
        if t in ("boundedBy","domainSet","rangeType","CoverageSubtype") and len(bounded_first)<25:
            bounded_first.append(t)
    n=counter["CoverageDescription"]
    if n!=1:
        raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NOT_ONE_COVERAGE_DESCRIPTION")
    if FROZEN_NATIVE_NIL not in [x["native_literal"] for x in native_nil]:
        raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NIL_DID_NOT_MATCH_VERIFIED_V216")
    if "m" not in [x["native_uom_code"] for x in uoms]:
        raise ValueError("SOURCE_STOP_ORIGINAL_WCS_UOM_M_DID_NOT_MATCH_V216")
    return {
      "native_described_CoverageId":expected_cover,
      "native_root_element_tag_counts":{k:int(v) for k,v in sorted(counter.items())
           if k in ("Envelope","EnvelopeWithTimePeriod","boundedBy","RectifiedGrid",
               "ReferenceableGrid","Grid","domainSet","rangeType","timePosition",
               "beginPosition","endPosition","pos","origin","offsetVector","axisLabels",
               "gridEnvelope","low","high","CoverageId","NilValue","nilValue","uom")},
      "source_native_envelopes":envelopes,
      "source_native_grid_and_time_structure":grids,
      "source_native_grid_origins_offsets_limited":rectified,
      "source_time_positions_if_any":times,
      "source_coordinate_positions_if_any":positions,
      "source_UOM_tags":uoms,
      "source_nil_values":native_nil,
      "native_section_labels":bounded_first,
      "model_WCS_service_metadata_not_original_NetCDF_variable_attrs":True,
      "year_2018_2019_bird_GPS_local_height_not_extracted":True,
    }

def run(out=OUT):
    d={"version":"v217-original-BAW-2018-2019-WCS2-native-format-axis-metadata-only",
       "v216_source_success_runs":[44473878254,44473887025],
       "frozen_source_year_WCS_cap_SHA":FROZEN_WCS_CAP_SHA,
       "frozen_source_year_WCS_Describe_SHA":FROZEN_DESCRIBE_SHA,
       "frozen_native_original_height_CoverageId":FROZEN_COVERAGE_IDS,
       "WCS_GetCoverage_or_binary_NetCDF_not_attempted":True,
       "status":"SOURCE_STOP"}
    years={}
    for year in ("2018","2019"):
        row={"status":"SOURCE_STOP_YEARLY_WCS_SOURCE"}
        try:
            original_wms,wrec=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            if wrec["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year]:
                raise ValueError("STOP_YEAR_PUBLISHED_WMS_SHA_DRIFT")
            wms=inspect_WMS_xml(original_wms,target_year=year)
            if not any(n["name"]==NATIVE_HEIGHT_LAYERS[year] for n in
                       wms["source_tide_water_height_named_layers_cap45"]):
                raise ValueError("STOP_OFFICIAL_YEAR_WMS_LAYER_NOT_NATIVE_NL_SSH")
            xml,rec=original_GET(year,CANDIDATE[year],"GetCapabilities")
            if xml is None or rec["original_SHA256"]!=FROZEN_WCS_CAP_SHA[year]:
                raise ValueError("STOP_SOURCE_V216_YEAR_WCS_CAP_SHA_CHANGED_OR_HTTP")
            original=parse_native_WCS_capabilities(xml,year)
            if original["native_2018_2019_NL_SSH_CoverageId_candidates"]!=[
                {"native_CoverageId":FROZEN_COVERAGE_IDS[year],
                 "native_Title":NATIVE_HEIGHT_LAYERS[year]}]:
                raise ValueError("STOP_SOURCE_V216_TRUE_NL_WCS_COVERAGE_NOT_UNIQUE")
            row["actual_WCS_GetCapabilities_formats"]=source_native_formats(xml)
            doc_url=describe_URL(year,FROZEN_COVERAGE_IDS[year])
            desc,dr=original_GET(year,doc_url,"DescribeCoverage",FROZEN_COVERAGE_IDS[year],max_bytes=2000000)
            if desc is None or dr["original_SHA256"]!=FROZEN_DESCRIBE_SHA[year]:
                raise ValueError("STOP_SOURCE_V216_YEAR_WCS_DESCRIBE_SHA_CHANGED_OR_HTTP")
            row["actual_original_WCS_DescribeCoverage_axes"]=source_native_description_axes(
                desc,FROZEN_COVERAGE_IDS[year])
            row["original_WMS_SHA"]=wrec["original_WMS_xml_SHA256"]
            row["original_WCS_Capabilities_SHA"]=rec["original_SHA256"]
            row["original_WCS_DescribeCoverage_SHA"]=dr["original_SHA256"]
            row["status"]="TRUE_ORIGINAL_BAW_YEAR_WCS_SUPPORTED_FORMATS_AND_AXES_ADMITTED"
        except Exception as e:
            row["source_error_kind"]=type(e).__name__
            row["source_error_summary"]=str(e)[:240]
        years[year]=row
    d["original_native_year_source_metadata"]=years
    passed=all(x["status"]=="TRUE_ORIGINAL_BAW_YEAR_WCS_SUPPORTED_FORMATS_AND_AXES_ADMITTED"
               for x in years.values())
    netcdf_supported=passed and all(
        bool(x["actual_WCS_GetCapabilities_formats"]["native_explicit_NetCDF_output_format_if_any"])
        for x in years.values())
    d["scientific_gates"]={
      "both_original_years_native_WCS2_format_axis_Nil_metadata_reverified":passed,
      "both_original_years_WCS_advertise_NetCDF_output_format":bool(netcdf_supported),
      "native_WCS_OGC_year_height_coverage_unit_m_and_nil_authenticated":passed,
      "downloaded_any_source_native_binary_NetCDF_or_GetCoverage":False,
      "true_NetCDF_variable__FillValue_units_vertical_datum_read":False,
      "WMS_missingness_physical_dry_cell_caused_verified":False,
      "bird_GPS_cell_h_t_and_sun_tide_social_Boids_newly_estimated":False}
    d["status"]="ORIGINAL_BAW_WCS_YEAR_TWO_SOURCE_FORMAT_AXIS_METADATA_REPRODUCED" if passed else "SOURCE_STOP_YEAR_WCS_FORMAT_AXIS_METADATA_UNVERIFIED"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V217_NATIVE_WCS_FORMATS_AXES="+json.dumps({
        "status":d["status"],"gates":d["scientific_gates"],
        "by_year":{y:{
          "status":x["status"],
          "source_formats":x.get("actual_WCS_GetCapabilities_formats",{}).get(
              "native_WCS_formatSupported_and_other_format_tags"),
          "source_envelopes":x.get("actual_original_WCS_DescribeCoverage_axes",{}).get("source_native_envelopes"),
          "source_time":x.get("actual_original_WCS_DescribeCoverage_axes",{}).get("source_time_positions_if_any"),
          "source_grid":x.get("actual_original_WCS_DescribeCoverage_axes",{}).get("source_native_grid_origins_offsets_limited"),
          "source_tag_counts":x.get("actual_original_WCS_DescribeCoverage_axes",{}).get("native_root_element_tag_counts"),
          "error":x.get("source_error_summary")}
          for y,x in years.items()},
        "raw_original_NetCDF_2018_2019_and_ecology_not_admitted":True
    },sort_keys=True))
    return d

if __name__=="__main__":
    run()
