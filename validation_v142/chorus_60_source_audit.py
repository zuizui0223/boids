"""v142: acquire original 61-member California Dryad version ZIP and audit ALL 60 deployments.

Direct public, versioned Dryad original, SHA256 locked. Parses Excel XLS/XLSX
source sheets, isolates true metadata deployment and fish chorus onset/offset,
builds NOMINAL fully covered UTC source effort hours and chorus-overlap hours.

Important: deployment intervals do not establish all-time hydrophone
detectability, particularly masking by ambient/vessel noise. No-event hours
are NOMINAL sampled hours with no logged chorus, not absolute absence of fish.
No tide data have been joined, no independent-coast effect is estimated.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from hashlib import sha256
import io, json,math,sys,zipfile
from pathlib import Path
from urllib.request import urlopen,Request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v137"))
from appendix_site_macro import read_xlsx_table_rows
URL="https://datadryad.org/api/v2/versions/376573/download"
LOCK="c9e2a221955eedc76b9b1927d9cbd1c07fc99875bb661316c5cb516ee297a33e"
SHAPES={
 "MB01":1010,"MB02":738,"MB05":441,"CH01":339,
 "CI01":823,"CI02":913,"CI03":691,"CI04":1011,"CI05":718,
}
PUBLISHED={"Bocaccio":11.5,"Midshipman":10.4,"White Seabass":11.6,"UF310":5.6,"UF440":12.1}
EXPECTED_SITE_COUNT=9

def acquire():
    req=Request(URL,headers={"User-Agent":"Boids-SourceIntegrity/1.0","Accept":"application/zip,*/*"})
    with urlopen(req,timeout=45) as resp:
        buf=resp.read(12*1024*1024+1)
    if len(buf)>12*1024*1024:raise ValueError("Unexpected source original larger than cap")
    h=sha256(buf).hexdigest()
    # The Dryad public version ZIP is assembled per request and can vary in
    # internal ZIP header timestamps/order. The archive SHA is a receipt,
    # not a stable identity key for constituent original scientific files.
    if not zipfile.is_zipfile(io.BytesIO(buf)):raise ValueError("Not original ZIP")
    first_original_hashes={
       "CH01_01_fish.xlsx":"b9b12c09bc626da6bc1ce7465067df0891c44880518d27f4997a0e655c115003",
       "CH01_02_fish.xls":"7ca2184cade5f447e79620ced77e1aa5fb627c5a526b0883a66d69fa23bba3ad",
       "CH01_03_fish.xls":"fdbdd28a1630f3122c1ed78730a2355c6741854f31e03d19307899406a0a919a",
       "CI01_01_fish.xls":"0917cd94083e99865d4d7f7e02b9038501b17d3d8f6705093d3ab86af87be922",
       "CI01_02_fish.xls":"a51a39ed9b91f50e889fdca6665ca0cd09323db9aeede33724eede260694052d",
    }
    with zipfile.ZipFile(io.BytesIO(buf)) as z:
        if len([n for n in z.namelist() if not n.endswith("/")])!=61:
            raise ValueError("Dryad version source workbook membership changed")
        for name,expected_sha in first_original_hashes.items():
            if name not in z.namelist() or sha256(z.read(name)).hexdigest()!=expected_sha:
                raise AssertionError("Pinned original workbook content changed for "+name)

    return buf

def excel_reader(raw,filename):
    if filename.endswith(".xls"):
        import xlrd
        wb=xlrd.open_workbook(file_contents=raw,on_demand=True)
        return {sheet.name:[[sheet.cell_value(i,j) for j in range(sheet.ncols)]
                            for i in range(sheet.nrows)]
                for sheet in wb.sheets()}
    if filename.endswith(".xlsx"):
        d=read_xlsx_table_rows(raw)
        def column_index(col):
            n=0
            for c in col:n=n*26+ord(c)-64
            return n-1
        out={}
        for sheet,r in d.items():
            heads={}
            for cells in r.values():
                for k in cells:heads[k]=column_index(k)
            n=max(heads.values())+1 if heads else 0
            out[sheet]=[[cells.get(next((k for k,ci in heads.items() if ci==j),""),"")
                         for j in range(n)] for _,cells in sorted(r.items())]
        return out
    raise ValueError("Unknown spreadsheet source format "+filename)

def extract_sheet(rows,sheet_name):
    preferred=[name for name in rows if name.lower().strip()==sheet_name.lower()]
    if not preferred and sheet_name=="Detections":
        preferred=[name for name in rows if name.lower().strip().startswith("detection")]
    if len(preferred)!=1:
        raise ValueError("Required unique source tab "+sheet_name+" absent/ambiguous; got "+str(list(rows)))
    sh=rows[preferred[0]]
    if not sh:raise ValueError("Source tab empty")
    header=[str(v).strip().lower().replace("_"," ") for v in sh[0]]
    def one(cols):
        for name in cols:
            if name in header:return header.index(name)
        raise ValueError("Missing original expected header "+str(cols)+" in "+str(header))
    if sheet_name=="Detections":
        if "start time" not in header:
            # Some logs have 5 columns (Input file, Event Number,...);
            # start and end are still header-determined.
            pass
        start=one(("start time","start"))
        end=one(("end time","end"))
        lab=one(("comments","comment","species"))
        return sh,{"start":start,"end":end,"label":lab}
    start=one(("effort start",))
    end=one(("effort end",))
    return sh,{"start":start,"end":end}

def numeric_excel(v):
    if isinstance(v,(int,float)):
        x=float(v)
        if math.isfinite(x) and 35000<x<51000:return x
    if isinstance(v,str):
        s=v.strip()
        if not s:return None
        try:
            x=float(s)
            if math.isfinite(x) and 35000<x<51000:return x
        except ValueError:pass
        for fmt in ("%m/%d/%Y %H:%M:%S.%f","%m/%d/%Y %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S","%m/%d/%Y %H:%M"):
            try:
                dt=datetime.strptime(s,fmt)
                return (dt-datetime(1899,12,30)).total_seconds()/86400
            except ValueError:pass
    return None

def classify(label):
    s=str(label or "").strip()
    t=s.lower().replace(" ","").replace("-","")
    if "bocaccio" in t:return "Bocaccio"
    if "midshipman" in t:return "Midshipman"
    if "seabass" in t or "seabass" in t:return "White Seabass"
    if "uf310" in t:return "UF310"
    if "uf440" in t:return "UF440"
    return "UNRESOLVED:"+s[:45]

def analyze():
    zip_bytes=acquire()
    out={
      "version":"v142_source_60_california_deployment_integrity_1",
      "source_Dryad_DOI":"10.5061/dryad.q2bvq83sw",
      "source_version":7,
      "original_public_zip_url":URL,
      "original_60_files_are_individually_SHA256_fingerprinted":True,
      "first_probed_archive_SHA256_receipt":LOCK,
      "archive_sha_may_vary_because_dynamic_public_assembly":True,
      "pinned_original_workbooks_from_prior_public_receipt":5,
      "source_summary_only_original_not_redistributed":True,
      "nominal_effort_is_not_true_audible_hours":True,
      "hourly_event_absence_not_fish_absence":True,
      "source_study_DOI":"10.3354/meps14910",
      "per_file_quality":[],
      "overall":{},
      "per_site":[],
      "per_chorus":{},
      "global_tide_solar_effect":"NOT_ESTIMATED",
      "independent_coasts_admitted_for_tide_solar_meta":0
    }
    site_sets=defaultdict(set)
    site_types=defaultdict(lambda:defaultdict(set))
    detected_events=Counter()
    total_reported_events=0
    alllabels=Counter()
    invalid=[]
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        members=[m for m in archive.namelist() if not m.endswith("/")]
        sourcefiles=[m for m in members if m.lower().endswith((".xls",".xlsx"))]
        if len(sourcefiles)!=60 or len(members)!=61:
            raise AssertionError("Unexpected source public release file count")
        for filename in sorted(sourcefiles):
            orig=archive.read(filename)
            site=filename.split("_")[0]
            if site not in SHAPES:raise ValueError("Unrecognized published site "+site)
            tables=excel_reader(orig,filename)
            detects,di=extract_sheet(tables,"Detections")
            metadata,mi=extract_sheet(tables,"MetaData")
            efforts=[]
            for r in metadata[1:]:
                a=numeric_excel(r[mi["start"]] if len(r)>mi["start"] else None)
                b=numeric_excel(r[mi["end"]] if len(r)>mi["end"] else None)
                if a is None and b is None:continue
                if a is None or b is None or b<=a:
                    invalid.append({"file":filename,"issue":"broken_meta_effort_pair","values":str([a,b])})
                    continue
                efforts.append((a,b))
            if not efforts:
                raise ValueError("Original workbook deployment has no effort: "+filename)
            if len(efforts)!=1:
                invalid.append({"file":filename,"issue":"multiple_recording_intervals", "n":len(efforts)})
            fullhours=set()
            for a,b in efforts:
                # UTC source time serial days; fully enclosed integer UTC hours.
                first=math.ceil(a*24-1e-8)
                last=math.floor(b*24+1e-8)
                fullhours.update(range(first,last))
            events=[]
            bad=Counter()
            for r in detects[1:]:
                a=numeric_excel(r[di["start"]] if len(r)>di["start"] else None)
                b=numeric_excel(r[di["end"]] if len(r)>di["end"] else None)
                if a is None and b is None:continue
                if a is None or b is None or b<=a or b-a>100:
                    bad["invalid_time_or_pair"]+=1
                    continue
                lab=str(r[di["label"]] if len(r)>di["label"] else "").strip()
                norm=classify(lab)
                all_labels_key=lab if lab else "EMPTY_SOURCE_LABEL"
                alllabels[all_labels_key]+=1
                events.append((a,b,norm))
                if not any(a>=t0-1/24 and b<=t1+1/24 for t0,t1 in efforts):
                    bad["event_outside_nominal_deployment_effort"]+=1
                if norm.startswith("UNRESOLVED:"):bad["unrecognized_chorus_label"]+=1
            if bad:invalid.append({"file":filename,"issues":dict(bad)})
            total_reported_events+=len(events)
            local_type_hours=defaultdict(set)
            for a,b,norm in events:
                first=math.floor(a*24+1e-8)
                last=math.ceil(b*24-1e-8)
                if last-first>3000:raise ValueError("Absurd positive event duration")
                local_type_hours[norm].update(range(first,last))
                detected_events[norm]+=1
            for k,hrs in local_type_hours.items():
                site_types[site][k].update(hrs & fullhours)
            site_sets[site].update(fullhours)
            out["per_file_quality"].append({
               "file":filename,
               "sha256":sha256(orig).hexdigest(),
               "source_detection_sheet_rows_including_header":len(detects),
               "nominal_metadata_intervals":len(efforts),
               "effort_start_excel_serial":round(min(t[0] for t in efforts),8),
               "effort_end_excel_serial":round(max(t[1] for t in efforts),8),
               "nominal_deployed_days":round(sum(b-a for a,b in efforts),5),
               "nominal_full_UTC_hours":len(fullhours),
               "raw_detection_events":len(events),
               "has_zero_events":len(events)==0,
               "chorus_labels_events":dict(sorted(Counter(c for a,b,c in events).items())),
               "nominal_chorus_positive_hours":{k:len(hrs & fullhours) for k,hrs in local_type_hours.items()},
               "source_date_cell_layout":list(tables.keys())
            })
    n_hrs=sum(len(x) for x in site_sets.values())
    if n_hrs<150000 or n_hrs>170000:
        invalid.append({"issue":"published_18.3_years_total_effort_disagrees","total_full_hours":n_hrs})
    for site in sorted(site_sets):
        den=len(site_sets[site])
        out["per_site"].append({
            "site":site,
            "n_deployments":sum(f["file"].startswith(site+"_") for f in out["per_file_quality"]),
            "nominal_UTC_full_hrs_union":den,
            "nominal_effort_days_union":round(den/24,5),
            "published_effort_days":SHAPES[site],
            "difference_days_from_published":round(den/24-SHAPES[site],5),
            "raw_detection_event_rows":sum(f["raw_detection_events"] for f in out["per_file_quality"] if f["file"].startswith(site+"_")),
            "category_positive_hours_nominal":{
                name:len(site_types[site][name]) for name in PUBLISHED},
            "category_positive_fraction_nominal":{
                name:round(len(site_types[site][name])/den,6) for name in PUBLISHED},
        })
    out["overall"]={
        "source_workbook_files":len(out["per_file_quality"]),
        "source_sites":len(site_sets),
        "source_with_zero_detected_events":sum(f["has_zero_events"] for f in out["per_file_quality"]),
        "source_event_rows_accepted":total_reported_events,
        "source_labels_raw":dict(sorted(alllabels.items())),
        "nominal_full_UTC_recording_hours_across_nine_sites":n_hrs,
        "nominal_cumulative_recording_years":round(n_hrs/(24*365.25),5),
        "published_total_days":sum(SHAPES.values()),
        "published_cumulative_years":round(sum(SHAPES.values())/365.25,5),
        "source_anomaly_count":len(invalid),
        "source_anomalies":invalid[:50],
    }
    out["per_chorus"]={
        c:{
          "source_event_count":detected_events[c],
          "positive_nominal_recording_hours_across_sites":sum(len(site_types[site][c]) for site in site_sets),
          "percent_nominal_source_site_hours":round(
              100*sum(len(site_types[site][c]) for site in site_sets)/n_hrs,4),
          "published_overall_percent_rounded":PUBLISHED[c],
        } for c in PUBLISHED}
    out["overall"]["unresolved_event_labels"]={k:v for k,v in detected_events.items() if k.startswith("UNRESOLVED:")}
    return out

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    out=analyze()
    path=Path(__file__).parent/"results"/"all_60_chorus_original_source_audit.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    if args.check:
        if out!=json.loads(path.read_text()):
            raise AssertionError("Frozen 60-original workbook audit changed from source")
    else:
        path.write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print("V142_ALL_60_START")
    print(json.dumps(out,ensure_ascii=False))
    print("V142_ALL_60_END")
    # Not all anomalies invalidate descriptive audit; original must remain visible.
    if out["overall"]["source_sites"]!=9 or out["overall"]["source_workbook_files"]!=60:
        raise AssertionError("Missing original site or source workbook")

if __name__=="__main__":main()
