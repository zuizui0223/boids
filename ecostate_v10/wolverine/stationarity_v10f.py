#!/usr/bin/env python3
"""v10f POST-RESULT source QC: distinguish stationary steps from copied environmental states.

No ecological choice model is fitted. Uses only official 2017 Wolverine workbook
with checksum verified by field_v10c.source. Exports pooled, nonidentifying
counts/quantiles, never individual locations or tag identifiers.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np
from field_v10c import source,build,group_admit

def quant(a):
    a=np.asarray(a,dtype=float)
    if not np.isfinite(a).all():raise ValueError('BAD_NONFINITE')
    q=np.quantile(a,[0,.01,.1,.25,.5,.75,.9,.99,1.])
    return {n:float(v) for n,v in zip(('min','q01','q10','q25','median','q75','q90','q99','max'),q)}

def fraction(a):
    return float(np.mean(a)) if len(a)>0 else None

def run(d,groups):
    u=d['used']==1
    if int(u.sum())!=len(groups):raise ValueError('INVALID_GROUP_STRUCTURE')
    sl=d['sl']
    rd=np.abs(d['road_end']-d['road_start'])
    sd=np.abs(d['stream_end']-d['stream_start'])
    eqr=rd<=1e-10
    eqs=sd<=1e-10
    both=eqr&eqs
    bins=[(0,1),(1,10),(10,30),(30,100),(100,300),(300,1000),(1000,float('inf'))]
    out={'schema':'ecostate.v10f.wolverine_original_source_motion_state_qc',
      'evidence_class':'postresult_source_artifact_diagnostic_not_field_selection_test',
      'status':'SOURCE_QUALITY_AUDIT_COMPUTED',
      'source_rows':len(u),'source_groups':len(groups),
      'moving_thresholds_m':[1,10,30,100,300,1000],
      'per_case':{},'by_length_bin':[],
      'claim_boundary':'Identical source and end covariates can reflect real stationarity, identical raster cells, source preparation, or variable copying. Without locations and process metadata no one cause is established.'}
    for name,mask in (('used',u),('available',~u)):
        out['per_case'][name]={
          'n':int(mask.sum()),'step_length_m':quant(sl[mask]),
          'zero_length_exact_fraction':fraction(sl[mask]==0),
          'fraction_step_le_1m':fraction(sl[mask]<=1),
          'fraction_step_le_10m':fraction(sl[mask]<=10),
          'fraction_step_le_30m':fraction(sl[mask]<=30),
          'fraction_step_le_100m':fraction(sl[mask]<=100),
          'fraction_exact_road_change_zero':fraction(eqr[mask]),
          'fraction_exact_stream_change_zero':fraction(eqs[mask]),
          'fraction_both_exact_zero':fraction(both[mask]),
          'fraction_both_zero_for_steps_gt_100m':fraction(both[mask & (sl>100)]),
          'steps_gt_100m':int(np.sum(mask & (sl>100))),
          'fraction_road_delta_gt_sl':fraction(rd[mask]>sl[mask]+1e-5),
          'fraction_stream_delta_gt_sl':fraction(sd[mask]>sl[mask]+1e-5)}
    for lo,hi in bins:
        row={'bin_m':[lo,None if hi==float('inf') else hi]}
        for name,mask in (('used',u),('available',~u)):
            mm=mask&(sl>=lo)&(sl<hi)
            row[name]={'n':int(mm.sum()),'road_exact_same':fraction(eqr[mm]),
                       'stream_exact_same':fraction(eqs[mm]),
                       'both_exact_same':fraction(both[mm]),
                       'road_delta_gt_sl':fraction(rd[mm]>sl[mm]+1e-5)}
        out['by_length_bin'].append(row)
    rank=[]
    for _,idx in groups:
        idx=np.asarray(idx,dtype=int)
        subsl=sl[idx]
        used=np.flatnonzero(u[idx])
        if len(used)!=1:raise ValueError('INVALID_USED')
        usl=subsl[used[0]]
        av=np.delete(subsl,used[0])
        rank.append(float((av>usl).mean()+0.5*(av==usl).mean()))
    out['used_step_length_rank_vs_20_source_alternatives']={
      'mean_fraction_longer_with_half_ties':float(np.mean(rank)),
      'median':float(np.median(rank)),
      'fraction_used_in_shortest_decile':float(np.mean(np.asarray(rank)>=.9))}
    return out

def main(out):
    result={'status':'SOURCE_OR_MODEL_STOP','evidence_class':'postresult_source_artifact_diagnostic_not_field_selection_test'}
    try:
        t,p=source()
        try:d,qc=build(p)
        finally:t.cleanup()
        groups,qc=group_admit(d,qc)
        result=run(d,groups)
        result['source_qc']=qc
    except Exception as e:
        result['reason']=str(e)[:1200]
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('V10F_ORIGINAL_SOURCE',result['status'])
    if result['status']=='SOURCE_QUALITY_AUDIT_COMPUTED':
        for k,v in result['per_case'].items():
            print('V10F_CASE',k,json.dumps(v,separators=(',',':')))
        print('V10F_LENGTH_BINS',json.dumps(result['by_length_bin'],separators=(',',':')))
        print('V10F_LENGTH_RANK',json.dumps(result['used_step_length_rank_vs_20_source_alternatives']))
    else:print('STOP_REASON',result.get('reason',''))
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v10/results/wolverine_source_stationarity_v10f.json')
