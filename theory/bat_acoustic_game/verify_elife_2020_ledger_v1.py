"""Validate committed aggregate ledger against freshly obtained original 2020 sources.
Never downloads animal telemetry or overwrites a published source file.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"ELIFE_FIG2_SOURCE_COMPARISON_V1.json"
LEDGER=ROOT/"ELIFE_2020_SOURCE_PAYOFF_LEDGER_V1.json"

def close(a,b):
    return a is not None and b is not None and math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-9)

def main():
    report=json.loads(SOURCE.read_text())
    led=json.loads(LEDGER.read_text())
    assert report["status"]=="SECONDARY_PUBLISHED_SIMULATION_OUTPUT_REANALYSIS"
    assert led["status"]=="SECONDARY_PUBLISHED_SIMULATION_OUTPUT_REANALYSIS_NOT_NEW_BAT_EVIDENCE"
    for key in ("correlation","filter_bank"):
        r=report["results"][key]
        f=led["fig2"][key]
        assert r["source"]["source_sha"]==f["sha256"]
        assert r["source"]["rows"]==f["rows"]==240
        assert len(r["groups"])==len(f["group_size_cells"])==6
        for row,a in zip(r["groups"],f["group_size_cells"]):
            assert row["number_of_bats"]==a["group_size"]
            assert row["no_JAR_row_count"]==row["JAR_row_count"]==a["output_rows_per_JAR_arm"]==20
            m=row["metric_summaries"]
            assert close(m["NumberOfCatches"]["JAR_minus_noJAR"],a["delta_catches"])
            assert close(m["TotalInterferenceRatio"]["JAR_minus_noJAR"],a["delta_total_interference_ratio"])
            if key=="correlation":
                assert close(m["NumberOfInterfernces"]["JAR_minus_noJAR"],a["delta_interference_count"])
            else:
                assert close(m["fb_FA_rate"]["JAR_minus_noJAR"],a["delta_fb_false_alarm_rate"])
                assert close(m["NumberOfCatches"]["without_JAR"]["mean"],a["mean_catches_no_JAR"])
                assert close(m["NumberOfCatches"]["with_JAR"]["mean"],a["mean_catches_JAR"])
        if key=="correlation":
            assert close(r["balanced_groups_JAR_minus_noJAR"]["NumberOfCatches"],f["equal_group_delta_catches"])
        else:
            for metric,field in [
                ("NumberOfCatches","balanced_delta_catches"),
                ("TotalInterferenceRatio","balanced_delta_total_interference_ratio"),
                ("fb_FA_rate","balanced_delta_fb_false_alarm_rate")]:
                assert close(r["balanced_groups_JAR_minus_noJAR"][metric],f[field])
    print("ORIGINAL_ELIFE_2020_LEDGER_MATCHES_SOURCE_EXACTLY")
    return 0

if __name__=="__main__":raise SystemExit(main())
