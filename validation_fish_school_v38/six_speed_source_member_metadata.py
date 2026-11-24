"""v38b only original Royal Society 2026 six-speed VR supplement FIGSHARE
article FILE METADATA. No original PDF/movie/animal data file bytes downloaded.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from validation_fish_school_v38.source_vr_collection_gate import (
   author_json,decode_json_bytes,author_article_manifest,SourceStop
)
SOURCE_ARTICLES={
    "LOW_SPEED_S1_ORIGINAL_MOVIE":32323963,
    "SIX_SPEED_ORIGINAL_ELECTRONIC_SUPPLEMENT":32323960,
    "HIGH_SPEED_S2_ORIGINAL_MOVIE":32323957
}
FREEZE="docs/V38B_SIX_SPEED_ORIGINAL_COLLECTION_MEMBER_FILE_MANIFEST_FREEZE.md"

def run(fetch=author_json):
    out={
      "status":"SOURCE_METADATA_STOP",
      "frozen_before_six_speed_supplementary_file_metadata":FREEZE,
      "original_six_speed_paper_DOI":"10.1098/rspb.2026.0146",
      "original_author_collection_DOI":"10.6084/m9.figshare.c.8485282.v1",
      "source_article_IDs":SOURCE_ARTICLES,
      "original_movie_or_PDF_source_bytes_downloaded":False,
      "original_experimental_fish_trajectory_rows_loaded":False,
      "original_speed_condition_animal_effects_reanalyzed":False,
      "source_2026_experiment_subject_trial_IDs_admitted":False,
      "source_member_file_manifests":{}
    }
    n=0
    for key,id in SOURCE_ARTICLES.items():
        rec={"status":"SOURCE_METADATA_STOP","original_published_figshare_article_ID":id}
        try:
            url=f"https://api.figshare.com/v2/articles/{id}"
            body=fetch(url)
            x=author_article_manifest(decode_json_bytes(body),id)
            rec.update(x)
            rec["source_original_Figshare_metadata_response_SHA256"]=hashlib.sha256(body).hexdigest()
            n+=1
        except (SourceStop,KeyError,ValueError,UnicodeError) as ex:
            rec["source_error"]=str(ex)
        out["source_member_file_manifests"][key]=rec
    out["n_original_source_article_file_manifests_verified"]=n
    out["status"]=("ORIGINAL_THREE_FIGSHARE_SOURCE_ARTICLE_FILE_MANIFESTS_VERIFIED" if n==3
             else "PARTIAL_ORIGINAL_2026_SIX_SPEED_SOURCE_METADATA_STOP" if n>0
             else "SOURCE_METADATA_STOP")
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    r=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
