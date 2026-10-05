#!/usr/bin/env python3
import argparse
from pathlib import Path
from common import load_json,save_json
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args(); p=Path(args.project).resolve(); st=load_json(p/'STATE.json'); ver=str(st.get('system_version'))
if not ver.startswith('1.10'): raise SystemExit(f'unsupported direct migration from {ver}; migrate/bootstrap to v1.10 first')
print(f'SUPPORTED {ver} -> 1.11.0')
if args.apply:
 st['system_version']='1.11.0'; save_json(p/'STATE.json',st)
 rs=load_json(p/'RUN_STATE.json'); rs['system_version']='1.11.0'; rs.setdefault('active_use_case_id',None); rs.setdefault('next_use_case_id','UC03'); save_json(p/'RUN_STATE.json',rs)
 # Existing Task Manifests keep the registry version used when they were routed; do not rewrite lineage.
 print('MIGRATION APPLIED')
