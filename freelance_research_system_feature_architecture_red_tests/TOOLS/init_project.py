#!/usr/bin/env python3
import argparse, shutil, json
from pathlib import Path
from common import load_json, save_json
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('project_id'); args=ap.parse_args(); p=Path(args.project).resolve(); p.mkdir(parents=True,exist_ok=True)
for srcname,dstname in [('PROJECT_CONFIG.template.json','PROJECT_CONFIG.json'),('PROJECT_INDEX.template.json','PROJECT_INDEX.json'),('STATE.template.json','STATE.json'),('RUN_STATE.template.json','RUN_STATE.json'),('METHOD_REGISTRY.template.json','METHOD_REGISTRY.json'),('SOURCE_REGISTRY.template.json','SOURCE_REGISTRY.json'),('SOURCE_USE_PLAN.template.json','SOURCE_USE_PLAN.json'),('DEPENDENCY_GRAPH.template.json','DEPENDENCY_GRAPH.json'),('ENTITY_REGISTRY.template.json','ENTITY_REGISTRY.json')]: shutil.copy2(ROOT/'TEMPLATES'/srcname,p/dstname)
shutil.copy2(ROOT/'TEMPLATES/PROJECT_BRIEF_TEMPLATE.md',p/'PROJECT_BRIEF.md'); shutil.copy2(ROOT/'WORKBOOK/research_system_template.xlsx',p/'research.xlsx')
s=load_json(p/'STATE.json'); s['project_id']=args.project_id; save_json(p/'STATE.json',s)
(p/'TASKS').mkdir(exist_ok=True); (p/'LEDGER').mkdir(exist_ok=True); (p/'RUNS').mkdir(exist_ok=True)
save_json(p/'LAST_ROUTE.json',{'schema_version':'1.0','selected_at':None,'request':None,'use_case_id':'UC01','route_reason':'project initialized; awaiting request routing','registry_version':'3.0.0','router_kind':'system','state':{}})
for f in ['DAILY_RUNS.jsonl','OBSERVATIONS.jsonl','CHANGE_EVENTS.jsonl','DAILY_DIFFS.jsonl','INTERESTING_ITEMS.jsonl','WORKFLOW_EVENTS.jsonl']: (p/'LEDGER'/f).touch()
print(f'INITIALIZED {p}')
