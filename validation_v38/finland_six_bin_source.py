#!/usr/bin/env python3
"""Source-only Finnish 2026 original XLSX night/bin grain; no activity values."""
import csv,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path
from bat_diel_source_gate import original

URL="https://zenodo.org/records/18298435/files/Data.xlsx?download=1"
EXPECTED="444c510bcb154bf9272d620f1ce0ec5a"
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
OUT=Path("validation_v38/results/finland_six_bin_structure_v38c.json")
KEY=("region","location","device","year","startdate")
CAT=("species","region","period","location","device","year","startdate","quartiles","hours_after_sunset_group")
MISSING=("prop_activity","n","total_nightly_activity","mean_temp","night_length","sum_rain","mean_wind")
def values_of_cell(c,shared):
    t=c.attrib.get("t","");v=c.find(NS+"v")
    if t=="s" and v is not None:
        try:return shared[int(v.text)]
        except (TypeError,IndexError,ValueError):return ""
    if t=="inlineStr":return "".join(e.text or "" for e in c.iter(NS+"t"))
    return (v.text if v is not None else "") or ""
def scan(path,shared,first_bin):
    rows=0;header=None;catvals=defaultdict(set);nonmissing=Counter();sizes=Counter()
    nights=defaultdict(lambda:{"bins":set(),"n":0,"valid":0,"valid_n":0})
    dup=0
    for _,el in ET.iterparse(path,events=("end",)):
        if el.tag!=NS+"row":continue
        cells=list(el);vals=[]
        for c in cells:
            m=re.match(r"([A-Z]+)",c.attrib.get("r",""))
            if not m:continue
            col=0
            for ch in m.group(1):col=col*26+ord(ch)-64
            idx=col-1
            if header is None:
                vals.append((idx,values_of_cell(c,shared)))
            else:
                field=header.get(idx,"UNKNOWN")
                if field in KEY or field in CAT:
                    vals.append((idx,values_of_cell(c,shared)))
                elif field in MISSING:
                    # Inspect only presence of a stored cell, never its numeric value.
                    stored=c.find(NS+"v")
                    vals.append((idx,"PRESENT" if stored is not None and stored.text is not None else ""))

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
            if row.get(k)=="PRESENT":nonmissing[k]+=1
        key=tuple(row.get(k,"") for k in KEY)
        binval=row.get(first_bin,"")
        info=nights[key]
        if binval in info["bins"]:dup+=1
        info["bins"].add(binval);info["n"]+=1
        if row.get("prop_activity")=="PRESENT":info["valid"]+=1
        if row.get("n")=="PRESENT":info["valid_n"]+=1
        el.clear()
    complete=sum(len(x["bins"])==6 and x["n"]==6 for x in nights.values())
    valid=sum(len(x["bins"])==6 and x["n"]==6 and x["valid"]==6 and x["valid_n"]==6 for x in nights.values())
    return {"rows":rows,"original_header_columns":[header[k] for k in sorted(header)],
            "source_night_keys":len(nights),"source_duplicate_night_bin_keys":dup,
            "source_nights_with_exactly_6_distinct_bins":complete,
            "nights_with_6_bins_and_all_nonempty_n_and_prop_activity":valid,
            "distinct_category_counts":{k:len(v) for k,v in catvals.items()},
            "source_original_bin_labels":sorted(catvals[first_bin]),
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
            with zip_.open(sheet) as f:result["files"][sheet]=scan(f,shared,"quartiles" if "sheet1.xml" in sheet else "hours_after_sunset_group")
    q=result["files"]["xl/worksheets/sheet1.xml"]
    fixed={
        "three_or_more_original_years":q["distinct_category_counts"].get("year",0)>=3,
        "two_or_more_original_regions":q["distinct_category_counts"].get("region",0)>=2,
        "one_thousand_unique_nights":q["source_night_keys"]>=1000,
        "one_thousand_complete_six_bin_nights":q["source_nights_with_exactly_6_distinct_bins"]>=1000,
        "one_thousand_valid_six_bin_nights":q["nights_with_6_bins_and_all_nonempty_n_and_prop_activity"]>=1000,
        "exactly_six_global_bin_labels":q["distinct_category_counts"].get("quartiles",0)==6,
        "no_duplicate_night_quartile_keys":q["source_duplicate_night_bin_keys"]==0}
    result["predeclared_conditions"]=fixed
    result["admission"]="V38C_SIX_BIN_SOURCE_READY_FOR_NEW_FROZEN_MODEL" if all(fixed.values()) else "V38C_SIX_BIN_SOURCE_SUPPORT_STOP"
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
    print("V38C_FINLAND_SIX_BIN_GRAIN="+json.dumps(res,sort_keys=True))
    assert res["raw_bat_activity_weather_values_opened"] is False
