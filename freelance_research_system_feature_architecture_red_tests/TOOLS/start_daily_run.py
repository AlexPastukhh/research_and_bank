#!/usr/bin/env python3
import argparse, json, uuid
from pathlib import Path
from datetime import datetime, timezone
from common import load_json,save_json
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--run-id'); ap.add_argument('--method-id',required=True); ap.add_argument('--method-version',required=True); ap.add_argument('--scope-fingerprint',required=True); ap.add_argument('--source-route',action='append',default=[]); ap.add_argument('--now'); args=ap.parse_args(); p=Path(args.project).resolve(); rs=load_json(p/'RUN_STATE.json')
if rs.get('active_daily_run_id'): raise SystemExit('active daily run already exists')
now=args.now or datetime.now(timezone.utc).isoformat(); rid=args.run_id or 'run-'+uuid.uuid4().hex[:12]
run={'run_id':rid,'started_at':now,'completed_at':None,'research_date':now[:10],'method_id':args.method_id,'method_version':args.method_version,'scope_fingerprint':args.scope_fingerprint,'source_route_ids':sorted(args.source_route),'coverage_status':'in_progress'}
save_json(p/'RUNS'/f'{rid}.json',run); rs['active_daily_run_id']=rid; rs['active_daily_run_path']=f'RUNS/{rid}.json'; save_json(p/'RUN_STATE.json',rs); print(rid)
