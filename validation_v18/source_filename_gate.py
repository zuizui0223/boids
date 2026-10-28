#!/usr/bin/env python3
"""v18 source-only filename incompatibility diagnostic; NEVER reads GPS data rows."""
from __future__ import annotations
import argparse
import collections
import json
import tempfile
import zipfile
from pathlib import Path
import fourteen_pair_source_gate as v17
import slow_pair_memory as v18

def run()->dict:
    with tempfile.TemporaryDirectory() as tmp:
        src=Path(tmp)/"original_author.zip"
        provenance=v17.download_pinned(v17.ZIP_PATH,v17.ZIP_BYTES,
                       v17.ZIP_BLOB_SHA1,v17.ZIP_CAP,src)
        with zipfile.ZipFile(src) as z:
            allnames=sorted(x for x in z.namelist()
                            if x.lower().endswith(".csv") and
                            not Path(x).name.startswith("._"))
            missing=[x for x in allnames if v18.file_identity(x) is None]
            recognized=[v18.file_identity(x) for x in allnames
                        if v18.file_identity(x) is not None]
        return {"status":"GPS_FILENAME_STRUCTURE_ONLY_NO_BEHAVIOR",
                "source_sha256":provenance["sha256"],
                "expected_source_gps_csv":v18.ORIGINAL_GPS_FILES,
                "total_source_gps_csv":len(allnames),
                "strict_filename_recognized":len(recognized),
                "unrecognized_count":len(missing),
                "unrecognized_original_basenames":list(map(
                    lambda x:Path(x).name,missing[:60])),
                "recognized_mode_counts":dict(collections.Counter(a[2] for a in recognized)),
                "recognized_stage_counts":dict(collections.Counter(a[3] for a in recognized)),
                "response_data_opened":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v18/results/source_filename_preflight_v18.json"))
    a=p.parse_args()
    d=run();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("V18_SOURCE_FILENAME_QC",json.dumps(d,sort_keys=True))
if __name__=="__main__":
    main()
