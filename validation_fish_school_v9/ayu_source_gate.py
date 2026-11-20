"""v9 independent species AYU 2024 fish schooling original source-only audit.
No fish coordinates/velocities exported or ecological effects computed.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PIN="158e8d7ebdef73752da63192ee36e3a099dd5dfa"
UPSTREAM="t-niizato/Information-structure-of-heterogeneous-criticality"
FILES={
 "10-fish-2016-part3.txt":("6b9c3c1a66cafaf3d2b03cdd014050ab132d683e",1603189),
 "10-fish-part1-2016.txt":("594863644f88c00623adb9f42e3af84db8838b86",1937655),
 "10-fish-part1.txt":("fefd4de08763aed56e9a4528a9d086a2e1a04de7",2104948),
 "10-fish-part2-2016.txt":("33a2d8784280d6fc0b4bf6a656d713cd35cf264f",1634771),
 "10-fish-part2.txt":("dcd1cf8123bcc42bdf8c2eb36744d0aac1bf92ca",2212169),
 "10-fish-part3.txt":("2301f0c0ac0e27c55425485cc2ae767b31620100",1785474),
 "10-fish-part5.txt":("5f73ae22d5f09869681223d54b585778abe292e8",1633705)
}
class SourceStop(Exception):pass
def blobsha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def fields(line):
    s=line.strip()
    if not s:return []
    return [x for x in re.split(r"[,\t; ]+",s) if x]
def structure(data):
    try: s=data.decode("utf-8-sig")
    except UnicodeError:raise SourceStop("NOT_UTF8_SOURCE_TEXT") from None
    lines=[l for l in s.splitlines() if l.strip()]
    if len(lines)<100:raise SourceStop("SOURCE_TOO_FEW_RECORDS")
    sampled=lines[:20]
    columns=[len(fields(l)) for l in sampled]
    if min(columns)<2:raise SourceStop("TOO_FEW_SOURCE_COLUMNS")
    if len(set(columns))>3:raise SourceStop("RAGGED_SOURCE_HEADERS")
    h=fields(sampled[0])
    try:
        num0=sum(bool(x) and float(x)==float(x) for x in h)
    except ValueError: num0=0
    source_first_numeric_count=num0
    return {"nonempty_source_lines":len(lines),
            "first20_field_count_min":min(columns),
            "first20_field_count_max":max(columns),
            "first_line_numeric_fraction":source_first_numeric_count/len(h),
            "first_line_has_string_header":source_first_numeric_count<len(h),
            "exact_location_track_format":"NOT_YET_IDENTIFIED"}
def run(root):
    base=Path(root)/"Compute_IIT/fish_revised"
    records=[]
    for name,(sha,size) in FILES.items():
        try:
            b=(base/name).read_bytes()
            if len(b)!=size or blobsha(b)!=sha:raise SourceStop("ORIGINAL_GIT_BLOB_STOP")
            records.append({"file":name,"original_git_blob_sha":sha,
                            "original_byte_size":size,"source_byte_provenance":"VERIFIED",
                            **structure(b)})
        except (SourceStop,OSError,ValueError) as ex:
            records.append({"file":name,"status":"SOURCE_STRUCTURE_STOP","reason":str(ex)})
    return {"version":"v9_independent_ayu_10fish_source_only_20261120",
            "upstream":UPSTREAM,"pinned_commit":PIN,
            "n_expected_original_sources":len(FILES),
            "n_provenance_verified":sum(z.get("source_byte_provenance")=="VERIFIED" for z in records),
            "records":records,"source_movement_values_redistributed":False,
            "fish_boides_effect":"NOT_TESTED",
            "status":"SOURCE_ALL_SEVEN_STRUCTURE_PASS" if all(z.get("source_byte_provenance")=="VERIFIED" for z in records)
            else "SOURCE_STRUCTURE_STOP"}
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    p.add_argument("--output",default="validation_fish_school_v9/results/ayu_original_structure.json")
    args=p.parse_args();d=run(args.root)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":d["status"],"n_verified":d["n_provenance_verified"],
      "layout":[{"file":z["file"],"rows":z.get("nonempty_source_lines"),
                 "fieldcount":z.get("first20_field_count_max"),"reason":z.get("reason")}
                for z in d["records"]]}))
if __name__=="__main__":main()
