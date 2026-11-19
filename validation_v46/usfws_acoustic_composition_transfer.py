#!/usr/bin/env python3
"""Frozen v46 conditional acoustic 14-label seasonality transport, original USFWS."""
import argparse,collections,datetime,hashlib,io,json,math,re,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from usfws_zip_range_directory import ORIGINAL_TOTAL,TAIL_BYTES,central_location,http_range
from usfws_zip_in_tail_v43a import PINNED_TAIL_SHA256
from usfws_bounded_xlsx_headers import full_directory_entries,choose_members,fetch_member,NS
from usfws_nightly_effort_grain import first_row,colidx

CODES=("EPTFUS","LASBOR","LASCIN","LASNOC","MYOLUC","MYOSEP","PERSUB",
       "MYOLEI","MYOSOD","NYCHUM","CORRAF","ANTPAL","LASINT","TADBRA")
REQUIRED=("AcousticSite","NightOf","ALL")+CODES
OUT=Path("validation_v46/results/usfws_seasonal_acoustic_composition_v46.json")
SEED=20261119

def pinned_book():
    start=ORIGINAL_TOTAL-TAIL_BYTES
    receipt,tail=http_range(start,ORIGINAL_TOTAL-1)
    if tail is None or hashlib.sha256(tail).hexdigest()!=PINNED_TAIL_SHA256:
        raise ValueError("PINNED_USFWS_TAIL_UNAVAILABLE_OR_CHANGED")
    cd=central_location(tail)
    if cd["status"]!="STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED":
        raise ValueError("PINNED_ZIP_DIRECTORY_INVALID")
    p=cd["central_directory_offset"]-start
    if p<0 or p+cd["central_directory_size"]>len(tail)-22:
        raise ValueError("PINNED_ZIP_DIRECTORY_NOT_IN_TAIL")
    entries=full_directory_entries(tail[p:p+cd["central_directory_size"]],cd["declared_entry_count"])
    selection,chosen=choose_members(entries)
    if chosen is None:raise ValueError("SOURCE_NIGHTLY_MEMBER_NOT_UNIQUE")
    receipt,content=fetch_member(chosen["nightly_pass_counts"])
    if content is None or receipt["selected_original_member_crc32_hex"]!="3666e794":
        raise ValueError("ORIGINAL_USFWS_NIGHTLY_CRC_OR_RANGE_STOP")
    return content

def date_from_cell(s):
    if s is None:return None
    try:
        f=float(str(s).strip())
        if 20000<=f<=60000 and math.isfinite(f):
            return (datetime.datetime(1899,12,30)+datetime.timedelta(days=f)).date()
    except (TypeError,ValueError,OverflowError):pass
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%Y/%m/%d","%Y-%m-%d %H:%M:%S"):
        try:return datetime.datetime.strptime(str(s).strip(),fmt).date()
        except ValueError:pass
    return None

def count_int(s):
    try:
        n=float(str(s).strip())
        return int(n) if math.isfinite(n) and 0<=n<=1e9 and n.is_integer() else None
    except (ValueError,TypeError,OverflowError):return None

def shared_dates(z,indices):
    if not indices:return {}
    if "xl/sharedStrings.xml" not in z.namelist():return {}
    if z.getinfo("xl/sharedStrings.xml").file_size>20000000:
        raise ValueError("SHARED_STRING_SIZE_STOP")
    answer={};i=0
    with z.open("xl/sharedStrings.xml") as f:
        for _,e in ET.iterparse(f,events=("end",)):
            if e.tag==NS+"si":
                if i in indices:answer[i]="".join(t.text or "" for t in e.iter(NS+"t"))
                i+=1;e.clear()
    return answer

def read_original_rows(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if sum(x.file_size for x in z.infolist())>40000000:
            raise ValueError("INNER_WORKBOOK_SIZE_STOP")
        path="xl/worksheets/sheet1.xml"
        header=first_row(z,path)
        index={label:k for k,label in header.items()}
        if not set(REQUIRED).issubset(index):raise ValueError("PINNED_COLUMN_SCHEMA_CHANGED")
        wanted=[index[k] for k in REQUIRED]
        items=[];dates=set();started=False
        with z.open(path) as f:
            for _,row in ET.iterparse(f,events=("end",)):
                if row.tag!=NS+"row":continue
                if not started:started=True;row.clear();continue
                cells={}
                for c in row:
                    i=colidx(c.attrib.get("r"))
                    if i not in wanted:continue
                    t=c.attrib.get("t","")
                    v=c.find(NS+"v")
                    if t=="s" and v is not None and v.text is not None:
                        cells[i]=("shared",v.text)
                    elif t=="inlineStr":
                        cells[i]=("text","".join(x.text or "" for x in c.iter(NS+"t")))
                    elif v is not None and v.text is not None:
                        cells[i]=("number",v.text)
                x=[cells.get(i,(None,None)) for i in wanted]
                if x[1][0]=="shared":
                    try:dates.add(int(x[1][1]))
                    except (ValueError,TypeError):pass
                items.append(x);row.clear()
        translate=shared_dates(z,dates)
    rows=[];excluded=collections.Counter();label_positive=np.zeros(len(CODES),dtype=int)
    unequal_all=0
    for cells in items:
        site,date,all_,*taxa=cells
        if not site[1]:excluded["missing_site"]+=1;continue
        sitekey=site[0]+":"+str(site[1])
        day=date[1]
        if date[0]=="shared":
            try:day=translate.get(int(day))
            except (ValueError,TypeError):day=None
        d=date_from_cell(day)
        if d is None or not 2010<=d.year<=2018:
            excluded["unparseable_or_outside_year"]+=1;continue
        all_n=count_int(all_[1])
        if all_n is None:
            excluded["ALL_noninteger_missing_or_negative"]+=1;continue
        counts=[count_int(v) if typ in ("number","text") else None for typ,v in taxa]
        if any(q is None for q in counts):
            excluded["species_label_count_missing_or_invalid"]+=1;continue
        vec=np.asarray(counts,dtype=float)
        if vec.sum()==0:
            excluded["all_named_classifiers_zero"]+=1;continue
        unequal_all+=int(int(vec.sum())!=all_n)
        label_positive+=(vec>0)
        rows.append({"site":sitekey,"year":d.year,"doy":d.timetuple().tm_yday,
                     "counts":vec,"share":vec/vec.sum()})
    support={
        "source_table_rows":len(items),"valid_classified_positive_nights":len(rows),
        "row_exclusions":dict(excluded),
        "original_classifier_labels_positive_n":int(sum(label_positive>0)),
        "ALL_disagrees_with_named_classified_sum_nights":unequal_all,
        "source_site_labels_n":len({x["site"] for x in rows}),
        "source_years_n":len({x["year"] for x in rows}),
        "valid_nights_by_year":dict(sorted(collections.Counter(x["year"] for x in rows).items())),
    }
    return rows,support

def season_x(rows):
    doy=np.asarray([r["doy"] for r in rows],dtype=float)
    angle=2*np.pi*doy/365.2425
    return np.column_stack([np.sin(angle),np.cos(angle)])

def softmax(z):
    m=np.column_stack([z,np.zeros(len(z))])
    a=np.exp(m-m.max(axis=1,keepdims=True))
    return a/a.sum(axis=1,keepdims=True)

def predict(train,test,which):
    if which=="M0":
        a=np.stack([r["share"] for r in train]).sum(axis=0)+.25
        return np.repeat((a/a.sum())[None,:],len(test),axis=0)
    x=season_x(train); xx=season_x(test)
    scaler=StandardScaler().fit(x)
    a=scaler.transform(x); b=scaler.transform(xx)
    n=np.stack([r["counts"] for r in train])
    y=np.log((n[:,:-1]+.5)/(n[:,-1:]+.5))
    reg=Ridge(alpha=10.,fit_intercept=True).fit(a,y)
    return softmax(reg.predict(b))

def model_loss(train,test):
    y=np.stack([r["share"] for r in test])
    def ce(p):return float(np.mean(-np.sum(y*np.log(np.maximum(p,1e-10)),axis=1)))
    return ce(predict(train,test,"M0")),ce(predict(train,test,"M1"))

def sign_p(k,n):
    return float(sum(math.comb(n,i) for i in range(k,n+1))/2**n)

def summarize(g,bases,seasons):
    if not g:return {"status":"NO_EVALUABLE_GROUPS"}
    a=np.asarray(g);rng=np.random.default_rng(SEED)
    bootstrap=np.asarray([rng.choice(a,size=len(a),replace=True).mean() for _ in range(10000)])
    lo,hi=np.percentile(bootstrap,[2.5,97.5])
    k=int(np.sum(a>0));p=sign_p(k,len(a))
    return {"status":"EVALUATED","heldout_group_n":len(a),"positive_heldout_group_n":k,
            "M0_equal_group_cross_entropy":float(np.mean(bases)),
            "M1_equal_group_cross_entropy":float(np.mean(seasons)),
            "M0_minus_M1_gain_nats":float(np.mean(a)),
            "whole_group_bootstrap_95":[float(lo),float(hi)],
            "one_sided_exact_positive_sign_p":p,
            "frozen_primary_positive_gate":bool(np.mean(a)>0 and lo>0 and p<=.05)}

def leave_group(rows,key,min_test,min_group):
    by=collections.defaultdict(list)
    for r in rows:by[r[key]].append(r)
    groups=[(k,v) for k,v in by.items() if len(v)>=min_test]
    if len(groups)<min_group:return {"status":"GROUP_SUPPORT_STOP","eligible_groups_n":len(groups)}
    gains=[];base=[];season=[]
    for label,test in groups:
        train=[r for r in rows if r[key]!=label]
        if len(train)<500:continue
        a,b=model_loss(train,test)
        gains.append(a-b);base.append(a);season.append(b)
    out=summarize(gains,base,season)
    out["eligible_group_candidates_n"]=len(groups)
    return out

def evaluate(rows,support):
    site=collections.Counter(r["site"] for r in rows)
    year=collections.Counter(r["year"] for r in rows)
    gate={
        "1000_valid_detector_nights":len(rows)>=1000,
        "30_sites_each_20_nights":sum(v>=20 for v in site.values())>=30,
        "5_years_each_50_nights":sum(v>=50 for v in year.values())>=5,
        "10_classified_labels_positive":support["original_classifier_labels_positive_n"]>=10,
    }
    result={
        "programme":"v46_original_USFWS_detected_night_14_label_seasonal_composition",
        "source_reference":112151,
        "original_nightly_XLSX_CRC32":"3666e794",
        "source_support":support,"predeclared_gates":gate,
        "original_source_original_v45_effort_stop_retained":True,
        "no_full_recording_effort_or_species_absence_inferred":True,
        "no_causal_bat_behavior_or_ecological_resource_claim":True,
        "no_source_site_names_geocoordinates_or_records_exported":True}
    if not all(gate.values()):
        result["status"]="SOURCE_RESPONSE_SUPPORT_STOP";return result
    result["primary_whole_site"]=leave_group(rows,"site",20,30)
    result["secondary_whole_year"]=leave_group(rows,"year",50,5)
    result["status"]="FROZEN_EVALUATED"
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    src=pinned_book();rows,support=read_original_rows(src);result=evaluate(rows,support)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V46_FROZEN_USFWS_SEASONAL_COMPOSITION="+json.dumps(result,sort_keys=True))
    assert not result["no_full_recording_effort_or_species_absence_inferred"] is False
