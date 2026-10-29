#!/usr/bin/env python3
"""v25-B2-lite: original USGS FGDC XML only, when large CSV is still transferring.

This reads original 26,316-byte documented SOURCE FIELD definitions, not
bird fixes, step outcomes, habitat measurements or animal identifiers.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import usgs_step_manifest_gate as manifest
import usgs_step_schema_gate as source

XML="Data Release P9ELSUHN.xml"
def run():
    official=None;attempts=[]
    for url in manifest.ENDPOINTS:
        try:
            official=manifest.original_item(manifest.original_json(url))
            break
        except Exception as e:
            attempts.append({"url":url,"error":manifest.error(e)})
    out={"study":"v25-USGS-original-fgdc-schema-only",
         "source_doi":manifest.SOURCE_DOI,
         "status":"NOT_ADMITTED_FGDC_SOURCE_UNAVAILABLE",
         "source_integrity":None,
         "source_field_dictionary":None,
         "attempts":attempts,
         "animal_GPS_or_habitat_selection_values_read":False,
         "animal_prediction_scores_computed":False}
    if official is None:return out
    pin=source.select_files(official)[XML]
    with tempfile.TemporaryDirectory() as root:
        dest=Path(root)/"original.xml"
        receipt=source.fetch_verified(XML,pin,dest)
        fields=source.fgdc_schema_only(dest)
    out.update({"status":"ORIGINAL_FGDC_SCHEMA_ONLY_VERIFIED",
                "source_integrity":receipt,
                "source_field_dictionary":fields})
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v25/results/usgs_fgdc_original_v25.json"))
    a=p.parse_args()
    r=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("V25_ORIGINAL_FGDC_ONLY",json.dumps(r,sort_keys=True))
if __name__=="__main__":
    main()
