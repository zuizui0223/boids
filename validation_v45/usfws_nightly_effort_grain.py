#!/usr/bin/env python3
"""v45 original USFWS Nightly XLSX source-grain audit, no species/pass values."""
import argparse, collections, hashlib, io, json, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from usfws_zip_range_directory import ORIGINAL_TOTAL,TAIL_BYTES,central_location,http_range
from usfws_zip_in_tail_v43a import PINNED_TAIL_SHA256
from usfws_bounded_xlsx_headers import full_directory_entries,choose_members,fetch_member,NS

OUT=Path("validation_v45/results/usfws_nightly_source_grain_v45.json")
CATS={
 "site":("site","station","location"),
 "night":("night","date","day"),
 "year":("year",),
 "detector":("detector","recorder","device"),
 "effort":("wac","recording hours","recorded hours","recording time","hours operated","hours of operation","minutes recorded","number of files"),
}
PRIV=("roost","lat","lon","coordinate","gps","person","email","address")

def colidx(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    if not m:return None
    n=0
    for x in m[1]:n=n*26+ord(x)-64
    return n-1

def first_row(z,p):
    refs={}
    with z.open(p) as f:
        for _,row in ET.iterparse(f,events=("end",)):
            if row.tag!=""+NS+"row":continue
            for c in row:
                idx=colidx(c.attrib.get("r"))
                if idx is None:continue
                t=c.attrib.get("t","")
                v=c.find(NS+"v")
                if t=="s" and v is not None:
                    try:refs[idx]=("s",int(v.text))
                    except (ValueError,TypeError):pass
                elif t=="inlineStr":refs[idx]=("t","".join(x.text or "" for x in c.iter(NS+"t")))
            break
    wanted={v for typ,v in refs.values() if typ=="s"}
    found={}
    if wanted and "xl/sharedStrings.xml" in z.namelist():
        if z.getinfo("xl/sharedStrings.xml").file_size>20000000:
            raise ValueError("SHARED_STRING_CAP_STOP")
        i=0
        with z.open("xl/sharedStrings.xml") as f:
            for _,e in ET.iterparse(f,events=("end",)):
                if e.tag==NS+"si":
                    if i in wanted:found[i]="".join(t.text or "" for t in e.iter(NS+"t"))
                    e.clear();i+=1
    return {idx:found.get(v,"") if t=="s" else v for idx,(t,v) in refs.items()}

def sanitized_label(value):
    s=str(value).strip()
    if len(s)>70 or not s or not re.fullmatch(r"[A-Za-z0-9 #_()/:+.%-]+",s):
        return None
    if any(x in s.casefold() for x in PRIV):return None
    return s

def inspect_sheet(z,path):
    header=first_row(z,path)
    categories=collections.defaultdict(list)
    for idx,val in header.items():
        low=val.casefold().replace("_"," ")
        if len(val)>75:continue
        for kind,terms in CATS.items():
            if any(t in low for t in terms):
                if kind!="effort" and any(t in low for t in ("pass","count","activity","species","detection")):
                    continue
                categories[kind].append(idx)
    # Ambiguous field family is never silently selected.
    grouped={kind:ix[0] for kind,ix in categories.items() if kind!="effort" and len(ix)==1}
    effort_cols=categories.get("effort",[])
    needed=set(grouped.values())|set(effort_cols)
    rows=0;present_effort=0;complete_keys=0;groups=collections.Counter()
    with z.open(path) as f:
        seen_first=False
        for _,row in ET.iterparse(f,events=("end",)):
            if row.tag!=NS+"row":continue
            if not seen_first:
                seen_first=True;row.clear();continue
            rows+=1
            if rows>1000000:raise ValueError("ROW_CAP_STOP")
            found={}
            for cell in row:
                col=colidx(cell.attrib.get("r"))
                if col not in needed:continue
                t=cell.attrib.get("t","")
                v=cell.find(NS+"v")
                if t=="s" and v is not None:
                    found[col]="shared_index_"+(v.text or "")
                elif t=="inlineStr":
                    s="".join(x.text or "" for x in cell.iter(NS+"t"))
                    found[col]="opaque_"+hashlib.sha256(s.encode()).hexdigest()[:15] if s else ""
                elif v is not None and v.text is not None:
                    # ONLY parse source grouping ID or recorder-effort field,
                    # no acoustic count or species response cells.
                    found[col]=v.text
            present_effort+=sum(bool(found.get(j)) for j in effort_cols)
            key=tuple(found.get(j,"") for j in grouped.values())
            if key and all(key):
                complete_keys+=1;groups[key]+=1
            row.clear()
    return {
        "source_rows_excluding_header":rows,
        "original_first_row_header_cell_n":len(header),
        "generic_header_labels":[v for v in (sanitized_label(x) for x in header.values()) if v],
        "unambiguous_id_column_categories":sorted(grouped),
        "candidate_column_counts":{k:len(v) for k,v in categories.items()},
        "source_rows_with_all_parsed_key_values":complete_keys,
        "distinct_anonymized_observation_keys":len(groups),
        "duplicate_source_rows_under_key":sum(v-1 for v in groups.values() if v>1),
        "nonempty_effort_field_cells":present_effort,
        "original_site_names_or_keys_exported":False,
        "original_bat_pass_count_values_interpreted":False,
    }

def inspect_book(blob,kind):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if sum(x.file_size for x in z.infolist())>40000000:
            return {"status":"INNER_WORKBOOK_CAP_STOP"}
        paths=sorted(x for x in z.namelist()
                     if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",x))
        return {"status":"WORKSHEET_GRAIN_AUDITED_NO_BAT_VALUES","category":kind,
                "sheet_n":len(paths),
                "sheets":[inspect_sheet(z,p) for p in paths[:4]]}

def run(fetcher=None,tail_sha=PINNED_TAIL_SHA256):
    d={"programme":"v45_usfws_nightly_recorder_effort_grain",
       "prior_v42_v43_stops_unchanged":True,
       "original_complete_zip_checksum_not_claimed":True,
       "bat_pass_counts_or_species_numeric_values_interpreted":False,
       "true_zero_nights_verified":False,
       "full_recording_effort_verified":False,
       "behavior_model_fitted":False}
    start=ORIGINAL_TOTAL-TAIL_BYTES
    rr,tail=http_range(start,ORIGINAL_TOTAL-1,fetcher=(
        (lambda u,s,e:fetcher(u,s,e-s+1)) if fetcher else None))
    if tail is None:d["status"]="TAIL_RANGE_STOP";d["receipt"]=rr;return d
    if hashlib.sha256(tail).hexdigest()!=tail_sha:
        d["status"]="PINNED_TAIL_CHECKSUM_STOP";return d
    cd=central_location(tail)
    pos=cd.get("central_directory_offset",-1)-start
    if cd["status"]!="STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED" or pos<0 or pos+cd.get("central_directory_size",0)>len(tail)-22:
        d["status"]="SOURCE_DIRECTORY_STOP";return d
    try:
        entries=full_directory_entries(tail[pos:pos+cd["central_directory_size"]],cd["declared_entry_count"])
        selection,chosen=choose_members(entries)
        d["source_member_sizes"]=selection
        if chosen is None:d["status"]="MEMBER_SELECTION_STOP";return d
        books={}
        for kind,e in chosen.items():
            verified,body=fetch_member(e,fetcher=fetcher)
            if body is None:
                d["status"]="MEMBER_SOURCE_OR_CRC_STOP";d["member_error"]=verified;return d
            books[kind]=inspect_book(body,kind)
        d["workbook_source_grain"]=books
    except (OSError,ValueError,KeyError,ET.ParseError,zipfile.BadZipFile) as exc:
        d["status"]="WORKBOOK_STRUCTURAL_AUDIT_STOP"
        d["failure_type"]=type(exc).__name__;return d
    observed=books["nightly_pass_counts"]["sheets"]
    d["site_night_effort_column_structurally_admitted"]=any(
        x["source_rows_excluding_header"]>=100 and
        {"site","night"}.issubset(x["unambiguous_id_column_categories"]) and
        x["candidate_column_counts"].get("effort",0)>0
        for x in observed)
    d["status"]=("SOURCE_SITE_NIGHT_EFFORT_COLUMNS_IDENTIFIED"
                 if d["site_night_effort_column_structurally_admitted"]
                 else "SOURCE_NIGHT_OR_EFFORT_GRAIN_UNRESOLVED_STOP")
    return d

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=Path("validation_v45/results/usfws_nightly_source_grain_v45.json"))
    args=p.parse_args()
    data=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V45_USFWS_ORIGINAL_NIGHT_GRAIN="+json.dumps(data,sort_keys=True))
    assert data["bat_pass_counts_or_species_numeric_values_interpreted"] is False
    assert data["behavior_model_fitted"] is False
