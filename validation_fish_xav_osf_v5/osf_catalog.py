"""V5 source-only bounded OSF catalog for Mouy XAV fish audio-video archive.
This does NOT acquire or fit animal audio/video measurements.
"""
from __future__ import annotations
import json
from collections import Counter,deque
from pathlib import Path
from urllib.parse import urlparse
from urllib import request,error
START="https://api.osf.io/v2/nodes/q8dz4/files/osfstorage/"
def api_json(url):
    p=urlparse(url)
    if p.scheme!="https" or p.netloc!="api.osf.io" or not p.path.startswith("/v2/"):
        raise ValueError("OSF API domain stop")
    try:
        req=request.Request(url,headers={"User-Agent":"fish-school-v5-original-OSF-structure/1.0",
                                         "Accept":"application/json"})
        with request.urlopen(req,timeout=25) as resp:
            b=resp.read(2_000_001)
            if len(b)>2_000_000:raise ValueError("OSF JSON too large")
            return json.loads(b)
    except error.HTTPError as exc:raise RuntimeError("HTTP_"+str(exc.code)) from None
    except error.URLError as exc:raise RuntimeError("NETWORK_"+type(exc.reason).__name__) from None
def crawl(fetch=api_json,limit=120):
    todo=deque([START]);seen_urls=set();files=[];folders=[];truncated=False
    while todo:
        url=todo.popleft()
        if url in seen_urls:continue
        if len(seen_urls)>=limit:truncated=True;break
        seen_urls.add(url)
        page=fetch(url);rows=page.get("data",[])
        if not isinstance(rows,list):raise ValueError("OSF data not a list")
        for x in rows:
            meta=x.get("attributes",{}) or {}
            name=str(meta.get("name") or "").split("/")[-1]
            kind=str(meta.get("kind") or "")
            if not name or name in (".",".."):continue
            if kind=="file":
                size=meta.get("size")
                files.append({"name":name,"size_bytes":size,"mime_type":meta.get("content_type"),
                              "id":x.get("id")})
            elif kind=="folder":
                folders.append(name)
                rel=x.get("relationships",{}).get("files",{}).get("links",{}).get("related",{})
                href=rel.get("href") if isinstance(rel,dict) else rel
                if href:todo.append(href)
        nxt=page.get("links",{}).get("next")
        if nxt:todo.append(nxt)
    summary=Counter(Path(x["name"]).suffix.lower() for x in files)
    return {"status":"OSF_FILE_CATALOG_PARTIAL" if truncated else "OSF_FILE_CATALOG_PASS",
            "n_api_pages":len(seen_urls),"n_directories":len(folders),"n_files":len(files),
            "extension_counts":dict(summary),"folder_names":sorted(set(folders)),
            "source_member_names":files[:150],"source_opened":False,
            "biological_correlation_estimated":False}
def main():
    try:out=crawl()
    except (ValueError,RuntimeError,TypeError,KeyError) as exc:
        out={"status":"SOURCE_CATALOG_STOP","reason":str(exc)}
    out["source"]="Mouy 2023 XAV published OSF https://osf.io/q8dz4"
    path=Path("validation_fish_xav_osf_v5/results/osf_file_catalog.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"reason":out.get("reason"),
                      "n_files":out.get("n_files"),"n_pages":out.get("n_api_pages"),
                      "extension_counts":out.get("extension_counts")}))
if __name__=="__main__":main()
