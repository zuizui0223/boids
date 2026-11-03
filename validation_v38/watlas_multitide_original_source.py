"""v38 original source-only WATLAS red-knot Figshare repeated tideID gate.

No fitted social responses. Published original HOME-RANGE file may be too sparse
for social experiments: source failure/insufficiency is a hard STOP.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from watlas_published_pair_source import get_bytes,heading

ARTICLE_ID=26553446
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
DOI="https://doi.org/10.6084/m9.figshare.26553446.v1"
CAP=150_000_000
NEEDED={"TAG","TIME","X","Y","NBS","VARX","VARY","COVXY",
        "tideID","tidaltime","waterlevel"}

def original_source():
    meta=json.loads(get_bytes(API,2_000_000))
    if meta.get("id")!=ARTICLE_ID:
        raise ValueError("Unexpected original Figshare article identity")
    candidates=[f for f in meta.get("files",[]) if str(f.get("name","")).lower().endswith(".csv") and not f.get("is_link_only")]
    if len(candidates)!=1:
        raise ValueError("Expected exactly one original supplement 14 CSV")
    file=candidates[0]
    raw=get_bytes(file["download_url"],CAP)
    expected=file.get("computed_md5") or file.get("supplied_md5")
    calculated_md5=hashlib.md5(raw).hexdigest()
    if expected and calculated_md5.lower()!=str(expected).lower():
        raise ValueError("Original Figshare provider MD5 fails")
    if file.get("size") is not None and len(raw)!=int(file["size"]):
        raise ValueError("Original size differs from provider file metadata")
    return raw,{"source":DOI,"article_id":ARTICLE_ID,
                "original_filename":file.get("name"),
                "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                "provider_md5_available":bool(expected),
                "provider_md5_matched":bool(expected),
                "original_provider_bytes_matched":file.get("size")==len(raw)}

def source_quality(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not NEEDED<=set(reader.fieldnames or []):
        raise ValueError("Original WATLAS supplement 14 field dictionary changed")
    raw_count=0;qc=0;drop=Counter();all_tags=set();all_tides=set()
    original_tides=defaultdict(list)
    for row in reader:
        raw_count+=1
        bird=(row.get("TAG") or "").strip()
        tide=(row.get("tideID") or "").strip()
        try:
            time=float(row["TIME"]);x=float(row["X"]);y=float(row["Y"])
            nbs=float(row["NBS"])
            varx=float(row["VARX"]);vary=float(row["VARY"]);cov=float(row["COVXY"])
        except (ValueError,TypeError):
            drop["bad_original_numeric"]+=1;continue
        if not bird or not all(map(math.isfinite,(time,x,y,nbs,varx,vary,cov))):
            drop["source_missing_or_nonfinite"]+=1;continue
        all_tags.add(bird)
        if not(1_480_000_000<time<1_700_000_000):
            drop["outside_source_2017_2023_unix"]+=1;continue
        if not(3<=nbs and 0<=varx<=5000 and 0<=vary<=5000):
            drop["source_uncertainty_gate"]+=1;continue
        if not(100000<=x<=900000 and 4_000_000<=y<=7_000_000):
            drop["source_utm31_bounds"]+=1;continue
        if tide:all_tides.add(tide)
        original_tides[(bird,int(time//30))].append((x,y,tide))
        qc+=1
    if not raw_count:raise ValueError("Empty original original published home range source")
    tracks=defaultdict(list);tides_in_bins=set()
    for (bird,bucket),pts in original_tides.items():
        candidates={v[2] for v in pts}
        clean_tide=next(iter(candidates)) if len(candidates)==1 and "" not in candidates else None
        if clean_tide:tides_in_bins.add(clean_tide)
        tracks[bird].append((bucket*30,
                             sum(a for a,_,_ in pts)/len(pts),
                             sum(b for _,b,_ in pts)/len(pts),
                             clean_tide))
    flat=[]
    for bird,trace in tracks.items():
        trace.sort()
        for i,(time,x,y,tide) in enumerate(trace):
            a=(time,x,y)
            past=heading(trace[i-1][:3],a) if i else None
            future=heading(a,trace[i+1][:3]) if i+1<len(trace) else None
            flat.append((time,x,y,tide,bird,past,future))
    flat.sort()
    same_bin=defaultdict(list)
    totalnear=0;qualified=0;participants=set();dyads=set()
    bycycle=defaultdict(lambda:{"pairs":0,"dyads":set()})
    for stamp,x,y,tide,bird,past,future in flat:
        for other in same_bin[stamp]:
            _,xo,yo,ot,otherbird,otherpast,otherfuture=other
            if otherbird==bird or math.hypot(x-xo,y-yo)>50:continue
            totalnear+=1
            if not tide or tide!=ot:continue
            this=int(past is not None and otherpast is not None and future is not None)
            this+=int(otherpast is not None and past is not None and otherfuture is not None)
            if this:
                qualified+=this
                pair=tuple(sorted([bird,otherbird]))
                participants.update(pair);dyads.add(pair)
                bycycle[tide]["pairs"]+=this
                bycycle[tide]["dyads"].add(pair)
        same_bin[stamp].append((stamp,x,y,tide,bird,past,future))
    qualifying_cycles=sum(v["pairs"]>=10 and len(v["dyads"])>=2 for v in bycycle.values())
    eligible=(qualified>=200 and len(participants)>=5 and len(dyads)>=5 and
              qualifying_cycles>=4)
    return {"status":"SOURCE_FEASIBLE_FOR_PRE_REGISTERING_MULTITIDE_FORECAST" if eligible else "NOT_ADMITTED_MULTITIDE_SOCIAL",
            "original_rows":raw_count,"quality_admitted_rows":qc,
            "original_unique_tags":len(all_tags),"original_unique_tideID":len(all_tides),
            "unique_tideID_after_30s_binning":len(tides_in_bins),
            "unique_tag_30s_position_bins":len(flat),
            "source_quality_drops":dict(drop),
            "near_tag_position_pairs_30s_50m":totalnear,
            "directed_prior_headings_and_future_target_eligible":qualified,
            "contributing_tags":len(participants),"contributing_dyads":len(dyads),
            "tide_cycles_with_any_eligible_pairs":len(bycycle),
            "tide_cycles_meeting_10pairs_2dyads":qualifying_cycles,
            "minimum_required_tide_cycles":4,
            "source_waterlevel":"WesterTerschelling_cm_datum_UNVERIFIED",
            "biological_social_cohesion_or_alignment_effect":"NOT_ESTIMATED"}

def run(path):
    raw,manifest=original_source()
    counts=source_quality(raw)
    result={"analysis":"V38_WATLAS_REPEATED_TIDE_ORIGINAL_SOURCE_ONLY",
            "source_manifest":manifest,"source_admission":counts}
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
