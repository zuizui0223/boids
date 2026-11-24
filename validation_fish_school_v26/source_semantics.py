"""v26b source-semantic only: names, numeric/missing support, native clocks.

No original movement derivatives, forecasts, speeds, coordinates or model fits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from validation_fish_school_v26.eidc_source_only import BASE, PROBES, FILE_LIMIT, fetch_bound, SourceStop

PINS={
 "01.txt":("657872348cdf31b90e01c9f087df64937cb435f14d92eb1b1b9c3bc59a4b314a",9422363),
 "02.txt":("552f766d2a72926d041df8316caf8a0e2454aee64746ca837ad60e83973d10ed",8144030),
 "105.txt":("541617d6458a07c22bedeca43636c76e59e4dc30cfb12eedfa038d168cec0336",8734098)
}


def parse_numeric(value):
    try: x=float(value)
    except (ValueError,TypeError): return None
    return x if math.isfinite(x) else None


def semantics(blob):
    try: raw_lines=blob.decode("utf-8-sig").splitlines()
    except UnicodeError as e:raise SourceStop("EIDC_UTF8_READ_STOP") from e
    rows=[line.strip().split() for line in raw_lines if line.strip()]
    if len(rows)<3000:raise SourceStop("INSUFFICIENT_OBSERVED_SOURCE_ROWS")
    headers=rows[0]
    if len(headers)!=17 or len(set(headers))!=17:
        raise SourceStop("EIGHT_FISH_SOURCE_HEADER_17COL_STOP")
    if all(parse_numeric(t) is not None for t in headers):
        raise SourceStop("SOURCE_FIRST_ROW_NOT_PUBLISHED_HEADER_STOP")
    n=len(rows)-1
    finite=[0]*17
    complete=0
    initial_complete=0
    first_frame=None
    frame_steps=0
    positive_unit_steps=0
    invalid_shape=0
    nonfinite_counters=0
    # Original published shape is tracked without returning any fish values.
    for row_idx,tokens in enumerate(rows[1:]):
        if len(tokens)!=17:
            invalid_shape+=1
            continue
        numeric=[parse_numeric(x) for x in tokens]
        finite=[x+int(y is not None) for x,y in zip(finite,numeric)]
        good=all(x is not None for x in numeric[1:])
        complete+=int(good)
        if row_idx<1000:initial_complete+=int(good)
        if numeric[0] is not None:
            if first_frame is not None:
                frame_steps+=1
                positive_unit_steps+=int(numeric[0]-first_frame==1)
            first_frame=numeric[0]
        nonfinite_counters+=sum(x is None for x in numeric[1:])
    if invalid_shape>n*.01:
        raise SourceStop("EIDC_ORIGINAL_TOO_MANY_RAGGED_SOURCE_ROWS")
    if finite[0]<n*.99:
        raise SourceStop("SOURCE_FRAME_COLUMN_NONNUMERIC")
    if frame_steps<1000:
        raise SourceStop("SOURCE_FRAME_INDEX_NOT_VERIFIED")
    return {
      "header_names_from_original":headers,
      "original_nonempty_rows_including_header":len(rows),
      "n_observation_rows":n,
      "native_column_count":17,
      "native_published_fish_count":8,
      "finite_fraction_per_column":[round(t/n,6) for t in finite],
      "complete_eight_fish_coordinate_rows":complete,
      "complete_eight_fish_fraction":round(complete/n,6),
      "first_1000_complete_eight_fish_rows":initial_complete,
      "n_missing_fish_coordinate_tokens":nonfinite_counters,
      "original_frame_step_plus_one_fraction":round(positive_unit_steps/frame_steps,6),
      "ragged_original_rows":invalid_shape,
      "raw_position_values_exported":False,
      "original_school_mapping":"UNVERIFIED",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out={"status":"SOURCE_ACCESS_OR_SCHEMA_STOP","study":"MacGregor-Ioannou 2021 stickleback",
         "raw_fish_data_redistributed":False,"original_school_ID_known":False,
         "third_species_predictive_effect":None}
    try:
        parts=[]
        for name in PROBES:
            blob=fetch_bound(BASE+name,FILE_LIMIT)
            sha,size=PINS[name]
            if len(blob)!=size or hashlib.sha256(blob).hexdigest()!=sha:
                raise SourceStop("V26B_ORIGINAL_SHA_BYTES_REPLAY_STOP_"+name)
            parts.append({"source_name":name,"source_sha256":sha,**semantics(blob)})
        out["sources"]=parts
        out["status"]="ORIGINAL_SOURCE_COLUMN_AND_MISSINGNESS_ADMITTED_ONLY"
    except SourceStop as e:
        out["reason"]=str(e)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":main()
