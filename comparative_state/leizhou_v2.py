"""Reproducible *independent* Leizhou shorebird GPS×static-habitat test.

Never interpret these step-length-matched rotations as true dynamic state-portfolio
exhaustion or biological ability to move through inaccessible places.
Original public CC0 Dryad source is accessed at runtime, not redistributed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DOI = "10.5061/dryad.51c59zwm3"
API_URL = "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.51c59zwm3/download"
FOCAL = {"CORE": "Tringa totanus", "GRPL": "Pluvialis squatarola", "GSPL": "Charadrius leschenaultii", "REKN": "Calidris canutus"}
MAX_NETWORK = 20_000_000
MAX_UNCOMPRESSED = 100_000_000
RADII = (500.0, 1500.0)
ANGLES = 32
R_EARTH = 6_371_000.0
SEED = 20261115


def sha(b):
    return hashlib.sha256(b).hexdigest()


def secure_zip(blob, *, name="archive"):
    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as exc:
        raise ValueError(f"SOURCE_STOP: {name} not ZIP") from exc
    names = [a.filename for a in archive.infolist() if not a.is_dir()]
    if len(set(names)) != len(names) or sum(i.file_size for i in archive.infolist()) > MAX_UNCOMPRESSED:
        raise ValueError("SOURCE_STOP: duplicate paths or excessive decompressed size")
    if any(i.file_size > MAX_UNCOMPRESSED or re.search(r"(^/|(^|/)\.\.(/|$)|\\)", i.filename) for i in archive.infolist()):
        raise ValueError("SOURCE_STOP: unsafe archive member")
    return archive


def _download_limited(url, *, accept="application/zip,application/octet-stream,*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research data reuse; citation in repository)", "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as res:
        payload = res.read(MAX_NETWORK + 1)
        if len(payload) > MAX_NETWORK:
            raise ValueError("SOURCE_STOP: original download exceeds size bound")
        return payload, res.geturl()


def _api_json(url):
    blob, _ = _download_limited(url, accept="application/json")
    return json.loads(blob)


def _select_dryad_file_metadata():
    """Anonymous metadata only; do not inspect GPS values before protocol."""
    base="https://datadryad.org/api/v2"
    doi="doi%3A10.5061%2Fdryad.51c59zwm3"
    ds=_api_json(f"{base}/datasets/{doi}")
    # Dryad's HAL returns a current-version link in most public datasets.
    version_link=ds.get("_links",{}).get("stash:version",{}).get("href")
    if version_link:
        version_id=int(re.search(r"/versions/(\d+)",version_link).group(1))
    else:
        versions=_api_json(f"{base}/datasets/{doi}/versions?per_page=100")
        found=versions.get("_embedded",{}).get("stash:versions",[])
        if not found:
            raise ValueError("SOURCE_STOP: no published Dryad version in anonymous metadata")
        version_id=max(int(v["id"]) for v in found)
    files=_api_json(f"{base}/versions/{version_id}/files?per_page=100")
    a=files.get("_embedded",{}).get("stash:files",[])
    found=[v for v in a if v.get("path",v.get("filename",v.get("name",""))).lower().endswith("raw_data.zip")]
    if len(found)!=1:
        raise ValueError("SOURCE_STOP: missing/ambiguous Raw_data.zip in original public file inventory")
    return found[0],version_id


def fetch_bytes(url=API_URL):
    """API archive requires bearer token (401 anonymous); browser file route may work.

    Preserve both failures rather than fabricate field effects. No credentials used.
    """
    try:
        return _download_limited(url)
    except urllib.error.HTTPError as exc:
        if exc.code not in (401,403,404):
            raise
        original_status=f"HTTP {exc.code} on anonymous API package"
    try:
        metadata,version_id=_select_dryad_file_metadata()
        fid=metadata.get("id")
        if not isinstance(fid,int) or fid<=0:
            raise ValueError("SOURCE_STOP: original file inventory lacks numeric ID")
    except Exception as exc:
        raise ValueError(f"SOURCE_STOP: {original_status}; anonymous metadata fallback failed: {exc}") from exc
    failed=[]
    for path in (f"/downloads/file_stream/{fid}",f"/stash/downloads/file_stream/{fid}"):
        candidate=f"https://datadryad.org{path}"
        try:
            body,final=_download_limited(candidate)
            # Fail closed even if Dryad returns HTML login/access page as HTTP 200.
            secure_zip(body,name="Dryad public file-stream")
            return body,final
        except (urllib.error.URLError,ValueError) as exc:
            failed.append(f"{path}: {str(exc)[:180]}")
    raise ValueError(f"SOURCE_STOP: {original_status}; public browser file routes unavailable (file={fid}; version={version_id}); {'; '.join(failed)}")


def unpack_original(download):
    """Return source names+original bytes; handle Dryad outer ZIP nesting exactly once."""
    outer = secure_zip(download, name="Dryad download")
    zip_members = [n for n in outer.namelist() if n.lower().endswith("raw_data.zip")]
    if len(zip_members) == 1:
        inner = secure_zip(outer.read(zip_members[0]), name="Raw_data.zip")
        entries = {n: inner.read(n) for n in inner.namelist() if not n.endswith("/")}
        return entries, {"outer_zip_sha256": sha(download), "nested_raw_zip_name": zip_members[0], "inner_zip_sha256": sha(outer.read(zip_members[0]))}
    if not zip_members and any(n.lower().endswith("habitat map.tif") for n in outer.namelist()):
        return {n: outer.read(n) for n in outer.namelist() if not n.endswith("/")}, {"outer_zip_sha256": sha(download), "nested_raw_zip_name": None}
    raise ValueError("SOURCE_STOP: source has no unambiguous Raw_data.zip or unpacked habitat map")


def choose_required_files(entries):
    def single(test, field):
        matches = [n for n in entries if test(n.lower().replace("\\", "/"))]
        if len(matches) != 1:
            raise ValueError(f"SOURCE_STOP: {field} match count={len(matches)}; candidates={matches[:10]}")
        return matches[0]
    tif = single(lambda n:n.endswith("habitat map.tif"),"habitat_map")
    lookup = single(lambda n:n.endswith("sn to id.txt"), "tag_crosswalk")
    mapping = single(lambda n:n.endswith("habitat mapping scheme.txt"),"map_scheme")
    gps = single(lambda n:n.endswith(".csv") and ("tracking data/" in n or "tracking" in n.split("/")[-1]),"tracking_csv")
    return {"tif":tif,"lookup":lookup,"mapping":mapping,"gps":gps}


def source_only_manifest(entries, roles, origin):
    header = next(csv.reader(io.StringIO(entries[roles["gps"]].decode("utf-8-sig",errors="replace"))))
    needed = ["S/N","Collecting time","Longitude","Latitude","HorAccuracy"]
    if any(s not in header for s in needed):
        raise ValueError("SOURCE_STOP: GPS missing required original columns: "+str([s for s in needed if s not in header]))
    try:
        import rasterio
        from rasterio.io import MemoryFile
    except ImportError as exc:
        raise ValueError("SOURCE_STOP: rasterio unavailable") from exc
    with MemoryFile(entries[roles["tif"]]) as mem:
        with mem.open() as ds:
            if not ds.crs or ds.count != 1 or ds.width < 4 or ds.height < 4:
                raise ValueError("SOURCE_STOP: georeferencing, band count or map extent invalid")
            grid = {"width":ds.width,"height":ds.height,"crs":str(ds.crs),"nodata":ds.nodata,"transform":list(ds.transform)[:6],"datatype":str(ds.dtypes[0])}
    return {"status":"SOURCE_SCHEMA_PASS_NO_ECOLOGICAL_RESPONSE_OPENED","source_doi":DOI,"source_url":API_URL,
            "outer_archive":origin,"original_entries":[{"name":n,"bytes":len(v),"sha256":sha(v)} for n,v in sorted(entries.items())],
            "roles":roles,"gps_columns":header,"raster_metadata":grid,"original_habitat_use_or_effects_scored":False}


def read_tagmap(blob):
    """Known original README formats: S/N, individual ID and species; require mapping integrity."""
    text = blob.decode("utf-8-sig", errors="replace")
    found = {}
    for line in text.splitlines():
        # Match either comma/tab/whitespace fields with an identifier (prefix_number).
        m = re.search(r"(?<!\d)(\d{3,6})\s*[,\t ]+\s*((?:CORE|GRPL|GSPL|REKN|SAGU)_[A-Za-z0-9]+)\b", line, flags=re.I)
        if m:
            sn,id_ = m.group(1),m.group(2).upper()
            if sn in found and found[sn] != id_:
                raise ValueError("SOURCE_STOP: ambiguous tag mapping for serial "+sn)
            found[sn] = id_
    if not found or len(set(found.values())) != len(found):
        raise ValueError("SOURCE_STOP: source tag lookup not parsable without ambiguous identity")
    return found


def local_day(utc_time):
    hour = (utc_time.hour + 8) % 24  # exact PRC official zone; not solar sunrise
    return int(6 <= hour < 18)


def great_circle_m(lat1,lon1,lat2,lon2):
    a,b,c,d = [math.radians(float(t)) for t in (lat1,lon1,lat2,lon2)]
    h=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 2*R_EARTH*math.asin(min(1.,math.sqrt(h)))


def radial_endpoints(lon,lat,radius):
    # Bearings from north, 0, 11.25, ..., 348.75 degrees. No outcome-angle shift.
    import numpy as np
    b=np.arange(ANGLES)*2*np.pi/ANGLES
    lat1=np.deg2rad(lat); lon1=np.deg2rad(lon); ang=radius/R_EARTH
    lat2=np.arcsin(np.sin(lat1)*np.cos(ang)+np.cos(lat1)*np.sin(ang)*np.cos(b))
    lon2=lon1+np.arctan2(np.sin(b)*np.sin(ang)*np.cos(lat1),np.cos(ang)-np.sin(lat1)*np.sin(lat2))
    return np.rad2deg(lon2), np.rad2deg(lat2)


def map_sample(ds, arr, lon, lat):
    """Sample with array affine inverses; never treat out-of-map as other habitat."""
    import numpy as np
    from rasterio.warp import transform
    xs=np.asarray(lon,dtype=float); ys=np.asarray(lat,dtype=float)
    if str(ds.crs) not in ("EPSG:4326", "OGC:CRS84"):
        ox,oy=transform("EPSG:4326",ds.crs,xs.ravel().tolist(),ys.ravel().tolist())
        xs=np.asarray(ox).reshape(xs.shape);ys=np.asarray(oy).reshape(ys.shape)
    inv=~ds.transform
    cc=np.floor(inv.a*xs+inv.b*ys+inv.c).astype(int)
    rr=np.floor(inv.d*xs+inv.e*ys+inv.f).astype(int)
    inside=(cc>=0)&(rr>=0)&(cc<ds.width)&(rr<ds.height)
    vals=np.full(xs.shape,np.nan)
    vals[inside]=arr[rr[inside],cc[inside]]
    if ds.nodata is not None:
        vals[vals==ds.nodata]=np.nan
    vals[~np.isfinite(vals)]=np.nan
    return vals


def prepare_tracking(blob, mapping):
    import pandas as pd
    data=pd.read_csv(io.BytesIO(blob),dtype={"S/N":"string"},low_memory=False,encoding="utf-8-sig")
    required=["S/N","Collecting time","Longitude","Latitude","HorAccuracy"]
    if any(k not in data for k in required):
        raise ValueError("SOURCE_STOP: changed field schema")
    data["individual"]=data["S/N"].map(mapping)
    unknown=data[data["individual"].isna()]
    # Nonfocal unknown tags must not be silently treated as focal animals.
    data=data[data["individual"].notna()].copy()
    data["species"]=data["individual"].str.split("_").str[0]
    data=data[data["species"].isin(FOCAL)].copy()
    data["time"]=pd.to_datetime(data["Collecting time"],utc=True,errors="coerce")
    for x,y in [("Longitude","lon"),("Latitude","lat"),("HorAccuracy","acc")]:
        data[y]=pd.to_numeric(data[x],errors="coerce")
    data=data[data["time"].notna()].copy()
    # Even damaged GPS fixes remain between valid records until step construction.
    data=data.sort_values(["individual","time"]).copy()
    dups=data.duplicated(["individual","time"],keep=False)
    ambiguous=data.loc[dups].groupby(["individual","time"])[["lon","lat"]].nunique(dropna=False)
    if ((ambiguous > 1).any(axis=1)).any():
        raise ValueError("SOURCE_STOP: duplicate GPS acquisition time with conflicting original locations")
    data=data.drop_duplicates(["individual","time"],keep="first")
    return data, {"unknown_crosswalk_source_rows":len(unknown),"distinct_focal_birds":int(data.individual.nunique())}


def generate_steps(data, ds, arr, *, max_accuracy):
    import numpy as np
    byclass={}
    # Actual source fix state: raster-class sampling includes origin and destination.
    states=map_sample(ds,arr,data["lon"].to_numpy(),data["lat"].to_numpy())
    data=data.assign(cls=states)
    all_steps=[]
    stats=Counter()
    for ind,g in data.groupby("individual",sort=True):
        g=g.sort_values("time")
        prev=None
        for row in g.itertuples(index=False):
            # handle Pandas sanitized column values via _asdict keys named lon,lat,acc etc.
            d=row._asdict()
            if prev is None:
                prev=d;continue
            dt=(d["time"]-prev["time"]).total_seconds()/60
            stats["candidate_adjacent_fixes"]+=1
            vals=(d["lon"],d["lat"],d["acc"],d["cls"],prev["lon"],prev["lat"],prev["acc"],prev["cls"])
            if not all(math.isfinite(float(v)) for v in vals):
                stats["invalid_coordinates_accuracy_or_map"]+=1;prev=d;continue
            if d["acc"] > max_accuracy or prev["acc"] > max_accuracy or d["acc"] <0 or prev["acc"]<0:
                stats["accuracy_filter"]+=1;prev=d;continue
            if not (10<=dt<=90):
                stats["time_gap_filter"]+=1;prev=d;continue
            if not (-90<=d["lat"]<=90 and -180<=d["lon"]<=180 and -90<=prev["lat"]<=90 and -180<=prev["lon"]<=180):
                stats["coordinate_filter"]+=1;prev=d;continue
            dist=great_circle_m(d["lat"],d["lon"],prev["lat"],prev["lon"])
            if not 50<=dist<=3000:
                stats["distance_filter"]+=1;prev=d;continue
            origins=[int(prev["cls"])]
            c_fields={}
            for c_key,radius in (("C_distance",dist),("C_500",RADII[0]),("C_1500",RADII[1])):
                xs,ys=radial_endpoints(prev["lon"],prev["lat"],radius)
                v=map_sample(ds,arr,xs,ys)
                valid=v[np.isfinite(v)]
                if len(valid)<24:
                    c_fields=None;break
                val=float(np.mean(valid==prev["cls"]))
                c_fields[c_key]=val
            if c_fields is None:
                stats["circle_coverage_filter"]+=1;prev=d;continue
            all_steps.append({"individual":ind,"species":d["species"],"datetime_utc":d["time"].isoformat(),
                "origin_cls":int(prev["cls"]),"dest_cls":int(d["cls"]),"distance_m":float(dist),
                "day":local_day(d["time"]),"Y":int(prev["cls"]==d["cls"]),"R":int(prev["cls"]==d["cls"])-c_fields["C_distance"],**c_fields})
            stats["eligible"]+=1
            prev=d
    return all_steps,dict(stats)


def boot_ci(values, *, draws=10000, seed=SEED):
    import numpy as np
    v=np.asarray(values,dtype=float)
    if not len(v):return [None,None]
    rng=np.random.default_rng(seed)
    out=[]
    for _ in range(draws):out.append(np.mean(rng.choice(v,len(v),replace=True)))
    return [float(q) for q in np.quantile(out,[.025,.975])]


def summarize(steps, *, source_manifest, qc, crosswalk, max_accuracy):
    import numpy as np
    import pandas as pd
    tab=pd.DataFrame(steps)
    ind=[]
    for bird,g in tab.groupby("individual",sort=True):
        if len(g)<20:continue
        ind.append({"id":bird,"species":g.species.iloc[0],"n_steps":len(g),"R_mean":float(g.R.mean()),
            "observed_stay_fraction":float(g.Y.mean()),"matched_circle_stay_fraction":float(g.C_distance.mean()),
            "day_R":float(g[g.day==1].R.mean()) if (g.day==1).sum()>=10 else None,
            "night_R":float(g[g.day==0].R.mean()) if (g.day==0).sum()>=10 else None})
    core=[x for x in ind if x["species"]=="CORE"]
    receipt={"status":"PRIMARY_NOT_ADMITTED","source_doi":DOI,"source_sha256":source_manifest["outer_archive"]["outer_zip_sha256"],
      "reference":"single-date, static habitat raster; rotation null, not dynamic or physical reachability",
      "max_accuracy_m":max_accuracy,"eligible_steps_total":len(steps),"qc":qc,
      "eligible_birds_ge20":len(ind),"eligible_CORE_birds_ge20":len(core),
      "species_summary":{},"source_raster":source_manifest["raster_metadata"],
      "evidence_class":"independent original GPS+raster observational reanalysis conditional on source sampling"}
    for species in FOCAL:
        subs=[x for x in ind if x["species"]==species]
        if subs:
            vals=[x["R_mean"] for x in subs]
            receipt["species_summary"][species]={"birds":len(subs),"steps":sum(x["n_steps"] for x in subs),
                  "equal_bird_mean_R":float(np.mean(vals)),"equal_bird_R_CI":boot_ci(vals),
                  "positive_birds":sum(x>0 for x in vals),"individuals":subs}
        else:receipt["species_summary"][species]={"birds":0,"steps":0}
    if len(core)<6:
        return receipt
    receipt["status"]="PRIMARY_ADMITTED_EFFECT_AS_REPORTED"
    receipt["core_effect"]={k:v for k,v in receipt["species_summary"]["CORE"].items() if k!="individuals"}
    # Focal source rule is exactly 6 independent eligible CORE birds (out of 9 reported).
    n=sum(x["R_mean"]!=0 for x in core);pos=sum(x["R_mean"]>0 for x in core)
    from math import comb
    # Exact sign-test excludes ties, and the raw number of tied birds is reported.
    p=min(1.,2*sum(comb(n,k) for k in range(0,min(pos,n-pos)+1))/2**n) if n else None
    receipt["core_effect"]["two_sided_exact_sign_p"] = p
    receipt["core_effect"]["n_nonzero_signs"] = n
    receipt["core_effect"]["n_ties"] = len(core)-n
    low,up=receipt["core_effect"]["equal_bird_R_CI"]
    receipt["core_effect"]["pass_predeclared_direction"] = bool(low>0 and pos > len(core)/2)
    return receipt


def fit_holdout(steps, receipt):
    """Source-heldout bird gain M0 vs M1. C_500 known at origin; no destination leakage."""
    if not receipt["status"].startswith("PRIMARY_ADMITTED"):
        return {"status":"FORECAST_NOT_ESTIMABLE_PRIMARY_GATE"}
    import numpy as np
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder,StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import log_loss
    df=pd.DataFrame(steps)
    # Freeze primary to CORE, distinct birds with >=20 steps. Other taxa descriptive only.
    df=df[df.species=="CORE"].copy()
    n=df.groupby("individual").size();df=df[df.individual.isin(n[n>=20].index)]
    if df.Y.nunique()<2:
        return {"status":"FORECAST_NOT_ESTIMABLE_SINGLE_LABEL"}
    allscores=[]
    for holdout in sorted(df.individual.unique()):
        tr=df[df.individual!=holdout];te=df[df.individual==holdout]
        if tr.Y.nunique()<2 or len(tr)<50:
            return {"status":"FORECAST_NOT_ESTIMABLE_SINGLE_LABEL_FOLD"}
        weights=tr.groupby("individual")["individual"].transform("size").rdiv(1.0)
        L={}
        for key,features in [("M0",["origin_cls","day"]),("M1",["origin_cls","day","C_500"])]:
            cat=["origin_cls"];nums=[x for x in features if x not in cat]
            # One-hot origin state; reserve categories as learned from TRAIN individuals only.
            pre=ColumnTransformer([("origin",OneHotEncoder(handle_unknown="ignore"),cat),
                                   ("continuous",StandardScaler(),nums)],sparse_threshold=0.)
            model=Pipeline([("transform",pre),("model",LogisticRegression(C=1.,solver="liblinear",random_state=SEED,max_iter=500))])
            model.fit(tr[features],tr.Y,model__sample_weight=weights)
            probs=np.clip(model.predict_proba(te[features])[:,1],1e-6,1-1e-6)
            L[key]=float(log_loss(te.Y,probs,labels=[0,1]))
        allscores.append({"heldout_individual":holdout,"steps":int(len(te)),"M0":L["M0"],"M1":L["M1"],"gain_nats_per_step":L["M0"]-L["M1"]})
    gains=[r["gain_nats_per_step"] for r in allscores]
    return {"status":"SOURCE_SINGLE_SITE_BIRD_HELDOUT_RETROSPECTIVE","eligible_independent_CORE_birds":len(allscores),
            "M1_minus_M0_equal_bird_log_loss_gain":float(np.mean(gains)),"gain_bootstrap_95pct":boot_ci(gains),
            "positive_birds":sum(x>0 for x in gains),"bird_level_scores":allscores,
            "note":"Pre-destination conditional prediction at observed GPS origin/time uses static C_500. It does not estimate true time-varying habitat accessibility."}


def run(output, *, max_accuracy=50, zipped_source=None, dry_run=False):
    report={"source_doi":DOI,"stage":"SOURCE_ONLY","status":"SOURCE_STOP"}
    try:
        if zipped_source:
            payload=Path(zipped_source).read_bytes();request_url="local_sample_fixture"
        else:
            payload,request_url=fetch_bytes()
        entries,origin=unpack_original(payload)
        origin["source_request_final_url"]=request_url
        roles=choose_required_files(entries)
        source=source_only_manifest(entries,roles,origin)
        report=source.copy()
        if not dry_run:
            from rasterio.io import MemoryFile
            lookup=read_tagmap(entries[roles["lookup"]])
            data,crosswalk=prepare_tracking(entries[roles["gps"]],lookup)
            if data.empty:
                raise ValueError("SOURCE_STOP: zero eligible focal animals after crosswalk")
            with MemoryFile(entries[roles["tif"]]) as mem:
                with mem.open() as ds:
                    raster=ds.read(1)
                    if raster.size>10_000_000:raise ValueError("SOURCE_STOP: image exceeds size bound")
                    steps,qc=generate_steps(data,ds,raster,max_accuracy=max_accuracy)
            if not steps:
                report={**source,"status":"PRIMARY_NOT_ADMITTED_NO_ELIGIBLE_STEPS","qc":qc,"crosswalk":crosswalk}
            else:
                report=summarize(steps,source_manifest=source,qc=qc,crosswalk=crosswalk,max_accuracy=max_accuracy)
                report["prediction"]=fit_holdout(steps,report)
    except (ValueError, KeyError, RuntimeError, OSError, zipfile.BadZipFile, urllib.error.URLError) as exc:
        report={"source_doi":DOI,"status":"SOURCE_STOP","reason":str(exc),"original_habitat_use_or_effects_scored":False}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    print("LEIZHOU_V2_STATUS",report["status"], "RESULT",output)
    return report


if __name__=="__main__":
    pa=argparse.ArgumentParser();pa.add_argument("--out",required=True);pa.add_argument("--dry-run",action="store_true");pa.add_argument("--source-zip")
    pa.add_argument("--accuracy-m",type=int,default=50)
    args=pa.parse_args()
    run(args.out,max_accuracy=args.accuracy_m,zipped_source=args.source_zip,dry_run=args.dry_run)
