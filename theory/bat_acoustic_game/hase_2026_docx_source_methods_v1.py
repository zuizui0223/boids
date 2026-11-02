"""Read-only source method/figure DOCX structural and limited snippet inspection.

Only publicly published original supplemental files. Do not commit/rehost original
bytes or complete paragraphs. No bat participant observations are opened.
"""
import hashlib, json, re, io, zipfile, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

IDS={"methods":34022561,"figures":33439486}
API="https://api.figshare.com/v2/articles/"
OUT=Path(__file__).resolve().parent/"HASE_2026_SUPPLEMENT_METHOD_TERMS_V1.json"
NEEDLE=re.compile(
    r"waveform|frequency sweep|pulse shape|signal synth|spectro.?temporal|cross.?correl|"
    r"receiver|time.?window|flight|logarithmic|exponential|terminal frequency|"
    r"sound.*equation|synthe|pulse.*duration|masking",re.I)
W="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M="http://schemas.openxmlformats.org/officeDocument/2006/math"

def get(url,limit=6*1024*1024):
    req=urllib.request.Request(url,headers={"User-Agent":"bat-source-method-review/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read(limit+1)
def parse_docx(raw):
    if len(raw)>6*1024*1024:raise ValueError("SOURCE_TOO_LARGE")
    z=zipfile.ZipFile(io.BytesIO(raw))
    xml=z.read("word/document.xml")
    root=ET.fromstring(xml)
    paragraphs=[]
    for p in root.iter("{%s}p"%W):
        parts=[t.text or "" for t in p.iter() if t.tag in (f"{{{W}}}t",f"{{{M}}}t")]
        txt="".join(parts).strip()
        if txt:paragraphs.append(txt)
    omml=len(list(root.iter("{%s}oMath"%M)))
    inline=len(list(root.iter("{%s}oMathPara"%M)))
    imgs=len([n for n in z.namelist() if n.startswith("word/media/")])
    # Source values not retained: only short contextual snippets for methodological interpretation.
    match=[{"paragraph_index":i,"excerpt":p[:175],"chars":len(p)}
           for i,p in enumerate(paragraphs) if NEEDLE.search(p)]
    detailed=[{"p":i,"excerpt":paragraphs[i][:1250]} for i in
              (range(8,min(12,len(paragraphs))) if len(paragraphs)<20 else [])
              if i<len(paragraphs)]
    return {"read_only_detail":detailed,"paragraph_count":len(paragraphs),"math_inline_count":omml,
            "math_blocks_count":inline,"embedded_media":imgs,"matches":match[:42],
            "match_count":len(match),"headers":paragraphs[:5]}

def main():
    out={"schema":1,"status":"SUPPLEMENT_SOURCE_ONLY_METHOD_INSPECTION",
         "original_docx_bytes_committed":False,"biological_observation_values_opened":False,
         "articles":{}}
    for label,id in IDS.items():
        rec={"article_id":id,"source":API+str(id),"status":"NOT_CHECKED"}
        try:
            meta=json.loads(get(rec["source"]).decode())
            files=meta.get("files",[])
            rec["doi"]=meta.get("doi")
            rec["title"]=meta.get("title")
            rec["license_name"]=(meta.get("license") or {}).get("name")
            rec["files_metadata"]=[{"name":a.get("name"),"size":a.get("size"),
                                    "id":a.get("id")} for a in files]
            if len(files)!=1 or not files[0].get("name","").endswith(".docx"):
                raise ValueError("NOT_SINGLE_DOCX")
            raw=get(files[0]["download_url"])
            rec["bytes"]=len(raw)
            rec["sha256"]=hashlib.sha256(raw).hexdigest()
            rec.update(parse_docx(raw))
            rec["status"]="DOCX_PARAGRAPH_STRUCTURE_REVIEWED"
        except Exception as e:
            rec["status"]="STOP_SOURCE"
            rec["error"]=f"{type(e).__name__}:{str(e)[:180]}"
        out["articles"][label]=rec
        print("SUPPLEMENT",label,rec["status"],"SHA",rec.get("sha256"),
              "P",rec.get("paragraph_count"),"math",rec.get("math_inline_count"),
              "images",rec.get("embedded_media"),"error",rec.get("error"))
        print("SOURCE_HEADINGS",rec.get("headers",[])[:5])
        print("SOURCE_SELECTED_METHOD_EXCERPTS",json.dumps(rec.get("matches",[])[:32],ensure_ascii=False))
        if label=="methods":
            print("SOURCE_METHOD_DETAILS",json.dumps(rec.get("read_only_detail",[]),ensure_ascii=False))
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    return 0
if __name__=="__main__":raise SystemExit(main())
