#!/usr/bin/env python3
from pathlib import Path
import json, sys, subprocess
try: import jsonschema
except Exception: jsonschema=None
ROOT=Path(__file__).resolve().parents[1]
reg=json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text(encoding='utf-8')); errors=[]
ids=[u['id'] for u in reg['use_cases']]; valid=set(ids)
if len(ids)!=len(valid): errors.append('duplicate use_case_id')
if len({u['action_class'] for u in reg['use_cases']})!=len(ids): errors.append('duplicate action_class')
if jsonschema:
    try: jsonschema.Draft202012Validator(json.loads((ROOT/'CORE/SCHEMAS/USE_CASE_REGISTRY_SCHEMA.json').read_text())).validate(reg)
    except Exception as e: errors.append('registry schema: '+str(e))
for u in reg['use_cases']:
    if not (ROOT/u['workflow']).exists(): errors.append(f"missing workflow {u['workflow']}")
    outcomes=set(u['outcomes']); seen=[]
    for tr in u['transitions']:
        seen.append(tr['outcome'])
        if tr['outcome'] not in outcomes: errors.append(f"{u['id']} transition undeclared outcome {tr['outcome']}")
        if tr.get('to') is not None and tr['to'] not in valid: errors.append(f"{u['id']} bad target {tr['to']}")
    if set(seen)!=outcomes or len(seen)!=len(set(seen)): errors.append(f"{u['id']} outcomes/transitions not total+unique")
    # Every failure outcome, when declared, must be a legal outcome.
    for f in u['failure_modes']:
        if f.get('outcome') and f['outcome'] not in outcomes: errors.append(f"{u['id']} failure {f['code']} points to undeclared outcome {f['outcome']}")
    if u['comparability_requirements']['required'] and not u['comparability_requirements']['dimensions']: errors.append(f"{u['id']} requires comparability but declares no dimensions")
    if not u['outputs']: errors.append(f"{u['id']} has no typed outputs")
    if not u['acceptance']: errors.append(f"{u['id']} has no acceptance contract")
    text=(ROOT/u['workflow']).read_text(encoding='utf-8').lower()
    for forbidden in ['## intent','## route here','## do not route','## normal next','## acceptance','## allowed outcome','trigger examples:']:
        if forbidden in text: errors.append(f"{u['id']} workflow duplicates registry-owned contract: {forbidden}")

# Phase 2 result/query contract invariants.
query=[u for u in reg['use_cases'] if u['interaction_type']=='query']
if {u['id'] for u in query}!={'UC21','UC22','UC23','UC24','UC25'}: errors.append('query UC set must be exactly UC21-UC25 in Phase 2')
if any(u['group']!='results' for u in query): errors.append('all query UCs must belong to results group')
if any(u['writes'] for u in query): errors.append('query UCs must not write research/project truth')
if any(not any('read-only' in s.lower() for s in u['side_effects']) for u in query): errors.append('query UCs must declare read-only side effect contract')
if any(u['name'].lower().startswith(('build ','render ','screen ')) for u in reg['use_cases']): errors.append('builders/screens must not be top-level use cases')
contracts=json.loads((ROOT/'CORE/RESULT_PRODUCT_CONTRACTS.json').read_text())
product_names=set(contracts['products'])
for u in query:
    for o in u['outputs']:
        if o['type'] not in product_names: errors.append(f"{u['id']} output type {o['type']} missing from result product contracts")

# Golden membership exact parity.
gp=json.loads((ROOT/'CORE/GOLDEN_PATH_REGISTRY.json').read_text())
expected={uid:set() for uid in ids}
for p in gp['paths']:
    for uid in p['expected_use_case_sequence']:
        if uid in expected: expected[uid].add(p['id'])
for u in reg['use_cases']:
    if set(u['golden_paths'])!=expected[u['id']]: errors.append(f"{u['id']} golden_paths drift")
for cmd in [[sys.executable,str(ROOT/'TOOLS/generate_use_case_views.py'),'--check'],[sys.executable,str(ROOT/'TOOLS/generate_system_map.py'),'--check']]:
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    if p.returncode: errors.append((p.stdout+p.stderr).strip())
if errors:
    print('USE CASE VALIDATION: FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print(f"USE CASE VALIDATION: OK — {len(ids)} complete v3 contracts")
