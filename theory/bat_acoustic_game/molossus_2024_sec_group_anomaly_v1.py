"""Post-outcome targeted original sec_group gap/duplicate diagnosis.

Reports only anonymized aggregate anomaly counts and min/max source group
coverage, not bat identity or source row values.
"""
from __future__ import annotations
from collections import defaultdict,Counter
from pathlib import Path
from statistics import median
import io,hashlib,json,zipfile

from molossus_2024_supplement_structure_v1 import download_bounded,URL,EXPECTED
from molossus_2024_source_capture_LOBO_v1 import decode_sheet,SOURCE_SHA

OUT=Path(__file__).resolve().parent/"MOLOSSUS_2024_ONE_BAT_GRAIN_ANOMALY_V1.json"
def run():
    binary,_,_=download_bounded(URL)
    z=zipfile.ZipFile(io.BytesIO(binary))
    files=[v for v in z.infolist() if v.filename.split("/")[-1]==EXPECTED]
    assert len(files)==1
    raw=z.read(files[0])
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    rows=decode_sheet(raw)
    bat_groups=defaultdict(list)
    for r in rows:
        bat_groups[str(r[0])].append(int(float(r[1])))
    summary=[]
    for bat,keys in bat_groups.items():
        c=Counter(keys)
        values=sorted(c)
        gaps=sum(b-a-1 for a,b in zip(values,values[1:]) if b>a+1)
        unique=len(values)
        repeated=sum(count-1 for count in c.values())
        deltas=[b-a for a,b in zip(values,values[1:])]
        summary.append({
            "n_rows":len(keys),"distinct_time_group_count":unique,
            "min_group_index":min(values),"max_group_index":max(values),
            "missing_group_index_count_between_minmax":gaps,
            "duplicate_group_index_count":repeated,
            "non_unit_group_increments":sum(1 for d in deltas if d!=1),
            "all_source_5s_group_indices_unique_and_consecutive":
               repeated==0 and gaps==0
        })
    anomalies=[x for x in summary if not x["all_source_5s_group_indices_unique_and_consecutive"]]
    return {
      "schema":1,
      "status":"SOURCE_POSTOUTCOME_ONE_BAT_INTERVAL_GRAIN_DIAGNOSTIC",
      "source_sha256":SOURCE_SHA,
      "source_original_5sec_groups_n":len(rows),
      "source_original_bats_n":len(summary),
      "bats_with_unique_and_consecutive_sec_group":len(summary)-len(anomalies),
      "bat_groups_with_anomalies_n":len(anomalies),
      "anomalous_bat_only_structure":anomalies,
      "original_bat_IDs_or_raw_rows_exported":False,
      "first_version_numel_5swindows_exposure_invalid":True,
      "new_bat_measurements":False,
      "possible_next_action":"Correct to source rows-as-5-sec only under a separately frozen postoutcome contract; 9 source-clean bats primary, all 10 secondary only if anomalies source-interpretable."
    }
def main():
    try:a=run()
    except Exception as e:a={"schema":1,"status":"STOP_ORIGINAL_ANOMALY_SOURCE",
       "reason":str(e)[:200],"original_bat_IDs_or_raw_rows_exported":False,
       "new_bat_measurements":False}
    OUT.write_text(json.dumps(a,indent=2)+"\n")
    print("BAT_GROUP_SOURCE_ANOMALY",a)
    return 0
if __name__=="__main__":raise SystemExit(main())
