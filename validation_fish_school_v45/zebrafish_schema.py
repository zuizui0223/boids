"""v45 actual source header and clock/identity schema only; no model outcome."""
from pathlib import Path
import hashlib,json,re,urllib.request,zipfile,tempfile,io
import numpy as np
URL="https://zenodo.org/records/1470446/files/data.zip?download=1"
SHA="03a754d8e6d9084bd8944540189c65a20d63644063e127bf586feb5c4eacdfe0"
MD5="542382a5d3a9043734a3c9d617eacba5"
PINS={
"identNogaps-2015-10-27T165259formated.txt":"67accbf98a725fcc11823bd0ea9c7ab3c96ab3dbdc9402c77d381e642c395c33",
"identNogaps-2016-02-10T125503-orientation0formated.txt":"07160364e7f2cad570ebd5f55985dba1a402ff8c9d4def09c160f31555445183",
"identNogaps-2015-10-27T140627formated.txt":"375be427ada71a38079a890c7172f6ced454791c852401d3bad1fe754e2075af",
"identNogaps-2015-12-02T152638-orientation90formated.txt":"1ca5670cd6fb27c92d4d6862f9362aebc87f22224c286c08973be0f479734936",
"identNogaps-2015-10-27T112606formated.txt":"e5a514d53f38b2a853795cfd0c679463c8712a38e797fe2da7e586b85afc24d4",
"identNogaps-2015-10-27T095056formated.txt":"bfdd11b759483f5ae39b38bd2e8ad97b29cd283d66c2e68b9047c3e2173e44f3",
"identNogaps-2016-02-03T114311-orientation0formated.txt":"ef853905a034bbf9ccb2a15ad5488ab7c11c3c1c49e1ee6f1456d00c0a9589c9",
"identNogaps-2015-12-02T121958-orientation90formated.txt":"58bedc059b41edd3081ae810e365b9437a762913ad74ca0c755ba21812e25740"}
def acquire(path):
    req=urllib.request.Request(URL,headers={"User-Agent":"boids-v45-schema/1.0"})
    n=0
    with urllib.request.urlopen(req,timeout=90) as r,path.open("wb") as f:
        if not r.geturl().startswith("https://"):raise ValueError("TLS_STOP")
        for b in iter(lambda:r.read(1048576),b""):
            n+=len(b)
            if n>90_000_000:raise ValueError("SOURCE_CAP_STOP")
            f.write(b)
    b=path.read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHA or hashlib.md5(b).hexdigest()!=MD5:raise ValueError("ZIP_HASH_DRIFT")
def selected(z):
    names=[x.filename for x in z.infolist() if x.filename.startswith("data/10AB/ident") and x.filename.endswith(".txt")]
    if len(names)!=8 or set(names)!={"data/10AB/"+n for n in PINS}:raise ValueError("ARCHIVE_ROSTER_DRIFT")
    return sorted(names)
def read_header_and_data(z,name):
    raw=z.read(name)
    if hashlib.sha256(raw).hexdigest()!=PINS[Path(name).name]:raise ValueError("MEMBER_HASH_DRIFT")
    s=raw.decode("utf-8-sig")
    lines=s.splitlines()
    if not lines or not lines[0].lstrip().startswith("#"):raise ValueError("UNVERIFIED_HEADER_COMMENT_STOP")
    head=lines[0].strip().lstrip("#").strip()
    if len(head)>4096 or any(ord(c)<32 and c!="\t" for c in head):raise ValueError("HEADER_FORMAT_STOP")
    fields=re.split(r"[\s,;]+",head)
    if len(fields)!=31 or not all(re.search(r"[A-Za-z]",x) for x in fields):
        raise ValueError("EXPLICIT_LABELS_STOP")
    # Only schema/clock checks below; no movement or model scores.
    arr=np.loadtxt(io.StringIO(s),comments="#")
    if arr.shape!=(54001,31):raise ValueError("NATIVE_SHAPE_STOP")
    return head,fields,arr
def main():
    out={"status":"SOURCE_SCHEMA_ONLY","files":[],"original_archive_sha256":SHA,"raw_values_exported":False,"new_movement_score":None}
    p=Path("validation_fish_school_v45/results/schema.json");p.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"data.zip";acquire(path)
            with zipfile.ZipFile(path) as z:
                for name in selected(z):
                    head,fields,a=read_header_and_data(z,name)
                    f=a[:,0]; dt=np.diff(f)
                    clock={"all_finite":bool(np.isfinite(f).all()),"strictly_increasing":bool((dt>0).all()),
                           "integer_step1":bool(np.allclose(dt,1,atol=1e-8,rtol=0)),
                           "elapsed_15fps_rounded":bool(np.max(np.abs((f-f[0])-np.arange(len(f))/15))<=.0051)}
                    out["files"].append({"name":name,"header":head,"fields":fields,"shape":list(a.shape),"first_column_clock":clock,
                       "per_column_nonfinite_count":np.sum(~np.isfinite(a),axis=0).tolist(),
                       "per_column_all_finite_values_in_0_1":np.all(((a>=0)&(a<=1))|~np.isfinite(a),axis=0).tolist()})
        out["identical_headers"]=len({tuple(x["fields"]) for x in out["files"]})==1
    except Exception as e:
        out.update(status="SOURCE_STOP",reason=str(e))
        p.write_text(json.dumps(out,indent=2)+"\n");raise
    p.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out))
if __name__=="__main__":main()
