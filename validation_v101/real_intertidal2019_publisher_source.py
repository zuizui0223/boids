"""v101 first independent 2017–2019 real tidal-flat raster source admission.

New environmental habitat source, independent of UHSLC tidal form/source:
Murray Global Intertidal Classification v1.2 (1999–2019), genuine raster
metadata only. Never infer flat hectares, local height, tide dynamics or animal
behavior from a publisher Figshare article metadata listing.
"""
from __future__ import annotations
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from hashlib import sha256
from pathlib import Path
import argparse,json
FIGSHARE='https://api.figshare.com/v2/articles/19334465'
GIC_CLOUD='https://storage.googleapis.com/storage/v1/b/gic-archive/o?prefix=gic-2019-v1-0%2Fv1-0-1%2F&maxResults=5'
FIGSHARE_ARTICLE_ID=19334465
EARTH_ENGINE_SOURCE='UQ/murray/Intertidal/v1_2/global_intertidal'
MAX_SOURCE_META_BYTES=3_000_000
def fetch_json(url,max_bytes=MAX_SOURCE_META_BYTES):
    if url not in (FIGSHARE,GIC_CLOUD):
        raise ValueError('SOURCE_STOP_UNAUTHORIZED_OR_NON_ORIGINAL_HABITAT_METADATA_URL')
    with urlopen(Request(url,headers={
        'Accept':'application/json',
        'User-Agent':'boids-v101-2017-2019-original-global-tidalflat-habitat-source-only/1.0'}),timeout=25) as resp:
        raw=resp.read(max_bytes+1)
        if resp.status!=200 or len(raw)>max_bytes:
            raise ValueError('SOURCE_STOP_ORIGINAL_HABITAT_METADATA_MALFORMED_OR_TOO_LARGE')
    return json.loads(raw),sha256(raw).hexdigest(),len(raw)
def genuine_figshare_file_manifest(data):
    try:id_=int(data['id'])
    except (KeyError,TypeError,ValueError) as e:raise ValueError('SOURCE_STOP_FIGSHARE_ARTICLE_ID_MISSING') from e
    if id_!=FIGSHARE_ARTICLE_ID:
        raise ValueError('SOURCE_STOP_FIGSHARE_ARTICLE_ID_MISMATCH')
    title=(data.get('title') or '').lower()
    if not ('intertidal' in title and ('v1.2' in title or 'v1_2' in title or '1999-2019' in title)):
        raise ValueError('SOURCE_STOP_FIGSHARE_NOT_CORRECT_V12_ORIGINAL_INTERTIDAL')
    files=data.get('files') or []
    if not isinstance(files,list) or not files:
        raise ValueError('SOURCE_STOP_FIGSHARE_ORIGINAL_FILE_INVENTORY_UNAVAILABLE')
    seen=set();out=[]
    for f in files:
        name=f.get('name')
        size=f.get('size')
        url=f.get('download_url')
        fid=f.get('id')
        if not isinstance(name,str) or not name or not isinstance(size,int) or size<0:
            raise ValueError('SOURCE_STOP_FIGSHARE_ORIGINAL_FILE_METADATA_INCOMPLETE')
        if not url or not str(url).startswith(('https://springernature.figshare.com/ndownloader/files/',
                                              'https://ndownloader.figshare.com/files/',
                                              'https://api.figshare.com/v2/file/download/',
                                              'https://figshare.com/ndownloader/files/')):
            raise ValueError('SOURCE_STOP_FIGSHARE_ORIGINAL_PUBLISHER_FILE_URI_NOT_AUTHENTICATED')
        if fid in seen:raise ValueError('SOURCE_STOP_FIGSHARE_DUPLICATED_FILE_ID')
        seen.add(fid)
        out.append({'publisher_file_id':fid,'name':name,'bytes':size,
                    'md5_original':f.get('computed_md5'),
                    'download_url':url,
                    'is_temporal_2017_2019_candidate':any(
                       k in name.lower() for k in ('20172019','2017_2019','2017-2019','2019','v1_2')),
                    'is_qa_or_mask_candidate':any(k in name.lower() for k in ('qa','mask')),
                    'is_tiff_raster':name.lower().endswith(('.tif','.tiff'))})
    return {'source_article_id':id_,'original_publisher_title':data.get('title'),
            'original_publisher_doi':data.get('doi'),'original_files_n':len(out),
            'total_original_source_bytes':sum(x['bytes'] for x in out),
            'original_2019_temporal_candidate_files':sum(x['is_temporal_2017_2019_candidate'] for x in out),
            'raster_file_count':sum(x['is_tiff_raster'] for x in out),
            'original_publisher_files':out}
def run(out):
    report={'analysis':'V101_REAL_PUBLISHER_GLOBAL_INTERTIDAL_V12_2017_2019_ORIGINAL_SOURCE_GATE',
       'original_30m_tidalflat_source':EARTH_ENGINE_SOURCE,
       'figure_reference_DOI':'10.1038/s41597-022-01635-5',
       'year':'2017–2019','target_2019_UHSLC_160_gauge_habitat':'NOT_COMPUTED_SOURCE_ONLY',
       'NO_TIDAL_FLAT_PRESENCE_OR_ABSENCE_CLAIM':True,
       'NO_ACTUAL_EXPOSED_HABITAT_HOURS_OR_BIOLOGICAL_TIME_NICHE':True,
       'source_status':'SOURCE_UNAVAILABLE'}
    try:
        data,sha,size=fetch_json(FIGSHARE)
        source=genuine_figshare_file_manifest(data)
        report['figshare']={'provider_api':FIGSHARE,'genuine_source_sha256':sha,
                           'original_metadata_bytes':size,**source}
        report['source_status']='ORIGINAL_FIGSHARE_FILE_CATALOG_ADMITTED_NOT_RASTER_PIXELS'
    except (HTTPError,URLError,TimeoutError,ValueError,KeyError) as e:
        report['figshare_error']={'type':type(e).__name__,'reason':str(e)[:220]}
    try:
        cloud,sha,size=fetch_json(GIC_CLOUD)
        report['GIC_separate_global_tidal_wetland_cloud_listing']={
           'source_sha256':sha,'metadata_bytes':size,
           'n_objects':len(cloud.get('items') or []),
           'source_objects_exact':[{'name':v.get('name'),'size':v.get('size'),
              'contentType':v.get('contentType')}
              for v in (cloud.get('items') or [])[:5]],
           'nextPageToken_source_list_more':bool(cloud.get('nextPageToken')),
           'this_is_tidal_wetlands_combined_not_bare_tidalflats':True}
    except (HTTPError,URLError,TimeoutError,ValueError) as e:
        report['GIC_source_only_cloud_error']={'type':type(e).__name__,'reason':str(e)[:220]}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('V101_INTERTIDAL_ORIGINAL_SOURCE_GATE '+json.dumps({
       'status':report['source_status'],
       'original_files':(report.get('figshare') or {}).get('original_files_n'),
       'raster_count':(report.get('figshare') or {}).get('raster_file_count'),
       'figshare_original_file_catalog_summary':[
            {'name':item['name'],'bytes':item['bytes'],'download_url':item['download_url']}
            for item in (report.get('figshare') or {}).get('original_publisher_files',[])[:8]],
       'GIC_cloud_listed_objects':(report.get('GIC_separate_global_tidal_wetland_cloud_listing') or {}).get('source_objects_exact'),
       'source_error':report.get('figshare_error'),
       'GIC_separate_source_error':report.get('GIC_source_only_cloud_error'),
       'NOT_ACTUAL_MAPPED_INTERTIDAL_PIXELS':True},sort_keys=True),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
