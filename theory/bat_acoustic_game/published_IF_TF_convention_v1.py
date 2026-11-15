"""Source-pinned 2026 emitted IF/TF/bandwidth model-constraint comparison.

Secondary analysis of a published Figshare original bat playback experiment.
No new measurements, not independent biological replication, no raw IDs/rows
in any committed or CI artifact. Contract frozen before numerical IF opened
in this research branch.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from statistics import mean,median
from pathlib import Path
import csv,hashlib,io,json,math,random,re

from source_gate_v2 import FIGSHARE_API,get_bytes

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"PUBLISHED_IF_TF_PHYSICAL_CONVENTION_PREOUTPUT_V1.md"
OUT=ROOT/"PUBLISHED_IF_TF_PHYSICAL_CONVENTION_RESULTS_V1.json"
FILENAME="Data_jamming.csv"
SHA256="2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367"
EXPERIMENTS=("IPIlow","IPIhigh","SPLlow")
MIN_CALLS_PER_ARM=4
MIN_CONDITIONS=3
MIN_PRIMARY_BATS=5
N_BOOTSTRAP=5000
BOOTSTRAP_SEED=20261105


def required_float(record,key):
    try:
        value=float(record[key])
    except (ValueError,KeyError,TypeError):
        return None
    return value if math.isfinite(value) else None


def stimulus_coordinate(experiment,condition):
    c=condition.strip()
    if experiment.startswith("IPI"):
        match=re.fullmatch(r"([0-9]+)ms",c)
        return math.log10(int(match.group(1))) if match and int(match.group(1))>0 else None
    if experiment=="SPLlow":
        match=re.fullmatch(r"(-?[0-9]+)dB",c)
        return float(match.group(1)) if match else None
    return None


def bootstrap_means(values,seed=BOOTSTRAP_SEED,draws=N_BOOTSTRAP):
    if not values:return [None,None]
    rng=random.Random(seed)
    n=len(values)
    arr=sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(draws))
    def percentile(p):
        q=(len(arr)-1)*p
        i=int(q)
        j=min(i+1,len(arr)-1)
        return (1-(q-i))*arr[i]+(q-i)*arr[j]
    return [percentile(.025),percentile(.975)]


def leave_one_out_range(values):
    if len(values)<2:return [None,None]
    v=[mean(values[:i]+values[i+1:]) for i in range(len(values))]
    return [min(v),max(v)]


def two_sided_sign_p(positive,negative):
    n=positive+negative
    if not n:return None
    k=min(positive,negative)
    return min(1.0,2*sum(math.comb(n,i) for i in range(k+1))/(2**n))


def clean_source_rows(rows):
    """Internally keep source IDs only in ephemeral memory. Never serialize them."""
    by=defaultdict(lambda:{"0":[],"1":[]})
    rejected=Counter()
    nrows=0
    source_bats=set()
    for row in rows:
        nrows+=1
        e=(row.get("Experiment") or "").strip()
        if e not in EXPERIMENTS:
            rejected["source_experiment_outside_registered_three"]+=1
            continue
        on=(row.get("isON") or "").strip()
        if on not in ("0","1"):
            rejected["isON_not_binary"]+=1
            continue
        bat=(row.get("ID") or "").strip()
        if not bat:
            rejected["missing_bat_ID"]+=1
            continue
        f_start=required_float(row,"IF")
        f_end=required_float(row,"TF")
        if f_start is None or f_end is None:
            rejected["nonfinite_or_missing_shared_IF_TF"]+=1
            continue
        if not f_start>f_end:
            rejected["not_downward_FM_IF_gt_TF"]+=1
            continue
        condition=(row.get("Condition") or "").strip()
        coord=stimulus_coordinate(e,condition)
        if coord is None:
            rejected["invalid_stimulus_level"]+=1
            continue
        source_bats.add(bat)
        key=(bat,e,condition,(row.get("Var") or "").strip(),
             (row.get("jammingTF") or "").strip())
        by[key][on].append((f_start,f_end))
    return by,{"rows_inspected":nrows,"rows_excluded_by_reason":dict(rejected),
               "distinct_bat_ID_labels_after_IF_TF_QC":len(source_bats)}


def contrast_contexts(by,statistic):
    calc=median if statistic=="median" else mean
    contexts=defaultdict(list)
    n_contexts=Counter()
    for (bat,e,condition,var,jammingtf),conditions in by.items():
        if min(len(conditions["0"]),len(conditions["1"]))<MIN_CALLS_PER_ARM:
            continue
        off=conditions["0"]
        on=conditions["1"]
        delta_if=calc([a for a,b in on])-calc([a for a,b in off])
        delta_tf=calc([b for a,b in on])-calc([b for a,b in off])
        contexts[(bat,e,condition)].append((delta_if,delta_tf))
        n_contexts[e]+=1
    bat_conditions=defaultdict(dict)
    for (bat,e,condition),data in contexts.items():
        coord=stimulus_coordinate(e,condition)
        if coord is None:continue
        dif=mean([x for x,y in data])
        dtf=mean([y for x,y in data])
        bat_conditions[(bat,e)][condition]={"coordinate":coord,
            "delta_IF_khz":dif,"delta_TF_khz":dtf,"delta_B_khz":dif-dtf}
    return bat_conditions,dict(n_contexts)


def bat_error_summary(levels):
    if len(levels)<MIN_CONDITIONS:
        return None
    if len(set(v["coordinate"] for v in levels.values()))<MIN_CONDITIONS:
        return None
    v=list(levels.values())
    delta_if=mean([x["delta_IF_khz"] for x in v])
    delta_tf=mean([x["delta_TF_khz"] for x in v])
    delta_band=mean([x["delta_B_khz"] for x in v])
    err_start=mean([abs(x["delta_IF_khz"]) for x in v])
    err_band=mean([abs(x["delta_IF_khz"]-x["delta_TF_khz"]) for x in v])
    return {"eligible_conditions":len(v),
        "mean_delta_IF_khz":delta_if,"mean_delta_TF_khz":delta_tf,
        "mean_delta_B_khz":delta_band,
        "error_fixed_start_khz":err_start,
        "error_fixed_bandwidth_khz":err_band,
        "D_fixed_bandwidth_minus_fixed_start_khz":err_band-err_start}


def summarize_group(batlevel,e):
    arr=[v for (i,name),v in batlevel.items() if name==e and v is not None]
    n=len(arr)
    if n==0:
        return {"status":"STOP_NO_ELIGIBLE_BAT_CONDITIONS","n_bats":0,
                "no_raw_ID_output":True}
    def series(k):return [x[k] for x in arr]
    d=series("D_fixed_bandwidth_minus_fixed_start_khz")
    wins_start=sum(x>1e-12 for x in d)
    wins_band=sum(x< -1e-12 for x in d)
    ties=n-wins_start-wins_band
    out={"status":"PASS_SOURCE_SUPPORT" if n>=MIN_PRIMARY_BATS else "LOW_SOURCE_SUPPORT",
        "n_bats":n,
        "n_bat_condition_cells":sum(a["eligible_conditions"] for a in arr),
        "min_conditions_per_bat":min(a["eligible_conditions"] for a in arr),
        "max_conditions_per_bat":max(a["eligible_conditions"] for a in arr),
        "equal_bat_mean_delta_IF_khz":mean(series("mean_delta_IF_khz")),
        "equal_bat_mean_delta_TF_khz":mean(series("mean_delta_TF_khz")),
        "equal_bat_mean_delta_B_khz":mean(series("mean_delta_B_khz")),
        "equal_bat_mean_absolute_error_fixed_start_khz":mean(series("error_fixed_start_khz")),
        "equal_bat_mean_absolute_error_fixed_bandwidth_khz":mean(series("error_fixed_bandwidth_khz")),
        "mean_D_bandwidth_minus_start_khz":mean(d),
        "median_D_bandwidth_minus_start_khz":median(d),
        "mean_D_whole_bat_bootstrap95_khz":bootstrap_means(d),
        "mean_D_leave_one_bat_out_min_max_khz":leave_one_out_range(d),
        "source_bats_favor_fixed_start":wins_start,
        "source_bats_favor_fixed_bandwidth":wins_band,
        "source_bats_exact_or_near_ties":ties,
        "exploratory_two_sided_whole_bat_sign_p":two_sided_sign_p(wins_start,wins_band),
        "no_raw_ID_output":True}
    return out


def read_original_source():
    if not CONTRACT.exists():
        raise ValueError("STOP_PREOUTPUT_CONTRACT_NOT_COMMITTED")
    meta_raw,_=get_bytes(FIGSHARE_API,2*1024*1024)
    manifest=json.loads(meta_raw)
    files=[x for x in manifest.get("files",[]) if x.get("name")==FILENAME]
    if len(files)!=1:
        raise ValueError("STOP_NON_UNIQUE_ORIGINAL_SOURCE_FILE")
    raw,_=get_bytes(files[0]["download_url"],3*1024*1024)
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=SHA256:
        raise ValueError("STOP_ORIGINAL_SOURCE_SHA256_MISMATCH")
    content=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    must={"ID","IF","TF","Experiment","Condition","Var","jammingTF","isON"}
    if not must.issubset(set(content.fieldnames or [])):
        raise ValueError("STOP_SOURCE_REQUIRED_SCHEMA_MISSING")
    return clean_source_rows(content),{"sha256":digest,"file_length_bytes":len(raw)}


def run():
    (by,qc),file=read_original_source()
    views={}
    for method in ("median","mean"):
        context,support=contrast_contexts(by,method)
        out={(i,e):bat_error_summary(cs) for (i,e),cs in context.items()}
        eligible={k:v for k,v in out.items() if v is not None}
        views[method]={"registered_source_strata_with_onoff_min4":support,
                       "experiments":{e:summarize_group(eligible,e) for e in EXPERIMENTS},
                       "unique_bats_across_experiments":len({i for i,e in eligible}),
                       "n_unique_bat_experiment_units":len(eligible)}
    primary=views["median"]["experiments"]["IPIlow"]
    return {"schema":1,"status":(
        "SOURCE_ARCHIVAL_SECONDARY_IF_TF_RESPONSE_ANALYSIS"
        if primary["n_bats"]>=MIN_PRIMARY_BATS
        else "STOP_PRIMARY_FEWER_THAN_FIVE_BATS"),
      "source_paper_doi":"10.1098/rspb.2026.0921",
      "source_data_doi":"10.6084/m9.figshare.30937379",
      "source_filename":FILENAME,"source":file,
      "source_quality":qc,
      "primary_registered_experiment":"IPIlow",
      "native_frequency_units":"kHz",
      "physical_deltas":"Delta IF, TF and B=IF-TF, ON minus OFF at matched original source subcontexts",
      "model_errors":"M_start abs(DeltaIF); M_band abs(DeltaIF-DeltaTF); D=E_band-E_start",
      "medians_primary":views["median"],
      "means_sensitivity":views["mean"],
      "new_bat_observations":False,"source_original_audio_recovered":False,
      "full_source_group_simulation_reproduced":False,
      "original_authors_prior_art_acknowledged":True,
      "no_original_bat_ids_or_raw_rows_exported":True,
      "source_IF_numerical_values_first_inspected_after_contract":True,
      "inference_limitations":[
        "ON/OFF recording order, individual time trends and bat physiology may differ",
        "Animal experimental results were already published; not independent confirmation",
        "Each bat can contribute multiple stimulus settings; inference is bat-level only",
        "Comparison scores assess descriptive spectral change, not how echolocation receivers discriminate calls",
        "2018 group-flight pulse shapes and source 2026 full group simulator remain unavailable",
        "No inferred causal prey-capture reward, fitness or cross-species generality"
      ]}


def main():
    try:
        result=run()
    except Exception as e:
        result={"schema":1,"status":"STOP_SOURCE_ACCESS_OR_FROZEN_GATE",
                "error":type(e).__name__+":"+str(e)[:240],
                "new_bat_observations":False,
                "no_original_bat_ids_or_raw_rows_exported":True}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_STATUS",result["status"])
    if result["status"].startswith("STOP"):
        print("SOURCE_STOP",result.get("error","insufficient original bat IF/TF support"))
        return 3 if result["status"]=="STOP_SOURCE_ACCESS_OR_FROZEN_GATE" else 0
    print("SOURCE_SHA",result["source"]["sha256"])
    print("ROW_QC",result["source_quality"])
    for name,data in (("median",result["medians_primary"]),
                      ("mean_sensitivity",result["means_sensitivity"])):
        print("METHOD",name,"unique_bats",data["unique_bats_across_experiments"],
              "n_bat_experiments",data["n_unique_bat_experiment_units"],
              "support",data["registered_source_strata_with_onoff_min4"])
        for e,a in data["experiments"].items():
            print("EXPERIMENT",name,e,"bats",a["n_bats"],
                  "bat_conditions",a.get("n_bat_condition_cells"),
                  "dIF_kHz",a.get("equal_bat_mean_delta_IF_khz"),
                  "dTF_kHz",a.get("equal_bat_mean_delta_TF_khz"),
                  "dB_kHz",a.get("equal_bat_mean_delta_B_khz"),
                  "err_fixed_start",a.get("equal_bat_mean_absolute_error_fixed_start_khz"),
                  "err_fixed_bandwidth",a.get("equal_bat_mean_absolute_error_fixed_bandwidth_khz"),
                  "D_band_minus_start",a.get("mean_D_bandwidth_minus_start_khz"),
                  "D_CI",a.get("mean_D_whole_bat_bootstrap95_khz"),
                  "D_LOO",a.get("mean_D_leave_one_bat_out_min_max_khz"),
                  "wins_start",a.get("source_bats_favor_fixed_start"),
                  "wins_bw",a.get("source_bats_favor_fixed_bandwidth"),
                  "ties",a.get("source_bats_exact_or_near_ties"),
                  "p_descriptive",a.get("exploratory_two_sided_whole_bat_sign_p"))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
