"""v172 authentic Deltares THREDDS small NetCDF tile-index inventory.

Original v171 XML source verified 166 original native .nc tile paths.
A tile name alone is not a survey year, datum or habitat footprint.
This gate reads genuine published catalog.nc binary to identify possible
original tile bounds, without animal GPS or any biological response.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.request
from pathlib import Path
import numpy as np
from netCDF4 import Dataset,chartostring

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_v172/results/original_deltares_vaklodingen_catalog_nc_v172.json"
PRIOR=ROOT/"validation_v171/results/official_historical_vlieland_tile_catalog_source_v171.json"
URLS=(
    "https://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/vaklodingen/catalog.nc",
    "https://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/vaklodingen/catalog.nc"
)
MAX_BYTES=1_000_000
MAX_PREVIEW=35
VLIE_RD_SEARCH=[120000,575000,150000,615000]

def acquire():
    errors=[]
    for url in URLS:
        try:
            req=urllib.request.Request(url,headers={
              "User-Agent":"OpenScienceBoids/1.0 academic attribution Rijkswaterstaat Deltares",
              "Accept":"application/octet-stream,application/x-netcdf,*/*"
            })
            with urllib.request.urlopen(req,timeout=45) as f:
                raw=f.read(MAX_BYTES+1)
                resolved=f.geturl()
            if not(200<len(raw)<MAX_BYTES and (raw[:3]==b"CDF" or raw[:4]==b"\x89HDF")):
                raise ValueError("Original NetCDF missing/size/magic invalid")
            return raw,{"original_url":url,"resolved_url":resolved,
                        "original_content_bytes":len(raw),
                        "original_binary_SHA256":hashlib.sha256(raw).hexdigest()}
        except Exception as e:errors.append({"source_url":url,"class":type(e).__name__,"detail":str(e)[:200]})
    raise RuntimeError("Official original NetCDF catalog unavailable: "+repr(errors))

def schema(raw,meta):
    with Dataset("index.nc",memory=raw) as nc:
        dims={k:len(v) for k,v in nc.dimensions.items()}
        globals_={k:str(nc.getncattr(k))[:360] for k in nc.ncattrs()}
        vars_={}
        for key,v in nc.variables.items():
            d={"dims":list(v.dimensions),"shape":list(v.shape),"dtype":str(v.dtype),
               "attrs":{k:str(v.getncattr(k))[:350] for k in v.ncattrs()}}
            if v.size<=100000:
                val=np.ma.asarray(v[:])
                if val.dtype.kind in "fiub":
                    data=val.compressed()
                    data=data[np.isfinite(data)]
                    if data.size:
                        d["numeric_min"]=float(data.min())
                        d["numeric_max"]=float(data.max())
                        d["n_numeric"]=int(data.size)
                        if data.size<=MAX_PREVIEW:d["numeric_first"]=[float(x) for x in data]
                elif val.dtype.kind in "SU":
                    z=chartostring(val) if val.dtype.kind=="S" and val.ndim>=2 and val.dtype.itemsize==1 else val
                    words=[str(x.decode("utf-8","replace") if isinstance(x,bytes) else x)
                           for x in np.ravel(z)]
                    d["n_string"]=len(words)
                    d["string_samples"]=[x[:120] for x in words[:MAX_PREVIEW]]
                    d["all_strings_SHA256"]=hashlib.sha256("\n".join(words).encode()).hexdigest()
            vars_[key]=d
    return {"version":"v172_genuine_thredds_catalog_nc_geoindex_1",
            "original_publisher_index_source":meta,
            "original_netcdf_dims":dims,
            "original_netcdf_variables":vars_,
            "original_netcdf_global_attrs":globals_,
            "v171_official_catalog_verified_166_tiles":True,
            "Vlieland_RD_search_box_not_actual_bird_GPS":VLIE_RD_SEARCH,
            "tile_2016_actual_xy_isource_and_NAP_coverage":"NOT_YET_VERIFIED",
            "original_bird_GPS_elevation_or_exposed_area":"NOT_ESTIMATED",
            "source_not_current_2025_2026_DEM_as_historical":True}

def run():
    prev=json.loads(PRIOR.read_text())
    x=prev["official_catalogs"]["legacy_vaklodingen"]
    if x["n_original_native_NetCDF_file_paths"]!=166 or x["original_catalog_binary_SHA256"]!="40a4881f4dad432e7b52e88fcff000b51943b81b0e256a3b09f68cb25f04f277":
        raise AssertionError("Frozen v171 real 166-tile XML inventory mismatch")
    raw,meta=acquire()
    return schema(raw,meta)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    x=run();OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if json.loads(OUT.read_text())!=x:raise AssertionError("Genuine catalog.nc source checksum/metadata changed")
        print("V172_GENUINE_DELTA_DUTCH_TILE_CATALOG_NETCDF_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V172_REAL_NATIVE_CATALOG_START")
        print(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V172_REAL_NATIVE_CATALOG_END")
    print("V172_SOURCE_INDEX_SUMMARY="+json.dumps({
        "SHA":x["original_publisher_index_source"]["original_binary_SHA256"],
        "nbytes":x["original_publisher_index_source"]["original_content_bytes"],
        "dims":x["original_netcdf_dims"],
        "names":list(x["original_netcdf_variables"])
    },sort_keys=True))
if __name__=="__main__":main()
