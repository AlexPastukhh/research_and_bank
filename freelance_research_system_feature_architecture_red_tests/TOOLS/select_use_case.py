#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from common import load_json, save_json
from route_use_case import route
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('project')
ap.add_argument('request')
ap.add_argument('--state-json')
ap.add_argument('--now')
args=ap.parse_args()
p=Path(args.project).resolve()
reg=load_json(ROOT/'CORE/USE_CASE_REGISTRY.json')
rs=load_json(p/'RUN_STATE.json')
state=json.loads(args.state_json) if args.state_json else {}
uc,reason=route(reg,args.request,state)
now=args.now or datetime.now(timezone.utc).isoformat()
rs['active_use_case_id']=None
rs['next_use_case_id']=uc
rs['last_updated']=now
save_json(p/'RUN_STATE.json',rs)
decision={
    'schema_version':'1.0','selected_at':now,'request':args.request,
    'use_case_id':uc,'route_reason':reason,'registry_version':reg['registry_version'],
    'router_kind':'deterministic_helper','state':state
}
save_json(p/'LAST_ROUTE.json',decision)
print(json.dumps(decision,ensure_ascii=False))
