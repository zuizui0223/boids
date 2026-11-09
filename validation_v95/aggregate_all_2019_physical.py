"""v95 stage-1 GLOBAL real observational physical tide×solar association generality audit.

Consumes all 12 completed v94 original UHSLC 2019 source cohorts. Does NOT infer
organism behavior, emergence of a temporal niche, prey, dry sediment, or causality.
Associations are geometrically expected to some extent; tests are descriptive.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from math import radians,sin,cos,sqrt,asin,log1p
from statistics import mean
import argparse,json
import numpy as np
from original_UHSLC_2019_tide_solar import _latitude_band
BANDS={f'{h}_{v:02d}_{v+15:02d}' for h in ('N','S') for v in (0,15,30,45,60,75)}
CLUSTER_RADIUS_KM=100.
N_PERM=5000; N_BOOT=4000; SEED=20261109
MIN_GOOD_DAYS=120

def earth_distance_km(a,b):
    lat1,lon1=radians(float(a['latitude'])),radians(float(a['longitude_signed']))
    lat2,lon2=radians(float(b['latitude'])),radians(float(b['longitude_signed']))
    dlat=lat2-lat1;dlon=lon2-lon1
    s=sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 12742*asin(min(1.,sqrt(s)))

def coastal_clusters(rows):
    # Conservative connected components: no two sites closer than 100km can masquerade as independent replicates.
    parent=list(range(len(rows)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(i,j):
        a,b=root(i),root(j)
        if a!=b:parent[max(a,b)]=min(a,b)
    for i in range(len(rows)):
        for j in range(i):
            if earth_distance_km(rows[i],rows[j])<=CLUSTER_RADIUS_KM:union(i,j)
    groups=defaultdict(list)
    for i,x in enumerate(rows):groups[root(i)].append(x)
    return [v for _,v in sorted(groups.items(),key=lambda z:min(r['uid'] for r in z[1]))]

def ranks(a):
    a=np.asarray(a,dtype=float)
    ix=np.argsort(a);out=np.empty(len(a),dtype=float)
    j=0
    while j<len(a):
        k=j+1
        while k<len(a) and a[ix[k]]==a[ix[j]]:k+=1
        out[ix[j:k]]=(j+1+k)/2.
        j=k
    return out

def pearson(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    aa=a-a.mean();bb=b-b.mean()
    den=np.linalg.norm(aa)*np.linalg.norm(bb)
    return float(aa@bb/den) if den>0 else None

def spearman(a,b):return pearson(ranks(a),ranks(b))

def macro_rows(files):
    byband={};stations=[];counts=Counter();regimes=Counter()
    for path in sorted(files):
        obj=json.loads(Path(path).read_text())
        if obj.get('analysis')!='V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL':
            raise ValueError('STOP non-v94 source artifact encountered')
        b=obj['band']
        if b not in BANDS or b in byband:raise ValueError('STOP duplicated/unknown latitude band')
        byband[b]=obj
        counts['candidate']+=obj['candidate_unique_UHSLC_station_ids']
        counts['eligible']+=len(obj['raw_station_outcomes'])
        counts['skipped_qc']+=len(obj['source_skipped_qc'])
        counts['source_failure']+=len(obj['source_failures'])
        if obj['source_candidates_attempted']!=obj['candidate_unique_UHSLC_station_ids']:
            raise ValueError('STOP v94 did not examine all genuine metadata UHSLC IDs in a band')
        for r in obj['raw_station_outcomes']:
            if _latitude_band(r['latitude'])!=b or r.get('qc')!='ADMITTED_2019_ORIGINAL_HOURLY_PHYSICAL':
                raise ValueError('STOP artifact geo/source mismatch')
            stations.append(r);regimes[r['regime']]+=1
    if set(byband)!=BANDS or counts['candidate']!=564:
        raise ValueError('STOP must inspect all 564 original station IDs across ALL 12 bands before global result')
    if len(set(x['uid'] for x in stations))!=len(stations):
        raise ValueError('STOP station ID pseudo-replication')
    if counts['candidate']!=counts['eligible']+counts['skipped_qc']+counts['source_failure']:
        raise ValueError('STOP incomplete source failure accounting')
    return stations,byband,dict(counts),dict(regimes)

def row_for_cluster(source_rows):
    rows=[x for x in source_rows if x['opportunity']['n_valid_day_low_2']>=MIN_GOOD_DAYS]
    if not rows:return None
    # No predictor/outcome grain mismatch: every cluster feature uses identical supported source gauges.
    f=lambda key:mean(float(x[key]) for x in rows)
    amp=[sum(x['harmonics_mm'].values()) for x in rows]
    lat=f('latitude')
    bands=Counter(_latitude_band(x['latitude']) for x in rows)
    band=sorted(bands,key=lambda b:(-bands[b],b))[0]
    r2=mean(x['harmonic_four_constituent_R2'] for x in rows)
    return {'cluster_source_station_n':len(source_rows),
        'gauge_station_ids':sorted(x['uid'] for x in source_rows),
        'latitude':lat,'abs_lat':abs(lat),'hemisphere':int(lat>=0),'band':band,
        'F_mean':f('form_factor_F'),
        'amp_4_const_mm':mean(amp),
        'mean_R2_4const':r2,
        'mean_daily_abs_M':mean(x['opportunity']['mean_daily_abs_M'] for x in rows),
        'mean_null_random_assignment_abs_M':mean(x['opportunity']['null_random_hour_baseline_abs_M'] for x in rows),
        'mean_fraction_paired_daylength_ge_1h':mean(x['matched_fraction_delta_low_sun_ge_1h'] for x in rows if x['matched_fraction_delta_low_sun_ge_1h'] is not None) if any(x['matched_fraction_delta_low_sun_ge_1h'] is not None for x in rows) else None,
        'n_supported_stations':len(rows)}

def features(rows,full):
    x=np.array([[x['abs_lat']/60.,float(x['hemisphere']),
                 np.log1p(x['amp_4_const_mm'])/6.]+
                ([np.log1p(x['F_mean'])] if full else [])
                for x in rows],dtype=float)
    return x

def ridge_predict(Xtr,ytr,Xte,lam=1.):
    mu=Xtr.mean(axis=0);sd=Xtr.std(axis=0)
    sd[sd<1e-10]=1.
    a=(Xtr-mu)/sd; z=(Xte-mu)/sd
    mat=np.column_stack([np.ones(len(a)),a])
    penalty=np.eye(mat.shape[1])*lam;penalty[0,0]=0.
    b=np.linalg.solve(mat.T@mat+penalty,mat.T@ytr)
    return np.column_stack([np.ones(len(z)),z])@b

def heldout_band_models(rows):
    obs=np.array([x['mean_daily_abs_M'] for x in rows],dtype=float)
    pre0=np.full(len(rows),np.nan);pre1=np.full(len(rows),np.nan)
    bands=sorted({x['band'] for x in rows})
    for band in bands:
        test=np.array([i for i,x in enumerate(rows) if x['band']==band])
        train=np.array([i for i,x in enumerate(rows) if x['band']!=band])
        if len(test)<1 or len(train)<10:continue
        pre0[test]=ridge_predict(features([rows[i] for i in train],False),
                                obs[train],features([rows[i] for i in test],False))
        pre1[test]=ridge_predict(features([rows[i] for i in train],True),
                                obs[train],features([rows[i] for i in test],True))
    good=np.isfinite(pre0)&np.isfinite(pre1)
    err0=(obs[good]-pre0[good])**2;err1=(obs[good]-pre1[good])**2
    if not len(err0):return None
    m0=float(np.mean(err0));m1=float(np.mean(err1))
    rng=np.random.default_rng(SEED)
    idx=rng.integers(0,len(err0),size=(N_BOOT,len(err0)))
    delta=np.mean(err0[idx]-err1[idx],axis=1)
    byband={b:{'n_clusters':int(sum((rows[i]['band']==b) for i in range(len(rows)) if good[i])),
       'M0_mse':float(np.mean([(obs[i]-pre0[i])**2 for i in range(len(rows)) if good[i] and rows[i]['band']==b])),
       'M1_mse':float(np.mean([(obs[i]-pre1[i])**2 for i in range(len(rows)) if good[i] and rows[i]['band']==b]))}
       for b in bands if any(good[i] and rows[i]['band']==b for i in range(len(rows)))}
    return {'baseline_features':['abs_lat','hemisphere','log1p_harmonic_total_amplitude'],
       'extra_feature':'log1p(F)',
       'assessment':'LEAVE_WHOLE_15DEG_LATITUDE_BAND_OUT_2019_SAME_YEAR_SITE_CONTEXT_NOT_FUTURE_YEAR_FORECAST',
       'clusters_with_OOF_predictions':len(err0),'tested_bands':len(byband),
       'M0_mse':m0,'M1_mse':m1,'M0_minus_M1_gain':m0-m1,
       'relative_MSE_improvement_percent':100*(m0-m1)/m0,
       'conditional_fixed_pred_cluster_resample_CI95':np.quantile(delta,[.025,.975]).tolist(),
       'by_band':byband}

def within_band_permutation(rows):
    x=np.array([np.log1p(r['F_mean']) for r in rows])
    y=np.array([r['mean_daily_abs_M'] for r in rows])
    ranks_x=ranks(x);ranks_y=ranks(y)
    cov=np.column_stack([np.ones(len(rows)),
          [r['abs_lat']/60 for r in rows],[r['hemisphere'] for r in rows]])
    resx=ranks_x-cov@np.linalg.lstsq(cov,ranks_x,rcond=None)[0]
    resy=ranks_y-cov@np.linalg.lstsq(cov,ranks_y,rcond=None)[0]
    main=pearson(resx,resy)
    bands=defaultdict(list)
    for i,r in enumerate(rows):bands[r['band']].append(i)
    rng=np.random.default_rng(SEED)
    exceed=0
    for _ in range(N_PERM):
        reordered=ranks_x.copy()
        for ind in bands.values():
            if len(ind)>1:reordered[ind]=rng.permutation(reordered[ind])
        residual=reordered-cov@np.linalg.lstsq(cov,reordered,rcond=None)[0]
        effect=pearson(residual,resy)
        if effect is not None and abs(effect)+1e-12>=abs(main):exceed+=1
    return {'unadjusted_spearman_all_independent_100km_clusters':spearman(x,y),
       'ranks_partial_pearson_adjust_abs_lat_hemisphere':main,
       'within_15deg_latitude_band_permutation_two_sided_exploratory_p':(1+exceed)/(N_PERM+1),
       'n_permutations':N_PERM,
       'regional_cluster_unit':'100km_connected_source_geolocation_regions_not_independent_individuals',
       'n_clusters':len(rows)}

def run(artifacts_dir,output):
    paths=list(Path(artifacts_dir).rglob('v94-2019-original-source-*.json'))
    if len(paths)!=12:raise ValueError('STOP expected 12 true source band JSON artifacts')
    sites,band_data,counts,regimes=macro_rows(paths)
    clusters=coastal_clusters(sites)
    rows=[row_for_cluster(x) for x in clusters]
    rows=[r for r in rows if r is not None]
    out={'analysis':'V95_TRUE_GLOBAL_2019_ORIGINAL_UHSLC_TIDAL_SOLAR_PHYSICAL_MACRO',
       'source_run_v94':42616065580,
       'source_original_station_counts':counts,'original_source_tidal_type_counts':regimes,
       'n_observed_source_100km_geo_clusters':len(clusters),
       'n_inference_100km_clusters_min120_days':len(rows),
       'inference_mean_daily_abs_M_equal_clusters':float(mean(x['mean_daily_abs_M'] for x in rows)),
       'inference_mean_random_hour_reference_abs_M':float(mean(x['mean_null_random_assignment_abs_M'] for x in rows)),
       'inference_mean_equal_daylength_1h_fraction':float(mean(x['mean_fraction_paired_daylength_ge_1h'] for x in rows if x['mean_fraction_paired_daylength_ge_1h'] is not None)),
       'inference_tidal_type_group_ranges':{},
       'source_gauge_by_band':{b:{'candidates':v['candidate_unique_UHSLC_station_ids'],
           'admitted':len(v['raw_station_outcomes']),'failures':len(v['source_failures'])}
           for b,v in sorted(band_data.items())},
       'statistical_boundary':'ANALYSIS_POST_V93_OUTCOME_PHYSICAL_ONLY; NO_ANIMAL_TIME_NICHE; LIMITED_TO_2019',
       'selection':'all preexisting original 564 station IDs; source QC-only, 2019; no selecting high tide x sunlight overlap',
       'independence':'each spatial 100km connected coastal group is given one average across source gauge IDs'}
    for kind in sorted(set(x['band'] for x in rows)):pass
    classified=defaultdict(list)
    for r in rows:
        # Group uses median physical form factor over admitted sources, not arbitrary site records.
        f=r['F_mean']; category='semidiurnal' if f<.25 else 'mixed_semidiurnal' if f<1.5 else 'mixed_diurnal' if f<3 else 'diurnal'
        classified[category].append(r)
    out['inference_tidal_type_group_ranges']={
       c:{'geo_clusters':len(z),'mean_daily_abs_M':float(mean(x['mean_daily_abs_M'] for x in z)),
          'range_daily_abs_M':[min(x['mean_daily_abs_M'] for x in z),max(x['mean_daily_abs_M'] for x in z)]}
       for c,z in classified.items()}
    if len(rows)>=12:
        out['regional_band_constrained_association']=within_band_permutation(rows)
        out['out_of_latitude_band_association']=heldout_band_models(rows)
        for amp in (10.,25.,50.,100.):
            for r2 in (.2,.4,.6):
                subset=[r for r in rows if r['amp_4_const_mm']>=amp and r['mean_R2_4const']>=r2]
                if len(subset)<10:continue
                out.setdefault('tidal_constituent_quality_sensitivity',[]).append({
                   'min_four_constituent_amplitude_mm':amp,'min_four_constituent_R2':r2,
                   'n_clusters':len(subset),
                   'F_vs_daily_absM_spearman':spearman(
                      [r['F_mean'] for r in subset],[r['mean_daily_abs_M'] for r in subset])})
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V95_TRUE_2019_PHYSICAL_GLOBAL '+json.dumps(out,sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--artifact-dir',required=True);a.add_argument('--output',required=True)
    o=a.parse_args();run(o.artifact_dir,o.output)
