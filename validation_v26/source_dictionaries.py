#!/usr/bin/env python3
"""v26-B2 official small original source dictionaries: turtle FGDC, mammal README.

Exact provider full bytes/MD5 and newly computed SHA256. No turtle GPS
numeric steps, animal IDs, environmental depth/chl or mammal iSSA rows read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import source_manifests as source

TURTLE_XML="iSSA data release V3.xml"
TURTLE_BYTES=22606
TURTLE_MD5="bb23daf440cb8ee6932f60a8fc7293a5"
MAMMAL_README="README.txt"
MAMMAL_BYTES=3580
MAMMAL_MD5="b03a51664b620a2cdd3cc38bb20b4215"
MAX_SOURCE=200_000
UA="boids-v26-author-original-FGDC-and-Zenodo-README-MD5/1.0"

def validate_url(url:str,origin:str)->None:
    if origin=="USGS":
        if not url.startswith(
            "https://www.sciencebase.gov/catalog/file/get/"+source.TURTLE_ITEM):
            raise ValueError("Source XML not official USGS turtle attachment")
    elif origin=="Zenodo":
        if not url.startswith("https://zenodo.org/"):
            raise ValueError("Source README not original Zenodo record")
    else:
        raise ValueError("Unknown source authority")

def selected_source_item(original:dict,filename:str,source_name:str,
                         expected_bytes:int,expected_md5:str)->dict:
    if source_name=="USGS":
        items=(original.get("original_source_metadata") or {}).get("files") or []
        match=[x for x in items if x.get("original_filename")==filename]
        if len(match)!=1:raise ValueError("Expected original USGS FGDC absent")
        item=match[0]
        ch=item.get("provider_MD5_or_checksum") or {}
        digest=str(ch.get("value") or "").lower() if str(ch.get("type")).lower()=="md5" else ""
        url=item.get("download_provider_uri")
    elif source_name=="Zenodo":
        items=(original.get("original_source_metadata") or {}).get("files") or []
        match=[x for x in items if x.get("original_filename")==filename]
        if len(match)!=1:raise ValueError("Expected original mammal README absent")
        item=match[0]
        digest=str(item.get("provider_MD5_or_checksum") or "").lower().removeprefix("md5:")
        url=item.get("content_url")
    else:raise ValueError("Unknown original provider")
    if item["provider_bytes"]!=expected_bytes or digest!=expected_md5:
        raise ValueError("Published original source byte count/MD5 changed")
    validate_url(url,source_name)
    return {"name":filename,"source":source_name,"bytes":expected_bytes,
            "md5":expected_md5,"url":url}

def acquire_original(s:dict,path:Path)->dict:
    req=urllib.request.Request(s["url"],headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=60) as stream:
        if not stream.geturl().startswith("https://"):
            raise ValueError("Original publication source redirected insecurely")
        raw=stream.read(MAX_SOURCE+1)
    if len(raw)>MAX_SOURCE or len(raw)!=s["bytes"]:
        raise ValueError("Original dictionary has mismatched size")
    real_md5=hashlib.md5(raw).hexdigest()
    if real_md5!=s["md5"]:
        raise ValueError("Original published provider MD5 mismatch: "+real_md5)
    path.write_bytes(raw)
    return {"status":"ORIGINAL_AUTHOR_SOURCE_BYTES_VERIFIED",
            "file":s["name"],"bytes":len(raw),
            "published_md5":s["md5"],
            "independent_sha256":hashlib.sha256(raw).hexdigest(),
            "animal_movement_values_or_model_scores_computed":False}

def original_fgdc_labels(path:Path)->dict:
    root=ET.parse(path).getroot()
    attrs=[]
    for node in root.findall(".//attr"):
        label=node.findtext("attrlabl")
        defin=node.findtext("attrdef")
        if label:
            attrs.append({"name":label.strip()[:120],
                          "definition":(defin or "").strip()[:700]})
    if not attrs:
        return {"status":"NO_USABLE_ORIGINAL_FGDC_ATTRIBUTES",
                "field_definitions":[]}
    return {"status":"SOURCE_ORIGINAL_FGDC_DICTIONARY_ONLY",
            "attributes_documented":len(attrs),
            "field_definitions":attrs[:120],
            "original_PIT_or_habitat_values_read":False}

def original_readme_structure(path:Path)->dict:
    text=path.read_text(encoding="utf-8-sig",errors="replace")
    lines=text.splitlines()
    # Original public source README is a 3.58KB data-format dictionary;
    # quote only format descriptors, not any original animal records.
    return {"status":"SOURCE_ORIGINAL_MAMMAL_README_ONLY",
            "n_lines":len(lines),
            "public_source_dictionary_text":text[:5000],
            "source_original_animal_step_rows_read":False}

def run()->dict:
    turtle=source.turtle_manifest()
    mammal=source.mammal_manifest()
    ret={
        "study":"v26-original-USGS-turtle-FGDC-and-global-mammal-Zenodo-README",
        "turtle":{"status":"NOT_ADMITTED_ORIGINAL_DICTIONARY_UNAVAILABLE"},
        "mammal":{"status":"NOT_ADMITTED_ORIGINAL_DICTIONARY_UNAVAILABLE"},
        "original_movement_or_environment_values_read":False,
        "all_v13_to_v25_results_unchanged":True
    }
    configs=(
        ("turtle",turtle,TURTLE_XML,"USGS",TURTLE_BYTES,TURTLE_MD5),
        ("mammal",mammal,MAMMAL_README,"Zenodo",MAMMAL_BYTES,MAMMAL_MD5)
    )
    with tempfile.TemporaryDirectory() as tmp:
        for key,meta,name,origin,bytes_,md5 in configs:
            try:
                spec=selected_source_item(meta,name,origin,bytes_,md5)
                file=Path(tmp)/("turtle.xml" if key=="turtle" else "mammal.txt")
                receipt=acquire_original(spec,file)
                dictionary=(original_fgdc_labels(file) if key=="turtle"
                            else original_readme_structure(file))
                ret[key]={"status":"ORIGINAL_DICTIONARY_BYTES_VERIFIED",
                          "receipt":receipt,"source_dictionary":dictionary}
            except Exception as e:
                ret[key]={"status":"NOT_ADMITTED_DICTIONARY_BYTES_OR_FORMAT",
                          "error":type(e).__name__+": "+str(e)[:180]}
    return ret

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "validation_v26/results/original_dictionaries_v26.json"))
    a=p.parse_args()
    r=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V26_TURTLE_FGDC_DICTIONARY",json.dumps(r["turtle"],sort_keys=True))
    print("V26_MAMMAL_README_DICTIONARY",json.dumps(r["mammal"],sort_keys=True))
    print("V26_NO_ORIGINAL_ANIMAL_HABITAT_SELECTION_SCORES")
if __name__=="__main__":
    main()
