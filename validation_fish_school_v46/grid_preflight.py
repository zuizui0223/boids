import numpy as np

def grid(frame, pos, fps):
    """Shared v30/v42 physical-time grid; no interpolation or additional smoothing."""
    f=np.asarray(frame); p=np.asarray(pos,float)
    if fps not in (15,25,30,50) or p.ndim!=3 or p.shape[1:] not in ((8,2),(10,2)) or len(f)!=len(p):
        raise ValueError('source shape')
    if not np.isfinite(f).all() or not np.equal(f,np.round(f)).all() or not (np.diff(f)>0).all():
        raise ValueError('integer source frame')
    s=round(fps*.2); offsets=np.array([-11,-10,-6,-5,-3,-2,-1,0,1,3,4])*s
    t=np.arange(11*s,len(f)-4*s,s); ix=t[:,None]+offsets
    valid=np.isfinite(p[ix]).all((1,2,3)) & ((f[ix]-f[t,None])==offsets).all(1)
    t=t[valid]
    if len(t)<300:raise ValueError('too few complete source events')
    return t

def panels(frame,pos,fps):
    t=grid(frame,pos,fps); s=round(fps*.2); p=np.asarray(pos,float); n=p.shape[1]
    now=p[t]; vel=(now-p[t-s])/.2; prev=(p[t-s]-p[t-2*s])/.2
    off=now[:,None,:,:]-now[:,:,None,:]; d2=np.sum(off**2,axis=-1); i=np.arange(n); d2[:,i,i]=np.inf
    order=np.argsort(d2,axis=2)[:,:,:n-1]; near=order[:,:,:3]; far=order[:,:,-3:]
    assert not np.any(near==i[None,:,None]) and not np.any(far==i[None,:,None]); assert np.all(np.take_along_axis(d2,near,2)[:,:,-1]<=np.take_along_axis(d2,far,2)[:,:,0])
    gp=(vel.sum(axis=1,keepdims=True)-vel)/(n-1); oldgp=(prev.sum(axis=1,keepdims=True)-prev)/(n-1)
    G=np.concatenate((now,vel,prev,vel-prev,np.linalg.norm(vel,axis=-1,keepdims=True),now.mean(1,keepdims=True)-now,np.take_along_axis(off,near[:,:,:,None],2).mean(2),np.sqrt(np.take_along_axis(d2,near,2)).mean(2)[:,:,None]),axis=-1)
    glob=np.concatenate((G,gp-vel),axis=-1)
    ix=np.arange(len(t))[:,None,None]; rot=np.zeros_like(vel)
    for focal in range(n):
        others=np.delete(i,focal); v=vel[:,others]; w=np.roll(v,1,axis=1); np.testing.assert_allclose(v.sum(1),w.sum(1),atol=1e-9,rtol=0)
        rank=near[:,focal]-(near[:,focal]>focal)
        rot[:,focal]=np.take_along_axis(w,rank[:,:,None],1).mean(1)-gp[:,focal]
    extras={'NEAR_TRUE':vel[ix,near].mean(2)-gp,'FAR_TRUE':vel[ix,far].mean(2)-gp,'NEAR_ROT1':rot,'NEAR_STALE_0.2S':prev[ix,near].mean(2)-oldgp}
    X={'G_geometry':G.reshape(-1,14),'GLOBAL':glob.reshape(-1,16)}
    for k,x in extras.items(): X[k]=np.concatenate((glob,x),axis=-1).reshape(-1,18)
    Y=np.concatenate(((p[t+s]-now)/.2,(p[t+4*s]-p[t+3*s])/.2),axis=-1).reshape(-1,4)
    assert all(len(v)==len(Y) and np.isfinite(v).all() for v in X.values()) and np.isfinite(Y).all()
    return X,Y,t

def tests():
    # Same analytic synthetic paths sampled at 15 and 30Hz; endpoints exactly coincide.
    def fixture(fps):
        time=np.arange(301*fps+1)/fps
        j=np.arange(10)[None,:]
        p=np.stack((j*5+np.sin(time[:,None]*(.3+j*.05))+.05*time[:,None], j*3+np.cos(time[:,None]*(.2+j*.03))),axis=-1)
        return np.arange(len(time)),p
    f,p=fixture(15); a,y,t=panels(f,p,15); f2,p2=fixture(30); b,z,u=panels(f2,p2,30)
    assert np.array_equal(t*2,u)
    for k in a:np.testing.assert_allclose(a[k],b[k],atol=1e-12,rtol=0)
    np.testing.assert_allclose(y,z,atol=1e-12,rtol=0)
    print('15/30Hz common-grid parity PASS; frames=',len(t),'fish-time rows=',len(y))
    p3=p.copy(); p3[t[-1]+12]+=3; c,w,_=panels(f,p3,15)
    for k in a:np.testing.assert_array_equal(a[k],c[k])
    assert not np.array_equal(y,w)
    print('future-only target perturbation leaves predictors identical PASS')
    p4=p.copy(); p4[t[20]-3,0,0]=np.nan; d,v,t4=panels(f,p4,15)
    assert t[20] not in t4 and len(t4)<len(t)
    for k in d:assert len(d[k])==len(v)
    print('NA excludes same source support from every panel PASS')
    print('SYNTHETIC_ONLY: no zebrafish outcomes scored')
if __name__=='__main__':tests()
