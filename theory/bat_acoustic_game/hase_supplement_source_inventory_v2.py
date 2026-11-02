"""No-response original supplementary-source availability inventory.
This tool collects public provider metadata and ZIP member filenames only.
No PDF content, bat animal response or copyrighted code is read/published.
"""
import hashlib,json,urllib.request,urllib.error,zipfile,io
from pathlib import Path

OUT=Path(__file__).resolve().parent/"HASE_SUPPLEMENT_SOURCE_INVENTORY_V2.json"
URLS={
    "figshare_collection":"https://api.figshare.com/v2/collections/8694625",
    "figshare_collection_articles":"https://api.figshare.com/v2/collections/8694625/articles",
    "figshare_collection_versions":"https://api.figshare.com/v2/collections/8694625/versions",
    "existing_data_article":"https://api.figshare.com/v2/articles/30937379",
    "pmc_supplement_zip":"https://pmc.ncbi.nlm.nih.gov/articles/PMC13678626/bin/rspb.2026.0921.zip"
}
MAX_BYTES=12*1024*1024
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"bat-public-supplement-inventory/2.0","Accept":"application/json,*/*"})
    with urllib.request.urlopen(req,timeout=50) as r:
        chunks=[];tot=0
        while True:
            b=r.read(256*1024)
            if not b: break
            tot+=len(b)
            if tot>MAX_BYTES: raise ValueError("STOP_LARGE_SOURCE")
            chunks.append(b)
        return b"".join(chunks),r.status

def main():
    data={"schema":2,"source_only":True,"supplement_PDF_content_opened":False,
          "biological_outcomes_opened":False,"original_source_redistributed":False,"targets":{}}
    for k,url in URLS.items():
        row={"url":url,"status":"NOT_CHECKED"}
        try:
            raw,status=fetch(url)
            row.update(status="FETCHED",http_status=status,nbytes=len(raw),
                       sha256=hashlib.sha256(raw).hexdigest())
            if raw[:2]==b"PK":
                z=zipfile.ZipFile(io.BytesIO(raw))
                row["source_type"]="ZIP"
                row["members"]=[{"filename":i.filename,"bytes":i.file_size} for i in z.infolist()][:150]
                row["member_count"]=len(z.infolist())
            else:
                obj=json.loads(raw)
                if isinstance(obj,list):
                    row["source_type"]="JSON_LIST"
                    row["item_count"]=len(obj)
                    row["items"]=[{"id":x.get("id"),"title":x.get("title"),"doi":x.get("doi"),
                                   "url_public_api":x.get("url_public_api")} for x in obj[:30]
                                  if isinstance(x,dict)]
                elif isinstance(obj,dict):
                    row["source_type"]="JSON_OBJECT"
                    row["title"]=obj.get("title");row["id"]=obj.get("id")
                    row["doi"]=obj.get("doi")
                    row["articles"]=obj.get("articles")
                    row["files"]=[{"id":x.get("id"),"name":x.get("name"),"size":x.get("size"),
                                   "download_url":x.get("download_url")}
                                for x in obj.get("files",[]) if isinstance(x,dict)][:50]
                else: row["source_type"]="JSON_OTHER"
        except Exception as e:
            row.update(status="STOP_ACCESS_OR_FORMAT",error=f"{type(e).__name__}: {str(e)[:200]}")
        data["targets"][k]=row
        print("SOURCE",k,row["status"],"bytes",row.get("nbytes"),"items",row.get("item_count"),
              "members",row.get("member_count"),"error",row.get("error"))
        if "members" in row:print("MEMBERS",[(x["filename"],x["bytes"]) for x in row["members"]])
        if "items" in row:print("ARTICLE_ITEMS",[(x["id"],x["title"]) for x in row["items"]])
        if "files" in row:print("FILES",[(x["name"],x["size"]) for x in row["files"]])
    OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
    print("SOURCE_INVENTORY_READY")
    return 0
if __name__=="__main__":raise SystemExit(main())
