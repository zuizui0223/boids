"""v180: native original Deltares isource variable flag metadata DIAGNOSIS.

v179 correctly replays 149446/119778 GPS-native-DEM matches but cannot map
original isource indices to filename years, hence provenance SOURCE_STOP.
This stage inspects ONLY provider metadata (no DEM pixels, no wild GPS),
and freezes exact attribute existence/types/counts to distinguish a genuinely
missing mapping from a decoder failure. No ecological effect estimates.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json"
PRIOR=ROOT/"validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
OUT=ROOT/"validation_v180/results/real_ten_isource_flag_metadata_v180.json"
EXPECTED_TILES=10
BASE="https://opendap.deltares.nl/"
MAX_ATTRIBUTE_TEXT=250000

def numeric_codes(raw):
    if raw is None:
        return None
    try:
        x=np.ma.asarray(raw,dtype=float)
        if x.ndim!=1 or not 1<=len(x)<=1000:return None
        v=x.filled(np.nan)
        if not np.isfinite(v).all() or not np.allclose(v,np.rint(v)):
            return None
        values=[int(a) for a in v]
        return values if len(set(values))==len(values) else None
    except (ValueError,TypeError,OverflowError):
        return None

def names_from_native_attribute(raw):
    if raw is None:return None
    if isinstance(raw,bytes):
        try: raw=raw.decode("utf-8")
        except UnicodeDecodeError:return None
    if isinstance(raw,str):
        if len(raw)>MAX_ATTRIBUTE_TEXT:return None
        return raw.split()
    if isinstance(raw,np.ndarray) and raw.ndim==1:
        items=[]
        for item in raw:
            if isinstance(item,bytes):
                try:item=item.decode("utf-8")
                except UnicodeDecodeError:return None
            if not isinstance(item,str):return None
            # A native vector-of-strings is a separate source name per item.
            items.append(item)
        return items
    return None

def digest_short(x):
    if x is None:return None
    if isinstance(x,bytes):b=x
    else:b=str(x).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def safe_attr_summary(value):
    if value is None:return {"present":False}
    items=names_from_native_attribute(value)
    return {"present":True,"python_type":type(value).__name__,
            "native_shape":list(value.shape) if isinstance(value,np.ndarray) else None,
            "string_or_array_length":len(value) if hasattr(value,"__len__") else None,
            "tokens_or_vector_items":len(items) if items is not None else None,
            "raw_attribute_sha256":digest_short(value),
            "first_three_label_examples":items[:3] if items else []}

def inspect_var_attributes(v):
    attrs=set(v.ncattrs())
    rawvalues=v.getncattr("flag_values") if "flag_values" in attrs else None
    rawmeaning=v.getncattr("flag_meanings") if "flag_meanings" in attrs else None
    codes=numeric_codes(rawvalues)
    names=names_from_native_attribute(rawmeaning)
    matches=codes is not None and names is not None and len(codes)==len(names)
    # Native per-pixel code->original filename exists only when exact distinct
    # origin code and source filename lists correspond.
    return {
      "original_variable_isource_ncattrs":sorted(attrs),
      "flag_values_summary":safe_attr_summary(rawvalues),
      "flag_meanings_summary":safe_attr_summary(rawmeaning),
      "numeric_flag_values_n":len(codes) if codes is not None else None,
      "native_flag_meaning_items_n":len(names) if names is not None else None,
      "exact_unambiguous_code_filename_mapping_possible":bool(matches),
      "source_filename_year_examples_not_survey_dates":names[:3] if matches else [],
      "source_mapping_status":"MAPPING_POSSIBLE_METADATA_ONLY" if matches else "SOURCE_STOP_FLAGS_ABSENT_OR_UNPAIRED"
    }

def run():
    old=json.loads(SOURCE.read_text())
    v174=json.loads(PRIOR.read_text())
    tiles=old["all_original_intersecting_native_tile_source_metadata"]
    old_rows={z["tile"]:z for z in v174["all_original_tile_source_schema_or_STOP"]}
    if len(tiles)!=EXPECTED_TILES or set(old_rows)!={x["source_tile_basename"] for x in tiles}:
        raise AssertionError("Original provider 10 tile identities differ from frozen v173/v174")
    records=[]
    for t in sorted(tiles,key=lambda x:x["source_tile_basename"]):
        label=t["source_tile_basename"]
        uri=t["source_original_native_tile_url"].replace("http://","https://",1)
        if not uri.startswith(BASE) or not uri.endswith(".nc"):
            raise AssertionError("Wrong provider source URL")
        with Dataset(uri,mode="r") as nc:
            if "isource" not in nc.variables or "time" not in nc.variables or "z" not in nc.variables:
                raise AssertionError("Native original variable missing")
            src=nc.variables["isource"]
            item=inspect_var_attributes(src)
            item.update({
                "tile":label,
                "original_z_source_grid_not_loaded":True,
                "native_isource_source_grid_not_loaded":True,
                "wild_GPS_ACC_tide_not_loaded":True,
                "original_global_source_attribute_summary":
                    safe_attr_summary(nc.getncattr("source")) if "source" in nc.ncattrs() else {"present":False},
            })
        records.append(item)
        print("V180_METADATA_TILE="+json.dumps({k:item[k] for k in ("tile","numeric_flag_values_n","native_flag_meaning_items_n","exact_unambiguous_code_filename_mapping_possible","source_mapping_status")},sort_keys=True),flush=True)
    return {"version":"v180_authentic_provider_native_isource_filename_flag_attribute_probe_v1",
            "previous_v179_source_origin_year_gate":"SOURCE_STOP_0_PROVEN_PREYEAR_OBSERVATIONS",
            "original_ten_native_tiles_metadata_probed":len(records),
            "original_native_source_tiles_with_code_to_filename_map":sum(r["exact_unambiguous_code_filename_mapping_possible"] for r in records),
            "per_tile_original_provider_metadata":records,
            "no_GPS_tide_z_or_perpixel_isource_values_read":True,
            "no_biological_mechanism_or_tide_solar_causal_test":"NOT_ESTIMATED"}

def main():
    p=argparse.ArgumentParser()
    a=p.add_mutually_exclusive_group(required=True)
    a.add_argument("--emit",action="store_true")
    a.add_argument("--check",action="store_true")
    c=p.parse_args()
    r=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if c.check:
        if not OUT.exists() or json.loads(OUT.read_text())!=r:
            raise AssertionError("Original source metadata identity changed")
        print("V180_NATIVE_FLAG_METADATA_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V180_NATIVE_FLAG_SOURCE_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V180_NATIVE_FLAG_SOURCE_END")
    print("V180_METADATA_SUMMARY="+json.dumps({
      "tiles":r["original_ten_native_tiles_metadata_probed"],
      "matched":r["original_native_source_tiles_with_code_to_filename_map"],
      "rows":[{k:t[k] for k in ("tile","numeric_flag_values_n","native_flag_meaning_items_n","exact_unambiguous_code_filename_mapping_possible")} for t in r["per_tile_original_provider_metadata"]]
    },sort_keys=True))

if __name__=="__main__":
    main()
