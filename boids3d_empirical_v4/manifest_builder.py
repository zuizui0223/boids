import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
files=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.name=='FILE_MANIFEST_V4.json' or '__pycache__' in p.parts:continue
    files.append({'path':str(p.relative_to(root)),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'FILE_MANIFEST_V4.json').write_text(json.dumps({'artifact_version':'4.0','purpose':'exploratory real-data transition benchmark plus archived synthetic v3 code','raw_gps_included':False,'files':files},indent=2)+'\n')
print(len(files),'files indexed')
