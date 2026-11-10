"""v104 public original GIC 2019 tidal wetland probability TIFF layer source-only.

The 2017–2019 'twprobability_end' raster is tidal wetland (flats AND vegetated
wetlands), not Murray v1.2 nonvegetated tidal flat nor momentary dry area.
"""
from __future__ import annotations
import argparse,json
from urllib.request import Request,urlopen
from urllib.parse import quote
from urllib.error import HTTPError,URLError
from pathlib import Path
from hashlib import sha256
BUCKET='gic-archive'
FIXED_BASE='gic-2019-v1-0/v1-0-1/'
SOURCE='https://storage.googleapis.com/storage/v1/b/gic-archive/o'
TARGET_SUFFIXES=[
  'murray-gic-v1.0.1-twprobability_end-',
  'murray-gic-v1.0.1-twprobability-end-',
  'murray-gic-v1.0.1-twprobability-',
  'murray-gic-v1.0.1-']
LAYER_DISCOVERY_ONLY='__NATIVE_2019_GIC_LAYER_PREFIXES__'
def source_url(suffix):
    if suffix==LAYER_DISCOVERY_ONLY:
        # GCS delimiter exposes native source layer directories without enumerating
        # potentially thousands of large raster tiles or inspecting pixel outcomes.
        return SOURCE+'?prefix='+quote(FIXED_BASE+'murray-gic-v1.0.1-',safe='')+'&delimiter=-&maxResults=1000'
    if suffix not in TARGET_SUFFIXES:raise ValueError('STOP_NOT_FROZEN_2019_PUBLIC_GIC_SOURCE_PREFIX')
    return SOURCE+'?prefix='+quote(FIXED_BASE+suffix,safe='')+'&maxResults=4'
def fetch(suffix):
    with urlopen(Request(source_url(suffix),headers={
       'Accept':'application/json',
       'User-Agent':'boids-v104-native-GIC-2019-tidalwetland-t7-source-only/1.0'}),timeout=30) as r:
        b=r.read(1_000_001)
        if r.status!=200 or len(b)>1_000_000:raise ValueError('STOP_INVALID_OR_OVERSIZED_GIC_SOURCE_METADATA')
    return json.loads(b),sha256(b).hexdigest()
def original_objects(obj,suffix):
    if not isinstance(obj,dict):raise ValueError('STOP_ORIGINAL_GIC_METADATA_NOT_JSON_OBJECT')
    items=obj.get('items') or []
    if not isinstance(items,list):raise ValueError('STOP_ORIGINAL_GIC_OBJECTS_NON_LIST')
    out=[]
    for item in items:
        name=item.get('name','')
        if not (name.startswith(FIXED_BASE+suffix) and name.lower().endswith('.tif')):
            continue
        if item.get('contentType') not in ('image/tiff','application/octet-stream'):
            raise ValueError('STOP_NON_RASTER_OBJECT_MIME_TYPE')
        out.append({'native_bucket':BUCKET,'original_name':name,
                    'size_bytes':int(item['size']),'content_type':item['contentType'],
                    'generation':item.get('generation'),
                    'md5Hash_original_GCS_base64':item.get('md5Hash'),
                    'crc32c_original_GCS_base64':item.get('crc32c'),
                    'source_URL_unmodified':'https://storage.googleapis.com/'+BUCKET+'/'+name})
    return out
def run(path):
    out={'analysis':'V104_GIC_2017_2019_ORIGINAL_TIDAL_WETLAND_GCS_TILE_SOURCE_ONLY',
         'source_bucket':BUCKET,'source_prefix':FIXED_BASE,
         '2017_2019_target':'twprobability_end 0-100 t7',
         'different_from_bare_nonvegetated_intertidal_v12':True,
         'NO_SITE_HABITAT_PIXELS_OR_BEHAVIOR_MEASURED':True,
         'attempts':[],'source_status':'SOURCE_NOT_YET_ADMITTED'}
    try:
        layers, layer_sha=fetch(LAYER_DISCOVERY_ONLY)
        native_layer_names=[v for v in (layers.get('prefixes') or [])
            if v.startswith(FIXED_BASE+'murray-gic-v1.0.1-')]
        out['public_native_source_layer_prefixes']={
            'original_bucket_list_SHA256':layer_sha,
            'n_source_layer_prefixes':len(native_layer_names),
            'first_50_native_layer_names':native_layer_names[:50],
            'source_list_pagination_exists':bool(layers.get('nextPageToken'))}
        print('V104_ORIGINAL_GIC_NATIVE_LAYER_PREFIXES '+json.dumps(
            out['public_native_source_layer_prefixes'],sort_keys=True),flush=True)
    except (HTTPError,URLError,TimeoutError,ValueError,KeyError) as e:
        out['public_native_source_layer_prefix_error']={'type':type(e).__name__,'reason':str(e)[:220]}
    for suffix in TARGET_SUFFIXES:
        try:
            obj,sh=fetch(suffix)
            tiles=original_objects(obj,suffix)
            out['attempts'].append({'suffix':suffix,'response_sha256':sh,'original_tile_count_in_first_page':len(tiles),
                  'n_possible_more_pages':bool(obj.get('nextPageToken')),
                  'original_tile_source_records':tiles})
            if 'twprobability' in suffix and tiles and all('twprobability' in x['original_name'] for x in tiles):
                out['source_status']='ORIGINAL_T7_TIDAL_WETLAND_TILE_METADATA_ADMITTED'
                out['selected_source_prefix']=suffix
                break
        except (HTTPError,URLError,TimeoutError,ValueError,KeyError) as e:
            out['attempts'].append({'suffix':suffix,'status':'SOURCE_UNAVAILABLE',
                                    'error':type(e).__name__,'detail':str(e)[:180]})
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('V104_REAL_GIC_T7_SOURCE_CATALOG '+json.dumps({
        'status':out['source_status'],'selected_prefix':out.get('selected_source_prefix'),
        'first_native_t7_objects':next((z['original_tile_source_records'] for z in out['attempts'] if z.get('original_tile_source_records') and 'twprobability' in z['suffix']),[]),
        'attempts':[{'suffix':z['suffix'],'n_tile':z.get('original_tile_count_in_first_page'),'error':z.get('detail')}
                    for z in out['attempts']],
        'not_flat_area':True},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
