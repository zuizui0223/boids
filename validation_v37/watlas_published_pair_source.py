"""v37 published seven-red-knot WATLAS Figshare source and heading preflight.

Only source observability. NOT social field effect or multi-tide replication.
Published selected single 2018-08-31 tide can never satisfy ≥4 cycle gate.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

API="https://api.figshare.com/v2/articles/26553440"
DOI="https://doi.org/10.6084/m9.figshare.26553440.v1"
MAX_BYTES=60_000_000
NEEDED={"TAG","TIME","X","Y","NBS","VARX","VARY","COVXY"}

def get_bytes(url,max_size):
    if not url.startswith("https://"):
        raise ValueError("Only https published figshare original URL")
    with urlopen(Request(url,headers={"User-Agent":"Boids-WATLAS-Source-Gate/1.0"}),
                 timeout=90) as source:
        payload=source.read(max_size+1)
    if len(payload)>max_size:raise ValueError("Original source exceeds fixed cap")
    return payload

def published_csv():
    article=json.loads(get_bytes(API,2_000_000))
    if article.get("id")!=26553440:
        raise ValueError("Figshare API response mismatch")
    files=article.get("files") or []
    csv_items=[f for f in files if str(f.get("name","")).lower().endswith(".csv") and not f.get("is_link_only")]
    if len(csv_items)!=1:
        raise ValueError("Expected exactly one original WATLAS supplementary CSV")
    meta=csv_items[0]
    url=meta.get("download_url")
    if not url or not url.startswith("https://"):
        raise ValueError("Missing authorized published download_url")
    content=get_bytes(url,MAX_BYTES)
    sha=hashlib.sha256(content).hexdigest()
    md5=hashlib.md5(content).hexdigest()
    provider_md5=meta.get("computed_md5") or meta.get("supplied_md5")
    if provider_md5 and md5.lower()!=str(provider_md5).lower():
        raise ValueError("Provider original Figshare MD5 mismatch")
    if meta.get("size") is not None and len(content)!=meta["size"]:
        raise ValueError("Downloaded original Figshare byte length mismatch")
    audit={"source":DOI,"figshare_article_id":26553440,
           "original_filename":meta["name"],"original_bytes":len(content),
           "original_sha256":sha,"original_download_md5":md5,
           "provider_md5_published":bool(provider_md5),
           "provider_md5_match":bool(provider_md5),
           "provider_size_match":meta.get("size")==len(content)}
    return content,audit

def heading(before,after):
    d=after[0]-before[0]
    if not 30<=d<=90:return None
    dx=after[1]-before[1];dy=after[2]-before[2]
    dist=math.hypot(dx,dy)
    if not(.2<=dist/d<=30.):return None
    return (dx/dist,dy/dist)

def source_observability(raw):
    if not isinstance(raw,bytes):raise TypeError("Original CSV must be source bytes")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not NEEDED<=set(reader.fieldnames or []):
        raise ValueError("Unexpected Figshare data schema; required high-frequency source columns absent")
    nraw=0;nqc=0;failed=Counter()
    bins=defaultdict(list);alltags=set();time_extrema=[float("inf"),float("-inf")]
    for row in reader:
        nraw+=1
        ident=(row.get("TAG") or "").strip()
        try:
            tt=float(row["TIME"])
            x=float(row["X"]);y=float(row["Y"])
            nbs=float(row["NBS"])
            varx=float(row["VARX"]);vary=float(row["VARY"])
            covxy=float(row["COVXY"])
        except (ValueError,TypeError):
            failed["invalid_numeric"]+=1;continue
        if not ident or not all(math.isfinite(a) for a in (tt,x,y,nbs,varx,vary,covxy)):
            failed["missing_or_nonfinite"]+=1;continue
        alltags.add(ident)
        if not(1_500_000_000<tt<1_600_000_000):
            failed["outside_published_2018_time_range"]+=1;continue
        if nbs<3 or not(0<=varx<=5000 and 0<=vary<=5000):
            failed["low_quality_nbs_or_variance"]+=1;continue
        if not(100000<=x<=900000 and 4_000_000<=y<=7_000_000):
            failed["invalid_utm31_metre_coordinate"]+=1;continue
        time_extrema[0]=min(time_extrema[0],tt)
        time_extrema[1]=max(time_extrema[1],tt)
        bins[(ident,int(tt//30))].append((x,y))
        nqc+=1
    if nraw==0:raise ValueError("Original figshare CSV empty")
    trajectories=defaultdict(list)
    for (bird,bucket),values in bins.items():
        trajectories[bird].append((bucket*30,
                                   sum(v[0] for v in values)/len(values),
                                   sum(v[1] for v in values)/len(values)))
    obs=[]
    for bird,triples in trajectories.items():
        triples.sort()
        for i,fix in enumerate(triples):
            prev=heading(triples[i-1],fix) if i else None
            nxt=heading(fix,triples[i+1]) if i+1<len(triples) else None
            obs.append((fix[0],fix[1],fix[2],bird,prev,nxt))
    obs.sort()
    from collections import deque
    waiting=defaultdict(list)
    raw_pairs=0;qualified=0;dyads=set();pair_bins=set()
    participated=set()
    for stamp,x,y,bird,past,nxt in obs:
        for other in waiting[stamp]:
            _,xo,yo,otherbird,otherpast,othernxt=other
            if bird==otherbird:continue
            if math.hypot(x-xo,y-yo)>50:continue
            raw_pairs+=1
            count=int(past is not None and nxt is not None and otherpast is not None)
            count+=int(otherpast is not None and othernxt is not None and past is not None)
            if count:
                qualified+=count
                dyad=tuple(sorted((bird,otherbird)))
                dyads.add(dyad)
                pair_bins.add((stamp,dyad))
                participated.update(dyad)
        waiting[stamp].append((stamp,x,y,bird,past,nxt))
    if math.isfinite(time_extrema[0]):
        first=datetime.fromtimestamp(time_extrema[0],timezone.utc).date().isoformat()
        last=datetime.fromtimestamp(time_extrema[1],timezone.utc).date().isoformat()
        timespan=time_extrema[1]-time_extrema[0]
    else:
        first=last=None;timespan=0
    within_tide=(len(participated)>=5 and len(dyads)>=5 and qualified>=200)
    return {"published_nonrandom_selected_tides":1,
            "number_original_source_rows":nraw,"source_unique_tag_count":len(alltags),
            "admitted_quality_controlled_source_rows":nqc,
            "admitted_unique_30_second_tag_bins":len(obs),
            "quality_rejected":dict(failed),
            "UTC_day_range":[first,last],"source_span_seconds":timespan,
            "different_tag_near_pair_30sec_bin_within_50m":raw_pairs,
            "qualifying_directed_prior_heading_and_future_outcome_pairs":qualified,
            "unique_qualifying_tags":len(participated),
            "unique_qualifying_dyads":len(dyads),
            "unique_qualifying_dyad_bins":len(pair_bins),
            "within_tide_exploratory_source_eligible":within_tide,
            "independent_multitide_social_force_admission":"NOT_ADMITTED_ONE_PUBLISHED_NONRANDOM_TIDE",
            "biological_social_force_or_tide_effect":"NOT_ESTIMATED",
            "original_tag_clock":"UNIX_SECONDS_FROM_PUBLISHER",
            "location_variance_source":"VARX_VARY_original_squared_metres"}

def run(output):
    raw,receipt=published_csv()
    quality=source_observability(raw)
    result={"source_metadata":receipt,"field_source_feasibility":quality,
            "status":"ORIGINAL_PUBLISHED_WATLAS_SOURCE_ONLY"}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
