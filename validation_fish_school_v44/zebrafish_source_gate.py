"""v44 source-only original zebrafish archive inspection. No source outcomes."""
import csv,hashlib,io,json,re,sys,tempfile,urllib.request,zipfile
from pathlib import Path,PurePosixPath
from collections import Counter
URL="https://zenodo.org/records/1470446/files/data.zip?download=1"
MD5="542382a5d3a9043734a3c9d617eacba5"
def gate(path):
    b=path.read_bytes()
    if hashlib.md5(b).hexdigest()!=MD5 or len(b)>90_000_000:raise ValueError("SOURCE_MD5_OR_CAP_STOP")
    out={"status":"ORIGINAL_ZIP_AUTHENTICATED_SOURCE_SCHEMA_ONLY","original_md5":MD5,"original_sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"source_url":URL,"members":[],"source_positions_or_effects_exported":False}
    with zipfile.ZipFile(path) as z:
        inf=z.infolist()
        if len({x.filename for x in inf})!=len(inf) or sum(x.file_size for x in inf)>1_000_000_000:raise ValueError("ZIP_DUPLICATE_OR_CAP_STOP")
        for x in inf:
            p=PurePosixPath(x.filename)
            if p.is_absolute() or ".." in p.parts or "\\" in x.filename or x.file_size>200_000_000:raise ValueError("ZIP_MEMBER_STOP")
            if x.is_dir():continue
            h=hashlib.sha256()
            with z.open(x) as f:
                for block in iter(lambda:f.read(1048576),b""):h.update(block)
            row={"name":x.filename,"bytes":x.file_size,"sha256":h.hexdigest()}
            if p.suffix.lower() in (".txt",".csv",".tsv",".dat"):
                widths=Counter(); nonnum=0; n=0; first=None
                with z.open(x) as f:
                    for line in io.TextIOWrapper(f,encoding="utf-8-sig",errors="replace"):
                        t=line.strip()
                        if not t:continue
                        parts=re.split(r"[\s,;]+",t)
                        widths[len(parts)]+=1
                        n+=1
                        bad=[]
                        for v in parts:
                            try:float(v)
                            except ValueError:
                                if v.upper() not in {"NA","NAN","NULL","NONE"}:bad.append(v)
                        if bad:
                            nonnum+=1
                            if n==1 and len(bad)==len(parts) and all(re.fullmatch(r"[A-Za-z][A-Za-z0-9_ .()\[\]-]{0,79}",v) for v in parts):
                                first=parts
                row.update(nonempty_rows=n,field_count_histogram=dict(widths),n_rows_with_non_numeric_nonmissing_tokens=nonnum,explicit_all_label_header=first)
            out["members"].append(row)
    out["member_count"]=len(out["members"])
    out["readme_or_metadata_names"]=[x["name"] for x in out["members"] if re.search(r"(readme|metadata|manifest|legend)",PurePosixPath(x["name"]).name,re.I)]
    return out

def run():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"data.zip"
        req=urllib.request.Request(URL,headers={"User-Agent":"boids-v44-original-source-gate/1.0"})
        n=0
        with urllib.request.urlopen(req,timeout=90) as r,p.open("wb") as f:
            if not r.geturl().startswith("https://"):raise ValueError("NON_TLS_REDIRECT")
            while True:
                b=r.read(1048576)
                if not b:break
                n+=len(b)
                if n>90_000_000:raise ValueError("SOURCE_CAP_STOP")
                f.write(b)
        return gate(p)
if __name__=="__main__":
    p=Path("validation_fish_school_v44/results/source_gate.json");p.parent.mkdir(parents=True,exist_ok=True)
    try:o=run()
    except Exception as e:
        o={"status":"SOURCE_STOP","reason":str(e),"new_observed_result":None}
        p.write_text(json.dumps(o,indent=2)+"\n")
        raise
    p.write_text(json.dumps(o,indent=2)+"\n")
    print(json.dumps({"status":o["status"],"sha256":o["original_sha256"],"member_count":o["member_count"],"names_and_schema":[{"name":x["name"],"rows":x.get("nonempty_rows"),"fields":x.get("field_count_histogram"),"header":x.get("explicit_all_label_header")} for x in o["members"]],"readme_or_metadata_names":o["readme_or_metadata_names"]}))
