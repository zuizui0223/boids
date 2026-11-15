"""Published California site Table 1 -> NOAA source-gauge nearest-distance preflight.

This is *geometric* proximity, never a measured offshore tidal phase, current,
amplitude, or a justified ecological exposure assignment. A tide gauge is a
candidate reference source, not the actual acoustic sensor location.
"""
from __future__ import annotations
from pathlib import Path
from math import sin,cos,atan2,sqrt,pi
import json,argparse

ROOT=Path(__file__).resolve().parents[1]
SITES={
 "MB01":{"lat":36.798,"lon":-121.976,"depth_m":119,"published_effort_days":1010,"sanctuary":"Monterey Bay"},
 "MB02":{"lat":36.648,"lon":-121.908,"depth_m":68,"published_effort_days":738,"sanctuary":"Monterey Bay"},
 "MB05":{"lat":35.770,"lon":-121.430,"depth_m":98,"published_effort_days":441,"sanctuary":"Monterey Bay"},
 "CH01":{"lat":35.468,"lon":-121.023,"depth_m":19,"published_effort_days":339,"sanctuary":"Chumash"},
 "CI01":{"lat":34.044,"lon":-120.081,"depth_m":21,"published_effort_days":823,"sanctuary":"Channel Islands"},
 "CI02":{"lat":34.085,"lon":-120.523,"depth_m":77,"published_effort_days":913,"sanctuary":"Channel Islands"},
 "CI03":{"lat":33.487,"lon":-119.016,"depth_m":26,"published_effort_days":691,"sanctuary":"Channel Islands"},
 "CI04":{"lat":33.848,"lon":-120.117,"depth_m":156,"published_effort_days":1011,"sanctuary":"Channel Islands"},
 "CI05":{"lat":34.018,"lon":-119.317,"depth_m":139,"published_effort_days":718,"sanctuary":"Channel Islands"},
}

def haversine(a,b):
    p1,l1=map(lambda d:d*pi/180,a)
    p2,l2=map(lambda d:d*pi/180,b)
    delta=p2-p1
    dlon=l2-l1
    h=sin(delta/2)**2+cos(p1)*cos(p2)*sin(dlon/2)**2
    return 2*6371.0088*atan2(sqrt(h),sqrt(1-h))

def run():
    original=json.loads((ROOT/"validation_v141/results/noaa_hourly_verified_reference_gauges.json").read_text())
    gauges=original["station_gauges"]
    if len(gauges)!=4:raise ValueError("Four original NOAA station-source records required")
    out={"version":"v142_published_site_vs_verified_NOAA_gauge_geometric_proximity_1",
         "site_source":"Kim et al. 2025 MEPS 764:135-159 Table 1, doi:10.3354/meps14910",
         "gauge_source":"v141 NOAA CO-OPS verified station coordinates; no acoustic tide join",
         "n_source_acoustic_sites":len(SITES),
         "n_gauge_reference_sites":len(gauges),
         "coordinates_decimal_degrees_and_longitudes_negative_W":True,
         "nearest_is_geometric_only_not_hydrodynamic":True,
         "exposure_at_recorders":"NOT_ESTIMATED",
         "site_rows":[],
         "global_tide_by_solar_effect":"NOT_ESTIMATED"}
    for site,info in sorted(SITES.items()):
        dis=[]
        for gauge,g in gauges.items():
            coords=(float(g["NOAA_lat"]),float(g["NOAA_lon"]))
            distance=haversine((info["lat"],info["lon"]),coords)
            dis.append((gauge,round(distance,3),g["NOAA_station_id"]))
        dis.sort(key=lambda p:p[1])
        out["site_rows"].append({
            "acoustic_site":site,**info,
            "nearest_NOAA_physical_gauge":dis[0][0],
            "nearest_NOAA_station_id":dis[0][2],
            "nearest_direct_geodesic_km":dis[0][1],
            "all_candidate_gauges_by_distance":[{"gauge":g,"distance_km":d,"station":id} for g,d,id in dis],
            "offshore_phase_and_amplitude_calibration":"MISSING",
            "geometry_alone_not_valid_physical_exposure":True})
    out["sites_with_nearest_gauge_more_than_80_km"]=sum(
        x["nearest_direct_geodesic_km"]>80 for x in out["site_rows"])
    return out

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--check",action="store_true")
    a=cli.parse_args()
    result=run()
    path=Path(__file__).parent/"results"/"nine_sites_reference_gauge_geography.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    if a.check:
        assert result==json.loads(path.read_text()),"Site-to-gauge distance table differs from source"
    else:path.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V142_GEOGRAPHY_START")
    print(json.dumps(result,ensure_ascii=False))
    print("V142_GEOGRAPHY_END")

if __name__=="__main__":main()
