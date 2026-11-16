"""v164: inspect ORIGINAL published R analysis script and input provenance.

Original source: Stavenow Jerremalm et al. 2025, Ecology & Evolution
doi:10.1002/ece3.72566, Europe PMC supplementaryFiles for PMC12664825.

Source ZIP has original Data S2 CSV and Data S1 R script, both author-published.
Reacquire and SHA verify CSV against v158-v163; extract R member checksum
and lexical method/data input manifest. Disclose no copyrighted source code,
local computer paths, raw CSV rows, or animal timestamps.

This is a SOURCE-only lexical method audit, NOT evidence that R actually
executed a command, and absence of a term is not evidence the underlying
raw monitoring effort or device deployment did not exist.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,zipfile,os
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
SOURCE="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12664825/supplementaryFiles?includeInlineImage=false"
R_MEMBER="ECE3-15-e72566-s001.R"
CSV_MEMBER="ECE3-15-e72566-s002.csv"
CSV_SHA256="972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf"
EXPECTED_CSV_BYTES=26454371
OUTPUT=ROOT/"validation_v164/results/porpoise_published_R_source_provenance_v164.json"
FROZEN=ROOT/"validation_v163/results/frozen_record_trim_receipt_v163.json"
TOKENS={
 "read_csv_call":r"\b(?:read\.csv|read_csv|read\.table|fread|read_delim)\s*\(",
 "read_RDS_call":r"\b(?:readRDS|load|read_excel|read\.xlsx)\s*\(",
 "file_write_call":r"\b(?:write\.csv|write_csv|saveRDS|write_xlsx)\s*\(",
 "missing_value_replace":r"\b(?:replace_na|fill_na|na\.omit|drop_na|complete\.cases)\s*\(",
 "explicit_hour_grid":r"\b(?:complete|expand|expand_grid|seq\.POSIXt|full_join|merge)\s*\(",
 "left_or_inner_join":r"\b(?:left_join|inner_join|right_join|semi_join|anti_join)\s*\(",
 "filter_operation":r"\b(?:filter|subset)\s*\(",
 "mutate_operation":r"\b(?:mutate|transform)\s*\(",
 "group_by_operation":r"\b(?:group_by|aggregate|summarise|summarize)\s*\(",
 "model_operation":r"\b(?:glmmTMB|glmer|glm|gam|gamm|bam|lm|lmer)\s*\(",
 "period_OR_source_strings":r"\b(?:SITE|COUNTRY|GROUP|HONO|NVSK4|LS4|MRC3|AWAC|year|YDAY)\b",
 "hour_keywords":r"\b(?:hour|hr|timestamp|date|as\.POSIXct|as\.Date)\b",
 "acoustic_keywords":r"\b(?:clicks|click|buzz|buzprop|foraging_click|DPM|CPOD|C.POD)\b",
 "zero_filling_keywords":r"\b(?:replace_na|complete|expand|fill|full_join|zero|zeros)\b",
 "effort_keywords":r"\b(?:effort|deployment|operating|on.effort|coverage|off.time|duty.cycle)\b",
}
SOURCE_FILE_LITERAL=re.compile(r"""(?P<q>['"])(?P<name>[^'"\r\n]{1,220}\.(?:csv|txt|rds|rdata|xlsx|xls|cp1|cp3|r))(?P=q)""", re.I)
MAX_ZIP=20*1024*1024
MAX_R=5*1024*1024

def sha(data):
    return hashlib.sha256(data).hexdigest()

def acquire_originals():
    req=Request(SOURCE,headers={"User-Agent":"OpenScienceBoids-SourceAudit/1.0","Accept":"application/zip,*/*"})
    with urlopen(req,timeout=90) as resp:
        content=resp.read(MAX_ZIP+1)
    if len(content)>MAX_ZIP or not zipfile.is_zipfile(io.BytesIO(content)):
        raise ValueError("Original supplementary archive unavailable/too large")
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        names=z.namelist()
        matches_R=[n for n in names if n.rsplit("/",1)[-1].lower()==R_MEMBER.lower()]
        matches_C=[n for n in names if n.rsplit("/",1)[-1].lower()==CSV_MEMBER.lower()]
        if len(matches_R)!=1 or len(matches_C)!=1:
            raise AssertionError("Original published supplementary R/CSV members missing or ambiguous")
        if z.getinfo(matches_R[0]).file_size>MAX_R:
            raise AssertionError("Unexpected >5 MB supplementary R source")
        rraw=z.read(matches_R[0])
        csv_sha=sha(z.read(matches_C[0]))
        if csv_sha!=CSV_SHA256 or z.getinfo(matches_C[0]).file_size!=EXPECTED_CSV_BYTES:
            raise AssertionError("Publisher's archived original CSV DATA S2 SHA/bytes changed")
    return rraw,{"original_R_script_filename":os.path.basename(matches_R[0]),
                 "original_R_script_bytes":len(rraw),
                 "original_R_script_SHA256":sha(rraw),
                 "original_CSV_member_filename":os.path.basename(matches_C[0]),
                 "original_CSV_member_bytes":EXPECTED_CSV_BYTES,
                 "original_CSV_member_SHA256":CSV_SHA256,
                 "R_lexical_classification_not_execution_trace":True}

def audit_R(rbytes,original):
    source=rbytes.decode("utf-8-sig",errors="replace")
    lines=source.splitlines()
    if len(lines)<20 or source.count("\ufffd")>len(source)//10:
        raise AssertionError("Original R script unexpectedly missing / corrupt encoding")
    code_lines=[]
    for i,line in enumerate(lines,1):
        stripped=line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        # Comment characters in R strings are possible: conservative lexical
        # count, NOT executable AST parsing. Avoid claiming execution.
        code_lines.append((i,line))
    lexical={}
    for name,pattern in TOKENS.items():
        reg=re.compile(pattern,re.I)
        matching=[i for i,line in code_lines if reg.search(line)]
        lexical[name]={"n_code_lines_with_token":len(matching),
                       "source_line_numbers_first_40":matching[:40]}
    file_refs=Counter()
    for i,line in code_lines:
        for match in SOURCE_FILE_LITERAL.finditer(line):
            # No absolute local paths, only basename and a count.
            path=match.group("name").replace("\\","/")
            file_refs[os.path.basename(path)]+=1
    # Inspect only existence of source utility constructs by lexical pattern.
    # Never reveal full author code or claim a missing keyword proves absent
    # raw equipment effort.
    a={
        "version":"v164_authentic_publisher_R_analysis_and_CSV_source_manifest_only_1",
        "paper_DOI":"10.1002/ece3.72566",
        "PMC":"PMC12664825",
        "source_EuropePMC_supplement_archive_url":SOURCE,
        "source_original_provenance":original,
        "R_total_lines":len(lines),
        "R_nonempty_noncomment_code_lines":len(code_lines),
        "R_code_replacement_character_count":source.count("\ufffd"),
        "named_source_file_literals_basename_ONLY":dict(sorted(file_refs.items())),
        "lexical_pattern_code_line_hits":lexical,
        "R_source_READER_contract":"LEXICAL_ONLY_NOT_PROOF_OF_EXECUTED_WORKFLOW",
        "R_source_not_redistributed_due_to_copyright":True,
        "no_public_Cpod_no_click_effort_denominator_in_DataS2":True,
        "original_TableA1_vs_CSV_site_month_mismatch_unresolved":True,
        "analysis_dispositive_for_published_Site_group_year_OR_offeffort":"NOT_YET_ESTABLISHED",
        "new_biological_tide_x_solar_effect":"NOT_ESTIMATED",
        "individual_social_Boids_effect":"NOT_IDENTIFIED"
    }
    return a

def analyze():
    old=json.loads(FROZEN.read_text())
    if (old["source_quality"]["source_original_records"]!=126231 or
        old["source_quality"]["source_records_within_published_months"]!=105916 or
        old["original_wiley_member_SHA256"]!=CSV_SHA256):
        raise AssertionError("Prior original full source quality receipt changed")
    rbytes,source=acquire_originals()
    return audit_R(rbytes,source)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    opts=p.parse_args()
    result=analyze()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    if opts.check:
        if not OUTPUT.is_file():raise AssertionError("Published source-only R audit receipt missing")
        previous=json.loads(OUTPUT.read_text())
        if previous!=result:
            raise AssertionError("Original R or CSV member SHA, source token counts or referenced file names changed")
        print("V164_ORIGINAL_CSV_AND_R_SOURCE_REPLAY_PASS")
    else:
        OUTPUT.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V164_ORIGINAL_R_SOURCE_RESULT_START")
        print(json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V164_ORIGINAL_R_SOURCE_RESULT_END")
    print("V164_SOURCE_DIGEST="+json.dumps({
        "R_bytes":result["source_original_provenance"]["original_R_script_bytes"],
        "R_sha":result["source_original_provenance"]["original_R_script_SHA256"],
        "R_code_lines":result["R_nonempty_noncomment_code_lines"],
        "file_literal_names":list(result["named_source_file_literals_basename_ONLY"]),
        "lexical_code_line_hits":{k:v["n_code_lines_with_token"]
                     for k,v in result["lexical_pattern_code_line_hits"].items()},
    },ensure_ascii=True,sort_keys=True))

if __name__=="__main__":
    main()
