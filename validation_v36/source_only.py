#!/usr/bin/env python3
"""v36-A source-only official BAW TrilaWatt Dutch historical 10m DEM catalog.

NO GeoTIFF pixels, bird GPS, original RWS tide, or inferred exposed area read.
Do not equate DHHN2016 heights with NAP water levels.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BAW_DATA="https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Topographie_PP_1996-2014_NL/"
BAW_WCS="https://mdi-dienste.baw.de/geoserver/TrilaWatt_Topographie/wcs"
BAW_WCS_CAPS=BAW_WCS+"?SERVICE=WCS&REQUEST=GetCapabilities&VERSION=2.0.1"
YEAR_WINDOW=tuple(range(2008,2013))
MAX_METADATA_BYTES=15_000_000
MAX_ADVERTISED_FILES=1000
MAX_WCS_COVERAGES=1000
AGENT="boids-v36-official-BAW-original-source-only-annual-raster/1.0"
EXPECTED_DEM_HORIZONTAL="EPSG:25832"
EXPECTED_VERTICAL_SOURCE="DE_DHHN2016_NH"
ORIGINAL_RWS_TIDE_VERTICAL="NAP"

def _request_metadata(url):
    allowed=(BAW_DATA,BAW_WCS+"?")
    if not url.startswith(allowed):raise ValueError("BAW metadata source host not registered")
    req=urllib.request.Request(url,headers={"Accept":"text/html,application/xml,text/xml,*/*","User-Agent":AGENT})
    with urllib.request.urlopen(req,timeout=60) as response:
        effective=response.geturl()
        if not effective.startswith(("https://dl.datenrepository.baw.de/","https://mdi-dienste.baw.de/")):
            raise ValueError("Original BAW metadata redirected off approved publisher hosts")
        data=response.read(MAX_METADATA_BYTES+1)
        typ=response.headers.get("Content-Type")
    if len(data)>MAX_METADATA_BYTES:raise ValueError("BAW metadata exceeds source cap")
    return data,{"source_metadata_bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
                  "content_type":typ}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.all=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            params=dict(attrs)
            href=params.get("href")
            if href:self.all.append(href)

def parse_index(data):
    decoded=data.decode("utf-8",errors="replace")
    if "<html" not in decoded.casefold() and "<a " not in decoded.casefold():
        raise ValueError("BAW NL source directory not HTML with source links")
    p=Links();p.feed(decoded)
    if len(p.all)>MAX_ADVERTISED_FILES:raise ValueError("BAW source directory link cap exceeded")
    catalog=[]
    for href in p.all:
        complete=urllib.parse.urljoin(BAW_DATA,href)
        if not complete.startswith(BAW_DATA):continue
        basename=complete.rsplit("/",1)[-1]
        # Only original-source file names, no secret/auth URLs kept.
        catalog.append({"original_basename":basename,"possible_years":years_in_text(basename),
                       "looks_raster":any(s in basename.lower() for s in (".tif",".tiff",".zip",".nc"))})
    peryear={str(y):[x["original_basename"] for x in catalog if y in x["possible_years"]]
             for y in YEAR_WINDOW}
    return {"original_relative_file_links":len(catalog),
            "source_linked_year_specific_files":peryear,
            "first_100_published_original_filenames":[x["original_basename"] for x in catalog[:100]],
            "all_five_historical_year_names_advertised":all(peryear[str(y)] for y in YEAR_WINDOW),
            "NO_raster_pixel_values_or_original_GPS_read":True}

def years_in_text(s):
    # Precommit simple source file year recognition. A range 1996-2014 is metadata,
    # not proof of each annual GeoTIFF being accessible.
    return sorted({int(y) for y in re.findall(r"(?<!\d)(?:19\d\d|20\d\d)(?!\d)",s) if int(y) in YEAR_WINDOW})

def bare(tag):return tag.rsplit("}",1)[-1]

def parse_wcs(data):
    root=ET.fromstring(data)
    if bare(root.tag)!="Capabilities":raise ValueError("BAW WCS metadata returned non-capabilities XML")
    names=[]
    for parent in root.iter():
        if bare(parent.tag)!="CoverageSummary":continue
        found={}
        for child in parent.iter():
            if bare(child.tag) in ("CoverageId","Title","Abstract"):
                val=(child.text or "").strip()
                if val:found[bare(child.tag)]=val
        if found:
            names.append(found)
    if len(names)>MAX_WCS_COVERAGES:raise ValueError("Original source WCS coverages exceed metadata cap")
    target={str(y):[x["CoverageId"] for x in names if y in years_in_text(x.get("CoverageId","")+" "+x.get("Title",""))
                       and "CoverageId" in x] for y in YEAR_WINDOW}
    version=root.attrib.get("version","")
    return {"original_WCS_root":bare(root.tag),"original_WCS_version":version,
            "all_source_coverage_summaries":len(names),
            "original_coverage_ids_for_2008_2012":target,
            "all_five_years_WCS_discoverable":all(target[str(y)] for y in YEAR_WINDOW),
            "first_50_published_coverage_ids":[v.get("CoverageId") for v in names[:50]],
            "NO_GetCoverage_called_or_raster_pixels_read":True}

def source_error(e):
    result={"source_status":"SOURCE_METADATA_ERROR","error_type":type(e).__name__,
            "http_code":getattr(e,"code",None),"message":str(e)[:220]}
    if isinstance(e,urllib.error.HTTPError):
        result["provider_error_type"]="HTTPError"
    return result

def run():
    report={"study":"v36 original BAW TrilaWatt NL historical 10m bed elevation source-only",
            "original_publisher":"Bundesanstalt für Wasserbau",
            "original_dataset_doi":"10.48437/4baaf0-aeaf58",
            "original_map_years":[2008,2009,2010,2011,2012],
            "official_original_data_directory":BAW_DATA,
            "official_original_WCS_service":BAW_WCS,
            "source_published_horizontal_CRS":EXPECTED_DEM_HORIZONTAL,
            "source_published_vertical_datum":EXPECTED_VERTICAL_SOURCE,
            "unconverted_original_RWS_tide_datum":ORIGINAL_RWS_TIDE_VERTICAL,
            "vertical_datum_transformation_verified":False,
            "no_dem_height_minus_tide_exposure_calculated":True,
            "no_original_animal_GPS_or_raster_pixels_opened":True}
    results={}
    for key,url,func in (("original_NL_historical_file_directory",BAW_DATA,parse_index),
                         ("original_OGC_WCS_capabilities",BAW_WCS_CAPS,parse_wcs)):
        try:
            raw,stamp=_request_metadata(url)
            results[key]={"source_status":"PUBLIC_METADATA_VERIFIED",
                          "original_response":stamp,**func(raw)}
        except (urllib.error.URLError,ValueError,ET.ParseError,TimeoutError) as e:
            results[key]=source_error(e)
    report["source_only_metadata_and_coverage"]=results
    idx=results["original_NL_historical_file_directory"]
    wcs=results["original_OGC_WCS_capabilities"]
    if idx.get("all_five_historical_year_names_advertised") or wcs.get("all_five_years_WCS_discoverable"):
        report["status"]="BAW_HISTORICAL_2008_2012_RASTER_METADATA_AVAILABLE_VERTICAL_DATUM_NOT_ADMITTED"
    else:
        report["status"]="BAW_HISTORICAL_DEM_RASTER_SOURCE_NOT_ADMITTED"
    report["any_spatial_bird_habitat_effect_exported"]=False
    report["vertical_ref_NOP"]="Do not subtract DHHN2016 GeoTIFF heights from NAP gauge heights without official transformation"
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,
      default=Path("validation_v36/results/BAW_original_topography_source_only.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V36_BAW_SOURCE_ONLY_STATUS",result["status"])
    print("V36_COMPLETE_SOURCE_METADATA",json.dumps(result,sort_keys=True,separators=(",",":")))
    print("V36_NO_EXPOSURE_OR_ANIMAL_GPS_JOIN")
if __name__=="__main__":main()
