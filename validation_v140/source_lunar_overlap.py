"""Check original 20 tide-stratified days have lunar-phase overlap.
All values derive from the original source-fingerprinted 2026 acoustic XLSX.
The true lunar illuminated fraction is NOT direct measured moonlight lux.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean
import json
from astro_confounds import augment_source
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v139"))
from empirical_reanalysis import source_rows

def binmoon(v):
    return "dark_disk_fraction_lt_25pct" if v<.25 else (
        "bright_disk_fraction_ge_75pct" if v>=.75 else "intermediate_disk_fraction")

def source_matrix():
    rows,periods,unused=source_rows()
    augment_source(rows)
    items=[]
    combo=defaultdict(Counter)
    for pid,part in sorted(periods.items(),key=lambda x:int(x[0])):
        moon=mean(r["moon"] for r in part)
        tide=mean(r["tide_coefficient"] for r in part)
        level=part[0]["coefficient_level"]
        if any(r["coefficient_level"]!=level for r in part):
            raise ValueError("More than one source tide class per original 24h block")
        nights=[r for r in part if r["night"]]
        days=[r for r in part if not r["night"]]
        if not nights or not days:
            raise ValueError("No within-source-24h day-night contrast")
        row={
            "source_24h_id":int(pid),
            "start_date_excel_serial":part[0]["anchor"],
            "tide_coefficient_class":level,
            "tide_coefficient_mean_across_retained_hours":round(tide,5),
            "tide_coefficient_min_across_retained_hours":min(r["tide_coefficient"] for r in part),
            "tide_coefficient_max_across_retained_hours":max(r["tide_coefficient"] for r in part),
            "mean_disk_illumination_fraction":round(moon,5),
            "disk_illumination_class":binmoon(moon),
            "retained_hours":len(part),
            "missing_tide_flow_masked_hours":24-len(part),
            "retained_day_hours":len(days),
            "retained_night_hours":len(nights),
            "mean_acoustic_annotations_day_per_retained_hour":round(mean(r["n_acoustic_annotations"] for r in days),5),
            "mean_acoustic_annotations_night_per_retained_hour":round(mean(r["n_acoustic_annotations"] for r in nights),5),
        }
        combo[level][row["disk_illumination_class"]]+=1
        items.append(row)
    if sum(x["retained_hours"] for x in items)!=421 or sum(x["missing_tide_flow_masked_hours"] for x in items)!=59:
        raise AssertionError("Original source total not reproduced")
    return {
        "version":"v140_20_source_blocks_lunar_overlap_1",
        "source_doi":"10.1186/s12862-026-02521-z",
        "original_workbook_sha256":"2df8fac5749d804b8d16d98db065ba19dc3796a4a01ce1cfa87c56f5d622d0d0",
        "n_original_independent_24h_sampling_blocks":20,
        "n_sites":1,
        "n_retained_hours":421,
        "n_masked_hours":59,
        "mean_lunar_disk_illumination_not_measured_moonlight":True,
        "phase_classes_are_arbitrary_descriptive_thresholds":True,
        "original_24h_block_class_by_lunar_illumination_table":{
            level:dict(sorted(comb.items())) for level,comb in sorted(combo.items())
        },
        "periods":items,
        "moon_tide_causal_separation":"NOT_IDENTIFIED",
        "coast_meta_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=source_matrix()
    out=Path(__file__).parent/"results"/"original_20day_lunar_tide_support.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    if a.check:
        assert result==json.loads(out.read_text()),"Lunar overlap frozen source audit changed"
    else:
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V140_OVERLAP_START")
    print(json.dumps(result,sort_keys=True))
    print("V140_OVERLAP_END")

if __name__=="__main__":
    main()
