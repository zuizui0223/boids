"""v11: source-gated original audio/video scene matching + human-auditable frames.

Mouy et al. MEE 2023, OSF q8dz4 (CC BY-SA 4.0).
This gate does not identify or track fish in video and does not estimate Boids
forces or local social-to-vocal interactions. Published Figure9 and Figure10
clips are supporting-figure videos, not necessarily original synchronized
unannotated video; synchronization must be separately demonstrated.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, subprocess, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error, parse

VIDEO={
  "Figure9_Lingcod": {"id":"640113ebf014b90ad1eb4471","file":"SuppInfo_Video_Figure9.mp4",
                       "source_start":"2019-06-17T15:13:07+00:00", "clip_seconds":10,
                       "original_events_sha256":"095f1f3dbe9b45c480c1987a83a3a2459d38baa3f2ccfccf4824e2f308d7143b",
                       "localization_file_id":"6335fcfa31d65303352de2bc"},
  "Figure10_Rockfish_Lingcod":{"id":"640113f940cecd0b3d76e56f",
                       "file":"SuppInfo_Video_Figure10.mp4",
                       "source_start":"2019-09-20T16:38:58+00:00", "clip_seconds":17,
                       "original_events_sha256":"a2270a82dae5435ba992cdeef002e7cdca1aa054edf3e336f80f986f2d9c841b",
                       "localization_file_id":"6335fd3aec7f3f0337f5f9a4"}
}
MAX_VIDEO_BYTES=8_000_000
MAX_CSV_BYTES=60_000
WEB_TZ="UTC"
RETRY=3

class SourceStop(Exception):
    pass

def official_osf_meta(fid):
    url=f"https://api.osf.io/v2/files/{fid}/"
    return json.loads(request.urlopen(request.Request(
        url,headers={"User-Agent":"boids-v11-source-scene-gate/1.0",
                     "Accept":"application/json"}),timeout=45).read(400_000))

def safe_original_download(item,max_bytes):
    attr=item.get("attributes") or {}
    url=(item.get("links") or {}).get("download")
    if not isinstance(url,str):raise SourceStop("NO_SOURCE_DOWNLOAD")
    p=parse.urlparse(url)
    if p.scheme!="https" or p.hostname not in ("osf.io","files.osf.io"):
        raise SourceStop("NONOFFICIAL_SOURCE_HOST")
    size=int(attr.get("size") or 0)
    if size<=0 or size>max_bytes:raise SourceStop("ORIGINAL_SOURCE_SIZE_STOP")
    last_error=None
    for attempt in range(RETRY):
        try:
            resp=request.urlopen(request.Request(url,headers={
                "User-Agent":"boids-v11-official-OSF-original/1.0"}),timeout=65)
            with resp:
                raw=resp.read(max_bytes+1)
            if len(raw)!=size:raise SourceStop("ORIGINAL_BYTES_SIZE_MISMATCH")
            hashes=(attr.get("extra") or {}).get("hashes") or {}
            for name in ("md5","sha256"):
                if hashes.get(name) and hashlib.new(name,raw).hexdigest()!=str(hashes[name]).lower():
                    raise SourceStop("ORIGINAL_PROVIDER_HASH_MISMATCH")
            return raw,bool(hashes.get("md5") or hashes.get("sha256"))
        except (TimeoutError,error.URLError,OSError) as exc:
            last_error=type(exc).__name__
    raise SourceStop("SOURCE_TRANSPORT_STOP_"+str(last_error))

def parse_src_time(text):
    s=str(text or "").strip().replace("Z","+00:00")
    try: value=datetime.fromisoformat(s)
    except ValueError: raise SourceStop("UNPARSEABLE_TIMESTAMP") from None
    if value.tzinfo is None:value=value.replace(tzinfo=timezone.utc)
    return value.timestamp()

def original_acoustic_counts(raw, scene):
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=scene["original_events_sha256"]:
        raise SourceStop("FROZEN_V6_OSF_ACOUSTIC_SHA_DRIFT")
    decoded=raw.decode("utf-8-sig")
    rows=list(csv.DictReader(io.StringIO(decoded)))
    anchor=parse_src_time(scene["source_start"])
    duration=float(scene["clip_seconds"])
    # Figure video may be edited; this is only the original audio-file
    # source interval, not exact frame-wise video synchronization.
    all_events=[]
    anchored=[]
    for row in rows:
        stamp=row.get("time_min_date")
        if not stamp:continue
        try: offset=parse_src_time(stamp)-anchor
        except SourceStop:continue
        all_events.append(offset)
        if -.1<=offset<=duration+.1:
            anchored.append(offset)
    return {"source_localization_csv_sha256":sha,
            "original_csv_all_rows":len(rows),
            "n_source_records_with_parseable_date":len(all_events),
            "n_events_with_original_audio_time_in_window":len(anchored),
            "original_audio_window_seconds":duration,
            "relative_event_seconds_minmax":[min(anchored),max(anchored)] if anchored else None,
            "video_frame_level_times_reconciled":"NOT_PROVEN",
            "original_scene_publisher_video_audio_sync":"DOCUMENTED_AUTHOR_MANUAL_REVIEW_NOT_REPLAYED"}

def ffprobe_json(path):
    args=["ffprobe","-v","error","-select_streams","v:0",
          "-show_entries","stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames",
          "-show_entries","format=duration,format_name",
          "-of","json",str(path)]
    result=subprocess.run(args,check=True,capture_output=True,text=True,timeout=50)
    z=json.loads(result.stdout)
    if not z.get("streams"):raise SourceStop("ORIGINAL_VIDEO_NO_VIDEO_STREAM")
    return {"video_stream":z["streams"][0],"format":z.get("format",{})}

def contact_sheet(video,out_dir,name,nominal_seconds):
    # These are contact sheets of original published *supplemental editing*,
    # NOT visually validated individual fish trajectory measurements.
    from PIL import Image,ImageDraw
    out_dir.mkdir(exist_ok=True,parents=True)
    times=[round(i*nominal_seconds/6,2) for i in range(6)]
    thumbs=[]
    for i,seconds in enumerate(times):
        p=out_dir/f"{name}_sample_{i}.png"
        args=["ffmpeg","-nostdin","-y","-v","error","-ss",str(seconds),
              "-i",str(video),"-frames:v","1","-update","1",str(p)]
        z=subprocess.run(args,capture_output=True,text=True,timeout=45)
        if z.returncode!=0 or not p.exists() or p.stat().st_size==0:
            raise SourceStop(f"VIDEO_FRAME_ACCESS_STOP_{i}")
        with Image.open(p) as im:thumbs.append(im.convert("RGB"))
        p.unlink()
    width=550;height=350
    canvas=Image.new("RGB",(width*2,height*3),(250,250,250))
    d=ImageDraw.Draw(canvas)
    for i,im in enumerate(thumbs):
        im.thumbnail((width-12,height-35))
        x=(i%2)*width+(width-im.width)//2
        y=(i//2)*height+26
        canvas.paste(im,(x,y))
        d.text(((i%2)*width+8,(i//2)*height+6),
               f"{name} source video frame at {times[i]}s",fill=(20,20,20))
    p=out_dir/(name+"_contact.png")
    canvas.save(p,optimize=True)
    return {"contact_sheet":p.name,"sampling_relative_seconds":times,
            "contact_sheet_file_sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def run():
    out={"version":"v11_original_same_scene_video_audio_source_gate",
        "source":"Mouy et al 2023 OSF q8dz4, original videos CC BY-SA 4.0",
        "true_fish_body_tracks_extracted":False,
        "source_fish_individual_call_attribution_fitted":False,
        "source_scene_complete":False,"scenes":[]}
    frames=Path("validation_fish_joint_v11/results/frames")
    for name,scene in VIDEO.items():
        receipt={"scene":name,"video_id":scene["id"],
            "sound_source_csv_original_file_id":scene["localization_file_id"]}
        try:
            video_metadata=official_osf_meta(scene["id"]).get("data")
            csv_metadata=official_osf_meta(scene["localization_file_id"]).get("data")
            if not video_metadata or not csv_metadata:raise SourceStop("OFFICIAL_OSF_METADATA_MISSING")
            if (video_metadata.get("attributes") or {}).get("name")!=scene["file"]:
                raise SourceStop("ORIGINAL_PUBLISHED_VIDEO_NAME_CHANGED")
            if (csv_metadata.get("attributes") or {}).get("name")!="localization_results.csv":
                raise SourceStop("ORIGINAL_PUBLISHED_SOUND_NAME_CHANGED")
            raw,provider_hash=safe_original_download(video_metadata,MAX_VIDEO_BYTES)
            table,provider_csv_hash=safe_original_download(csv_metadata,MAX_CSV_BYTES)
            receipt.update({"source_video_bytes":len(raw),
                 "video_sha256":hashlib.sha256(raw).hexdigest(),
                 "source_video_publisher_checksum_verified":provider_hash,
                 "source_sound_publisher_checksum_verified":provider_csv_hash,
                 "original_acoustic_table":original_acoustic_counts(table,scene)})
            with tempfile.TemporaryDirectory(prefix="boids_v11_mp4_") as tmp:
                p=Path(tmp)/scene["file"];p.write_bytes(raw)
                receipt["source_video_technical"]=ffprobe_json(p)
                receipt["source_published_video_contact"]=contact_sheet(p,frames,name,scene["clip_seconds"])
            receipt["status"]="SOURCE_SAME_SCENE_VIDEO_AND_ORIGINAL_ACOUSTIC_TABLE_VERIFIED"
        except (OSError,TimeoutError,SourceStop,ValueError,subprocess.CalledProcessError) as exc:
            receipt["status"]="SOURCE_VIDEO_OR_SYNC_STOP"
            receipt["stop_reason"]=str(exc)
        out["scenes"].append(receipt)
    out["n_original_video_scenes_admitted"]=sum(x["status"]=="SOURCE_SAME_SCENE_VIDEO_AND_ORIGINAL_ACOUSTIC_TABLE_VERIFIED"
         for x in out["scenes"])
    out["source_scene_complete"]=out["n_original_video_scenes_admitted"]==len(VIDEO)
    out["status"]="ORIGINAL_TWO_VIDEO_SCENES_SOURCE_VERIFIED" if out["source_scene_complete"] else "PARTIAL_SOURCE_VIDEO_STOP"
    return out

if __name__=="__main__":
    obj=run()
    path=Path("validation_fish_joint_v11/results/video_audio_scene_manifest.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":obj["status"],"n_scenes":obj["n_original_video_scenes_admitted"],
      "summaries":[{"scene":x["scene"],"status":x["status"],"reason":x.get("stop_reason"),
                   "source_video_bytes":x.get("source_video_bytes"),
                   "video_spec":x.get("source_video_technical"),
                   "acoustic_matching":x.get("original_acoustic_table")}
                   for x in obj["scenes"]]}))
