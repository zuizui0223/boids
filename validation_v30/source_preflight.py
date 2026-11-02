"""v30 original-source admission (source observations, never a tidal effect).

Downloads original Zenodo annual GPS gzip files, pins the provider MD5, audits
sampling and simultaneous-neighbor observability. No raw tracks or animal IDs
are persisted; original tag clocks are not independently verified as UTC.
"""
from __future__ import annotations
import argparse
from collections import Counter, deque
from datetime import datetime
import csv, gzip, hashlib, json, math, statistics, tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ZENODO_RECORD = "https://zenodo.org/records/22296922"
GPS_MD5 = {
    2008: "2624a15e124450f54ddc5a4b5c5fce91",
    2009: "1967bdcd6a4720c63bb986abdaf48ab0",
    2010: "0f1c603a285f1980a5b4ee962e2e28ad",
    2011: "610e3edb48bda7d922d63978feb22ac1",
    2012: "a2ccce5afe2a6cad09a27e2957beacaf",
    2013: "6137d93ee58289fc8a5e2163aa4c05fc",
    2014: "21e7fda801096449e6974f616d6dedd9",
}
NEEDED = {"event-id", "timestamp", "location-long", "location-lat",
          "individual-local-identifier"}


def download_and_pin(year: int, target: Path):
    if year not in GPS_MD5:
        raise ValueError("Year is not a pinned original 2008-2014 GPS source")
    name = f"O_SCHIERMONNIKOOG-gps-{year}.csv.gz"
    url = f"{ZENODO_RECORD}/files/{name}?download=1"
    req = Request(url, headers={"User-Agent": "Boids-Research-Original-Source-Audit/1.0"})
    md5, sha = hashlib.md5(), hashlib.sha256()
    n = 0
    with urlopen(req, timeout=90) as inp, target.open("wb") as out:
        while True:
            part = inp.read(1 << 19)
            if not part:
                break
            n += len(part)
            if n > 30_000_000:
                raise ValueError("Original annual GPS object exceeds safety cap")
            md5.update(part); sha.update(part); out.write(part)
    if md5.hexdigest() != GPS_MD5[year]:
        target.unlink(missing_ok=True)
        raise ValueError("Original Zenodo gzip MD5 differs from published provider MD5")
    return {"year": year, "original_filename": name, "provider_md5_match": True,
            "original_bytes": n, "original_sha256": sha.hexdigest(),
            "record": ZENODO_RECORD}


def parse_stamp(s: str):
    # Original source attribute dictionary allows UTC OR GPS time.
    # Preserve the naive source clock; do not silently relabel UTC.
    s = s.strip()
    if not s or s[-1:] == 'Z' or '+' in s or 'T' in s:
        raise ValueError("Unexpected original GPS timestamp representation")
    return datetime.fromisoformat(s)


def haversine_m(a, b):
    lat1, lon1 = math.radians(a[1]), math.radians(a[2])
    lat2, lon2 = math.radians(b[1]), math.radians(b[2])
    dlat, dlon = lat2-lat1, lon2-lon1
    q = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 12742000*math.asin(min(1., math.sqrt(q)))


def audit_gps_gz(path, *, file_sha256=None):
    rows = []; n_all = bad_location = missing_ids = not_visible = bad_clock = bad_event = 0
    events = set()
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not NEEDED <= set(reader.fieldnames or ()):
            raise ValueError(f"Missing original Movebank fields: {sorted(NEEDED-set(reader.fieldnames or ()))}")
        for line in reader:
            n_all += 1
            ident = (line.get("individual-local-identifier") or "").strip()
            if not ident:
                missing_ids += 1; continue
            if "visible" in line and line["visible"].strip().upper() in ("FALSE", "0"):
                not_visible += 1; continue
            event = (line.get("event-id") or "").strip()
            if not event or event in events:
                bad_event += 1; continue
            events.add(event)
            try:
                t = parse_stamp(line["timestamp"])
            except (ValueError, TypeError):
                bad_clock += 1; continue
            try:
                lat, lon = float(line["location-lat"]), float(line["location-long"])
            except (ValueError, TypeError):
                bad_location += 1; continue
            if not all(map(math.isfinite, [lat, lon])) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                bad_location += 1; continue
            rows.append((t, lat, lon, ident))
    if n_all == 0:
        raise ValueError("Empty original GPS")
    per = {}
    within_region = 0
    for t, lat, lon, ident in rows:
        per.setdefault(ident, []).append((t, lat, lon))
        within_region += 53.2 <= lat <= 53.7 and 5.7 <= lon <= 6.6
    by_gap = Counter(); identical_times = speed_pairs = extreme_speed = 0; gap_sample=[]
    for fixes in per.values():
        fixes.sort(key=lambda v: v[0])
        for a, b in zip(fixes, fixes[1:]):
            d = (b[0]-a[0]).total_seconds()
            if d <= 0:
                identical_times += 1; continue
            if len(gap_sample) < 200000: gap_sample.append(d)
            for name, threshold in [("<=5s",5), ("<=10s",10), ("<=60s",60),
                                    ("<=5min",300), ("<=1h",3600), ("<=2h",7200)]:
                if d <= threshold: by_gap[name] += 1
            if 1 <= d <= 7200:
                speed_pairs += 1
                kmph = haversine_m((None,a[1],a[2]),(None,b[1],b[2])) * 3.6 / d
                if kmph > 120: extreme_speed += 1
    # Candidate distinct-animal pairs within five source-clock seconds and 100m.
    # This says nothing about genuine social forces.
    nearby=deque(); ids_pairing=set(); candidate_pairs=0
    for item in sorted(rows):
        t,lat,lon,ident=item
        while nearby and (t-nearby[0][0]).total_seconds()>5: nearby.popleft()
        for other in nearby:
            if other[3]!=ident and haversine_m(item, other)<=100:
                candidate_pairs+=1
                ids_pairing.add(other[3]); ids_pairing.add(ident)
        nearby.append(item)
    counts=sorted(len(v) for v in per.values())
    return {
        "source_type":"ORIGINAL_ZENODO_GPS_FIELD_OBSERVABILITY_ONLY",
        "original_sha256":file_sha256,
        "raw_rows":n_all,
        "admitted_visible_valid_position_rows":len(rows),
        "original_individuals":len(per),
        "per_individual_fix_count_min_max":[min(counts) if counts else 0,max(counts) if counts else 0],
        "first_last_native_timestamp":[min(r[0] for r in rows).isoformat() if rows else None,
                                        max(r[0] for r in rows).isoformat() if rows else None],
        "time_between_fixes_median_seconds":statistics.median(gap_sample) if gap_sample else None,
        "successive_fix_pairs":by_gap.get("<=2h",0),
        "fix_gap_leq_cumulative_counts":dict(by_gap),
        "duplicate_individual_timestamps":identical_times,
        "source_near_neighbor_candidate_pairs_le5s_le100m":candidate_pairs,
        "individuals_in_near_neighbor_candidates":len(ids_pairing),
        "eligible_step_pairs_dt_1s_to_2h":speed_pairs,
        "candidate_steps_over_120_kmph":extreme_speed,
        "within_schiermonnikoog_region_rows":within_region,
        "dropped_missing_individual":missing_ids,
        "dropped_source_not_visible":not_visible,
        "dropped_bad_position":bad_location,
        "dropped_bad_timestamp":bad_clock,
        "dropped_duplicate_or_missing_event_id":bad_event,
        "clock_UTC_vs_GPS":"UNVERIFIED_METADATA_SAYS_UTC_OR_GPS_TIME",
        "tide_linked":False, "dem_joined":False,
        "biological_tide_or_social_effect":"NOT_ESTIMATED",
    }


def run(years, output):
    result={"study":"O_SCHIERMONNIKOOG","zenodo_version":5,
            "license_link":ZENODO_RECORD,
            "evidence":"REAL_ORIGINAL_GPS_SOURCE_AUDIT_NOT_TIDE_TEST","years":[]}
    with tempfile.TemporaryDirectory(prefix="source_z_") as folder:
        for year in years:
            path=Path(folder)/f"gps_{year}.csv.gz"
            manifest=download_and_pin(year,path)
            audit=audit_gps_gz(path,file_sha256=manifest["original_sha256"])
            result["years"].append({"manifest":manifest,"audit":audit})
            path.unlink(missing_ok=True)
    if output:
        Path(output).parent.mkdir(parents=True,exist_ok=True)
        Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--years",type=int,nargs="+",default=[2008])
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    x=run(args.years,args.output)
    print(json.dumps(x,sort_keys=True))
