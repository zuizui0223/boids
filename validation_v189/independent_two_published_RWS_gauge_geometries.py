"""v189: independently published 2006 RWS vs 2011 WEBTICS station RD geometry.
Posthoc reference check, not native 2018/2019 instrument geolocation or biological result.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from original_fifteen_wadden_gauge_inventory import ATLAS
from original_Wadden13_RWS_tide_LOO import STATIONS,REFERENCE_RD,geometry_for_target
from scipy.spatial import Delaunay
import numpy as np

SOURCE_2006="https://www.vliz.be/imisdocs/publications/282819.pdf"
SOURCE_2011="https://nam-feitenencijfers.data-app.nl/download/rapport/d360edf8-1955-4ee4-b0e9-58826d7e0a53?open=true"
# RWS RIKZ/2006.012 Appendix 2 printed p.69 original station reference RD coords.
# Manually transcribed, original PDF binary NOT hash-verified in this script.
PUBLISHED_2006_RD={
"DenHelder":(111776,553163),
"DenOever":(131911,549678),
"Kornwerderzand":(151500,564972),
"Harlingen":(156609,576553),
"Lauwersoog":(208853,602777),
"Eemshaven":(250792,607798),
"Nieuwstatenzijl":(276551,584320),
"Delfzijl":(258000,594430),
"Huibertgat":(222032,621365),
"Schiermonnikoog":(209220,609488),
"Wierumergronden":(192882,614562),
"Nes":(179707,604916),
"WestTerschelling":(143870,597420),
"VlielandHaven":(135307,589943),
"Oudeschild":(119053,561696),
}
OUT=Path(__file__).resolve().parent/"results/published_RWS2006_WEBTICS2011_fifteen_gauge_RD_geometry_v189.json"

def site_weights(target,rd):
    others=[s for s in STATIONS if s!=target]
    pt=np.asarray(rd[target],dtype=float)
    distance={s:float(np.linalg.norm(pt-np.asarray(rd[s]))) for s in others}
    if min(distance.values())<=0:raise ValueError("DUPLICATED_REFERENCE_STATION")
    ranked=sorted(others,key=lambda s:(distance[s],s))
    subset=ranked[:3]
    w=np.asarray([1/(distance[s]**2) for s in subset])
    w/=np.sum(w)
    tr=Delaunay(np.asarray([rd[s] for s in others],dtype=float))
    simplex=int(tr.find_simplex(pt.reshape(1,2))[0])
    triangle_site_names=None
    if simplex>=0:
        triangle_site_names=sorted(others[int(i)] for i in tr.simplices[simplex])
    return {"nearest":ranked[0],"idw3_sites":subset,
            "idw3_weights_by_name":{s:float(x) for s,x in zip(subset,w)},
            "inside_reference_triangle":simplex>=0,
            "triangle_site_names":triangle_site_names}

def run(path=OUT):
    atlas_names={a[0] for a in ATLAS}
    if set(PUBLISHED_2006_RD)!=atlas_names:
        raise ValueError("PUBLISHED_REPORT_15_STATIONS_INCOMPLETE")
    d={}
    for n in sorted(atlas_names):
        r11=REFERENCE_RD[n]
        r06=PUBLISHED_2006_RD[n]
        delta=math.hypot(r11[0]-r06[0],r11[1]-r06[1])
        d[n]={"2006_official_publication_RD_m":r06,
              "2011_WEBTICS_publication_RD_m":r11,
              "published_reference_location_difference_m":round(delta,3),
              "2018_2019_native_instrument_location_NOT_VERIFIED":True}
    vals=sorted(v["published_reference_location_difference_m"] for v in d.values())
    spatial={}
    for target in STATIONS:
        geo11=site_weights(target,REFERENCE_RD)
        geo06=site_weights(target,PUBLISHED_2006_RD)
        w1=geo11["idw3_weights_by_name"]
        w0=geo06["idw3_weights_by_name"]
        spatial[target]={"same_nearest_station":geo11["nearest"]==geo06["nearest"],
            "same_IDW3_neighbor_set":set(w1)==set(w0),
            "IDW3_weight_L1_difference_with_zero_for_different_neighbors":round(sum(
                abs(w1.get(s,0)-w0.get(s,0)) for s in set(w1)|set(w0)),8),
            "same_triangle_hull_status":geo11["inside_reference_triangle"]==geo06["inside_reference_triangle"],
            "2011_geometry":geo11,"2006_geometry":geo06}
    out={"status":"POSTHOC_PUBLISHED_GEOMETRY_REFERENCE_CONSISTENCY_ONLY",
      "original_source_2006_official_RWS_RIKZ_2006_012_printed_p69":SOURCE_2006,
      "independent_source_2011_WEBTICS_Appendix_A_Table_A1":SOURCE_2011,
      "original_pdf_binary_sha256_NOT_VERIFIED":True,
      "reference_location_comparison_not_2019_native_instrument_coordinate_check":True,
      "station_geometry_15":d,
      "published_2006_vs_2011_station_differences_m":{
        "n_stations":len(vals),"median":vals[len(vals)//2],
        "maximum":max(vals),"n_lt300m":sum(v<300 for v in vals)},
      "exploratory_13_station_L0_geometry_sensitivity":spatial,
      "geometry_13_summary":{
        "n_same_nearest":sum(s["same_nearest_station"] for s in spatial.values()),
        "n_same_IDW3_neighbor_set":sum(s["same_IDW3_neighbor_set"] for s in spatial.values()),
        "max_L1_IDW3_weight_change":round(max(s["IDW3_weight_L1_difference_with_zero_for_different_neighbors"] for s in spatial.values()),8),
        "n_same_inside_triangle_hull":sum(s["same_triangle_hull_status"] for s in spatial.values()),
      },
      "RWS_2018_2019_water_level_values_retrieved":False,
      "local_bird_GPS_tide_and_DEM_vertical_datum_still_STOP":True}
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V189_INDEPENDENT_PUBLISHED_RD_SOURCE="+json.dumps({
        "status":out["status"],
        "published_reference_differences_m":out["published_2006_vs_2011_station_differences_m"],
        "LOO_reference_geometry":out["geometry_13_summary"],
        "no_2018_instrument_or_new_bird_tide_source_claims":True},sort_keys=True))
    return out

if __name__=="__main__":run()
