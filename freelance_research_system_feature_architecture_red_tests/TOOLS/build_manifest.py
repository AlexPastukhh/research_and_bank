#!/usr/bin/env python3
import argparse, hashlib, json, os
from pathlib import Path
EXCLUDE={'MANIFEST.json'}
ap=argparse.ArgumentParser(); ap.add_argument('root'); args=ap.parse_args(); root=Path(args.root).resolve(); files=[]
for p in sorted(root.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(root).as_posix()
    if rel in EXCLUDE or '/__pycache__/' in '/'+rel or rel.endswith('.pyc') or rel.endswith('.tmp'): continue
    files.append({'path':rel,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'MANIFEST.json').write_text(json.dumps({'schema_version':'1.0','files':files},indent=2)+'\n')
print(f'MANIFEST {len(files)} files')
