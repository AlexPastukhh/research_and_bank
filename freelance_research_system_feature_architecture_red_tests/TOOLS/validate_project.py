#!/usr/bin/env python3
import argparse, json, sys, hashlib
from pathlib import Path
from common import load_json, confined
try: import jsonschema
except Exception: jsonschema=None
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('project'); args=ap.parse_args(); p=Path(args.project).resolve(); errors=[]
for req in ['PROJECT_INDEX.json','STATE.json','RUN_STATE.json','PROJECT_CONFIG.json']:
    if not (p/req).exists(): errors.append(f'missing {req}')
if not errors:
    idx=load_json(p/'PROJECT_INDEX.json')
    for key,rel in idx.get('artifacts',{}).items():
        try: confined(p,rel)
        except Exception as e: errors.append(str(e))
    rs=load_json(p/'RUN_STATE.json'); cfg=load_json(p/'PROJECT_CONFIG.json')
    if jsonschema:
        schema_objects=[(rs,'RUN_STATE_SCHEMA.json'),(cfg,'PROJECT_CONFIG_SCHEMA.json'),(idx,'PROJECT_INDEX_SCHEMA.json')]
        optional=[('METHOD_REGISTRY.json','METHOD_REGISTRY_SCHEMA.json'),('SOURCE_REGISTRY.json','SOURCE_REGISTRY_SCHEMA.json'),('SOURCE_USE_PLAN.json','SOURCE_USE_PLAN_SCHEMA.json')]
        for fname,sname in optional:
            if (p/fname).exists(): schema_objects.append((load_json(p/fname),sname))
        for obj,schema_name in schema_objects:
            try: jsonschema.validate(obj,load_json(ROOT/'CORE/SCHEMAS'/schema_name))
            except Exception as e: errors.append(f'{schema_name}: {e.message if hasattr(e,"message") else e}')
    # one in-progress task; done means acceptance all pass/not_applicable + outputs exist if file paths
    active=[]
    for tf in (p/'TASKS').glob('*.json') if (p/'TASKS').exists() else []:
        t=load_json(tf)
        if t.get('status')=='in_progress': active.append(t.get('task_id'))
        if t.get('status')=='done':
            bad=[a for a in t.get('acceptance_tests',[]) if a.get('status') not in {'pass','not_applicable'}]
            if bad: errors.append(f'{tf.name}: done with incomplete acceptance')
    if len(active)>1: errors.append(f'multiple in_progress tasks: {active}')
    # manifest strict if present
    mp=p/'MANIFEST.json'
    if mp.exists():
        man=load_json(mp)
        for item in man.get('files',[]):
            fp=p/item['path']
            if not fp.exists(): errors.append(f'manifest missing {item["path"]}'); continue
            h=hashlib.sha256(fp.read_bytes()).hexdigest()
            if h!=item['sha256']: errors.append(f'manifest hash mismatch {item["path"]}')
if errors:
    print('PROJECT VALIDATION: FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print('PROJECT VALIDATION: OK')
