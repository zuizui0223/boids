"""v139: verify 421 actual annotated hours against 480 selected hours and
the hourly environmental table in the primary original supplement.

No ecological interaction fitted by this first diagnostics stage; outcomes
will be separately audited before a preregistered contrast is computed.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import json
import hashlib
from math import isfinite
from pathlib import Path
from statistics import mean, median
from source_probe import acquire, read_xlsx_table_rows

SOURCE_SHA="2df8fac5749d804b8d16d98db065ba19dc3796a4a01ce1cfa87c56f5d622d0d0"
ROOT=Path(__file__).resolve().parents[1]

def number(s):
    try:
        val=float(s)
    except (ValueError, TypeError):
        return None
    return val if isfinite(val) else None

def acol(idx):
    out=""
    while idx:
        idx,rem=divmod(idx-1,26)
        out=chr(65+rem)+out
    return out

def key_from(s_date,s_hour,is_fraction=False):
    d=number(s_date);h=number(s_hour)
    if d is None or h is None:
        raise ValueError("source key missing calendar date or hour")
    hh=round(h*24 if is_fraction else h)
    if abs((h*24 if is_fraction else h)-hh)>0.001 or hh<0 or hh>23:
        raise ValueError("not an integral local 0-23 observation hour")
    return (int(round(d)),hh)

def audit():
    raw=acquire()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA:
        raise AssertionError("Original source bytes changed. Reaudit sha "+sha)
    all_tables=read_xlsx_table_rows(raw)
    table=all_tables["Table S1"]
    h=table[3]
    sound_cols=[acol(i) for i in range(16,42)] # P through AO, 26 sound types
    if len(set(h.get(c) for c in sound_cols))!=26:
        raise ValueError("Expected 26 unique sound types, original headers changed")
    annotations=[]
    for rowno,r in sorted(table.items()):
        if rowno<4:continue
        key=key_from(r.get("C"),r.get("D"))
        val=[]
        for col in sound_cols:
            n=number(r.get(col))
            if n is None or n<0 or abs(n-round(n))>1e-6:
                raise ValueError("Invalid actual acoustic sound count at "+str(rowno)+col)
            val.append(int(round(n)))
        annotations.append({
            "key":key,"source_replicate_id":r.get("A"),
            "day":r.get("B"),"source_period":r.get("E"),
            "coefficient_level":r.get("L"),
            "water_m":number(r.get("J")),
            "lux":number(r.get("G")),
            "wave_m":number(r.get("O")),
            "sound_count":sum(val),"sound_type_richness":sum(x>0 for x in val)})
    if len({x["key"] for x in annotations})!=len(annotations):
        raise ValueError("Repeated source hour key across 421 original rows")
    env=all_tables["Table S2"]
    env_rows={}
    for rowno,r in sorted(env.items()):
        if rowno<3:continue
        try:key=key_from(r.get("A"),r.get("B"),is_fraction=True)
        except ValueError:continue
        if key in env_rows:
            raise ValueError("Duplicate environmental hour key")
        env_rows[key]={
            "water_m":number(r.get("G")),
            "lux":number(r.get("D")),
            "wind":number(r.get("E")),
            "wave_m":number(r.get("H"))}
    days=sorted(set(x["key"][0] for x in annotations))
    scheduled={(d,h) for d in days for h in range(24)}
    observed={x["key"] for x in annotations}
    absent=scheduled-observed
    not_in_environment=scheduled-set(env_rows)
    water_diff=[abs(x["water_m"]-env_rows[x["key"]]["water_m"])
                for x in annotations
                if x["key"] in env_rows and x["water_m"] is not None
                and env_rows[x["key"]]["water_m"] is not None]
    summary={}
    for period in sorted(set(x["source_period"] for x in annotations)):
        present=[x for x in annotations if x["source_period"]==period]
        summary[period]={
            "observed_hours":len(present),
            "sound_annotations":sum(x["sound_count"] for x in present),
            "mean_sound_annotations_per_hour":round(mean(x["sound_count"] for x in present),6),
            "mean_sound_types_per_hour":round(mean(x["sound_type_richness"] for x in present),6),
            "mean_height_m":round(mean(x["water_m"] for x in present if x["water_m"] is not None),6)}
    by_level=defaultdict(list)
    for x in annotations:
        by_level[x["coefficient_level"]].append(x)
    levels={str(t):{
        "sampled_hours":len(rows),
        "mean_abundance":round(mean(x["sound_count"] for x in rows),6),
        "mean_richness":round(mean(x["sound_type_richness"] for x in rows),6)}
        for t,rows in sorted(by_level.items())}
    if not water_diff:
        raise ValueError("No environmental table matched to acoustic hours")
    return {
        "version":"v139_original_workbook_observability_audit_1",
        "doi":"10.1186/s12862-026-02521-z",
        "source_sha256":sha,"source_xlsx_bytes":len(raw),
        "all_table_s1_headers":h,
        "annotated_unique_hours":len(observed),
        "primary_paper_annotated_hours":421,
        "source_sound_types":len(sound_cols),
        "source_sound_annotations":sum(x["sound_count"] for x in annotations),
        "primary_paper_reported_annotations":6172,
        "source_unique_24h_periods":len(set(x["day"] for x in annotations)),
        "source_unique_excel_dates":len(days),
        "scheduled_24h_period_hours_if_one_date_per_period":len(scheduled),
        "source_missing_from_scheduled_hours":len(absent),
        "scheduled_hours_without_environment_record":len(not_in_environment),
        "environmental_hours_in_sheet":len(env_rows),
        "mean_absolute_waterheight_difference_between_sheets":round(mean(water_diff),8),
        "max_absolute_waterheight_difference_between_sheets":round(max(water_diff),8),
        "by_published_day_night_period":summary,
        "by_tidal_coefficient_level":levels,
        "original_source_dates_excel_serial":days,
        "missing_hour_keys_sample":sorted(absent)[:16],
        "measured_outcome":"hourly acoustic sound type annotations and richness, not individually identified animals",
        "independent_coasts":1,
        "excluded_hours_have_masking_risk":True,
        "global_pooled_effect":"NOT_ESTIMATED"
    }

def main():
    obj=audit()
    out=Path(__file__).parent/"original_observability_diagnostic.json"
    out.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print("V139_DIAG_START")
    print(json.dumps(obj,sort_keys=True,ensure_ascii=False))
    print("V139_DIAG_END")

if __name__=="__main__":
    main()
