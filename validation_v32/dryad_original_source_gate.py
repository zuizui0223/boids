#!/usr/bin/env python3
"""v32 original Dryad CSV source-only structural admission, NO numeric outcomes."""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import urllib.error
import urllib.request

DOI = "10.5061/dryad.6q573n6b0"
CANDIDATE_URLS = [
    # Original official landing-page file ID, then documented Dryad REST v2 file.
    "https://datadryad.org/downloads/file_stream/4258753",
    "https://datadryad.org/api/v2/files/4258753/download",
]
REQUIRED = (
    "id_site", "IdTraj", "Species_corrected", "guild",
    "meanBuzz", "meanVfinal", "traj_length",
    "dist_Eau", "dist_Lisiere", "foret_500",
    "Conspecific_sp", "Heterospecific_intraMRE",
    "Heterospecific_inter_nonMRE",
)
CO = ("Conspecific_sp","Heterospecific_intraMRE","Heterospecific_inter_nonMRE")
FEATURE = ("meanBuzz","meanVfinal","traj_length","dist_Eau","dist_Lisiere","foret_500")
MAX_BYTES=1_500_000
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; boids-source-structural-audit/1.0)",
         "Accept":"text/csv,text/plain,application/octet-stream;q=0.7,*/*;q=0.5"}
OUTPUT=Path("validation_v32/results/dryad_bat_trajectory_structural_gate_v32.json")


def download_original(getter=None):
    if getter is None:
        def getter(url):
            req=urllib.request.Request(url,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=25) as response:
                payload=response.read(MAX_BYTES+1)
                return response.status, response.headers.get("content-type",""), payload
    attempts=[]
    for url in CANDIDATE_URLS:
        try:
            code,typ,data=getter(url)
            if len(data)>MAX_BYTES:
                attempts.append({"url":url,"status":"SIZE_CAP_STOP","http":code})
                continue
            if code!=200 or data.lstrip().startswith((b"<!DOCTYPE",b"<html",b"<HTML")):
                attempts.append({"url":url,"status":"NON_CSV_OR_NON_200_STOP","http":code,
                                 "content_type":typ})
                continue
            # Try UTF-8-SIG and latin-1 for ordinary French CSV text.
            try: text=data.decode("utf-8-sig")
            except UnicodeDecodeError: text=data.decode("latin-1")
            first=text.splitlines()[0] if text.splitlines() else ""
            delim=";" if ";" in first else ("," if "," in first else "\t")
            cols=next(csv.reader([first],delimiter=delim))
            if len(cols)<len(REQUIRED) or not all(k in cols for k in REQUIRED):
                import re
                sanitized_header = re.sub(r"[0-9]", "#", first[:160]).replace("\\n", " ")
                attempts.append({"url":url,"status":"NOT_EXPECTED_SOURCE_SCHEMA","http":code,
                                 "header_column_count":len(cols), "content_type": typ,
                                 "source_bytes_received":len(data),
                                 "first_line_sanitized":sanitized_header,
                                 "looks_like_html_or_json":("<html" in text[:2000].lower() or "<!doctype" in text[:2000].lower() or text.lstrip().startswith("{"))})
                continue
            return {"status":"ORIGINAL_CSV_RETRIEVED","source_url":url,
                    "sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),
                    "data":text,"delimiter":delim,"attempts":attempts}
        except urllib.error.HTTPError as exc:
            attempts.append({"url":url,"status":"HTTP_ACCESS_STOP","http":exc.code})
        except (urllib.error.URLError, OSError,TimeoutError) as exc:
            attempts.append({"url":url,"status":"TRANSPORT_ACCESS_STOP","error_type":type(exc).__name__})
    return {"status":"SOURCE_ACCESS_STOP","attempts":attempts}


def nonmissing(val):
    return str(val).strip().lower() not in ("","na","n/a","n.a.","nan","null","-",".")


def normalize_binary(x):
    k=x.strip().lower()
    return {"true":"1","false":"0","yes":"1","no":"0","1":"1","0":"0",
            "1.0":"1","0.0":"0","1,0":"1","0,0":"0"}.get(k,"UNKNOWN")


def audit_structure(source):
    reader=csv.DictReader(io.StringIO(source["data"]),delimiter=source["delimiter"])
    headers=[str(s).strip() for s in (reader.fieldnames or [])]
    missing=[c for c in REQUIRED if c not in headers]
    if missing:
        return {"status":"SCHEMA_STOP","missing_columns":missing}
    n=0; usable=0
    keys=Counter(); site=Counter(); species=Counter(); guild=Counter()
    site_species=Counter(); co=defaultdict(Counter); co_site=defaultdict(lambda:defaultdict(Counter))
    lengths=Counter(); invalid_context=Counter()
    for row in reader:
        n+=1
        s=(row.get("id_site") or "").strip()
        sp=(row.get("Species_corrected") or "").strip()
        g=(row.get("guild") or "").strip()
        traj=(row.get("IdTraj") or "").strip()
        keys[(s,traj)]+=1
        site[s]+=1;species[sp]+=1;guild[g]+=1;site_species[(s,sp)]+=1
        eligible=all(nonmissing(row.get(c,"")) for c in REQUIRED)
        for c in CO:
            v=normalize_binary(row.get(c,"") or "")
            co[c][v]+=1;co_site[c][s][v]+=1
            if v=="UNKNOWN":invalid_context[c]+=1
            if v not in ("0","1"):eligible=False
        lengths["nonmissing_response_and_model_fields" if eligible else "missing_or_unrecognized"]+=1
        if eligible:usable+=1
    nsites=sum(x>=10 for x in site.values())
    context_variation=any(co[c]["0"]>0 and co[c]["1"]>0 for c in CO)
    dup={f"{s}|{traj}":count for (s,traj),count in keys.items() if count>1}
    conditions={
        "at_least_8_sites":len(site)>=8,
        "at_least_4_species":len(species)>=4,
        "at_least_300_usable_rows":usable>=300,
        "at_least_6_sites_with_10_trajectories":nsites>=6,
        "some_community_category_has_two_values":context_variation,
        "no_site_trajectory_duplicates":not dup,
        "no_blank_site_species_labels":("" not in site and "" not in species),
        "all_cooccurrence_categories_are_boolean":not invalid_context,
    }
    if dup: status="GRAIN_STOP"
    elif not all(conditions.values()):status="SUPPORT_STOP"
    else:status="STRUCTURAL_PASS_ONLY"
    return {
        "status":status,"frozen_structure_gate_conditions":conditions,
        "source_row_count":n,"usable_row_count_missingness_only":usable,
        "trajectory_key_unique_n":len(keys),
        "duplicate_site_trajectory_id_n":len(dup),
        "sample_duplicate_keys_only":dict(list(dup.items())[:10]),
        "site_count":len(site),"focal_species_count":len(species),
        "guild_count":len(guild),
        "source_site_counts":dict(sorted(site.items())),
        "source_species_counts":dict(sorted(species.items())),
        "source_guild_counts":dict(sorted(guild.items())),
        "site_species_cell_count":len(site_species),
        "sites_at_least_10_trajectories":nsites,
        "cooccurrence_support":{c:dict(co[c]) for c in CO},
        "cooccurrence_site_binary_support":{
            c:{"both_0_and_1_sites":sum(v["0"]>0 and v["1"]>0 for v in co_site[c].values()),
               "all_0_sites":sum(v["0"]>0 and v["1"]==0 for v in co_site[c].values()),
               "all_1_sites":sum(v["1"]>0 and v["0"]==0 for v in co_site[c].values())}
            for c in CO},
        "source_data_outcome_numeric_values_accessed":False,
        "no_behavioral_model_fitted":True,
        "prior_boids_and_batter_results_unchanged":True,
    }


def run(getter=None):
    r=download_original(getter)
    out={"programme":"bat_community_context_site_species_transfer_v32",
         "source_doi":DOI,"source_published_year":2025,
         "download_attempts":r.get("attempts",[]),
         "source_access_status":r["status"],
         "source_data_outcome_numeric_values_accessed":False,
         "no_behavioral_model_fitted":True,
         "no_universality_claim":True}
    if r["status"]!="ORIGINAL_CSV_RETRIEVED":
        out["status"]="SOURCE_ACCESS_STOP"
        return out
    out.update({"source_url_used":r["source_url"],"source_sha256":r["sha256"],
                "source_bytes":r["bytes"],"original_csv_delimiter":r["delimiter"]})
    out.update(audit_structure(r))
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUTPUT)
    a=p.parse_args()
    data=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V32_SOURCE_ONLY="+json.dumps({
        k:data.get(k) for k in (
            "status","source_access_status","source_sha256","source_bytes",
            "original_csv_delimiter","source_row_count","usable_row_count_missingness_only",
            "site_count","focal_species_count","cooccurrence_support",
            "frozen_structure_gate_conditions","download_attempts")},sort_keys=True,ensure_ascii=False))
    assert data["source_data_outcome_numeric_values_accessed"] is False
    assert data["no_behavioral_model_fitted"] is True


if __name__=="__main__":
    main()
