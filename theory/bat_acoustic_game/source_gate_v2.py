"""Read-only external source preflight. Never executes/rehosts original code.
Only JSON receipt/log are collected in this workflow. No biological observations created.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "source_gate_v2_receipt.json"
ARCHIVE_URL = "https://cdn.elifesciences.org/articles/55539/elife-55539-code1-v2.rar"
FIGSHARE_API = "https://api.figshare.com/v2/articles/30937379"
MAX_BYTES = 64 * 1024 * 1024
HEADERS = {"User-Agent": "bat-literature-source-audit/1.0 (scientific source verification)"}


def get_bytes(url: str, limit: int = MAX_BYTES):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=65) as response:
        chunks = []
        total = 0
        while True:
            block = response.read(min(256 * 1024, limit + 1 - total))
            if not block:
                return b"".join(chunks), response.status
            total += len(block)
            if total > limit:
                raise ValueError("SIZE_LIMIT_EXCEEDED")
            chunks.append(block)


def check_figshare():
    rec = {"doi": "10.6084/m9.figshare.30937379", "api": FIGSHARE_API,
           "status": "NOT_CHECKED"}
    try:
        data, status = get_bytes(FIGSHARE_API, limit=2*1024*1024)
        x = json.loads(data.decode("utf-8"))
        files = x.get("files", [])
        if not isinstance(files, list):
            raise ValueError("FILES_NOT_LIST")
        rec.update(status="METADATA_AVAILABLE", http_status=status,
                   title=x.get("title"), published_date=x.get("published_date"),
                   version=x.get("version"),
                   license=x.get("license", {}).get("name") if isinstance(x.get("license"), dict) else None,
                   files=[{"name": f.get("name"), "size": f.get("size"),
                           "id": f.get("id"), "download_url": f.get("download_url")}
                          for f in files],
                   file_count=len(files))
    except Exception as e:
        rec.update(status="STOP_SOURCE_ACCESS_OR_SCHEMA", error=f"{type(e).__name__}:{str(e)[:200]}")
    return rec


def check_elife():
    rec = {"doi": "10.7554/eLife.55539", "source_url": ARCHIVE_URL,
           "status": "NOT_CHECKED"}
    try:
        data, status = get_bytes(ARCHIVE_URL)
        rec.update(status="DOWNLOADED_FOR_TEMPORARY_INSPECTION",
                   http_status=status, bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest(),
                   magic_header=data[:12].hex())
        if data.startswith(b"Rar!"):
            rec["file_type"] = "RAR"
        elif data.startswith(b"PK\x03\x04"):
            rec["file_type"] = "ZIP"
        else:
            rec["file_type"] = "OTHER_NOT_IDENTIFIED"
        # Access the archive transiently, list entries only; do not unrar or execute.
        if data.startswith(b"Rar!") and shutil.which("7z"):
            archive = Path(os.environ.get("RUNNER_TEMP","/tmp")) / "bat-source-rar-temp.rar"
            try:
                archive.write_bytes(data)
                listing = subprocess.run(["7z", "l", "-slt", str(archive)],
                                         capture_output=True,text=True,timeout=40)
                entries = [line.split(" = ",1)[1] for line in listing.stdout.splitlines()
                           if line.startswith("Path = ")][1:]
                rec["archive_entry_count"] = len(entries)
                rec["archive_entries"] = [p for p in entries if p and not p.startswith("..")][:300]
                rec["listing_status"] = "OK" if listing.returncode==0 else "STOP_LISTING_FAILED"
                if listing.returncode:
                    rec["listing_error"] = listing.stderr[-350:]
            finally:
                if archive.exists(): archive.unlink()
        else:
            rec["listing_status"] = "STOP_LISTING_TOOL_OR_MAGIC_UNAVAILABLE"
    except Exception as e:
        rec.update(status="STOP_SOURCE_ACCESS_OR_SIZE",error=f"{type(e).__name__}:{str(e)[:220]}")
    return rec


def main():
    obj = {"schema":2,"programme":"bat-sonar-no-new-measurements",
           "source_only": True, "raw_biological_outcomes_opened":False,
           "no_original_source_files_persisted":True,
           "elife_2020":check_elife(),"figshare_2026":check_figshare()}
    OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    for k in ("elife_2020","figshare_2026"):
        x=obj[k]
        print(f"{k} STATUS={x['status']} files={x.get('file_count',x.get('archive_entry_count','NA'))} bytes={x.get('bytes','NA')} sha256={x.get('sha256','NA')}")
        if x.get("archive_entries"):
            print("eLife RAR entries:",json.dumps(x["archive_entries"][:100]))
        if x.get("files"):
            print("2026 figshare file names / sizes:",json.dumps([(a["name"],a["size"]) for a in x["files"]]))
        if x.get("error"):
            print("STOP_REASON:",x["error"])
    print("SOURCE_GATE_JSON="+str(OUT))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
