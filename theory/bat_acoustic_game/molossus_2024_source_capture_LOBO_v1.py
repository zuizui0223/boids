"""Original PNAS 2024 Molossus source capture success: source-bat heldout forecast.

NO NEW BAT MEASUREMENTS. Secondary already-published 10 bat study.
Original supplementary XLSX SHA pin, no original bat IDs/rows/files rehosted.
M0 constant catch rate; M1 quadratic Poisson log-catch-rate in call density;
M2 product of source attack-rate Poisson and success-among-attempts binomial.
M2 factorization is descriptive, not a causal "public info versus jamming" proof.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean,median
import hashlib,io,json,math,random,zipfile,xml.etree.ElementTree as ET
import numpy as np
from scipy.optimize import minimize
from molossus_2024_supplement_structure_v1 import download_bounded,URL,EXPECTED

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"MOLOSSUS_2024_CAPTURE_BAT_HOLDOUT_RESULT_V1.json"
CONTRACT=ROOT/"MOLOSSUS_2024_LEAVE_BAT_OUT_CAPTURE_PREOUTPUT_V1.md"
SOURCE_SHA="92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d"
COLS=("bat","sec_group","numel_5swindows","sum_attacks","sum_success",
      "sum_cons","sum_commute","sum_disrupt")
SHEET="xl/worksheets/sheet1.xml"
XML_NAMESPACE={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
L2=.1
TRAIN_BAT_MIN=7
SCALE=math.log1p(100.)
SEED=20261105
N_BOOTS=5000
DENSITY_BINS=("zero","positive_to_25","25_to_75","above_75")


def decode_sheet(raw):
    """One original XLSX worksheet through stdlib OOXML, no extra file persisted."""
    z=zipfile.ZipFile(io.BytesIO(raw))
    strings=[]
    if "xl/sharedStrings.xml" in z.namelist():
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si",XML_NAMESPACE):
            strings.append("".join(x.text or "" for x in si.findall(".//m:t",XML_NAMESPACE)))
    root=ET.fromstring(z.read(SHEET))
    output=[]
    for row in root.findall(".//m:sheetData/m:row",XML_NAMESPACE):
        values={}
        for cell in row.findall("m:c",XML_NAMESPACE):
            a=cell.get("r","")
            key="".join(x for x in a if x.isalpha())
            tag=cell.get("t")
            v=cell.find("m:v",XML_NAMESPACE)
            if tag=="s":
                if v is None:raise ValueError("STOP_SHARED_CELL_NO_VALUE")
                value=strings[int(v.text)]
            elif tag=="inlineStr":
                s=cell.find("m:is",XML_NAMESPACE)
                value="".join(x.text or "" for x in s.findall(".//m:t",XML_NAMESPACE)) if s is not None else None
            else:
                value=v.text if v is not None else None
            values[key]=value
        if any(k in values for k in "ABCDEFGH"):
            output.append([values.get(c) for c in "ABCDEFGH"])
    if tuple(output[0])!=COLS:
        raise ValueError("STOP_ORIGINAL_SHEET_HEADER_DIFFERENT")
    if len(output)!=4300:
        raise ValueError("STOP_ORIGINAL_SHEET_ROW_COUNT_CHANGED")
    return output[1:]


def parse_integer(x,field):
    if x is None or str(x).strip()=="":
        raise ValueError("STOP_EMPTY_"+field)
    try:v=float(x)
    except (ValueError,TypeError):raise ValueError("STOP_NOT_NUMERIC_"+field)
    if not math.isfinite(v) or v<0 or abs(v-round(v))>1e-6:
        raise ValueError("STOP_NONNEGATIVE_INTEGER_VIOLATION_"+field)
    return int(round(v))


def admit_rows(rawrows):
    records=[]
    labels=set()
    grouped_sec=[]
    for row in rawrows:
        bat=str(row[0]).strip() if row[0] is not None else ""
        if not bat:raise ValueError("STOP_MISSING_BAT_ID")
        if row[1] is None or str(row[1]).strip()=="":
            raise ValueError("STOP_MISSING_ORIGINAL_SEC_GROUP")
        E=parse_integer(row[2],"numel_5swindows")
        A=parse_integer(row[3],"sum_attacks")
        Y=parse_integer(row[4],"sum_success")
        C=parse_integer(row[5],"sum_cons")
        commute=parse_integer(row[6],"sum_commute")
        disrupt=parse_integer(row[7],"sum_disrupt")
        if E<=0:raise ValueError("STOP_NONPOSITIVE_GROUP_EXPOSURE")
        if Y>A:raise ValueError("STOP_SUCCESS_EXCEEDS_ATTACK")
        dens=C/E
        z=math.log1p(dens)/SCALE
        if not 0<=z<=2:raise ValueError("STOP_DENSITY_OUTSIDE_FROZEN_NUMERIC_SUPPORT")
        labels.add(bat)
        grouped_sec.append(str(row[1]).strip())
        records.append({"bat":bat,"E":E,"A":A,"Y":Y,"C":C,
                        "commute":commute,"disrupt":disrupt,
                        "z":z,"density":dens})
    if len(labels)<8:
        raise ValueError("STOP_INSUFFICIENT_INDEPENDENT_SOURCE_BAT_IDS")
    return records,{"source_original_source_row_count":len(rawrows),
                    "source_individual_bat_ID_count":len(labels),
                    "source_sec_group_distinct_global_count":len(set(grouped_sec)),
                    "source_bat_IDs_exported":False,
                    "sum_five_second_exposures":sum(x["E"] for x in records),
                    "total_original_attacks":sum(x["A"] for x in records),
                    "total_original_confirmed_success":sum(x["Y"] for x in records),
                    "total_source_conspecific_calls":sum(x["C"] for x in records),
                    "unique_original_bat_row_count_min_max":
                      [min(sum(y["bat"]==b for y in records) for b in labels),
                       max(sum(y["bat"]==b for y in records) for b in labels)]}


def density_bin(d):
    if d==0:return "zero"
    if d<=25:return "positive_to_25"
    if d<=75:return "25_to_75"
    return "above_75"


def bin_support(rows):
    bins=defaultdict(list)
    for r in rows:bins[density_bin(r["density"])].append(r)
    out=[]
    for b in DENSITY_BINS:
        xs=bins[b]
        if not xs:
            out.append({"density_bin":b,"rows":0,"individual_bats":0,"five_second_exposure":0})
            continue
        out.append({
            "density_bin":b,"rows":len(xs),
            "individual_bats":len(set(x["bat"] for x in xs)),
            "five_second_exposure":sum(x["E"] for x in xs),
            "attacks":sum(x["A"] for x in xs),
            "captures":sum(x["Y"] for x in xs),
            "capture_rate_per_5s":sum(x["Y"] for x in xs)/sum(x["E"] for x in xs),
            "attacks_per_5s":sum(x["A"] for x in xs)/sum(x["E"] for x in xs),
            "capture_per_attack":sum(x["Y"] for x in xs)/sum(x["A"] for x in xs)
                if sum(x["A"] for x in xs)>0 else None
        })
    return out


def sigmoid(v):
    v=np.asarray(v,dtype=float)
    return np.exp(-np.logaddexp(0.,-v))


def predictor_values(rows):
    z=np.array([r["z"] for r in rows],dtype=float)
    E=np.array([r["E"] for r in rows],dtype=float)
    A=np.array([r["A"] for r in rows],dtype=float)
    Y=np.array([r["Y"] for r in rows],dtype=float)
    return z,E,A,Y


def optimize_source_glm(train,model):
    z,E,A,Y=predictor_values(train)
    if model=="capture_quadratic":
        X=np.stack([np.ones_like(z),z,z*z],axis=1)
        response=Y
        initial=[math.log((float(np.sum(Y))+.5)/(float(np.sum(E))+1)),0,0]
        mode="poisson"
    elif model=="attack_linear":
        X=np.stack([np.ones_like(z),z],axis=1)
        response=A
        initial=[math.log((float(np.sum(A))+.5)/(float(np.sum(E))+1)),0]
        mode="poisson"
    elif model=="success_logistic":
        X=np.stack([np.ones_like(z),z],axis=1)
        response=Y
        initial=[math.log((float(np.sum(Y))+.5)/(float(np.sum(A-Y))+.5)),0]
        mode="binomial"
    else:
        raise ValueError("STOP_UNREGISTERED_SOURCE_MODEL")
    response=np.asarray(response,dtype=float)
    initial=np.clip(np.array(initial,dtype=float),-12.,12.)
    ridge=np.ones(X.shape[1]);ridge[0]=0
    if not np.all(np.isfinite(initial)):
        raise ValueError("STOP_NONFINITE_SOURCE_INITIAL_STATE")

    def objective(beta):
        eta=X@beta
        if mode=="poisson":
            mu=E*np.exp(np.clip(eta,-25,25))
            # Pseudo-frequency independent combinatorial count constant
            val=float(np.sum(mu-response*eta))
            grad=X.T@(mu-response)
        else:
            val=float(np.sum(A*np.logaddexp(0,eta)-Y*eta))
            grad=X.T@(A*sigmoid(eta)-Y)
        val+=.5*L2*np.sum((ridge*beta)**2)
        grad+=L2*ridge*beta
        return val,np.asarray(grad,dtype=float)
    fit=minimize(objective,initial,jac=True,
                 method="L-BFGS-B",
                 bounds=[(-15,15)]*X.shape[1],
                 options={"maxiter":1200,"ftol":1e-10,"gtol":1e-8})
    if not fit.success or not np.all(np.isfinite(fit.x)):
        raise ValueError("STOP_SOURCE_GLM_NO_CONVERGENCE_"+model+": "+fit.message.__str__()[:110])
    return np.asarray(fit.x,dtype=float)


def model_rates(train,test):
    z,E,A,Y=predictor_values(test)
    train_E=sum(r["E"] for r in train);train_Y=sum(r["Y"] for r in train)
    if train_E<=0:raise ValueError("STOP_TRAINING_ZERO_EXPOSURE")
    source_mean=(train_Y+.5)/(train_E+1)
    bx=optimize_source_glm(train,"capture_quadratic")
    ba=optimize_source_glm(train,"attack_linear")
    bp=optimize_source_glm(train,"success_logistic")
    X2=np.stack([np.ones_like(z),z],axis=1)
    X3=np.stack([np.ones_like(z),z,z*z],axis=1)
    direct=np.exp(np.clip(X3@bx,-20,20))
    attempts=np.exp(np.clip(X2@ba,-20,20))
    succ=sigmoid(X2@bp)
    return {
        "M0":np.full_like(z,source_mean),
        "M1":direct,
        "M2":attempts*succ,
        "source_predicted_attack_rate":attempts,
        "source_predicted_attack_success_fraction":succ
    }


def poisson_deviance_per_exposure(y,mu,denominator):
    mu=np.asarray(mu,dtype=float);y=np.asarray(y,dtype=float)
    if denominator<=0 or np.any(mu<=0):
        raise ValueError("STOP_NONPOSITIVE_POISSON_DEVIANCE_MEAN")
    terms=np.zeros_like(y)
    nonzero=y>0
    terms[nonzero]=y[nonzero]*np.log(y[nonzero]/mu[nonzero])
    return float(2*np.sum(terms-y+mu)/denominator)


def score_source_test(test,rates):
    z,E,A,Y=predictor_values(test)
    out={}
    for model in ("M0","M1","M2"):
        lam=rates[model]
        if np.any(~np.isfinite(lam)) or np.any(lam<=0):
            raise ValueError("STOP_NONFINITE_SOURCE_RATE_"+model)
        mu=E*lam
        out[model]={
            "capture_deviance_per_5s":poisson_deviance_per_exposure(Y,mu,np.sum(E)),
            "mean_absolute_captures_error_per_5s":float(np.sum(np.abs(Y-mu))/np.sum(E)),
            "predicted_total_captures":float(np.sum(mu)),
            "observed_total_captures":float(np.sum(Y)),
        }
    # These factor-stage scores are conditional source diagnostics only.
    attempts=E*rates["source_predicted_attack_rate"]
    out["attack_stage_deviance_per_5s"] = poisson_deviance_per_exposure(A,attempts,np.sum(E))
    p=np.clip(rates["source_predicted_attack_success_fraction"],1e-12,1-1e-12)
    out["success_stage_negloglik_per_original_attack"] = (
        float(-np.sum(Y*np.log(p)+(A-Y)*np.log(1-p))/np.sum(A)) if np.sum(A)>0 else None)
    return out


def bootstrap_bat_mean(xs,seed=SEED):
    rng=random.Random(seed);n=len(xs)
    out=sorted(mean([xs[rng.randrange(n)] for _ in range(n)]) for _ in range(N_BOOTS))
    def q(p):
        v=(len(out)-1)*p
        j=int(v)
        return out[j]*(1-(v-j))+out[min(j+1,len(out)-1)]*(v-j)
    return [q(.025),q(.975)]


def summary_folds(folds):
    methods=("M0","M1","M2")
    metric="capture_deviance_per_5s"
    out={"original_bat_independent_fold_count":len(folds),
         "source_model_scores":{},
         "paired_bat_comparisons":{},
         "n_original_5s_windows_total":sum(f["source_5s_exposure"] for f in folds),
         "source_total_bats_contribute_once_each":True,
         "no_original_bat_IDs_exported":True}
    for m in methods:
        vv=[f["scores"][m][metric] for f in folds]
        mae=[f["scores"][m]["mean_absolute_captures_error_per_5s"] for f in folds]
        out["source_model_scores"][m]={
           "equal_bat_mean_capture_deviance_per_5s":mean(vv),
           "median_source_bat_capture_deviance_per_5s":median(vv),
           "equal_bat_mean_capture_MAE_per_5s":mean(mae),
           "source_model_evaluated_original_bats":len(folds)
        }
    for name,a,b in [("M1_minus_M0","M1","M0"),
                     ("M2_minus_M0","M2","M0"),
                     ("M2_minus_M1","M2","M1")]:
        d=[f["scores"][a][metric]-f["scores"][b][metric] for f in folds]
        out["paired_bat_comparisons"][name]={
            "mean_bat_deviance_difference_per_5s":mean(d),
            "median_bat_deviance_difference_per_5s":median(d),
            "whole_bat_bootstrap_95":bootstrap_bat_mean(d),
            "source_bats_first_better":sum(v < -1e-12 for v in d),
            "source_bats_second_better":sum(v > 1e-12 for v in d),
            "source_bats_equal":sum(abs(v)<=1e-12 for v in d),
            "descriptive_source_internal_only":True
        }
    return out


def evaluate_source(rows):
    bats=sorted(set(r["bat"] for r in rows))
    folds=[]
    for bat in bats:
        train=[r for r in rows if r["bat"]!=bat]
        test=[r for r in rows if r["bat"]==bat]
        if len(set(r["bat"] for r in train))<TRAIN_BAT_MIN:
            raise ValueError("STOP_FEWER_THAN_SEVEN_SOURCE_TRAIN_BATS")
        rates=model_rates(train,test)
        scores=score_source_test(test,rates)
        folds.append({
            "source_5s_exposure":sum(r["E"] for r in test),
            "scores":scores
        })
    return summary_folds(folds)


def source():
    if not CONTRACT.exists():
        raise ValueError("STOP_UNCOMMITTED_SOURCE_RESPONSE_CONTRACT")
    b,http,ctype=download_bounded(URL)
    z=zipfile.ZipFile(io.BytesIO(b))
    matching=[f for f in z.infolist() if f.filename.split("/")[-1]==EXPECTED]
    if len(matching)!=1:raise ValueError("STOP_NON_UNIQUE_SOURCE_S01")
    xlsx=z.read(matching[0])
    digest=hashlib.sha256(xlsx).hexdigest()
    if digest!=SOURCE_SHA:raise ValueError("STOP_ORIGINAL_XLSX_SHA256_CHANGED")
    rows=decode_sheet(xlsx)
    groups,metadata=admit_rows(rows)
    return groups,metadata,hashlib.sha256(b).hexdigest()


def run():
    groups,meta,source_zip_sha=source()
    score=evaluate_source(groups)
    return {
      "schema":1,
      "status":"SOURCE_ORIGINAL_MOLOSSUS_2024_LEAVE_BAT_OUT_CAPTURE_REANALYSIS",
      "source_2024_paper":"10.1073/pnas.2321724121",
      "source_original_supplement_URL":URL,
      "source_original_xlsx_sha256":SOURCE_SHA,
      "source_original_package_sha256":source_zip_sha,
      "source_grouping_note":"Source Excel grouped 5-second exposure rows, not 4299 independent biological bats.",
      "source_meta":meta,
      "source_density_bins":bin_support(groups),
      "source_heldout_bat_evaluation":score,
      "models_predeclared":{
         "M0":"Constant density-blind capture count per 5-second exposure",
         "M1":"Quadratic in log1p mean conspecific calls / 5s, Poisson capture rate",
         "M2":"Attack-rate Poisson×capture-given-attack logistic, same calls/5s predictor",
         "ridge_nonintercept":L2,
         "spatial_3D_or_actual_distance_unavailable":True
      },
      "new_bat_measurements":False,
      "original_bat_IDs_or_original_rows_exported":False,
      "same_2024_source_already_established_inverted_U":True,
      "source_original_article_reproduced_exactly":False,
      "source_generalization_is_within_original_ten_bats":True,
      "ecology_inference_limit":"Predictive transport within a published 10-bat cohort cannot establish causal social information benefit, acoustic jamming or independent taxa."
    }


def main():
    try:
        obj=run()
    except Exception as e:
        obj={"schema":1,"status":"STOP_ORIGINAL_SOURCE_OR_PREDECLARED_MODEL",
            "error":type(e).__name__+":"+str(e)[:260],
            "new_bat_measurements":False,
            "original_bat_IDs_or_original_rows_exported":False}
    OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("MOLOSSUS_2024_ORIGINAL_CAPTURE_REANALYSIS",obj["status"])
    if obj["status"].startswith("STOP"):
        print("STOP_REASON",obj["error"])
        return 3
    print("SOURCE_SHA",obj["source_original_xlsx_sha256"])
    print("ORIGINAL_SOURCE_BIOLOGICAL_UNITS",obj["source_meta"])
    print("DENSITY_SUPPORT",obj["source_density_bins"])
    print("SOURCE_HOLDOUT_RESULT",obj["source_heldout_bat_evaluation"])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
