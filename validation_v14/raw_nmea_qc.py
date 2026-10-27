#!/usr/bin/env python3
"""v14 source-only RMC timing, geometry and per-member checksum gate.

Read original ZIP directly. No interpolation, no fitted motion outcomes, no
social coefficient or animal-level location records ever leave the runner.
"""
from __future__ import annotations

import bisect
import collections
import datetime as dt
import hashlib
import math
import re
import statistics
import zipfile
from pathlib import Path

RMC_PREFIXES = ("$GNRMC,", "$GPRMC,")
ZIP_MANIFEST = "data/checksums_sha256.txt"
MIN_VALID_FIXES_FOR_PAIR = 50
TIME_WINDOWS_SEC = (0.2, 1., 5.)
DISTANCE_METRES = (10., 25., 100.)
EARTH_RADIUS_M = 6371008.8


def parse_manifest(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        # sha256sum: <hex>  <path>, or <hex> *<path>.
        m = re.match(r"^([0-9A-Fa-f]{64})\s+\*?(.+?)\s*$", raw)
        if not m:
            # Colon/double quoted formats should be made explicit, not guessed.
            raise ValueError("Unknown checksum-manifest line format")
        path = m.group(2).replace("\\","/").lstrip("./")
        if path in result and result[path] != m.group(1).lower():
            raise ValueError("Conflicting duplicate member digest")
        result[path] = m.group(1).lower()
    if not result:
        raise ValueError("Empty SHA256 member manifest")
    return result


def verify_members(archive: zipfile.ZipFile) -> dict:
    if ZIP_MANIFEST not in archive.namelist():
        return {"status":"blocked_missing_sha256_manifest"}
    expected = parse_manifest(archive.read(ZIP_MANIFEST).decode("utf-8-sig"))
    listed = [m for m in archive.infolist() if not m.is_dir() and
              ("/raw_gps/" in m.filename or "/raw_attitude/" in m.filename)]
    if not listed:
        return {"status":"blocked_no_animal_sensor_files"}
    failures, checks = [], []
    for member in listed:
        # The public manifest may be rooted at data/ or the trial subfolder.
        possibilities = (member.filename, member.filename.removeprefix("data/"),
                         "./"+member.filename, "./"+member.filename.removeprefix("data/"))
        target = next((expected[k] for k in possibilities if k in expected), None)
        if target is None:
            failures.append({"file":member.filename,"error":"not_listed"})
            continue
        digest = hashlib.sha256()
        with archive.open(member) as fp:
            for block in iter(lambda:fp.read(1024*1024), b""):
                digest.update(block)
        if digest.hexdigest() != target:
            failures.append({"file":member.filename,"error":"sha256_mismatch"})
        else:
            checks.append(member.filename)
    return {
        "status":"all_sensor_members_verified" if not failures else "STOP_member_integrity_failed",
        "manifest_entries":len(expected),
        "sensor_files_expected":len(listed),
        "sensor_files_verified":len(checks),
        "failures":failures[:50],
        "gps_files_verified":sum("/raw_gps/" in x for x in checks),
        "imu_files_verified":sum("/raw_attitude/" in x for x in checks),
    }


def nmea_angle(value: str, hemi: str, is_lat: bool) -> float:
    if not value or not math.isfinite(float(value)):
        raise ValueError("Missing or nonfinite NMEA degrees/minutes")
    raw = float(value)
    deg = int(raw // 100)
    mins = raw-deg*100
    if not 0 <= mins < 60:
        raise ValueError("Minute outside 0..60")
    if not is_lat and not 0 <= deg <= 180:
        raise ValueError("Invalid longitude")
    if is_lat and not 0 <= deg <= 90:
        raise ValueError("Invalid latitude")
    if hemi not in (("N","S") if is_lat else ("E","W")):
        raise ValueError("Unexpected hemisphere code")
    signed = deg + mins/60
    if hemi in ("S","W"):
        signed = -signed
    return signed


def nmea_checksum_valid(sentence: str) -> bool | None:
    if not sentence.startswith("$") or "*" not in sentence:
        return None
    body, supplied = sentence[1:].split("*",1)
    if not re.fullmatch("[0-9a-fA-F]{2}", supplied[:2]):
        return False
    acc = 0
    for character in body:
        acc ^= ord(character)
    return acc == int(supplied[:2],16)


def parse_rmc(line: str) -> tuple[str,tuple[int,float,float]|None]:
    """Return (classification, (absolute_UTC_millis, latitude, longitude)).

    Only original valid raw RMC; preprocessor's repaired/interpolated times are
    not data. Device system time is not used to forge shared absolute UTC.
    """
    where = min((line.find(s) for s in RMC_PREFIXES if s in line), default=-1)
    if where < 0:
        return "non_rmc",None
    sentence = line[where:].strip()
    chk = nmea_checksum_valid(sentence)
    if chk is False:
        return "invalid_checksum",None
    payload = sentence.split("*")[0].split(",")
    if len(payload) < 10:
        return "malformed_rmc",None
    if payload[2].strip() != "A":
        return "invalid_status",None
    try:
        raw = payload[1].strip()
        if not re.fullmatch(r"\d{6}(?:\.\d+)?",raw):
            raise ValueError("Malformed UTC time")
        hr, minute, sec = int(raw[:2]),int(raw[2:4]),float(raw[4:])
        if not (0<=hr<24 and 0<=minute<60 and 0<=sec<60):
            raise ValueError("Impossible UTC time")
        day = dt.datetime.strptime(payload[9].strip(),"%d%m%y").date()
        lat = nmea_angle(payload[3].strip(),payload[4].strip(),True)
        lon = nmea_angle(payload[5].strip(),payload[6].strip(),False)
        t_ms = day.toordinal()*86400000 + round((hr*3600+minute*60+sec)*1000)
        return "valid",(t_ms,lat,lon)
    except (ValueError,TypeError,OverflowError):
        return "invalid_date_time_or_coordinates",None


def quantiles(values: list[float]) -> dict:
    if not values:
        return {"n":0}
    a = sorted(values)
    def at(q):
        ix = (len(a)-1)*q
        lo = math.floor(ix)
        hi = math.ceil(ix)
        return float(a[lo] + (a[hi]-a[lo])*(ix-lo))
    return {"n":len(a),"q05":at(.05),"median":at(.5),"q95":at(.95)}


def inspect_one_gps(archive: zipfile.ZipFile, file_name: str) -> tuple[dict,list[tuple[int,float,float]]]:
    counts: collections.Counter = collections.Counter()
    raw = []
    with archive.open(file_name) as reader:
        for line in reader:
            counts["lines"] += 1
            if counts["lines"] > 2_000_000:
                raise ValueError("GPS file exceeds conservative row cap")
            tag, item = parse_rmc(line.decode("utf-8", errors="replace"))
            counts[tag] += 1
            if item is not None:
                raw.append(item)
    raw.sort(key=lambda x:x[0])
    unique = []
    last = None
    for obs in raw:
        if obs[0] == last:
            counts["repeated_raw_utc_timestamp"] += 1
        else:
            unique.append(obs)
            last = obs[0]
    deltas = [(unique[i][0]-unique[i-1][0])/1000. for i in range(1,len(unique))]
    return {
        "nmea_counts":dict(counts),
        "raw_valid_fix_count":len(raw),
        "unique_utc_fix_count":len(unique),
        "positive_time_spacing_seconds":quantiles([x for x in deltas if x>0]),
        "recorded_utc_span_seconds":
           float((unique[-1][0]-unique[0][0])/1000.) if len(unique)>1 else None,
    }, unique


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    a,b,c,d = (math.radians(x) for x in (lat1,lon1,lat2,lon2))
    v=math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 2*EARTH_RADIUS_M*math.asin(math.sqrt(min(1.,v)))


def raw_neighbor_coverage(a: list[tuple[int,float,float]],
                          b: list[tuple[int,float,float]]) -> dict:
    """Nearest *measured* UTC fix in B for each A-fix, no interpolation.

    Pair asymmetry is structural; A is lexically first file. Output counts
    are observation opportunities, NOT independently tested social effects.
    """
    out={f"lag_le_{int(w*1000)}ms":0 for w in TIME_WINDOWS_SEC}
    out.update({f"lag_le_{int(w*1000)}ms_and_dist_le_{int(d)}m":0
                for w in TIME_WINDOWS_SEC for d in DISTANCE_METRES})
    if not a or not b:
        return out
    bt = [x[0] for x in b]
    for t,lat,lon in a:
        j=bisect.bisect_left(bt,t)
        opt=[b[z] for z in (j-1,j) if 0<=z<len(b)]
        other=min(opt,key=lambda x:abs(x[0]-t))
        delay=abs(other[0]-t)/1000.
        if delay>max(TIME_WINDOWS_SEC):
            continue
        distance=haversine_m(lat,lon,other[1],other[2])
        for w in TIME_WINDOWS_SEC:
            if delay <= w + 1e-9:
                out[f"lag_le_{int(w*1000)}ms"]+=1
                for d in DISTANCE_METRES:
                    if distance<=d:
                        out[f"lag_le_{int(w*1000)}ms_and_dist_le_{int(d)}m"]+=1
    return out


def _file_identity(fname: str) -> tuple[str,str]:
    parts = Path(fname).parts
    if len(parts)<4 or not re.fullmatch(r"analysis_trial_\d+",parts[1]):
        raise ValueError("Unexpected trial directory structure")
    bird=Path(fname).stem.removesuffix("_GPS")
    return parts[1],bird


def inspect_gps_archive(path: Path, max_files: int=40) -> dict:
    with zipfile.ZipFile(path,"r") as arc:
        verification = verify_members(arc)
        output = {"integrity":verification,
                  "status":"source_only_no_prediction"}
        if verification["status"] != "all_sensor_members_verified":
            output["status"]="STOP_source_member_verification"
            return output
        gps_names=sorted(n for n in arc.namelist()
                         if "/raw_gps/" in n and n.endswith("_GPS.txt"))
        if not 1<=len(gps_names)<=max_files:
            output["status"]="STOP_unexpected_gps_file_count"
            return output
        data={}
        summary={}
        by_trial: dict[str,list[str]]=collections.defaultdict(list)
        by_bird: dict[str,set]=collections.defaultdict(set)
        for name in gps_names:
            trial,bird=_file_identity(name)
            detail,fixes=inspect_one_gps(arc,name)
            data[name]=fixes
            summary[name]=detail
            by_trial[trial].append(name)
            by_bird[bird].add(trial)
        # No filenames are returned in the main receipt; only aggregate sensor
        # QC by trial, and smallest independent replication unit is flight.
        trial_reports={}
        pair_total=collections.Counter()
        for trial, names in sorted(by_trial.items()):
            cnt=collections.Counter()
            valid=[]
            for name in names:
                d=summary[name]
                for key,value in d["nmea_counts"].items():
                    cnt["nmea_"+key]+=value
                cnt["gps_unique_utc_fixes"]+=d["unique_utc_fix_count"]
                cnt["gps_files"]+=1
                if d["unique_utc_fix_count"]>=MIN_VALID_FIXES_FOR_PAIR:
                    valid.append(name)
            pair_reports=[]
            for ix,name_a in enumerate(valid):
                for name_b in valid[ix+1:]:
                    pair=raw_neighbor_coverage(data[name_a],data[name_b])
                    pair_reports.append(pair)
                    pair_total.update(pair)
            cnt["qualifying_pairs"]=len(pair_reports)
            cnt["all_matched_unique_birds"]=len(names)
            trial_reports[trial]=dict(cnt)
        all_q = [detail["positive_time_spacing_seconds"].get("median")
                 for detail in summary.values()]
        all_q = [x for x in all_q if x is not None]
        output.update({
            "source_trials":len(by_trial),
            "gps_files":len(gps_names),
            "distinct_individual_ids_in_source":len(by_bird),
            "individuals_in_3_source_trials":sum(len(x)==3 for x in by_bird.values()),
            "individuals_in_at_least_2_source_trials":sum(len(x)>=2 for x in by_bird.values()),
            "median_of_per_file_utc_cadence_seconds":statistics.median(all_q) if all_q else None,
            "trial_source_quality":trial_reports,
            "cross_bird_raw_utc_neighbor_counts":dict(pair_total),
            "raw_timestamp_not_interpolated":True,
            "absolute_altitude_available":False,
            "observational_GPS_error_calibrated":False,
            "conditional_3D_niche_admitted":False,
            "network_rewiring_causal_test_admitted":False,
            "independent_source_flight_trials":len(by_trial),
            "exact_group_sign_test_min_one_sided_p":
               float(0.5**len(by_trial)),
            "short_horizon_steering_confirmatory_admitted":
               len(by_trial)>=8 and
               sum(x["qualifying_pairs"] for x in trial_reports.values())>=8,
            "notes":[
                "Co-observation counts use nearest recorded UTC from separate animals; they are not social-force effects.",
                "No NMEA height coordinate; ground-track heading cannot provide 3D occupancy.",
                "Original publication repairs NMEA UTC in preprocessing; this gate does not interpolate or repair clocks.",
                "Only trial-level group independence is defensible, not fix-level independence.",
                "Partial overlap of bird IDs across trials is not manipulated network rewiring.",
                "All effects and predictive scores remain uncomputed."
            ]
        })
        return output
