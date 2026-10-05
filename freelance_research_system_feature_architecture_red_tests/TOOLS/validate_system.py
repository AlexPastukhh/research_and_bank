#!/usr/bin/env python3
import subprocess,sys,json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def run(args,label,timeout=30):
    try:
        p=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired:
        errors.append(f'{label}: timeout after {timeout}s'); return
    if p.returncode:
        errors.append(f'{label}: {p.stdout[-2500:]} {p.stderr[-1000:]}')
    elif p.stdout.strip():
        print(p.stdout.strip())

required=[
 'VERSION.json','CORE/SYSTEM_SPEC.json','CORE/USE_CASE_REGISTRY.json','CORE/GOLDEN_PATH_REGISTRY.json',
 'CORE/RESULT_PRODUCT_CONTRACTS.json','CORE/SYSTEM_MAP_SPEC.json','REFERENCE/SYSTEM_MAP.json',
 'REFERENCE/DEVELOPMENT_PLAN_vNext.md','REFERENCE/PHASE_ACCEPTANCE_QA.md','REFERENCE/UI_SCREEN_MAP.md','STAGE_STATUS.json',
 'CORE/SCHEMAS/PHASE_EXECUTION_RECORD_SCHEMA.json','AUDIT/PHASE_EXECUTION_RECORDS',
 'AUDIT/RUNS/STAGE2_ACCEPTANCE_REVIEW_v1.11.0_2026-10-01.md',
 'AUDIT/RUNS/ACCEPTANCE_QA_MODEL_REVIEW_v1.11.0_2026-10-01.md',
 'AUDIT/RUNS/RELEASE_EVIDENCE_v1.11.0_2026-10-01.json',
 'AUDIT/AUDIT_AXES.json','AUDIT/AXIS_TEST_MAP.json','WORKBOOK/research_system_template.xlsx'
]
for req in required:
    if not (ROOT/req).exists(): errors.append(f'missing required {req}')

# Fast canonical gates. Heavy test/smoke/benchmark execution is recorded in the release-evidence receipt.
run([ROOT/'TOOLS/validate_use_cases.py'],'use cases')
run([ROOT/'TOOLS/validate_architecture.py'],'architecture')
run([ROOT/'TOOLS/validate_stage2_acceptance.py'],'phase2 acceptance')
run([ROOT/'TOOLS/validate_phase_records.py'],'phase Q&A records')
run([ROOT/'TOOLS/generate_phase_qa_view.py','--check'],'phase Q&A view parity')
run([ROOT/'TOOLS/generate_system_map.py','--check'],'system map parity')
run([ROOT/'TOOLS/generate_use_case_views.py','--check'],'use-case view parity')

# Require green fresh release evidence for all named heavy gates.
evp=ROOT/'AUDIT/RUNS/RELEASE_EVIDENCE_v1.11.0_2026-10-01.json'
if evp.exists():
    ev=json.loads(evp.read_text())
    if ev.get('system_version')!='1.11.0': errors.append('release evidence system version mismatch')
    bad=[k for k,v in ev.get('checks',{}).items() if v.get('status')!='pass']
    if bad: errors.append('release evidence non-pass checks: '+', '.join(bad))

# Schema validity.
try:
    import jsonschema
    for p in (ROOT/'CORE/SCHEMAS').glob('*.json'):
        jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text()))
    jsonschema.Draft202012Validator(json.loads((ROOT/'CORE/SCHEMAS/USE_CASE_REGISTRY_SCHEMA.json').read_text())).validate(json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text()))
    jsonschema.Draft202012Validator(json.loads((ROOT/'CORE/SCHEMAS/RESULT_PRODUCT_CONTRACTS_SCHEMA.json').read_text())).validate(json.loads((ROOT/'CORE/RESULT_PRODUCT_CONTRACTS.json').read_text()))
except Exception as e:
    errors.append(f'schema validation: {e}')

# Workbook package integrity / required architecture sheets.
try:
    with zipfile.ZipFile(ROOT/'WORKBOOK/research_system_template.xlsx') as z:
        if z.testzip() is not None: errors.append('workbook ZIP corruption')
        xml=z.read('xl/workbook.xml').decode('utf-8','ignore')
        for sheet in ['UseCaseRegistry','ArchitectureBudget','AuditRun_AF2_v18','TaskManifests','RunState','GoldenPaths']:
            if f'name="{sheet}"' not in xml: errors.append(f'workbook missing sheet {sheet}')
except Exception as e:
    errors.append(f'workbook invalid xlsx: {e}')

# Strict release manifest.
mp=ROOT/'MANIFEST.json'
if not mp.exists():
    errors.append('missing MANIFEST.json')
else:
    man=json.loads(mp.read_text())
    for item in man.get('files',[]):
        p=ROOT/item['path']
        if not p.exists(): errors.append(f'manifest missing {item["path"]}'); continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
            errors.append(f'manifest hash mismatch {item["path"]}')

if errors:
    print('SYSTEM VALIDATION: FAIL')
    for e in errors: print('-',e)
    raise SystemExit(1)
print('SYSTEM VALIDATION: OK — 1.11.0')
