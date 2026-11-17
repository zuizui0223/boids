"""v171: real Deltares THREDDS historical vaklodingen tile inventory.

v170 source-verified two genuine 2016/2019 native NetCDFs, but their
AUTHENTIC original DATA source strings are Borndiep/Ameland (x155-175km,
y~602-620km), and their footprints do NOT intersect Vlieland target
x~120-150km,y~575-615km. This is a STOP for local tagged-bird habitat.

Find the correct historical Vlieland/Richel/Vliestroom tile by original
NetCDF tile catalog. Do not call a NetCDF '2016 Vlie' based on its filename;
verify actual x/y footprint, original isource and time slices, and NAP.
This stage acquires *inventory metadata only*, not elevation point samples
or ecological outcomes; no raw site-bird GPS/event data redistributed.

A 2026-released time-series tile may contain older (2016) surveys and
later (2025) data, requiring actual source-year selector. We must not use
future survey pixels to represent 2018/19 habitat.
"""
from __future__ import annotations
import argparse,hashlib,json,re,time,urllib.request,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_v171/results/official_historical_vlieland_tile_catalog_source_v171.json"
SOURCE_CATALOGS={
 "legacy_vaklodingen":"https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.xml",
 "vaklodingen_new":"https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen_new/catalog.xml",
}
MAX_XML_BYTES=7_000_000
GEO_SOURCE_YEAR_RWS=2016
VLIE_RD_BOX=[120000,575000,150000,615000]
MAX_DISPLAY_NAME_SAMPLE=110

def acquire_catalog(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":"OpenScienceBoidsResearch/1.0 (noncommercial original Rijkswaterstaat/Deltares source)",
        "Accept":"application/xml,text/xml,*/*"
    })
    with urllib.request.urlopen(req,timeout=60) as response:
        raw=response.read(MAX_XML_BYTES+1)
        final=response.geturl()
        ctype=response.headers.get("Content-Type","")
    if len(raw)>MAX_XML_BYTES or len(raw)<300:
        raise AssertionError("Original THREDDS XML catalog empty/too large")
    if raw.lstrip()[:1]!=b"<":
        raise AssertionError("THREDDS responded with non-XML content")
    return raw,{"source_catalog_url":url,
                "source_response_url":final,
                "original_catalog_binary_SHA256":hashlib.sha256(raw).hexdigest(),
                "original_catalog_bytes":len(raw),
                "source_content_type":ctype}

def inspect_xml(xml,prov):
    root=ET.fromstring(xml)
    if "catalog" not in root.tag.lower():
        raise AssertionError("Original THREDDS top XML not a catalog")
    child=[]
    for elem in root.iter():
        if elem.tag.rsplit("}",1)[-1] not in ("dataset","catalogRef"):
            continue
        name=(elem.get("name") or elem.get("{http://www.w3.org/1999/xlink}title") or "").strip()
        path=(elem.get("urlPath") or elem.get("{http://www.w3.org/1999/xlink}href") or "").strip()
        if not name and not path:
            continue
        child.append({"source_name":name[:150],"source_path":path[:200],
                      "source_type":elem.tag.rsplit("}",1)[-1]})
    names=[x["source_name"] for x in child]
    tile=[x for x in child if re.search(r"vaklodingenKB|KB\d+_|Vlieland|Vlie|vaklodingen",x["source_name"]+" "+x["source_path"],re.I)]
    filepaths=[x for x in child if x["source_path"].endswith(".nc")]
    examples=sorted(tile,key=lambda x:(x["source_name"],x["source_path"]))[:MAX_DISPLAY_NAME_SAMPLE]
    exact_named=[x for x in child if re.search(r"(vlieland|vlie|2016|2019)",x["source_name"]+" "+x["source_path"],re.I)][:MAX_DISPLAY_NAME_SAMPLE]
    if len(child)<3:raise AssertionError("Original catalog returned fewer than 3 datasets")
    return {
        **prov,
        "THREDDS_original_root_tag":root.tag,
        "n_XML_dataset_or_catalogRef_entries":len(child),
        "n_original_native_NetCDF_file_paths":len(filepaths),
        "n_tile_or_Vlieland_source_name_candidates":len(tile),
        "original_names_sorted_all_SHA256":hashlib.sha256(
            "\n".join(sorted(x["source_name"]+"|"+x["source_path"] for x in child)).encode()).hexdigest(),
        "source_dataset_name_samples_NOT_verified_GPS_coverage":examples,
        "catalog_entries_matching_2016_2019_or_Vlie_name_NOT_GPS_coverage":exact_named,
        "real_native_NetCDF_tile_crs_and_2016_altitude_DATE":"NOT_TESTED_FROM_CATALOG_NAMES",
        "actual_bird_GPS_inside_valid_2016_survey_height":"NOT_TESTED",
    }

def run():
    r={"version":"v171_real_Deltares_THREDDS_tile_source_inventory_1",
       "v170_Borndiep_standalone_2016_2019_source_STOP":"VLIELAND_BIRDS_OUTSIDE_BORNDIEP_CANDIDATE_FOOTPRINT",
       "public_Vlieland_RD_box_METADATA_SEARCH_ONLY":VLIE_RD_BOX,
       "survey_year_to_find":GEO_SOURCE_YEAR_RWS,
       "official_catalogs":{},
       "source_use_for_tagged_bird_elevation":"SOURCE_STOP_UNTIL_ACTUAL_2016_VALID_TILE_INTERSECTION"}
    for label,url in SOURCE_CATALOGS.items():
        try:
            raw,prov=acquire_catalog(url)
            r["official_catalogs"][label]={"status":"REAL_SOURCE_CATALOG_ACQUIRED",
                                           **inspect_xml(raw,prov)}
        except Exception as e:
            r["official_catalogs"][label]={
                "status":"SOURCE_ACCESS_STOP","source_requested":url,
                "error_type":type(e).__name__,
                "error_summary":str(e)[:280]}
    if not any(x["status"]=="REAL_SOURCE_CATALOG_ACQUIRED" for x in r["official_catalogs"].values()):
        raise RuntimeError("Both official THREDDS original historical catalogs inaccessible; no inferred tiles")
    return r

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    r=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        old=json.loads(OUT.read_text())
        if old!=r:raise AssertionError("Original official THREDDS XML SHA/catalog source inventory changed")
        print("V171_ORIGINAL_THREDDS_CATALOG_SOURCE_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V171_THREDDS_CATALOG_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V171_THREDDS_CATALOG_END")
    print("V171_CATALOG_SUMMARY="+json.dumps({
        k:{"status":v["status"],
           "catalog_sha":v.get("original_catalog_binary_SHA256"),
           "n_datasets":v.get("n_XML_dataset_or_catalogRef_entries"),
           "n_nc":v.get("n_original_native_NetCDF_file_paths"),
           "n_tiles":v.get("n_tile_or_Vlieland_source_name_candidates"),
           "samples":[x["source_name"] for x in v.get("source_dataset_name_samples_NOT_verified_GPS_coverage",[])][:40],
           "error":v.get("error_summary")}
        for k,v in r["official_catalogs"].items()},sort_keys=True))
if __name__=="__main__":main()
