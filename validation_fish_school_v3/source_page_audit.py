"""Page-aware official Dryad source manifest, no numerical acoustic outcomes.

The base v3 gate wrongly assumed the first page contained every file.
This explicit additive source-only correction preserves the frozen DOI,
file names, size/checksum policy and no-ecology endpoint.
"""
import json
import re
from pathlib import Path
from urllib.parse import urljoin
import dryad_source_gate as base

_original_json=base.json_get
_state={"pages":0,"file_names":[]}

def page_url(href):
    if isinstance(href,dict): href=href.get("href")
    if not isinstance(href,str) or not href: return None
    full=urljoin(base.BASE,href)
    if not full.startswith(base.BASE):raise base.SourceStop("SOURCE_URL_STOP","external pagination URL")
    return full

def get_files_with_pages(url, getter):
    """Use only official HAL next links, maximum 10, dedupe id+name."""
    all_items=[];seen=set();seen_urls=set();current=url
    for _ in range(10):
        if current in seen_urls:
            raise base.SourceStop("SOURCE_SCHEMA_STOP","pagination loops")
        seen_urls.add(current)
        page=getter(current)
        found=base.collection(page,"file")
        for item in found:
            k=json.dumps(item,sort_keys=True)
            if k not in seen:
                all_items.append(item);seen.add(k)
        links=page.get("_links",{})
        nxt=page_url(links.get("next") or links.get("stash:next"))
        if not nxt: break
        current=nxt
    else:
        raise base.SourceStop("SOURCE_SCHEMA_STOP","file metadata >10 pages")
    return all_items,len(seen_urls)

def patched_get(url):
    if re.search(r"/versions/\d+/files$",url):
        files,pages=get_files_with_pages(url,_original_json)
        _state["pages"]=pages
        _state["file_names"]=sorted(base.file_name(x) for x in files)
        return {"_embedded":{"stash:files":files}}
    return _original_json(url)

def enhanced_filename(item):
    return str(item.get("path") or item.get("filename") or item.get("fileName") or
               item.get("name") or item.get("originalFileName") or "").split("/")[-1]

def main():
    base.json_get=patched_get
    base.file_name=enhanced_filename
    result=base.run()
    result["file_metadata_pages"]= _state["pages"]
    result["file_metadata_member_count"]=len(_state["file_names"])
    result["public_source_member_names"]=_state["file_names"]
    result["source_only_pagination_fix"]=True
    p=Path("validation_fish_school_v3/results/ota_original_source_gate.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
                      "reason":result.get("stop_reason"),
                      "files_seen":result["file_metadata_member_count"],
                      "pages":result["file_metadata_pages"]}))

if __name__=="__main__":main()
