"""POST-OUTCOME diagnostic for incorrect original bat source exposure grain.

Original PNAS 2024 10-bat group worksheet previously analyzed; the initial
E=numel_5swindows assumption is quarantined, because it implies 274 hours
while original bat flights were ~17-50min. No source individual IDs exported.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from statistics import median
import hashlib,json,math,io,zipfile

from molossus_2024_supplement_structure_v1 import download_bounded,URL,EXPECTED
from molossus_2024_source_capture_LOBO_v1 import decode_sheet,SOURCE_SHA

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"MOLOSSUS_2024_ORIGINAL_SOURCE_GRAIN_DIAGNOSTIC_V1.json"
DOC=ROOT/"MOLOSSUS_2024_SOURCE_GRAIN_DIAGNOSTIC_AFTER_OUTCOMES_V1.md"

def numeric(source):
    try:
        v=float(source)
        if math.isfinite(v):return v
    except (ValueError,TypeError):pass
    return None

def three(values):
    s=sorted(values)
    return {"min":s[0],"median":median(s),"max":s[-1]}

def run():
    if not DOC.exists():raise ValueError("STOP_GRAIN_AUDIT_NOT_LOCKED")
    raw,http,ctype=download_bounded(URL)
    z=zipfile.ZipFile(io.BytesIO(raw))
    found=[x for x in z.infolist() if x.filename.split("/")[-1]==EXPECTED]
    if len(found)!=1:raise ValueError("STOP_ORIGINAL_PNAS_XLSX_MISSING")
    orig=z.read(found[0])
    sha=hashlib.sha256(orig).hexdigest()
    if sha!=SOURCE_SHA:raise ValueError("STOP_ORIGINAL_PNAS_XLSX_SHA_CHANGED")
    rows=decode_sheet(orig)
    bats=defaultdict(list)
    numel=[]
    attacks=[]
    successes=[]
    cons=[]
    for row in rows:
        bid=str(row[0]).strip()
        bats[bid].append(row)
        for x,output in ((row[2],numel),(row[3],attacks),
                         (row[4],successes),(row[5],cons)):
            v=numeric(x)
            if v is None:raise ValueError("STOP_NON_NUMERIC_ORIGINAL_SOURCE_FIELD")
            output.append(v)
    per_bat=[]
    for bid,subset in bats.items():
        groups=[numeric(r[1]) for r in subset]
        if any(v is None for v in groups):raise ValueError("STOP_ORIGINAL_SEC_GROUP_NONNUMERIC")
        integer=all(abs(v-round(v))<1e-7 for v in groups)
        allgroup=sorted(int(round(v)) for v in groups)
        unique=len(set(allgroup))
        increment=[b-a for a,b in zip(allgroup,allgroup[1:])]
        counts=len(subset)
        source_numel_sum=sum(float(r[2]) for r in subset)
        per_bat.append({"rows":counts,
                        "group_distinct":unique,
                        "groups_integer":integer,
                        "group_min":min(allgroup),
                        "group_max":max(allgroup),
                        "group_consecutive_1":integer and unique==counts and all(x==1 for x in increment),
                        "group_consecutive_5":integer and unique==counts and all(x==5 for x in increment),
                        "group_discrepancy":counts-unique,
                        "row_count_times_5s_minutes":counts*5/60,
                        "numel_total_times_5s_minutes":source_numel_sum*5/60})
    row5_true=all(t["group_consecutive_1"] or t["group_consecutive_5"] for t in per_bat)
    return {"schema":1,
        "status":"POST_OUTCOME_GRAIN_AUDIT_COMPLETED",
        "original_study":"Krivoruchko et al 2024 PNAS DOI 10.1073/pnas.2321724121",
        "source_xlsx_sha256":sha,
        "original_rows":len(rows),"original_bats":len(bats),
        "source_sec_group_row_consecutivity_all_bats":row5_true,
        "source_sec_group_consecutive_one_bats":sum(x["group_consecutive_1"] for x in per_bat),
        "source_sec_group_consecutive_five_bats":sum(x["group_consecutive_5"] for x in per_bat),
        "original_group_numeric_min_max":three([x["group_min"] for x in per_bat]),
        "original_group_numeric_max_by_bat_range":three([x["group_max"] for x in per_bat]),
        "original_source_rows_per_bat":three([x["rows"] for x in per_bat]),
        "source_original_rows_5s_minutes_by_bat":three([x["row_count_times_5s_minutes"] for x in per_bat]),
        "bad_numel_5s_minutes_by_bat":three([x["numel_total_times_5s_minutes"] for x in per_bat]),
        "source_numel_5swindows_field_per_row":three(numel),
        "source_numel_5swindows_field_sum":sum(numel),
        "sum_attacks_field_per_row":three(attacks),
        "sum_success_field_per_row":three(successes),
        "sum_conspecific_calls_per_row":three(cons),
        "source_attacks_sum":sum(attacks),
        "source_successful_attacks_sum":sum(successes),
        "total_source_row_minutes_if_5s_each":len(rows)*5/60,
        "impossible_total_minutes_if_numel_is_exposure":sum(numel)*5/60,
        "original_source_numel_not_validated_as_exposure":True,
        "first_version_source_poisson_model_exposure_definition_invalid":True,
        "source_bat_IDs_or_original_rows_released":False,
        "new_bat_measurements":False,
        "next_required":"Versioned postoutcome correction, use one group row as one 5s interval only if this group/time audit passes and source text permits."
    }

def main():
    try:out=run()
    except Exception as e:
        out={"schema":1,"status":"STOP_GRAIN_AUDIT_SOURCE",
             "error":type(e).__name__+":"+str(e)[:190],
             "source_bat_IDs_or_original_rows_released":False,
             "new_bat_measurements":False}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("SOURCE_GRAIN_AUDIT",out["status"])
    for k in ("source_sec_group_row_consecutivity_all_bats",
              "source_sec_group_consecutive_one_bats",
              "source_sec_group_consecutive_five_bats",
              "original_source_rows_per_bat",
              "source_original_rows_5s_minutes_by_bat",
              "bad_numel_5s_minutes_by_bat",
              "source_numel_5swindows_field_per_row",
              "sum_attacks_field_per_row",
              "sum_conspecific_calls_per_row",
              "source_numel_5swindows_field_sum",
              "total_source_row_minutes_if_5s_each",
              "impossible_total_minutes_if_numel_is_exposure"):
        print("GRAIN",k,out.get(k))
    if out.get("error"):print("STOP_REASON",out["error"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
