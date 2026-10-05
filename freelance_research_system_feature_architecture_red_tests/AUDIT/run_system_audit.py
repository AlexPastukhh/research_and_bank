#!/usr/bin/env python3
import argparse,subprocess,sys,json,hashlib,zipfile,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--target',default=str(ROOT)); args=ap.parse_args()

def run(cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True); return p.returncode==0,(p.stdout+p.stderr)[-6000:]
def exists(*rels): return all((ROOT/r).exists() for r in rels)
checks={}; detail={}
jobs={
 'use_cases':[sys.executable,str(ROOT/'TOOLS/validate_use_cases.py')],
 'architecture':[sys.executable,str(ROOT/'TOOLS/validate_architecture.py')],
 'full_tests':[sys.executable,str(ROOT/'TOOLS/run_tests.py'),'--full','--workers','4'],
 'smoke':[sys.executable,str(ROOT/'TOOLS/smoke_test.py')],
 'benchmark':[sys.executable,str(ROOT/'TOOLS/benchmark.py')],
 'phase2_acceptance':[sys.executable,str(ROOT/'TOOLS/validate_stage2_acceptance.py')],
 'phase_qa':[sys.executable,str(ROOT/'TOOLS/validate_phase_records.py')],
}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 futs={ex.submit(run,cmd):key for key,cmd in jobs.items()}
 for fut in concurrent.futures.as_completed(futs):
  key=futs[fut]; checks[key],detail[key]=fut.result()
checks['golden_paths']=checks.get('full_tests',False); detail['golden_paths']='covered by TESTS.test_golden_paths inside run_tests quick gate'
checks['system_map'],detail['system_map']=run([sys.executable,str(ROOT/'TOOLS/generate_system_map.py'),'--check'])
checks['phase_qa_view'],detail['phase_qa_view']=run([sys.executable,str(ROOT/'TOOLS/generate_phase_qa_view.py'),'--check'])
checks['docs']=exists('CORE/SYSTEM_SPEC.json','METHOD/01_RESEARCH_CONTRACT.md','REFERENCE/AUDIT_POLICY.md','REFERENCE/MIGRATION_SUPPORT.md')
# schema parse + Draft check when available
try:
 import jsonschema
 for p in (ROOT/'CORE/SCHEMAS').glob('*.json'):
  jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text()))
 checks['schemas']=True
except Exception as e: checks['schemas']=False; detail['schemas']=str(e)
checks['source_contracts']=exists('METHOD/15_SOURCE_REGISTRY_AND_PRIORITIZATION.md','CORE/SCHEMAS/SOURCE_REGISTRY_SCHEMA.json','CORE/SCHEMAS/SOURCE_USE_PLAN_SCHEMA.json')
checks['measurement_contracts']=exists('METHOD/07_MEASUREMENT_PROTOCOL.md','CORE/SCHEMAS/MEASUREMENT_SCHEMA.json')
checks['economics_contracts']=exists('METHOD/20_OPPORTUNITY_ECONOMICS.md','CORE/SCHEMAS/OPPORTUNITY_ECONOMICS_SCHEMA.json')
checks['dependency_contracts']=exists('TEMPLATES/DEPENDENCY_GRAPH.template.json','TOOLS/propagate_changes.py')
checks['bootstrap_contracts']=exists('BOOTSTRAP/00_BOOTSTRAP_RUNBOOK.md','TOOLS/bootstrap_cycle.py','TOOLS/checkpoint_project.py')
checks['config_contracts']=exists('CORE/SYSTEM_DEFAULTS.json','CORE/SCHEMAS/PROJECT_CONFIG_SCHEMA.json')
checks['repair_contracts']=exists('TOOLS/repair_project.py','TOOLS/validate_project.py')
checks['migration_contracts']=exists('TOOLS/migrate_project.py','REFERENCE/MIGRATION_SUPPORT.md')
checks['capability_contracts']=exists('CORE/SCHEMAS/METHOD_REGISTRY_SCHEMA.json')
checks['lineage_contracts']=exists('CORE/SCHEMAS/TASK_MANIFEST_SCHEMA.json') and all(k in json.loads((ROOT/'CORE/SCHEMAS/TASK_MANIFEST_SCHEMA.json').read_text())['required'] for k in ['request_ref','route_reason','use_case_registry_version','router_kind'])
# workbook
try:
 with zipfile.ZipFile(ROOT/'WORKBOOK/research_system_template.xlsx') as z:
  xml=z.read('xl/workbook.xml').decode('utf-8','ignore'); checks['workbook']=all(f'name="{s}"' in xml for s in ['UseCaseRegistry','ArchitectureBudget','AuditRun_AF2_v18','GoldenPaths'])
except Exception as e: checks['workbook']=False; detail['workbook']=str(e)
# manifest if present
mp=ROOT/'MANIFEST.json'; checks['manifest']=mp.exists()
if mp.exists():
 try:
  man=json.loads(mp.read_text()); checks['manifest']=all((ROOT/i['path']).exists() and hashlib.sha256((ROOT/i['path']).read_bytes()).hexdigest()==i['sha256'] for i in man['files'])
 except Exception as e: checks['manifest']=False; detail['manifest']=str(e)
req={
 'AX01':['docs'],'AX02':['full_tests'],'AX03':['schemas','full_tests'],'AX04':['full_tests'],'AX05':['full_tests'],'AX06':['full_tests'],
 'AX07':['source_contracts','full_tests'],'AX08':['measurement_contracts'],'AX09':['economics_contracts'],'AX10':['dependency_contracts','full_tests'],
 'AX11':['bootstrap_contracts','full_tests','smoke'],'AX12':['config_contracts','full_tests'],'AX13':['full_tests','smoke'],'AX14':['full_tests'],
 'AX15':['migration_contracts','full_tests'],'AX16':['capability_contracts','bootstrap_contracts'],'AX17':['benchmark'],'AX18':['repair_contracts'],
 'AX19':['full_tests','use_cases','golden_paths','phase_qa'],'AX20':['manifest','workbook','docs','system_map','phase_qa','phase_qa_view'],'AX21':['use_cases','phase2_acceptance','full_tests','golden_paths'],'AX22':['use_cases','architecture','phase2_acceptance'],
 'AX23':['use_cases','architecture','phase2_acceptance','golden_paths'],'AX24':['use_cases','architecture','system_map','phase2_acceptance','phase_qa','phase_qa_view'],'AX25':['lineage_contracts','phase2_acceptance','full_tests'],'AX26':['architecture','phase2_acceptance']}
axes=json.loads((ROOT/'AUDIT/AUDIT_AXES.json').read_text())['axes']; results=[]
for a in axes:
 needed=req[a['id']]; bad=[k for k in needed if not checks.get(k,False)]; results.append({'axis_id':a['id'],'name':a['name'],'status':'pass' if not bad else ('fail' if a['release_gate'] else 'partial'),'evidence_checks':needed,'failed_checks':bad})
clear=all(r['status']=='pass' for r in results)
out={'audit_framework':'2.0.0','target_system':'1.11.0','audit_clear':clear,'checks':checks,'axis_results':results,'details':detail}
print(json.dumps(out,indent=2)); raise SystemExit(0 if clear else 1)
