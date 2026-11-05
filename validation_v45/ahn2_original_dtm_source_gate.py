"""v45 source-only probe of official AHN2 (2007-2012) NAP terrain WCS.

All site points precommitted; NO bird GPS, biological endpoints, or observed tide
are opened. No full national raster downloaded. Original 128px/256m patch
values stay on ephemeral CI runner, only source coverage receipts persist.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from pyproj import Transformer

OFFICIAL_DTM_WCS="https://api.ellipsis-drive.com/v3/ogc/wcs/e96b10b9-e964-414c-958c-57a9dbe24e62"
OFFICIAL_AHN_DATAROOM="https://www.ahn.nl/dataroom"
AHN2_ACQUISITION_PERIOD="2007-2012"
SAMPLE_CENTRES={
    "schiermonnikoog":(53.470,6.200),
    "ameland":(53.430,5.760),
}
PATCH_METRES=256
PATCH_PIXELS=128
MAX_XML_BYTES=2_000_000
MAX_TIFF_BYTES=4_000_000
EXPOSE_BAND_NAP_M=(-3.,3.)

class SourceStop(RuntimeError):
    """Data availability or integrity not biological result."""

def bounded_get(base,params,limit,*,opener=urlopen):
    if base!=OFFICIAL_DTM_WCS:raise SourceStop("SOURCE_STOP_NOT_OFFICIAL_AHN2_WCS")
    url=base+"?"+urlencode(params)
    req=Request(url,headers={"Accept":"application/xml,application/octet-stream,image/tiff,*/*",
                             "User-Agent":"Boids-v45-AHN2-2007-2012-SourceGate/1.0"})
    with opener(req,timeout=38) as resp:
        ct=resp.headers.get("Content-Type","")
        blob=resp.read(limit+1)
        status=getattr(resp,"status",200)
    if status!=200:raise SourceStop("SOURCE_STOP_AHN2_WCS_HTTP_STATUS_"+str(status))
    if len(blob)>limit:raise SourceStop("SOURCE_STOP_AHN2_WCS_RESPONSE_OVER_CAP")
    if not blob:raise SourceStop("SOURCE_STOP_AHN2_WCS_EMPTY_RESPONSE")
    return blob,ct

def _local(tag):
    return tag.split("}")[-1].lower()

def parse_wcs_caps(raw):
    if len(raw)>MAX_XML_BYTES:raise SourceStop("SOURCE_STOP_CAPABILITIES_OVERSIZE")
    try:root=ET.fromstring(raw)
    except ET.ParseError as err:
        raise SourceStop("SOURCE_STOP_AHN2_WCS_NON_XML_CAPABILITIES") from err
    if "capabilit" not in _local(root.tag):
        raise SourceStop("SOURCE_STOP_AHN2_WCS_CAPABILITIES_TAG")
    offered=[]
    for item in root.iter():
        if _local(item.tag) in ("coverageofferingbrief","coveragesummary"):
            names=[child.text.strip() for child in item.iter()
                   if _local(child.tag) in ("name","coverageid") and child.text]
            if names:offered.append(names[0])
    offered=sorted(set(offered))
    if not offered:
        raise SourceStop("SOURCE_STOP_AHN2_WCS_NO_ADVERTISED_COVERAGES")
    matching=[name for name in offered if
              any(term in name.lower() for term in ("dtm","terrain","maaiveld","hoogte","ahn2"))]
    if len(offered)==1:
        coverage=offered[0]
    elif len(matching)==1:
        coverage=matching[0]
    else:
        raise SourceStop("SOURCE_STOP_AHN2_WCS_DTM_COVERAGE_AMBIGUOUS")
    if any(bad in coverage.lower() for bad in
           ("dsm","ahn3","ahn4","ahn5","ahn6","surface","oppervlak")):
        raise SourceStop("SOURCE_STOP_AHN2_WCS_NOT_ORIGINAL_DTM")
    return {"wcs_capabilities_root":_local(root.tag),
            "coverage_count":len(offered),"chosen_original_DTM_coverage":coverage,
            "advertised_coverage_names":offered[:15],
            "AHN2_source_version":"AHN2_2007_2012_PROVIDER_LINK"}

def parse_coverage_description(raw,coverage):
    if len(raw)>MAX_XML_BYTES:raise SourceStop("SOURCE_STOP_DESCRIBE_RESPONSE_OVERSIZE")
    try:root=ET.fromstring(raw)
    except ET.ParseError as err:
        raise SourceStop("SOURCE_STOP_AHN2_DESCRIBE_NON_XML") from err
    text=raw.decode("utf-8",errors="replace")
    if "28992" not in text:
        raise SourceStop("SOURCE_STOP_AHN2_DESCRIBE_EPSG28992_NOT_VERIFIED")
    matches=[x.text.strip() for x in root.iter() if _local(x.tag) in
             ("format","formats","nativeformat","supportedformat") and x.text]
    image_formats=sorted(set(x for x in matches if
                             any(term in x.lower() for term in ("tiff","geotiff"))))
    if not image_formats:
        raise SourceStop("SOURCE_STOP_AHN2_DTM_GEOTIFF_NOT_ADVERTISED")
    return {"describe_root":_local(root.tag),
            "chosen_DTM_coverage":coverage,
            "horizontal_CRS_declared":"EPSG:28992",
            "available_original_geotiff_formats":image_formats,
            "requested_format":next((s for s in image_formats
                                    if s.lower()=="geotiff"),image_formats[0])}

def inspect_patch(raw,centre_rd,site):
    if len(raw)>MAX_TIFF_BYTES:raise SourceStop("SOURCE_STOP_AHN2_PATCH_OVERSIZE")
    if not(raw.startswith(b"II*\x00") or raw.startswith(b"MM\x00*") or
           raw.startswith(b"II+\x00") or raw.startswith(b"MM\x00+")):
        raise SourceStop("SOURCE_STOP_AHN2_WCS_NOT_GEOTIFF")
    try:
        with MemoryFile(raw) as mem:
            with mem.open() as ds:
                if ds.count!=1 or ds.crs is None or ds.crs.to_epsg()!=28992:
                    raise SourceStop("SOURCE_STOP_AHN2_PATCH_CRS_OR_BANDS")
                if ds.width>512 or ds.height>512 or ds.width<8 or ds.height<8:
                    raise SourceStop("SOURCE_STOP_AHN2_PATCH_DIMENSIONS_NOT_BOUNDED")
                data=ds.read(1,masked=True)
                # NaN or NODATA = not observed substrate; never fill.
                vals=np.asarray(data.compressed(),dtype=float)
                vals=vals[np.isfinite(vals)]
                plausible=vals[(vals>=-20)&(vals<=50)]
                candidate=plausible[(plausible>=EXPOSE_BAND_NAP_M[0])&
                                    (plausible<=EXPOSE_BAND_NAP_M[1])]
                xmin,ymin,xmax,ymax=ds.bounds
                e,n=centre_rd
                if not (xmin<=e<=xmax and ymin<=n<=ymax):
                    raise SourceStop("SOURCE_STOP_AHN2_PATCH_MISREGISTERED")
                total=ds.width*ds.height
                return {"site":site,
                        "WCS_input_probe_original_WGS84_degrees":SAMPLE_CENTRES[site],
                        "original_image_bytes":len(raw),
                        "source_patch_SHA256":hashlib.sha256(raw).hexdigest(),
                        "original_raster_crs_epsg":ds.crs.to_epsg(),
                        "source_raster_pixel_width":ds.width,
                        "source_raster_pixel_height":ds.height,
                        "original_raster_nodata_defined":ds.nodata is not None,
                        "source_finite_pixels":int(vals.size),
                        "source_plausible_NAP_pixels":int(plausible.size),
                        "source_candidate_minus3_plus3_NAP_pixels":int(candidate.size),
                        "finite_fraction":float(vals.size/total),
                        "candidate_fraction_of_plausible":float(candidate.size/plausible.size) if plausible.size else None,
                        "source_horizontal_geo_transform_verified":True,
                        "vertical_NAP_m_stated_by_AHN_dataroom_not_independently_pixel_verified":True,
                        "historical_GPS_or_tide_join":False,
                        "real_intertidal_exposure_verified":False}
    except SourceStop:raise
    except Exception as e:
        raise SourceStop("SOURCE_STOP_AHN2_INVALID_GEOTIFF_"+type(e).__name__) from e

def probe():
    caps_raw,caps_type=bounded_get(OFFICIAL_DTM_WCS,
        {"service":"WCS","request":"GetCapabilities","version":"1.0.0",
         "requestedEpsg":"28992"},MAX_XML_BYTES)
    caps=parse_wcs_caps(caps_raw)
    coverage=caps["chosen_original_DTM_coverage"]
    desc_raw,desc_ct=bounded_get(OFFICIAL_DTM_WCS,
        {"service":"WCS","request":"DescribeCoverage","version":"1.0.0",
         "coverage":coverage,"requestedEpsg":"28992"},MAX_XML_BYTES)
    desc=parse_coverage_description(desc_raw,coverage)
    transform=Transformer.from_crs(4326,28992,always_xy=True)
    sites={}
    for site,(lat,lon) in SAMPLE_CENTRES.items():
        east,north=transform.transform(lon,lat)
        half=PATCH_METRES/2
        bbox=",".join(f"{v:.3f}" for v in
                      (east-half,north-half,east+half,north+half))
        raw,contenttype=bounded_get(OFFICIAL_DTM_WCS,
            {"service":"WCS","request":"GetCoverage","version":"1.0.0",
             "coverage":coverage,"crs":"EPSG:28992",
             "response_crs":"EPSG:28992",
             "bbox":bbox,"width":str(PATCH_PIXELS),"height":str(PATCH_PIXELS),
             "format":desc["requested_format"],"requestedEpsg":"28992"},
            MAX_TIFF_BYTES)
        sites[site]=inspect_patch(raw,(east,north),site)
        sites[site]["server_original_WCS_contenttype"]=contenttype
    enough=all(s["source_finite_pixels"]>0 for s in sites.values())
    return {"source_status":"AHN2_HISTORICAL_LIDAR_SOURCE_PATCHES_ADMITTED" if enough
            else "SOURCE_STOP_AHN2_NO_VALID_PATCH_SUBSTRATE",
            "original_provider":OFFICIAL_AHN_DATAROOM,
            "AHN2_original_source_period":AHN2_ACQUISITION_PERIOD,
            "original_provider_wcs":OFFICIAL_DTM_WCS,
            "AHN2_compound_horizontal_vertical_CRS":"EPSG:7415 RD New + NAP",
            "source_product":"DTM_not_DSM",
            "source_capabilities":caps,"source_describe":desc,
            "source_fixed_sites":sites,
            "original_GPS_join":False,
            "dynamic_wet_dry_or_prey_effect":"NOT_ESTIMATED"}

def run(output):
    try:r=probe()
    except Exception as error:
        r={"source_status":"SOURCE_STOP_AHN2_ORIGINAL_WCS_UNAVAILABLE_OR_UNVERIFIED",
           "original_provider":OFFICIAL_AHN_DATAROOM,
           "original_provider_wcs":OFFICIAL_DTM_WCS,
           "reason":(type(error).__name__+"_"+str(error).splitlines()[0])[:200],
           "original_GPS_join":False,
           "dynamic_wet_dry_or_prey_effect":"NOT_ESTIMATED"}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    return r

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
