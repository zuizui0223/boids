"""Reanalyse the ACTUAL published Appendix S1 site-level RAI and metadata.

Caution: this is a spatial habitat baseline; NOT tide×solar, foraging,
activity rates, same-animal transitions, or independent 32-coast meta effects.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from math import log, isfinite
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from supplement_probe import get_supplement

X="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
EXPECTED_SHA256="a1012d332fd9c8c1ee4933cb51242060bbd7aea0e8a048489a53e3563d980eee"

def read_xlsx_table_rows(raw):
    """Handle shared/inline strings and number cells without third-party libs."""
    z=zipfile.ZipFile(io.BytesIO(raw))
    sst=[]
    if "xl/sharedStrings.xml" in z.namelist():
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for node in root.findall("{%s}si"%X):
            sst.append("".join(t.text or "" for t in node.iter("{%s}t"%X)))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid={}
    for e in rels:
        target=e.attrib["Target"].lstrip("/")
        if not target.startswith("xl/"):
            target="xl/"+target
        rid[e.attrib["Id"]]=target
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    sheets={}
    for sheet in wb.find("{%s}sheets"%X):
        name=sheet.attrib["name"]
        path=rid[sheet.attrib["{%s}id"%R]]
        root=ET.fromstring(z.read(path))
        rows=[]
        for r in root.findall(".//{%s}sheetData/{%s}row"%(X,X)):
            cells={}
            for c in r.findall("{%s}c"%X):
                m=re.match("([A-Z]+)",c.attrib.get("r",""))
                if not m:continue
                col=m.group(1)
                node=c.find("{%s}v"%X)
                val="" if node is None else (node.text or "")
                if c.attrib.get("t")=="s" and val:
                    val=sst[int(val)]
                elif c.attrib.get("t")=="inlineStr":
                    val="".join(t.text or "" for t in c.findall(".//{%s}is/{%s}t"%(X,X)))
                cells[col]=str(val).strip()
            rows.append((int(r.attrib.get("r",0)),cells))
        sheets[name]=dict(rows)
    return sheets

def numeric(s):
    try:
        f=float(s)
        return f if isfinite(f) else None
    except (ValueError,TypeError):
        return None

def site_summary(sheets):
    meta=sheets["Station metadata"]
    first=meta[1]
    if ("Total deployment time" not in first.get("R","") or "Site code" not in first.get("D","")):
        raise ValueError("Source station metadata layout changed")
    stations=[]
    for row,r in meta.items():
        if row==1:continue
        hours=numeric(r.get("R"))
        if hours is not None and hours>0 and r.get("D") and r.get("F"):
            stations.append({"site_code":r["D"],"station":r["F"],
                             "site_name":r.get("E"),"wetland_type":r.get("G"),
                             "hours":hours,"latitude":numeric(r.get("M")),
                             "longitude":numeric(r.get("N"))})
    if not stations:
        raise ValueError("No valid camera deployment records")
    time_total=sum(s["hours"] for s in stations)
    entries=sheets["Site means"]
    if "Species" not in entries[5].get("E",""):
        raise ValueError("RAI species header changed")
    colsite=entries[4]
    habitat=entries[5]
    validcols={c:{"site":site,"habitat":habitat.get(c)}
               for c,site in colsite.items()
               if re.match(r"^[A-Z]+$",c) and len(c)>0 and
                  c not in ("A","B","C","D","E","F") and
                  habitat.get(c) in ("Wetland","Ecotone")}
    taxa=[]
    for row,r in entries.items():
        if row<6:continue
        if not r.get("E") or not r.get("A"):continue
        values={c:numeric(r.get(c)) for c in validcols}
        if not any(v is not None for v in values.values()):continue
        taxa.append({"class":r["A"],"species":r["E"],"values":values})
    tax_counts=Counter(t["class"] for t in taxa)
    pair=defaultdict(lambda:{"Wetland":[],"Ecotone":[]})
    for col,v in validcols.items():
        pair[v["site"]][v["habitat"]].append(col)
    paired=[]
    for site,cols in pair.items():
        if not cols["Wetland"] or not cols["Ecotone"]:continue
        vals={}
        for tax_class in ("Mammalia","Aves"):
            src=[t for t in taxa if t["class"]==tax_class]
            def class_mean_score(which):
                measurements=[]
                for c in cols[which]:
                    valid=[t["values"][c] for t in src if t["values"][c] is not None]
                    if valid:
                        measurements.append(sum(valid))
                return sum(measurements)/len(measurements) if measurements else None
            wet,eco=class_mean_score("Wetland"),class_mean_score("Ecotone")
            vals[tax_class]={
                "site_wetland_rai_sum":round(wet,5) if wet is not None else None,
                "site_ecotone_rai_sum":round(eco,5) if eco is not None else None,
                "log_ecotone_wetland_ratio_plus_one":round(log((eco+1)/(wet+1)),5) if wet is not None and eco is not None else None,
            }
        paired.append({"site":site,"n_wetland_columns":len(cols["Wetland"]),
                       "n_ecotone_columns":len(cols["Ecotone"]),
                       "taxonomic_rai":vals})
    paired.sort(key=lambda x:x["site"])
    def paired_class_summary(class_name):
        data=[x["taxonomic_rai"][class_name]["log_ecotone_wetland_ratio_plus_one"] for x in paired]
        data=[v for v in data if v is not None]
        return {"paired_locations_n":len(data),
                "median_log_pseudocount_ratio":round(statistics.median(data),5) if data else None,
                "ecotone_greater_n":sum(v>0 for v in data),
                "wetland_greater_n":sum(v<0 for v in data),
                "equal_n":sum(v==0 for v in data),
                "pseudocount":1,
                "statistical_test":"NOT_FITTED",
                "tide_effect":"NOT_ESTIMATED"}
    taxa_nonzero=sum(1 for t in taxa for v in t["values"].values() if v is not None and v>0)
    taxa_numeric=sum(1 for t in taxa for v in t["values"].values() if v is not None)
    return {
        "dataset_sha256":EXPECTED_SHA256,
        "dataset_type":"published site-mean species RAI and station deployment metadata, NOT photo events",
        "station_metadata":{
            "valid_positive_hours_stations":len(stations),
            "distinct_site_codes":len(set(s["site_code"] for s in stations)),
            "sum_listed_hours":round(time_total,2),
            "reported_manuscript_total_camera_hours":202146,
            "difference_from_manuscript":round(time_total-202146,2),
            "stations_with_coordinate_pair":sum(s["latitude"] is not None and s["longitude"] is not None for s in stations),
            "hours_range":[min(s["hours"] for s in stations), max(s["hours"] for s in stations)],
            "wetland_types":dict(sorted(Counter(s["wetland_type"] for s in stations).items())),
        },
        "site_mean_raI":{
            "numeric_site_by_habitat_columns":len(validcols),
            "site_labels_count":len(pair),
            "wetland_columns":sum(1 for v in validcols.values() if v["habitat"]=="Wetland"),
            "ecotone_columns":sum(1 for v in validcols.values() if v["habitat"]=="Ecotone"),
            "taxonomic_rows_with_data":len(taxa),
            "distinct_species_labels":len(set(t["species"] for t in taxa)),
            "class_row_counts":dict(sorted(tax_counts.items())),
            "numeric_rai_cells":taxa_numeric,
            "positive_rai_cells":taxa_nonzero,
            "paired_site_labels_with_both_habitats":len(paired),
            "paired_ecotone_minus_wetland_log_rai_pseudocount":{
                "Mammalia":paired_class_summary("Mammalia"),
                "Aves":paired_class_summary("Aves")},
        },
        "paired_site_descriptives":paired,
        "temporal_exposure_columns":"ABSENT",
        "event_timestamps":"ABSENT",
        "flooded_dry_effective_camera_hours":"ABSENT",
        "tide_by_solar_ecological_rate_effect":"NOT_ESTIMATED",
        "causal_habitat_switch":"NOT_ESTIMATED",
        "cautions":[
            "paired columns can reflect non-independent sites and shared reserve sampling",
            "RAI is mean detections per 100 camera days, not occupancy or individual movement",
            "sum of species RAI is not independent biological replication",
            "camera placement, detection and station design differ between wetland and ecotone",
            "zero/nonzero RAI is a site aggregate, not a tidal/diel zero-effort event",
        ],
    }

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--check",action="store_true")
    args=cli.parse_args()
    raw,url,container,attempts=get_supplement()
    if raw is None:
        raise RuntimeError("Could not reacquire original Appendix S1")
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=EXPECTED_SHA256:
        raise AssertionError("Original source bytes changed; provenance audit required "+sha)
    result=site_summary(read_xlsx_table_rows(raw))
    result["original_url"]=url
    result["source_file_bytes"]=len(raw)
    path=Path("validation_v137/appendix_macro_result.json")
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    if args.check:
        saved=json.loads(Path("validation_v137/results/site_macro_source_snapshot.json").read_text())
        if result != saved:
            raise AssertionError("Frozen published-source-derived site summary changed; review original source")
    print("APPENDIX_MACRO_JSON_START")
    print(json.dumps(result,ensure_ascii=False))
    print("APPENDIX_MACRO_JSON_END")

if __name__=="__main__":
    main()
