#!/usr/bin/env python3
"""v38 source-only original multi-region bat acoustics manifest; no response values."""
import csv,hashlib,io,json,re,urllib.request,urllib.parse,urllib.error,zipfile,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
FILES={
"Finland":[("18298435","Data.xlsx","444c510bcb154bf9272d620f1ce0ec5a")],
"Italy":[("21808015","Databats_Cansiglio.csv","76b954fd896ad182aa5a9b97516b6535")],
"Belgium":[("20137204","metadata_loc.csv","9672cb0e7dec4d0811540458375229b1"),
("20137204","Obs.AudioMoths-bats_activity.csv","d0588f30bf4ed86a168c5438373e6019"),
("20137204","Obs.AudioMoths-bats.csv","e048b351a5300e9cd30c7e4500a9259a"),
("20137204","Obs.Pitfalls.csv","fd45668086cc38fbfa9a4c682607d7fe"),
("20137204","Obs.Transects.csv","82a80234186bdeaeeace7d9859dd7e7e")]}
CATS=("site","plot","station","date","time","year","taxon","species","guild","sample","group","treat","habitat","device","recording")
PRIVATE=("lat","lon","utm","gps","coord","address","roost","file_name","filename")
CAP=12000000
def original(url):
    request=urllib.request.Request(url,headers={"User-Agent":"boids-bat-diel-structural/1.0"})
    with urllib.request.urlopen(request,timeout=45) as r:
        return r.status,r.headers.get("Content-Type",""),r.read(CAP+1)
def csv_structure(data):
    try:s=data.decode("utf-8-sig")
    except UnicodeDecodeError:s=data.decode("latin-1")
    first=s.splitlines()[0] if s.splitlines() else ""
    delim=max((";",",","	"),key=first.count)
    rd=csv.DictReader(io.StringIO(s),delimiter=delim)
    cols=[str(c).strip() for c in rd.fieldnames or []]
    if len(cols)<2:return {"status":"BAD_HEADER"}
    categories=[c for c in cols if any(x in c.casefold() for x in CATS) and not any(x in c.casefold() for x in PRIVATE)]
    values={k:set() for k in categories};obs=Counter();rows=0
    for rec in rd:
        rows+=1
        for k in categories:
            x=(rec.get(k) or "").strip()
            if x and x.casefold() not in ("na","nan","null"):
                obs[k]+=1
                if len(values[k])<50000:values[k].add(x)
    return {"status":"CSV_SCHEMA_ONLY","row_count":rows,"columns":cols,
            "categorical_support":{k:{"distinct":len(v),"nonempty":obs[k]} for k,v in values.items()}}
def xlsx_structure(data):
    if not zipfile.is_zipfile(io.BytesIO(data)):return {"status":"INVALID_XLSX"}
    ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        paths=set(z.namelist())
        if "xl/workbook.xml" not in paths:return {"status":"NOT_XLSX"}
        w=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=[x.attrib.get("name","") for x in w.iter(ns+"sheet")]
        shared=[]
        if "xl/sharedStrings.xml" in paths and z.getinfo("xl/sharedStrings.xml").file_size<60000000:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(t.text or "" for t in item.iter(ns+"t")) for item in root.findall(ns+"si")]
        headers=[]
        for name in sorted(p for p in paths if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",p)):
            header=[]
            with z.open(name) as f:
                for _,e in ET.iterparse(f,events=("end",)):
                    if e.tag==ns+"row":
                        for c in list(e)[:70]:
                            v=c.find(ns+"v");typ=c.attrib.get("t","")
                            if typ=="s" and v is not None:
                                try:label=shared[int(v.text)]
                                except (IndexError,TypeError,ValueError):label="UNRESOLVED_SHARED_STRING"
                            elif typ=="inlineStr":label="".join(q.text or "" for q in c.iter(ns+"t"))
                            else:label="NUMERIC_OR_BLANK"
                            header.append(label[:100])
                        break
            headers.append({"worksheet":name,"header_text_only":header})
    return {"status":"XLSX_SCHEMA_ONLY","sheets":sheets,"headers":headers}
def run(fetch=original):
    d={"source_only":True,"numeric_bat_or_insect_outcomes_opened":False,
       "behavior_model_fitted":False,"sources":{}}
    for area,files in FILES.items():
        d["sources"][area]={}
        for rec,name,expected in files:
            url=f"https://zenodo.org/records/{rec}/files/{urllib.parse.quote(name)}?download=1"
            obj={"record_id":rec,"filename":name,"expected_md5":expected}
            try:
                code,typ,data=fetch(url)
                obj.update({"http":code,"mime":str(typ)[:80],"source_bytes":len(data)})
                lead=data[:128].lstrip().lower()
                if code!=200 or len(data)>CAP or lead.startswith((b"<html",b"<!doctype",b"{")):
                    obj["status"]="ACCESS_OR_SIZE_STOP"
                else:
                    md5=hashlib.md5(data).hexdigest()
                    obj.update({"actual_md5":md5,"sha256":hashlib.sha256(data).hexdigest()})
                    if md5!=expected:obj["status"]="PUBLISHED_MD5_MISMATCH_STOP"
                    else:obj.update(xlsx_structure(data) if name.endswith(".xlsx") else csv_structure(data))
            except urllib.error.HTTPError as e:obj.update({"status":"HTTP_ACCESS_STOP","http":e.code})
            except (urllib.error.URLError,OSError,TimeoutError) as e:obj.update({"status":"TRANSPORT_STOP","exception":type(e).__name__})
            d["sources"][area][name]=obj
    return d
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=Path("validation_v38/results/multiregion_source_v38.json"));a=p.parse_args()
    d=run();a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V38_ORIGINAL_SOURCE_STRUCTURE="+json.dumps(d["sources"],ensure_ascii=False,sort_keys=True))
    assert not d["numeric_bat_or_insect_outcomes_opened"] and not d["behavior_model_fitted"]
