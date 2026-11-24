"""v34e source-only original 2026 PRX author README archives schema, NEVER fish data.

One source-authenticated Figshare->exact CDN hop; only small README members
decompressed after exact official source ZIP provider MD5, size and SHA256.
No original experimental/simulated fish track or model script body read.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, zipfile
from pathlib import Path, PurePosixPath

from validation_fish_school_v34.original_figshare_metadata import (
    original_figshare_record_bytes,decode_author_record,SourceStop)
from validation_fish_school_v34.original_small_source_files import safe_zip_original_members
from validation_fish_school_v34.onehop_figshare_original_files import verified_original_figshare_small_bytes

ORIGINALS={
 31378621:("Figs.zip",1863466,"4514391ae74d0715969159b9eda9c11a",
           "626b8e88e4df6de2ec95fdc0dd1066d1e979a5a199515133d7556a306b4973dd"),
 31386349:("Model code.zip",181872,"4e6cf4d167c6204d4f557ae456ed5ba1",
           "920ad8a9f89d32cfc4ec9adf9a1311185f5700050e419b532f424637cc904111")
}
KEYWORDS={
 "experiment_trajectory_file":r"(?i)\btraj_exp\b",
 "simulation_trajectory_file":r"(?i)\btraj_sim\b",
 "controller_kR1":r"(?i)\bkR?1\b",
 "controller_kR2":r"(?i)\bkR?2\b",
 "controller_kR4":r"(?i)\bkR?4\b",
 "controller_k_V":r"(?i)\bk[_ ]?V\b",
 "original_trial":r"(?i)\b(trial|session|run|recording)\b",
 "biological_subject":r"(?i)\b(subject|animal|individual|fish.?id)\b",
 "real_fish":r"(?i)\b(real fish|real agent|experimental fish)\b",
 "virtual_fish":r"(?i)\b(virtual fish|virtual agent|VR fish)\b",
 "source_column":r"(?i)\b(columns?|colnames?|field|format|header)\b",
 "physical_time":r"(?i)\b(timestamp|frame|fps|frequency|sample rate|sampling|time ?step)\b"
}
MAX_MEMBERS=20
MAX_EACH_BYTES=10000
MAX_TOTAL_BYTES=80000

def inspect_readme(b,source_member):
    if len(b)>MAX_EACH_BYTES or not b:
        raise SourceStop("V34E_AUTHOR_README_MEMBER_BYTES_BOUND_STOP")
    try: txt=b.decode("utf-8-sig"); encoding="utf-8-sig"
    except UnicodeError:
        txt=b.decode("cp1252"); encoding="windows-1252"
    lines=txt.splitlines()
    if not 1<=len(lines)<=200:
        raise SourceStop("V34E_AUTHOR_README_TEXT_TOO_MANY_SOURCE_LINES")
    counts={k:len(re.findall(rx,txt)) for k,rx in KEYWORDS.items()}
    related={k:[i+1 for i,line in enumerate(lines) if re.search(rx,line)][:12] for k,rx in KEYWORDS.items()}
    return {
      "source_readme_zip_member_filename":source_member,
      "original_unmodified_README_bytes_SHA256":hashlib.sha256(b).hexdigest(),
      "original_unmodified_README_source_bytes":len(b),
      "original_readme_encoding":encoding,
      "original_readme_n_lines":len(lines),
      "source_descriptor_term_occurrence_counts_only":counts,
      "source_descriptor_term_line_numbers_first_12_only":related,
      "original_source_readme_full_text_redistributed":False,
      "original_source_numerical_figure_or_trajectory_member_read":False
    }

def one_zip_readmes(data,article):
    directory=safe_zip_original_members(data)
    selected=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            original=PurePosixPath(info.filename.replace("\\","/"))
            isreadme=original.name.lower()=="readme.txt"
            if article==31386349:
                isreadme=info.filename in ("Model code/Readme.txt",
                                          "Model code/Parameters/README STEPHANE.txt")
            if isreadme and not info.is_dir():
                if info.file_size>MAX_EACH_BYTES or info.flag_bits & 1:
                    raise SourceStop("V34E_ORIGINAL_README_MEMBER_TOO_LARGE_OR_ENCRYPTED")
                selected.append(info)
        if not 1<=len(selected)<=MAX_MEMBERS or sum(m.file_size for m in selected)>MAX_TOTAL_BYTES:
            raise SourceStop("V34E_ORIGINAL_README_MEMBER_COUNT_OR_TOTAL_STOP")
        observed=[]
        for info in selected:
            with z.open(info,"r") as reader:
                b=reader.read(MAX_EACH_BYTES+1)
            if len(b)!=info.file_size:
                raise SourceStop("V34E_README_UNCOMPRESSED_BYTES_OR_CRC_MISMATCH")
            observed.append(inspect_readme(b,info.filename))
    return {
       "original_total_zip_entries":directory["original_archive_entries"],
       "original_total_verified_README_only_members":len(observed),
       "source_README_member_descriptors_only":observed,
       "original_non_README_data_or_code_member_contents_read":False,
       "original_trajectory_exp_sim_and_figure_data_member_contents_read":False
    }

def run(fetchmeta=original_figshare_record_bytes,fetch_original=verified_original_figshare_small_bytes):
    out={"status":"SOURCE_TRIAL_INTERVENTION_IDENTITY_NOT_ADMITTED",
         "original_source_frozen_before_member_extraction":"docs/V34E_SOURCE_ONLY_PRX_ARCHIVED_README_TRAJECTORY_TRIAL_DICTIONARY_FREEZE.md",
         "original_fish_trajectory_member_bodies_loaded":False,
         "original_simulated_trajectory_member_bodies_loaded":False,
         "real_fish_trial_or_virtual_controller_treatment_outcomes_fitted":False,
         "same_experimental_subject_session_source_IDs_verified":False,
         "original_fish_origin_acoustic_calls_identified":False,
         "source_original_2026_PRX_author_ZIP_README_metadata":[]}
    admitted=0
    for article,(name,size,md5,sha) in ORIGINALS.items():
        rec={"original_figshare_article_id":article,"original_author_ZIP_filename":name,
             "status":"SOURCE_ACCESS_STOP"}
        try:
            data=decode_author_record(fetchmeta(article),article)
            files={f["original_filename"]:f for f in data["original_provider_file_manifest"]}
            f=files.get(name)
            if (not f or f["original_source_file_bytes"]!=size or
                f["original_provider_supplied_MD5"]!=md5 or
                f["original_provider_computed_MD5"]!=md5):
                raise SourceStop("V34E_AUTHOR_OFFICIAL_SOURCE_MANIFEST_MD5_SIZE_DRIFT")
            body=fetch_original(f["original_file_download_url_PROVIDER_UNMODIFIED_NOT_ACCESSED"],size,md5)
            if len(body)!=size or hashlib.sha256(body).hexdigest()!=sha or hashlib.md5(body).hexdigest()!=md5:
                raise SourceStop("V34E_AUTHOR_ORIGINAL_ZIP_SHA256_OR_MD5_MISMATCH")
            rec.update(one_zip_readmes(body,article))
            rec["original_source_provider_MD5_pass"]=True
            rec["original_source_recomputed_SHA256"]=sha
            rec["status"]="AUTHOR_ORIGINAL_PRX_ZIP_README_SCHEMA_VERIFIED"
            admitted+=1
        except (SourceStop,KeyError,ValueError,UnicodeError,zipfile.BadZipFile) as e:
            rec["source_stop_reason"]=str(e)
        out["source_original_2026_PRX_author_ZIP_README_metadata"].append(rec)
    out["n_provider_verified_author_ZIP_README_source_records"]=admitted
    # Metadata alone does NOT assert 4-way trial/animal/k/clock source join.
    out["status"]=("SOURCE_TRIAL_INTERVENTION_IDENTITY_NOT_ADMITTED" if admitted==2
       else "PARTIAL_ORIGINAL_README_SOURCE_ACCESS_STOP" if admitted==1
       else "SOURCE_ACCESS_STOP")
    out["future_trial_group_causal_source_gate"]={
        "trial_level_k_values_with_recording_ID":"NOT_VERIFIED",
        "independent_biological_fish_or_session_ID":"NOT_VERIFIED",
        "source_physical_clock_fps":"NOT_VERIFIED",
        "real_vs_virtual_agent_track_mapping":"NOT_VERIFIED"
    }
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
