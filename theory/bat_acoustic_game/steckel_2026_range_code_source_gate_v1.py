"""Author-only 2026 bat 3D ERTF code gate via safe ZIP member HTTP ranges.

Reads source CODE, README, experiment index and checksums; does NOT read
original saved performance metrics or bat-like virtual trajectories.
Does not fetch or redistribute 988MB outer archive, author model weights,
3rd-party HRTF, training outcomes or original paper figures.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,io,json,re,struct,urllib.request,zipfile,zlib
from external_2026_EEG_and_3D_ERTF_source_gate_v1 import (
    ZENODO,ZIP_NAME,fetch,MAX_TAIL,TAIL_BYTES,MAX_CENTRAL,
    eocd_info,central_zip_names
)

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"STECKEL_2026_3D_RANGE_SOURCE_CODE_PREOUTPUT_2026_11_08.md"
OUT=ROOT/"STECKEL_2026_3D_ORIGINAL_CODE_SOURCE_GATE_V1.json"
ADMITTED={
    "README.md":100000,
    "experiments.json":250000,
    "MANIFEST.sha256":100000,
    "code.zip":15*1024*1024
}
MAX_CODE_UNCOMPRESSED=20*1024*1024

def sha(data):
    return hashlib.sha256(data).hexdigest()

def official_outer_catalog():
    original=json.loads(fetch(ZENODO,maxbytes=300000)[1])
    files=[x for x in original.get("files",[]) if x.get("key")==ZIP_NAME]
    if len(files)!=1:raise ValueError("STOP_NONUNIQUE_SOURCE_OUTER")
    entry=files[0]
    url=(entry.get("links") or {}).get("self") or (entry.get("links") or {}).get("content")
    if not url:raise ValueError("STOP_ORIGINAL_PROVIDER_FILE_URL_MISSING")
    size=int(entry["size"])
    h,tail=fetch(url,range_header=f"bytes=-{TAIL_BYTES}",maxbytes=MAX_TAIL)
    if h["http"]!=206:raise ValueError("STOP_ORIGINAL_SOURCE_RANGE_UNAVAILABLE")
    info=eocd_info(tail,size)
    start=info["directory_offset"];stop=start+info["directory_size"]-1
    h,data=fetch(url,range_header=f"bytes={start}-{stop}",maxbytes=MAX_CENTRAL)
    if h["http"]!=206:raise ValueError("STOP_CENTRAL_DIR_NOT_RANGE")
    outer=central_zip_names(data)
    if len(outer)!=info["member_count"]:raise ValueError("STOP_SOURCE_ZIP_MEMBER_COUNT")
    return url,size,entry.get("checksum"),outer

def extract_single_member(url,rec,cap):
    """Read exactly source original compressed member and verify CRC/sha.

    ZIP member header & payload are ORIGINAL provider HTTP206 Range reads;
    zipfile entries are NEVER created or uploaded in our output artifact.
    """
    size=int(rec["compressed_bytes"])
    if size<0 or size>cap:raise ValueError("STOP_ORIGINAL_ZIP_MEMBER_OVER_CAP")
    offset=int(rec["local_header_byte_offset"])
    h,header=fetch(url,range_header=f"bytes={offset}-{offset+29}",maxbytes=30)
    if h["http"]!=206 or len(header)!=30 or header[:4]!=b"PK\x03\x04":
        raise ValueError("STOP_ORIGINAL_LOCAL_ZIP_HEADER_INVALID")
    fields=struct.unpack_from("<IHHHHHIIIHH",header,0)
    flag=fields[2];method=fields[3];nlen=fields[-2];xlen=fields[-1]
    if flag&1:raise ValueError("STOP_ENCRYPTED_SOURCE_MEMBER")
    start=offset+30+nlen+xlen
    h,data=fetch(url,range_header=f"bytes={start}-{start+size-1}",maxbytes=cap)
    if h["http"]!=206 or len(data)!=size:raise ValueError("STOP_SOURCE_MEMBER_DOWNLOAD_RANGE_LENGTH")
    if method==0:raw=data
    elif method==8:raw=zlib.decompress(data,-15)
    else:raise ValueError("STOP_SOURCE_ZIP_MEMBER_UNSUPPORTED_COMPRESSION")
    if len(raw)!=rec["uncompressed_bytes"]:raise ValueError("STOP_SOURCE_UNCOMPRESSED_LENGTH")
    crc=zlib.crc32(raw)&0xffffffff
    if f"{crc:08x}"!=rec["crc32"]:raise ValueError("STOP_SOURCE_MEMBER_CRC")
    return raw,{"path":rec["path"],"compression_method":method,"original_compressed_bytes":size,
                "original_uncompressed_bytes":len(raw),"member_sha256":sha(raw),
                "source_original_CRC32":rec["crc32"]}

def inspect_author_code(original_codezip):
    out={}
    if len(original_codezip)>MAX_CODE_UNCOMPRESSED:raise ValueError("STOP_CODE_ZIP_TOO_LARGE")
    with zipfile.ZipFile(io.BytesIO(original_codezip)) as z:
        members=[{"path":i.filename,"original_size":i.file_size}
                 for i in z.infolist() if not i.is_dir()]
        out["code_zip_member_count"]=len(members)
        out["code_zip_members"]=members[:250]
        out["code_zip_manifest_truncated"]=len(members)>250
        out["python_bat3d_source_paths"]=[x["path"] for x in members if "/bat3d/" in "/"+x["path"]]
        out["source_test_paths"]=[x["path"] for x in members if re.search(r"(?:^|/)test[^/]*\.py$",x["path"],re.I)]
        out["source_requirements_paths"]=[x["path"] for x in members if x["path"].split("/")[-1] in
           ("requirements.txt","pyproject.toml","setup.py","environment.yml","README.md")]
        out["original_code_files_read_for_metadata"]=[]
        for entry in out["source_requirements_paths"]:
            info=z.getinfo(entry)
            if info.file_size>100000:continue
            raw=z.read(info)
            doc=raw.decode("utf-8","replace")
            out["original_code_files_read_for_metadata"].append({
                 "path":entry,"bytes":len(raw),"sha256":sha(raw),
                 "package_requirement_names":sorted(set(re.findall(
                    r"(?im)^\s*(?:torch|numpy|scipy|matplotlib|pandas|pytest|soundfile|librosa|torchaudio|pydantic|h5py|tqdm|einops|tensorboard|pyyaml|scikit-learn|numba)\b",doc)))})
    return out

def inspect_experiment_manifest(raw):
    doc=json.loads(raw)
    result={"json_type":type(doc).__name__,"experiment_keys":[],"mapping_item_count":0}
    if isinstance(doc,dict):
        result["experiment_keys"]=list(doc)[:100]
        result["mapping_item_count"]=len(doc)
        experiment_ids=[]
        for key,val in doc.items():
            if re.fullmatch(r"[EC]\d+",key):experiment_ids.append(key)
            elif isinstance(val,dict):
                experiment_ids.extend(z for z in val if re.fullmatch(r"[EC]\d+",z))
        result["source_declared_experiment_IDs"]=sorted(set(experiment_ids))
        # Avoid exporting original training metrics embedded in an unexpected
        # manifest. No numerical original model metrics are read from nested values.
    elif isinstance(doc,list):
        result["mapping_item_count"]=len(doc)
        result["source_declared_experiment_IDs"]=[]
    return result

def main():
    result={"schema":1,"date":"2026-11-08","status":"NOT_CHECKED",
            "source_doi":"10.5281/zenodo.23537553",
            "source_article_doi":"10.64898/2026.10.22.760884",
            "original_2026_code_executed":False,
            "original_simulated_3D_accuracy_values_opened":False,
            "original_model_checkpoint_or_3D_echoes_opened":False,
            "no_new_animal_measurements":True,
            "original_author_files_rehosted":False,
            "original_archive_read_whole":False,
            "admitted_sources":{}}
    try:
        if not CONTRACT.exists():raise ValueError("STOP_MISSING_FROZEN_SOURCE_CODE_PREOUTPUT")
        url,fullsize,checksum,members=official_outer_catalog()
        result["source_outer_size"]=fullsize
        result["source_outer_checksum"]=checksum
        result["source_original_members"]=len(members)
        originals={x["path"]:x for x in members}
        if any(name not in originals for name in ADMITTED):raise ValueError("STOP_MISSING_CODE_OR_ORIGINAL_SCHEMAS")
        opened={}
        for path,cap in ADMITTED.items():
            raw,receipt=extract_single_member(url,originals[path],cap)
            opened[path]=raw
            result["admitted_sources"][path]=receipt
            print("ORIGINAL_AUTHOR_SOURCE_CODE_MEMBER",path,receipt["member_sha256"],receipt["original_uncompressed_bytes"])
        result["original_code_structure"]=inspect_author_code(opened["code.zip"])
        result["original_experiment_index_structure"]=inspect_experiment_manifest(opened["experiments.json"])
        result["original_authored_readme_text_sha256"]=sha(opened["README.md"])
        result["original_manifest_sha256"]=sha(opened["MANIFEST.sha256"])
        result["status"]="PASS_EXACT_ORIGINAL_3D_AUTHOR_CODE_AND_EXPERIMENT_INDEX_ONLY"
    except Exception as e:
        result["status"]="STOP_AUTHOR_3D_CODE_RANGE_OR_SCHEMA"
        result["error"]=type(e).__name__+":"+str(e)[:250]
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("BAT3D_ORIGINAL_SOURCE_GATE",result["status"])
    if result["status"].startswith("STOP"):print("SOURCE_STOP_REASON",result.get("error"))
    else:
        s=result["original_code_structure"]
        print("SOURCE_CODE_ARCHITECTURE",json.dumps({
            "source_files":s["code_zip_member_count"],
            "python_modules":len(s["python_bat3d_source_paths"]),
            "source_tests":s["source_test_paths"][:50],
            "requirements":s["source_requirements_paths"],
            "code_member_keys":s["code_zip_members"][:55],
            "experiment_index_structure":result["original_experiment_index_structure"]},sort_keys=True)[:18000])
    return 0

if __name__=="__main__":raise SystemExit(main())
