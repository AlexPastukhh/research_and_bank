#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
from common import load_json,save_json
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--use-case-id',required=True); ap.add_argument('--outcome',required=True); ap.add_argument('--now'); args=ap.parse_args()
p=Path(args.project).resolve(); reg=load_json(ROOT/'CORE/USE_CASE_REGISTRY.json'); rs=load_json(p/'RUN_STATE.json')
u=next((x for x in reg['use_cases'] if x['id']==args.use_case_id),None)
if not u: raise SystemExit(f'unknown use case {args.use_case_id}')
if args.outcome not in u['outcomes']: raise SystemExit(f'unknown outcome {args.outcome} for {args.use_case_id}')
current=rs.get('next_use_case_id') or rs.get('active_use_case_id')
if current and current!=args.use_case_id: raise SystemExit(f'run state expects {current}, cannot apply outcome for {args.use_case_id}')
tr=next(t for t in u['transitions'] if t['outcome']==args.outcome); nxt=tr['to']; now=args.now or datetime.now(timezone.utc).isoformat()
rs['active_use_case_id']=None; rs['next_use_case_id']=nxt; rs['last_updated']=now
if nxt!='UC03':
    rs['next_task_id']=None; rs['next_question']=None; rs['next_task_inputs']=[]
save_json(p/'RUN_STATE.json',rs)
ledger=p/'LEDGER/WORKFLOW_EVENTS.jsonl'; ledger.parent.mkdir(parents=True,exist_ok=True)
e={'observed_at':now,'use_case_id':args.use_case_id,'outcome':args.outcome,'next_use_case_id':nxt,'registry_version':reg['registry_version']}
with ledger.open('a',encoding='utf-8') as f: f.write(json.dumps(e,ensure_ascii=False)+'\n')
print(json.dumps(e,ensure_ascii=False))
