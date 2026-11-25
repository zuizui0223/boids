"""Structural diagnostic after v54 duration STOP. No model fit or future outcomes."""
import hashlib,json,zipfile,subprocess,io,sys
from pathlib import Path,PurePosixPath
import numpy as np
import pandas as pd
from validation_fish_school_v54.illumination_triads import COMMIT,ARCH,EXPECTED,PREFIX,git,sha
root=Path(sys.argv[1])
out={'status':'SOURCE_SCHEMA_ONLY','author_commit':COMMIT,'prediction_scores_exported':False,'archives':{},'trials':{}}
if git(root,'rev-parse','HEAD')!=COMMIT:raise ValueError('SOURCE_DRIFT')
for fn,n in ARCH.items():
 p=root/fn;blob=git(root,'rev-parse',COMMIT+':'+fn)
 assert git(root,'hash-object',str(p.resolve()))==blob
 out['archives'][fn]={'git_blob':blob,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
 with zipfile.ZipFile(p) as z:
  inf=z.infolist();assert sum(x.file_size for x in inf)<=300_000_000 and len({x.filename for x in inf})==len(inf)
  for x in inf:
   name=x.filename;q=PurePosixPath(name)
   assert not q.is_absolute() and '..' not in q.parts and '\\' not in name
   if x.is_dir() or '__MACOSX' in q.parts or q.name.startswith('.') or q.suffix.lower()!='.csv':continue
   condition=[c for c in EXPECTED if c.startswith(PREFIX[n]+'-') and c in q.parts[:-1]]
   assert len(condition)==1 and x.file_size<=20_000_000
   b=z.read(x);header=b.splitlines()[0].decode('utf-8-sig')
   required=['Frame','Time']+[v for i in range(n) for v in (f'X_Arena0_Ind{i}',f'Y_Arena0_Ind{i}')]
   row={'condition':condition[0],'sha256':sha(b),'bytes':len(b),'header':header}
   out['trials'][fn+'/'+name]=row
   sep=next((v for v in [';',',','\t'] if header.split(v)==required),None)
   if sep is None:row['status']='HEADER_STOP';continue
   try:
    d=pd.read_csv(io.StringIO(b.decode('utf-8-sig')),sep=sep,keep_default_na=False,na_values=['','NA','NaN','nan','N/A']).apply(pd.to_numeric,errors='raise').to_numpy(float)
   except Exception as e:
    row['status']='TOKEN_STOP';row['error_type']=type(e).__name__;continue
   f,t=d[:,:2].T;p0=d[:,2:].reshape(len(f),n,2)
   row.update(status='STRUCTURE_READ',rows=len(f),all_clock_finite=bool(np.isfinite(d[:,:2]).all()),integer_frame=bool((f==np.round(f)).all()),strict_frame=bool((np.diff(f)>0).all()),strict_time=bool((np.diff(t)>0).all()),frame_span=float(f[-1]-f[0]+1),duration_seconds=float(t[-1]-t[0]),clock_30hz_max_error_seconds=float(np.max(np.abs(t-t[0]-(f-f[0])/30))),native_step_median=float(np.median(np.diff(f))),time_step_median_seconds=float(np.median(np.diff(t))),finite_xy_fraction=float(np.isfinite(p0).all(-1).mean()),coordinate_max_radius=float(np.nanmax(np.linalg.norm(p0,axis=-1))),coordinate_min_xy=np.nanmin(p0,axis=(0,1)).tolist(),coordinate_max_xy=np.nanmax(p0,axis=(0,1)).tolist())
out['counts']={c:sum(v['condition']==c for v in out['trials'].values()) for c in EXPECTED}
out['original_expected_counts_match']=out['counts']==EXPECTED
p=Path('validation_fish_school_v54/results/schema_diagnostic.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':out['status'],'counts':out['counts'],'archives':out['archives'],'rows_and_clock':[{'file':k,**{x:v.get(x) for x in ('status','rows','frame_span','duration_seconds','native_step_median','time_step_median_seconds','clock_30hz_max_error_seconds','coordinate_max_radius','finite_xy_fraction')}} for k,v in out['trials'].items()]},sort_keys=True))
