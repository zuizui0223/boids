"""v208 source-only primary JATS full-text methods audit of TrilaWatt (Lepper et al. 2025).

Evidence: official Europe PMC hosted open-access original paper, PMCID PMC12589441,
DOI 10.1038/s41597-025-06211-1. Fetch only source publication XML, never
raw BAW WMS values, RWS time series, GPS/ACC, original bathymetry or wildlife.
Publication-level NHN/NAP != uninspected native WMS GeoJSON unit/datum.
"""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OFFICIAL_FULLTEXT="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12589441/fullTextXML"
ORIGINAL_DOI="10.1038/s41597-025-06211-1"
ORIGINAL_PMCID="PMC12589441"
EXPECTED_TITLE="A hydrographic dataset of the Wadden Sea as a foundation for a digital twin of the coastal ocean"
MAX_SOURCE_BYTES=6_000_000
RESULT=Path(__file__).resolve().parent/"results/original_TrilaWatt_2025_JATS_forcing_gauge_NHN_source_v208.json"

def elem_tag(node):
    return node.tag.rsplit("}",1)[-1].lower() if isinstance(node.tag,str) else ""

def jats_text(node):
    return " ".join(" ".join(node.itertext()).split())

def strictly_original_XML(raw:bytes):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("SOURCE_STOP_ORIGINAL_JATS_XML_DTD_ENTITY")
    try:
        x=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("SOURCE_STOP_ORIGINAL_JATS_XML_NOT_PARSEABLE") from exc
    if elem_tag(x)!="article":
        raise ValueError("SOURCE_STOP_ORIGINAL_PAPER_NOT_JATS_ARTICLE")
    return x

def fetch_true_open_access_JATS(url=OFFICIAL_FULLTEXT):
    if url!=OFFICIAL_FULLTEXT:
        raise ValueError("SOURCE_STOP_UNFROZEN_ORIGINAL_PAPER_URL")
    parts=urllib.parse.urlsplit(url)
    if parts.scheme!="https" or parts.hostname!="www.ebi.ac.uk":
        raise ValueError("SOURCE_STOP_NOT_EUROPEPMC_PUBLICATION_HOST")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v208-TrilaWatt-primary-study-metadata-and-methods/1.0",
        "Accept":"application/xml,text/xml"})
    handler=urllib.request.HTTPSHandler(context=ssl.create_default_context())
    opener=urllib.request.build_opener(handler)
    with opener.open(req,timeout=45) as response:
        raw=response.read(MAX_SOURCE_BYTES+1)
        status=response.status
        ct=response.headers.get("Content-Type","")
        final=response.geturl()
    if status!=200 or not raw or len(raw)>MAX_SOURCE_BYTES:
        raise ValueError("SOURCE_STOP_PRIMARY_FULLTEXT_HTTP_OR_BYTES")
    if final!=url:
        raise ValueError("SOURCE_STOP_PRIMARY_PAPER_REDIRECT_UNPINNED")
    if not (raw.lstrip().startswith(b"<") and ("xml" in ct.lower() or "text" in ct.lower())):
        raise ValueError("SOURCE_STOP_NOT_XML_PRIMARY_SOURCE")
    return raw,{"original_primary_fullTextXML_SHA256":hashlib.sha256(raw).hexdigest(),
                "original_response_bytes":len(raw),
                "origin":"Europe PMC original open-access JATS primary paper",
                "verified_TLS_default_CA":True,
                "original_HTTP_status":status,
                "original_Content_Type":ct,
                "no_full_source_text_in_artifact":True}

def validate_identity(root):
    titles=[jats_text(node) for node in root.iter() if elem_tag(node)=="article-title"]
    if EXPECTED_TITLE not in titles:
        raise ValueError("SOURCE_STOP_ORIGINAL_PAPER_TITLE_MISMATCH")
    ids=[(node.attrib.get("pub-id-type","").lower(),jats_text(node))
         for node in root.iter() if elem_tag(node)=="article-id"]
    if ("doi",ORIGINAL_DOI) not in ids:
        raise ValueError("SOURCE_STOP_ORIGINAL_PAPER_DOI_MISMATCH")
    pmcid_values=[val.upper() for kind,val in ids if kind in ("pmcid","pmc")]
    if ORIGINAL_PMCID not in pmcid_values and ORIGINAL_PMCID.replace("PMC","") not in pmcid_values:
        raise ValueError("SOURCE_STOP_ORIGINAL_PAPER_PMCID_MISMATCH")
    return {"original_DOI":ORIGINAL_DOI,"original_PMCID":ORIGINAL_PMCID,
            "original_title":EXPECTED_TITLE,
            "original_jats_article_title_identity_verified":True}

def truth_fact_from_original_paragraph(paragraphs,pred,field):
    hits=[]
    for index,p in enumerate(paragraphs):
        if pred(p.lower()):
            hits.append({"primary_original_JATS_paragraph_index":index,
                         "primary_paragraph_text_SHA256":hashlib.sha256(p.encode()).hexdigest(),
                         "source_cue_first_90_chars_not_raw_fulltext":p[:90],
                         "original_paragraph_words_not_republished":True})
    return {"source_method_fact":field,
            "at_least_one_true_primary_original_paragraph":bool(hits),
            "n_source_original_paragraphs_matching":len(hits),
            "original_provenance_capped3":hits[:3]}

def original_method_gates(root):
    paragraphs=[jats_text(el) for el in root.iter() if elem_tag(el)=="p"]
    if len(paragraphs)<60:
        raise ValueError("SOURCE_STOP_JATS_PAPER_TOO_FEW_BODY_PARAGRAPHS")
    def hasall(*terms):
        return lambda t: all(term.lower() in t for term in terms)
    tests={
      "product_published_height_NHN_equivalent_NAP":hasall("height reference system","NHN","equivalent to NAP"),
      "open_boundary_FES2014b_tide_forcing":hasall("FES 2014b","open boundary"),
      "Helgoland_Roscoff_observed_SSH_for_open_boundary_bias_adjustment":hasall("Helgoland","Roscoff","observational"),
      "existing_observational_tide_gauge_validation":lambda t: (
          "sea surface elevation" in t and "tide gauges" in t and
          ("observations" in t or "measurements" in t)),
      "2019_atmospheric_forcing_ICON_EU_switch":lambda t: (
          "2019" in t and "icon-eu" in t and
          ("forcing" in t or "model" in t)),
      "yearly_model_approximately_500m_20minute_netcdf":lambda t: (
          "netcdf" in t and "500" in t and
          ("20-minute" in t or "20 minute" in t)),
    }
    facts={name:truth_fact_from_original_paragraph(paragraphs,fn,name)
           for name,fn in tests.items()}
    return {"facts":facts,"n_original_JATS_paragraphs":len(paragraphs),
            "all_six_methods_documented_in_primary_text":all(
                fact["at_least_one_true_primary_original_paragraph"]
                for fact in facts.values())}

def source_only_conclusion_gates(evidence):
    paper=evidence.get("primary_source_methods",{})
    facts=paper.get("facts",{})
    def documented(name):
        return bool(facts.get(name,{}).get("at_least_one_true_primary_original_paragraph"))
    return {
      "verified_original_JATS_article_DOI_PMCID_and_title":bool(
          evidence.get("primary_publication_identity",{}).get("original_jats_article_title_identity_verified")),
      "published_product_reference_NHN_equivalent_NAP":documented(
          "product_published_height_NHN_equivalent_NAP"),
      "published_model_atmospheric_forcing_break_in_2019":documented(
          "2019_atmospheric_forcing_ICON_EU_switch"),
      "published_observational_gauge_dependencies_exist":(
          documented("Helgoland_Roscoff_observed_SSH_for_open_boundary_bias_adjustment") and
          documented("existing_observational_tide_gauge_validation")),
      "native_WMS_Wasserstand_units_and_original_FillValue_verified":False,
      "three_specific_RWS_gauges_excluded_from_model_calibration_and_validation":False,
      "native_original_2018_2019_RWS_sensor_positions_verified":False,
      "correct_original_bird_GPS_local_TideHeight_EPSG_vertical_calibration":False,
      "retrospective_2019_hindcast_recast_as_2018_real_time_forecast":False,
      "source_applicable_bird_tide_solar_causal_mechanism_estimated":False,
    }

def run(out=RESULT):
    result={
        "version":"v208-official-primary-paper-methods-forcing-datum-only",
        "fixed_original_primary_source":OFFICIAL_FULLTEXT,
        "predeclared_original_DOI":ORIGINAL_DOI,
        "predeclared_original_PMCID":ORIGINAL_PMCID,
        "model_source_vs_tagged_bird_prediction_still_distinct":True,
        "source_year2019_forecast_was_retrospective_2025_model_publication":True,
        "status":"SOURCE_STOP_ORIGINAL_TRILAWATT_JATS_NOT_VERIFIED"
    }
    try:
        raw,receipt=fetch_true_open_access_JATS()
        root=strictly_original_XML(raw)
        identity=validate_identity(root)
        paper=original_method_gates(root)
        result["primary_publication_identity"]=identity
        result["primary_JATS_source_receipt"]=receipt
        result["primary_source_methods"]=paper
        if paper["all_six_methods_documented_in_primary_text"]:
            result["status"]="OFFICIAL_PRIMARY_PAPER_METHODS_SIX_SOURCE_GATES_PASS_NATIVE_WMS_AND_BIRDS_STILL_STOP"
        else:
            result["status"]="SOURCE_STOP_PRIMARY_PAPER_METHOD_STATEMENTS_NOT_ALL_VERIFIED"
    except Exception as exc:
        result["primary_source_failure_kind"]=type(exc).__name__
        result["primary_source_failure_summary"]=str(exc)[:220]
    result["scientific_source_gates"]=source_only_conclusion_gates(result)
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V208_TRILAWATT_PRIMARY_PAPER_METHODS="+json.dumps({
       "status":result["status"],
       "source_error":result.get("primary_source_failure_summary"),
       "facts":{k:{
           "documented":v["at_least_one_true_primary_original_paragraph"],
           "n_supporting_source_paragraphs":v["n_source_original_paragraphs_matching"]}
           for k,v in result.get("primary_source_methods",{}).get("facts",{}).items()},
       "scientific_source_gates":result["scientific_source_gates"],
       "NO_original_native_WMS_or_tagged_bird_data_scored":True
    },sort_keys=True))
    return result

if __name__=="__main__":
    run()
