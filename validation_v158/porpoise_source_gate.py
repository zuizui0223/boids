"""v158: independent 2009-2023 NE Atlantic harbour porpoise Data S2 source gate.

Literature: Stavenow Jerremalm et al. 2025 DOI 10.1002/ece3.72566,
open access PMC12664825; 43 C-POD sites grouped into six published
regions. Its 25.2 MB supplementary Data S2 CSV is published by Wiley.

This script tests the REAL provider supplementary CSV's existence, original
schema, row-level source completeness and column names BEFORE any biological
foraging or tide prediction is fit. A CSV row is NOT automatically an
independent positive or a valid non-detection hour, nor 43 biological coasts.

IMPORTANT: original source has foraging clicks and detections. A row-level
positive sound/click is not verified on-effort 0-click opportunity.
Never set unlisted timestamps to zero click/foraging, and never pool into a
global tide×solar coefficient without verified hourly effort denominators.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,re,zipfile
from pathlib import Path
from urllib.request import urlopen,Request
from collections import Counter

PMC="PMC12664825"
DOI="10.1002/ece3.72566"
SOURCE="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12664825/supplementaryFiles?includeInlineImage=false"
BASENAME="ece372566-sup-0002-DataS2.csv"
EPMC_ORIGINAL_MEMBER_ALIASES=(BASENAME,"ECE3-15-e72566-s002.csv")
ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"results"/"source_43site_sixregion_schema_gate_v158.json"
MAX_ARCHIVE_BYTES=130*1024*1024
MAX_CSV_BYTES=60*1024*1024
MAX_COLUMNS=160
MAX_DISTINCT_PER_CANDIDATE=201
MAX_SAMPLE_HEADERS=160

def acquire():
    req=Request(SOURCE,headers={"User-Agent":"OpenScienceBoids/1.0 (non-commercial primary-source audit)",
                               "Accept":"application/zip, */*"})
    with urlopen(req,timeout=100) as response:
        zbytes=response.read(MAX_ARCHIVE_BYTES+1)
    if len(zbytes)>MAX_ARCHIVE_BYTES or not zipfile.is_zipfile(io.BytesIO(zbytes)):
        raise ValueError("EuropePMC supplementary source ZIP missing or too large")
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        members=[f for f in z.namelist() if f.rsplit("/",1)[-1].lower() in {v.lower() for v in EPMC_ORIGINAL_MEMBER_ALIASES}]
        if len(members)!=1:
            raise ValueError("Expected original Data S2 CSV missing/ambiguous; member names="+repr(z.namelist()[:60]))
        info=z.getinfo(members[0])
        if info.file_size>MAX_CSV_BYTES:
            raise ValueError("Source DataS2 beyond predeclared 60 MB cap")
        raw=z.read(members[0])
        if len(raw)!=info.file_size:raise ValueError("CSV data incomplete")
    if b"\x00" in raw[:5000]:raise ValueError("Unexpected source NUL")
    return raw,{"source_archive_bytes":len(zbytes),
                "source_archive_sha256":hashlib.sha256(zbytes).hexdigest(),
                "named_csv_member":members[0],
                "source_csv_original_sha256":hashlib.sha256(raw).hexdigest(),
                "source_csv_bytes":len(raw)}

def audit_csv(raw,src):
    text=raw.decode("utf-8-sig",errors="replace")
    try:dialect=csv.Sniffer().sniff(text[:12000],delimiters=",;\t")
    except csv.Error:dialect=csv.excel
    if dialect.delimiter not in (",",";","\t"):raise AssertionError("Unsupported CSV delimiter")
    data=csv.DictReader(io.StringIO(text,newline=""),dialect=dialect)
    fields=list(data.fieldnames or [])
    if not fields or len(fields)>MAX_COLUMNS or len(set(fields))!=len(fields):
        raise AssertionError("Original source header missing or repeated or too wide")
    if any(not name.strip() for name in fields):
        raise AssertionError("Empty original source column name")
    nonempty=Counter();numeric=Counter();zeros=Counter();empty=Counter();candidates={}
    schema_tags={
        "time":re.compile(r"date|time|year|month|day|hour|utc|timestamp",re.I),
        "region":re.compile(r"region|area|country|sea|basin|latitude|longitude|lat$|lon$",re.I),
        "station":re.compile(r"site|station|cpod|deployment|recorder|location|device",re.I),
        "effort":re.compile(r"effort|availability|coverage|operating|record|exposure|monitor|duration|minutes|on[_ ]?time",re.I),
        "foraging":re.compile(r"forag|buzz|prey|feeding",re.I),
        "acoustics":re.compile(r"click|echolocat|detect|positive|train",re.I),
        "environment":re.compile(r"temp|salin|chlor|sst|prod|daylength|night|diel|solar|tide|moon|water",re.I),
    }
    for kind,rx in schema_tags.items():
        candidates[kind]=[f for f in fields if rx.search(f)]
    count=0
    for row in data:
        if set(row)!=set(fields):raise AssertionError("Original CSV row has unexpected column count")
        count+=1
        for col in fields:
            v=row[col]
            if v is None or not v.strip():
                empty[col]+=1;continue
            nonempty[col]+=1
            try:f=float(v)
            except ValueError:continue
            if math.isfinite(f):
                numeric[col]+=1
                if f==0:zeros[col]+=1
        if count>10000000:raise ValueError("Source unexpected >10M rows")
    if count<100:
        raise AssertionError("Original published Data S2 unexpectedly under 100 rows")
    return {
        "version":"v158_NE_Atlantic_2025_porpoise_supplement2_source_only_1",
        "study_DOI":DOI,"pmcid":PMC,"source_url":SOURCE,
        "published_original_scope":{"regions_reported":6,"field_sites_reported":43,
                                     "field_years_reported":"2009-2023",
                                     "reported_supplement_csv_human_size":"25.2 MB"},
        "source_provenance":src,
        "CSV_delimiter":dialect.delimiter,
        "n_csv_data_rows":count,
        "n_csv_columns":len(fields),
        "original_field_names":fields,
        "candidate_schema_columns_by_name_ONLY":candidates,
        "per_field_nonempty_rows":dict(nonempty),
        "per_field_blank_rows":dict(empty),
        "per_field_finite_numeric_rows":dict(numeric),
        "per_field_numeric_zero_rows":dict(zeros),
        "number_of_sites_regions_in_row_content":"NOT_COMPUTED_FROM_SCHEMA_ONLY",
        "fish_or_porc_cpod_detection_event_kind":"NOT_VALIDATED_FROM_COLUMN_NAMES_ALONE",
        "source_no_detection_effort_and_zero_hour_denominator":"NOT_VERIFIED",
        "site_timestamp_uniqueness":"NOT_VERIFIED",
        "negative_source_hours":"DO_NOT_CREATE_FROM_MISSING_ROWS",
        "physical_tide_aligned_to_sites":"NOT_JOINED",
        "can_fit_tide_solar_own_history_coast_models":"SOURCE_SCHEMA_ONLY_NOT_YET_ADMITTED",
        "global_tide_solar_pooled_biological_effect":"NOT_ESTIMATED",
        "no_raw_CSV_or_unique_event_timestamps_redistributed":True,
    }

def run():
    raw,meta=acquire()
    return audit_csv(raw,meta)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    result=run()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    if a.check:
        if not OUTPUT.exists():raise AssertionError("Original v158 source schema receipt not frozen")
        previous=json.loads(OUTPUT.read_text())
        # Compare exact provider CSV SHA + rows and schema, and all summary fields;
        # ZIP wrapper bytes can change without the original CSV bytes changing.
        if previous!=result:raise AssertionError("Original DataS2 contents/schema changed")
        print("V158_ORIGINAL_NE_ATLANTIC_DATA_S2_REPLAY_PASS")
    else:
        OUTPUT.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V158_ORIGINAL_SOURCE_SCHEMA_START")
    print(json.dumps(result,ensure_ascii=True,sort_keys=True,separators=(",",":")))
    print("V158_ORIGINAL_SOURCE_SCHEMA_END")

if __name__=="__main__":main()
