#!/usr/bin/env python3
"""Source-only Finnish 2026 original XLSX night/bin grain; no activity values."""
import csv,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path
from bat_diel_source_gate import original

URL="https://zenodo.org/records/18298435/files/Data.xlsx?download=1"
EXPECTED="444c510bcb154bf9272d620f1ce0ec5a"
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
OUT=Path("validation_v38/results/finland_night_bin_structure_v38b.json")
KEY=("region","location","device","year","startdate")
CAT=("species","region","period","location","device","year","startdate","quartiles","hours_after_sunset_group")
MISSING=("prop_activity","total_nightly_activity","mean_temp","night_length")
def values_of_cell(c,shared):
    t=c.attrib.get("t","");v=c.find(NS+"v")
    if t=="s" and v is not None:
        try:return shared[int(v.text)]
        except (TypeError,IndexError,ValueError):return ""
    if t=="inlineStr":return "".join(e.text or "" for e in c.iter(NS+"t"))
    return (v.text if v is not None else "") or ""
def scan(path,shared):
    rows=0;header=None;catvals=defaultdict(set);nonmissing=Counter();sizes=Counter()
    nights=defaultdict(lambda:{"bins":set(),"n":0,"valid":0})
    dup=0;first_bin="quartiles" if "sheet1.xml" in path else "hours_after_sunset_group"
    for _,el in ET.iterparse(path,events=("end",)):
        if el.tag!=NS+"row":continue
        cells=list(el);vals=[]
        for c in cells:
            m=re.match(r"([A-Z]+)",c.attrib.get("r",""))
            if not m:continue
            col=0
            for ch in m.group(1):col=col*26+ord(ch)-64
            vals.append((col-1,values_of_cell(c,shared)))
        if header is None:
            header={index:str(v).strip() for index,v in vals}
            if not set(KEY).issubset(header.values()) or first_bin not in header.values():
                raise ValueError("missing original source key/bin field "+first_bin)
            el.clear();continue
        row={header.get(index,"UNKNOWN"):str(v).strip() for index,v in vals}
        rows+=1
        for k in CAT:
            if row.get(k):
                if len(catvals[k])<100000:catvals[k].add(row[k])
        for k in MISSING:
            if row.get(k) not in ("", "NA", "NaN", "nan"):nonmissing[k]+=1
        key=tuple(row.get(k,"") for k in KEY)
        binval=row.get(first_bin,"")
        info=nights[key]
        if binval in info["bins"]:dup+=1
        info["bins"].add(binval);info["n"]+=1
        if row.get("prop_activity") not in ("", "NA", "NaN", "nan"):info["valid"]+=1
        el.clear()
    complete=sum(len(x["bins"])==4 and x["n"]==4 for x in nights.values())
    valid=sum(len(x["bins"])==4 and x["n"]==4 and x["valid"]==4 for x in nights.values())
    return {"rows":rows,"original_header_columns":[header[k] for k in sorted(header)],
            "source_night_keys":len(nights),"source_duplicate_night_bin_keys":dup,
            "source_nights_with_exactly_4_distinct_bins":complete,
            "nights_with_4_bins_and_all_nonempty_prop_activity":valid,
            "distinct_category_counts":{k:len(v) for k,v in catvals.items()},
            "nonempty_column_cells":dict(nonmissing),
            "numeric_bat_activity_or_weather_values_opened":False}
def audit(data):
    if not zipfile.is_zipfile(io.BytesIO(data)):raise ValueError("original XLSX invalid")
    with zipfile.ZipFile(io.BytesIO(data)) as zip_:
        shared=[]
        if "xl/sharedStrings.xml" in zip_.namelist():
            root=ET.fromstring(zip_.read("xl/sharedStrings.xml"))
            shared=["".join(x.text or "" for x in item.iter(NS+"t")) for item in root.findall(NS+"si")]
        result={"original_source_md5_verified":True,"files":{}}
        for sheet in ("xl/worksheets/sheet1.xml","xl/worksheets/sheet2.xml"):
            with zip_.open(sheet) as f:result["files"][sheet]=scan(f,shared)
    q=result["files"]["xl/worksheets/sheet1.xml"]
    fixed={
        "three_or_more_original_years":q["distinct_category_counts"].get("year",0)>=3,
        "two_or_more_original_regions":q["distinct_category_counts"].get("region",0)>=2,
        "one_thousand_unique_nights":q["source_night_keys"]>=1000,
        "one_thousand_complete_four_quartile_nights":q["source_nights_with_exactly_4_distinct_bins"]>=1000,
        "one_thousand_valid_activity_quartile_nights":q["nights_with_4_bins_and_all_nonempty_prop_activity"]>=1000,
        "no_duplicate_night_quartile_keys":q["source_duplicate_night_bin_keys"]==0}
    result["predeclared_conditions"]=fixed
    result["admission"]="SOURCE_BIN_GRAIN_READY_FOR_SEPARATE_FROZEN_MODEL" if all(fixed.values()) else "SOURCE_NIGHT_SUPPORT_STOP"
    result["raw_bat_activity_weather_values_opened"]=False
    result["behavior_model_fitted"]=False
    return result
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);args=p.parse_args()
    try:
        http,mime,data=original(URL)
        if http!=200 or hashlib.md5(data).hexdigest()!=EXPECTED:
            res={"admission":"PUBLISHED_XLSX_INTEGRITY_STOP","raw_bat_activity_weather_values_opened":False}
        else:
            res=audit(data);res["original_file_bytes"]=len(data);res["original_sha256"]=hashlib.sha256(data).hexdigest()
    except Exception as e:
        res={"admission":"SOURCE_STRUCTURE_EXCEPTION_STOP","error_type":type(e).__name__,
             "error_message":str(e)[:150],"raw_bat_activity_weather_values_opened":False}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("V38B_FINLAND_NIGHT_GRAIN="+json.dumps(res,sort_keys=True))
    assert res["raw_bat_activity_weather_values_opened"] is False
