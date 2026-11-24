"""v26c post-source-stop schema-only diagnostic. No animal movement scores."""
from __future__ import annotations
import argparse,collections,hashlib,json,math
from pathlib import Path
from validation_fish_school_v26.eidc_source_only import BASE,PROBES,FILE_LIMIT,fetch_bound,SourceStop
from validation_fish_school_v26.source_semantics import PINS

def numeric(t):
    try:v=float(t)
    except ValueError:return False
    return math.isfinite(v)

def schema_only(blob):
    rows=[r.split() for r in blob.decode("utf-8-sig").splitlines() if r.strip()]
    if len(rows)<3000 or len(rows[0])!=17:
        raise SourceStop("SOURCE_HEADER_OR_ROWS_INCOMPLETE")
    header=rows[0]
    counts=[0]*17
    missing=collections.Counter()
    xy_complete=0
    ragged=0
    for row in rows[1:]:
        if len(row)!=17:
            ragged+=1
            continue
        numbers=[numeric(t) for t in row]
        counts=[a+int(b) for a,b in zip(counts,numbers)]
        xy_complete+=int(all(numbers[1:]))
        if not numbers[0] and len(missing)<100:
            try: val=row[0].encode("ascii").decode()
            except UnicodeError: val="NON_ASCII_SOURCE_TOKEN"
            if len(val)>50: val="LONG_SOURCE_TOKEN"
            missing[val]+=1
    n=len(rows)-1
    return {
      "original_header_strings_only":header,
      "n_rows_excluding_header":n,
      "column_0_finite_count":counts[0],
      "column_0_finite_fraction":round(counts[0]/n,6),
      "column_0_nonnumeric_string_frequencies":missing.most_common(8),
      "fraction_finite_by_column":[round(x/n,6) for x in counts],
      "original_complete_eight_fish_XY_rows":xy_complete,
      "source_shape_mismatch_rows":ragged,
      "frame_column_identity":"NOT_VERIFIED",
      "original_school_ID":"UNKNOWN",
      "original_coordinates_or_model_effect_exported":False
    }

def run():
    out={"status":"SOURCE_SCHEMA_DIAGNOSTIC_STOP","original_fish_behavior_scored":False}
    try:
        cases=[]
        for name in PROBES:
            data=fetch_bound(BASE+name,FILE_LIMIT)
            sha,n=PINS[name]
            if len(data)!=n or hashlib.sha256(data).hexdigest()!=sha:
                raise SourceStop("V26C_SHA_BYTE_IDENTICAL_SOURCE_STOP_"+name)
            cases.append({"filename":name,"sha256":sha,**schema_only(data)})
        out.update({"status":"SOURCE_COLUMN_IDENTITY_DIAGNOSTIC_ONLY","files":cases})
    except SourceStop as e:
        out["reason"]=str(e)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    ans=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(ans,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(ans,sort_keys=True))

if __name__=="__main__":main()
