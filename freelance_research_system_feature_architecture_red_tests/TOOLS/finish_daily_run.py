#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
from common import load_json,save_json
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--coverage',choices=['complete','partial','failed'],required=True); ap.add_argument('--notes',default=''); ap.add_argument('--now'); args=ap.parse_args(); p=Path(args.project).resolve(); rs=load_json(p/'RUN_STATE.json'); rid=rs.get('active_daily_run_id')
if not rid: raise SystemExit('no active daily run')
runp=p/'RUNS'/f'{rid}.json'; run=load_json(runp)
if run.get('completed_at'): raise SystemExit('daily run already finalized')
run['completed_at']=args.now or datetime.now(timezone.utc).isoformat(); run['coverage_status']=args.coverage; run['coverage_notes']=args.notes; save_json(runp,run)
with (p/'LEDGER/DAILY_RUNS.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(run,ensure_ascii=False)+'\n')
rs['active_daily_run_id']=None; rs['active_daily_run_path']=None; save_json(p/'RUN_STATE.json',rs); print('FINALIZED')
