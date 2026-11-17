#!/usr/bin/env python3
"""v11c INDEPENDENT buffalo GPS x native raster whole-node-heldout equal-length bearing-choice test.

Before any biological source response was opened, see
INDEPENDENT_STATE_FIDELITY_PROTOCOL.md (2026-11-17).

All real and 20 alternative endpoints are extracted with the same function
from the exact same native raster. Observed step length and origin are held
fixed, alternatives are directed bearings at 2*pi increments. No raw animal
GPS coordinates or device identifiers are exported.
"""
from __future__ import annotations
import collections,hashlib,json,math,sys,tempfile,urllib.request
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

from buffalo_geo_qc import API, original_file,FILES,source_qc

SEED=20261117
ALT=20
MAX_GROUPS_PER_NODE=900
MIN_GROUPS_PER_NODE=100
MIN_NODES=10
BOOT=10000
L2=.02
EPS=1e-8
FEATURES0=['canopy_end','herb_end','slope_end','turn_cos','turn_sin',
           'canopy_diel_cos','canopy_diel_sin','herb_diel_cos','herb_diel_sin']
FEATURES1=FEATURES0+['canopy_abs_change','herb_state_switch']

_RASTER_CACHE={}

def sample_raster(ds,x,y):
    """Exact same affine and nodata/exterior gate for actual and alternatives."""
    col,row=~ds.transform * (np.asarray(x,dtype=float),np.asarray(y,dtype=float))
    ok=(np.isfinite(col)&np.isfinite(row)&(col>=0)&(row>=0)&
        (col<ds.width)&(row<ds.height))
    jj=np.clip(np.floor(col).astype(int),0,ds.width-1)
    ii=np.clip(np.floor(row).astype(int),0,ds.height-1)
    if ds.name not in _RASTER_CACHE:
        _RASTER_CACHE[ds.name]=ds.read(1)
    a=_RASTER_CACHE[ds.name]
    v=np.asarray(a[ii,jj],dtype=float)
    ok&=np.isfinite(v)
    if ds.nodata is not None:ok&=(v!=ds.nodata)
    v[~ok]=np.nan
    return v

def circular_options(x0,y0,x1,y1,n=ALT):
    """n same-distance bearing alternatives, one used endpoint for each stratum."""
    angle=math.atan2(y1-y0,x1-x0)
    length=math.hypot(x1-x0,y1-y0)
    # 20 deterministic angular offsets, none equal to the actual bearing.
    bearings=angle+2*math.pi*np.arange(1,n+1)/(n+1)
    xs=np.r_[x1,x0+length*np.cos(bearings)]
    ys=np.r_[y1,y0+length*np.sin(bearings)]
    return xs,ys

def prepare_tracks(table,crs):
    import pandas as pd
    from rasterio.warp import transform
    dt=pd.to_datetime(table['timestamp'],errors='coerce',utc=True)
    node=table['node'].astype(str).str.strip()
    lat=pd.to_numeric(table['lat'],errors='coerce')
    lon=pd.to_numeric(table['lon'],errors='coerce')
    valid=dt.notna() & lat.between(-90,90) & lon.between(-180,180) & node.ne('') & node.ne('nan')
    df=pd.DataFrame({'node':node[valid].to_numpy(),'datetime':dt[valid].to_numpy(),
                     'lat':lat[valid].to_numpy(),'lon':lon[valid].to_numpy()})
    # Reject duplicated node x timestamp pairs as ambiguous, not arbitrary keep-first.
    dupe=df.duplicated(['node','datetime'],keep=False)
    bad_dupe=int(dupe.sum())
    df=df.loc[~dupe].sort_values(['node','datetime']).reset_index(drop=True)
    x,y=transform('EPSG:4326',crs.to_string(),df['lon'].to_list(),df['lat'].to_list())
    df['x']=np.array(x,dtype=float)
    df['y']=np.array(y,dtype=float)
    qc={'original_rows':len(table),'valid_gps_with_timestamp_rows':int(valid.sum()),
        'duplicate_node_time_rows_excluded':bad_dupe,
        'unique_node_tokens_after_QC':int(df.node.nunique())}
    return df,qc

def make_groups(df):
    """Construct 3 consecutive source fix triples at hourly cadence, no location joins."""
    grouped={};valid_all=0
    for node,g in df.groupby('node',sort=True):
        g=g.sort_values('datetime')
        xx=g.x.to_numpy(float);yy=g.y.to_numpy(float)
        ts=g.datetime.astype('int64').to_numpy()/1e9
        if len(g)<3:continue
        d1=np.diff(ts)/3600.
        delta1=d1[:-1];delta2=d1[1:]
        good=(delta1>=.75)&(delta1<=1.25)&(delta2>=.75)&(delta2<=1.25)
        x0=xx[:-2];y0=yy[:-2];x1=xx[1:-1];y1=yy[1:-1];x2=xx[2:];y2=yy[2:]
        prev=np.hypot(x1-x0,y1-y0)
        dist=np.hypot(x2-x1,y2-y1)
        good &= (prev>=20)&(prev<=5000)&(dist>=20)&(dist<=5000)
        idx=np.flatnonzero(good)
        valid_all+=len(idx)
        if len(idx)<MIN_GROUPS_PER_NODE:continue
        # deterministic inclusion, no use of habitat values or movement labels.
        keep=idx[np.round(np.linspace(0,len(idx)-1,min(MAX_GROUPS_PER_NODE,len(idx)))).astype(int)]
        grouped[str(node)]=(np.stack([x0[keep],y0[keep],x1[keep],y1[keep],x2[keep],y2[keep]],axis=1),
                            pd_time_hour(g.datetime.iloc[2:].iloc[keep]))
    return grouped,{'hourly_movement_triples_before_subsampling':int(valid_all),
        'nodes_with_minimum_100_hourly_triples':len(grouped),
        'candidate_groups_before_raster_QC':int(sum(len(x[0]) for x in grouped.values()))}

def pd_time_hour(datetimes):
    import pandas as pd
    return pd.to_datetime(datetimes,utc=True).dt.hour.to_numpy(dtype=float)

def make_design(startxy,pairs,hour,ds):
    """Sample genuine and twenty simulated endpoints from identical native rasters."""
    x0,y0,x1,y1,x2,y2=pairs
    xx,yy=circular_options(x1,y1,x2,y2)
    # Current used movement is from (x1,y1), previous from (x0,y0).
    previous=math.atan2(y1-y0,x1-x0)
    bearings=np.arctan2(yy-y1,xx-x1)
    turns=bearings-previous
    starts=[];ends=[]
    for d in ds:
        starts.append(sample_raster(d,np.array([x1]),np.array([y1]))[0])
        ends.append(sample_raster(d,xx,yy))
    if not np.isfinite(np.array(starts)).all() or not np.isfinite(np.array(ends)).all():
        return None
    ca,herb,slope=ends
    sco,sh,ss=starts
    if not (np.isfinite([sco,sh,ss]).all() and (np.abs(ca).max()<=1000)):
        return None
    rad=2*math.pi*hour/24.
    aa=[ca,herb,slope,np.cos(turns),np.sin(turns),ca*np.cos(rad),ca*np.sin(rad),
        herb*np.cos(rad),herb*np.sin(rad),np.abs(ca-sco),np.abs(herb-sh)>.5]
    return np.stack(aa,axis=1).astype(float)

def condloss(beta,x,sizes,starts,used,weights):
    z=x@beta
    m=np.maximum.reduceat(z,starts)
    p=np.exp(z-np.repeat(m,sizes))
    den=np.add.reduceat(p,starts)
    val=m+np.log(den)-z[used]
    value=float(weights@val+.5*L2*(beta@beta))
    grad=x.T@(np.repeat(weights/den,sizes)*p) - x[used].T@weights + L2*beta
    return value,grad

def fit_heldout(grouped,source_qc_data=None):
    ids=sorted(grouped,key=lambda a:hashlib.sha256(a.encode()).hexdigest())
    if len(ids)<MIN_NODES:raise ValueError('SOURCE_SCHEMA_STOP_TOO_FEW_NODE_GROUPS')
    fold={a:i%5 for i,a in enumerate(ids)}
    groupX=[];groupids=[];accepted=collections.Counter();rejected=collections.Counter()
    for a in ids:
        for x in grouped[a]:
            if x is None or x.shape!=(ALT+1,len(FEATURES1)) or not np.isfinite(x).all():
                rejected[a]+=1;continue
            groupX.append(x);groupids.append(a);accepted[a]+=1
    ids=[a for a in ids if accepted[a]>=MIN_GROUPS_PER_NODE]
    if len(ids)<MIN_NODES:raise ValueError('SOURCE_SCHEMA_STOP_NOT_ENOUGH_RASTER_ADMITTED_NODES')
    keep=[i for i,a in enumerate(groupids) if a in ids]
    groupX=[groupX[i] for i in keep]; groupids=np.array([groupids[i] for i in keep],object)
    XX=np.concatenate(groupX,axis=0)
    sizes=np.full(len(groupX),ALT+1,dtype=int)
    starts=np.arange(len(groupX))* (ALT+1)
    chosen=starts.copy()
    loss={a:{'M0':[],'M1':[]} for a in ids}
    signs=[]
    fold_nodes={a:i%5 for i,a in enumerate(ids)}
    for k in range(5):
        training=np.flatnonzero(np.array([fold_nodes[a]!=k for a in groupids]))
        testing=np.flatnonzero(np.array([fold_nodes[a]==k for a in groupids]))
        if len(training)==0 or len(testing)==0:raise ValueError('SOURCE_SCHEMA_STOP_FOLD_EMPTY')
        def index(g):
            idx=(g[:,None]*(ALT+1)+np.arange(ALT+1)[None,:]).ravel()
            n=np.full(len(g),ALT+1,dtype=int)
            st=np.arange(len(g))*(ALT+1)
            return idx,n,st,st
        it,nt,st,ui=index(training);ie,ne,se,ue=index(testing)
        ct=collections.Counter(groupids[training]); w=np.array([1/(len(ct)*ct[a]) for a in groupids[training]],float)
        mu=XX[it].mean(0);sd=XX[it].std(0);sd[sd<EPS]=1
        Z=np.clip((XX-mu)/sd,-10,10)
        for name,p in (('M0',len(FEATURES0)),('M1',len(FEATURES1))):
            tx=Z[it,:p];te=Z[ie,:p]
            opt=minimize(lambda b:condloss(b,tx,nt,st,ui,w),np.zeros(p),
                 method='L-BFGS-B',jac=True,options={'maxiter':160,'gtol':1e-7,'ftol':1e-9})
            if not opt.success and np.linalg.norm(opt.jac)>1e-3:
                raise ValueError('MODEL_FIT_STOP_'+name+'_FOLD_'+str(k))
            zz=te@opt.x
            ll=logsumexp(zz.reshape(len(testing),ALT+1),axis=1)-zz[ue]
            for a in set(groupids[testing]):
                loss[a][name].extend(ll[groupids[testing]==a].tolist())
            if name=='M1':signs.append([float(opt.x[-2]),float(opt.x[-1])])
    gain=np.array([np.mean(loss[a]['M0'])-np.mean(loss[a]['M1']) for a in ids])
    rng=np.random.default_rng(SEED)
    bt=rng.choice(gain,size=(BOOT,len(gain)),replace=True).mean(1)
    ci=np.quantile(bt,[.025,.975])
    positive=int((gain>0).sum());bothnegative=sum(x[0]<0 and x[1]<0 for x in signs)
    gate=bool(ci[0]>0 and positive>=math.ceil(len(ids)*.65) and bothnegative>=4)
    return {'status':'FIELD_COMPUTED_EXPLORATORY','source_node_tokens_admitted':len(ids),
       'original_source_nodes_are_independent_biological_individuals':'UNVERIFIED',
       'heldout_source_device_groups':len(ids),'matched_direction_strata':len(groupX),
       'candidate_rows':len(XX),'alternative_bearings_per_observed':ALT,
       'mean_equal_node_NLL_M0':float(np.mean([np.mean(loss[a]['M0']) for a in ids])),
       'mean_equal_node_NLL_M1':float(np.mean([np.mean(loss[a]['M1']) for a in ids])),
       'mean_gain_nats_per_decision':float(gain.mean()),
       'bootstrap_node95':ci.tolist(),'positive_node_tokens':positive,
       'negative_node_tokens':int((gain<0).sum()),
       'median_node_gain':float(np.median(gain)),
       'state_divergence_coefficients_by_fold':signs,
       'folds_negative_both_divergence_coefficients':int(bothnegative),
       'prespecified_numeric_gate':'PASS' if gate else 'FAIL',
       'biological_independent_individual_inference':'NOT_VERIFIED',
       'claim_ceiling':'Synthetic same-length direction alternatives do not define all physically reachable habitat states; no causal intentional state retention, no validated independent animal-ID crosswalk and no out-of-study replication. Original study already shows dynamic diel habitat use.',
       'anonymous_node_step_counts':sorted([len(loss[a]['M0']) for a in ids]),
       'source_raster_QC':source_qc_data}

def main(out):
    import pandas as pd
    import rasterio
    result={'schema':'ecostate.v11c.independent_buffalo_origin_environment_choice',
       'status':'SOURCE_OR_MODEL_STOP','publication_doi':'10.1111/ecog.07421',
       'evidence_class':'single_source_new_observational_post_Zenodo_original_data',
       'raw_gps_coordinates_or_source_node_strings_exported':False,
       'original_source_checksum_gate':False}
    try:
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            meta=json.loads(urllib.request.urlopen(urllib.request.Request(API,headers={'User-Agent':'ecostate-v11c/1'}),timeout=45).read())
            fn={key:root/key for key in FILES}
            sourcehashes=[original_file(meta,key,fn[key]) for key in FILES]
            result['original_source_checksum_gate']=True
            result['original_sha256']={x['name']:x['actual_sha256'] for x in sourcehashes}
            table=pd.read_csv(fn['buffalo.csv'],low_memory=False)
            with rasterio.open(fn['canopy_cover.tif']) as canopy,\
                 rasterio.open(fn['veg_herby.tif']) as herb,\
                 rasterio.open(fn['slope_raster.tif']) as slope:
                if not canopy.crs or not herb.crs or not slope.crs:raise ValueError('SOURCE_SCHEMA_STOP_MISSING_CRS')
                if len({canopy.crs.to_string(),herb.crs.to_string(),slope.crs.to_string()})!=1:
                    raise ValueError('SOURCE_SCHEMA_STOP_CRS_MISMATCH')
                tracks,qc=prepare_tracks(table,canopy.crs)
                grouped,gqc=make_groups(tracks)
                if len(grouped)<MIN_NODES:raise ValueError('SOURCE_SCHEMA_STOP_FEW_DEVICE_TRACKS')
                ds=[canopy,herb,slope]
                choices={}
                for node,(pairs,hours) in grouped.items():
                    xx=[]
                    for row,h in zip(pairs,hours):
                        xx.append(make_design((row[2],row[3]),row,h,ds))
                    choices[node]=xx
                scored=fit_heldout(choices,{'GPS_QC':qc,'track_QC':gqc})
                result.update(scored)
                result['GPS_QC']=qc;result['track_QC']=gqc
    except Exception as e:
        result['status']='SOURCE_OR_MODEL_STOP';result['reason']=str(e)[:1500]
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2)+'\n')
    print('V11C_ORIGINAL_BUFFALO',result['status'],result.get('prespecified_numeric_gate'))
    if result['status']=='FIELD_COMPUTED_EXPLORATORY':
        keys=['source_node_tokens_admitted','matched_direction_strata','mean_equal_node_NLL_M0',
              'mean_equal_node_NLL_M1','mean_gain_nats_per_decision','bootstrap_node95',
              'positive_node_tokens','folds_negative_both_divergence_coefficients']
        print('V11C_FIELD_SUMMARY',json.dumps({k:result[k] for k in keys},separators=(',',':')))
    else:print('SOURCE_OR_MODEL_STOP',result.get('reason'))
    assert result['raw_gps_coordinates_or_source_node_strings_exported'] is False
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v11/results/buffalo_state_choice_v11c.json')
