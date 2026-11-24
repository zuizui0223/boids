"""v9b original ayu 7-file source semantics audit, no movement prediction.
Author MATLAB code D(:,3:12) x and D(:,13:22) y at analytical 20fps.
Read actual source values only for numeric support, all behavior models unopened.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from ayu_source_gate import FILES,PIN,blobsha,SourceStop

def one_source(path,expected_sha,expected_size):
    b=Path(path).read_bytes()
    if len(b)!=expected_size or blobsha(b)!=expected_sha:
        raise SourceStop("ORIGINAL_SOURCE_GIT_BLOB_CHANGED")
    D=np.loadtxt(path,dtype=np.float64)
    if D.ndim!=2 or D.shape[1]!=22 or D.shape[0]<5000:
        raise SourceStop("ORIGINAL_AUTHORS_COLUMN_OR_ROWS_STOP")
    x,y=D[:,2:12],D[:,12:22]
    xy=np.stack((x,y),axis=-1)
    fin=np.isfinite(xy).all(axis=2)
    if float(fin.mean())<.95:raise SourceStop("ORIGINAL_TRACK_NONFINITE_SUPPORT_STOP")
    def panel(a):
       ok=np.isfinite(a)
       if not ok.any():return {"finite":0}
       z=a[ok]
       d=np.diff(a)
       good=d[np.isfinite(d)]
       return {"finite_fraction":float(ok.mean()),"min":float(z.min()),
           "max":float(z.max()),
           "median_consecutive_delta":float(np.median(good)) if len(good) else None,
           "consecutive_positive_fraction":float((good>0).mean()) if len(good) else None,
           "consecutive_zero_fraction":float((good==0).mean()) if len(good) else None}
    return {"rows":int(len(D)),"columns":int(D.shape[1]),
       "source_column_map":"author D MATLAB x=3:12 y=13:22, first 2 unused",
       "first_col":panel(D[:,0]),"second_col":panel(D[:,1]),
       "fraction_full_10_fish_xy_finite_by_row":float(fin.all(axis=1).mean()),
       "fraction_fish_xy_finite":float(fin.mean()),
       "x_range":[float(np.nanmin(x)),float(np.nanmax(x))],
       "y_range":[float(np.nanmin(y)),float(np.nanmax(y))],
       "zero_coordinate_fraction":float(np.mean(xy==0)),
       "original_git_sha":expected_sha}
def run(root):
    base=Path(root)/"Compute_IIT/fish_revised"
    rows=[]
    for name,(sha,size) in FILES.items():
        try:
           obj=one_source(base/name,sha,size)
           rows.append({"filename":name,"status":"SOURCE_STRUCTURE_PASS",**obj})
        except (ValueError,SourceStop,OSError) as e:
           rows.append({"filename":name,"status":"SOURCE_STOP","reason":str(e)})
    return {"version":"v9b_ayu_numeric_schema_source_only_20261120",
       "source_original_commit":PIN,"original_X_Y_authors_matlab_index_verified":True,
       "published_analytical_sample_rate_hz":20,
       "n_source_files":7,
       "n_source_pass":sum(z["status"]=="SOURCE_STRUCTURE_PASS" for z in rows),
       "source_records":rows,"source_trajectory_values_exported":False,
       "behavior_model_fitted":False,
       "status":"SEVEN_SOURCE_NUMERIC_SCHEMAS_ADMITTED" if all(z["status"]=="SOURCE_STRUCTURE_PASS" for z in rows) else "SOURCE_STOP"}
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    a=p.parse_args();r=run(a.root)
    path=Path("validation_fish_school_v9/results/ayu_numeric_source_semantics.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":r["status"],"source_pass":r["n_source_pass"],
      "summary":[{"file":x["filename"],"status":x["status"],
        "rows":x.get("rows"),"xy_complete":x.get("fraction_full_10_fish_xy_finite_by_row"),
        "xrange":x.get("x_range"),"yrange":x.get("y_range"),
        "time0":x.get("first_col"),"meta1":x.get("second_col"),"error":x.get("reason")}
       for x in r["source_records"]]}))
