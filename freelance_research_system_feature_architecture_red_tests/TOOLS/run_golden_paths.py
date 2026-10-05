#!/usr/bin/env python3
import argparse, json, subprocess, sys, tempfile, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=json.loads((ROOT/'CORE/GOLDEN_PATH_REGISTRY.json').read_text(encoding='utf-8'))

class GPError(AssertionError): pass

def run_tool(*args, ok=True):
    p=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,capture_output=True,text=True)
    if ok and p.returncode:
        raise GPError(f"command failed: {' '.join(map(str,args))}\n{p.stdout}\n{p.stderr}")
    return p

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,obj): Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def expect(cond,msg):
    if not cond: raise GPError(msg)

def select(project, request, expected, state=None, now='2026-10-01T00:00:00+00:00'):
    args=[ROOT/'TOOLS/select_use_case.py',project,request,'--now',now]
    if state is not None: args += ['--state-json',json.dumps(state,ensure_ascii=False)]
    d=json.loads(run_tool(*args).stdout)
    expect(d['use_case_id']==expected,f'route expected {expected}, got {d}')
    return d

def outcome(project, uc, out, expected_next, now):
    d=json.loads(run_tool(ROOT/'TOOLS/apply_use_case_outcome.py',project,'--use-case-id',uc,'--outcome',out,'--now',now).stdout)
    expect(d['next_use_case_id']==expected_next,f'{uc}/{out}: expected next {expected_next}, got {d}')
    return d

def init(project,pid):
    run_tool(ROOT/'TOOLS/init_project.py',project,pid)
    run_tool(ROOT/'TOOLS/validate_project.py',project)

def checkpoint(project,now):
    run_tool(ROOT/'TOOLS/checkpoint_project.py',project,'--now',now)
    run_tool(ROOT/'TOOLS/validate_project.py',project)
    expect((Path(project)/'HANDOFF.json').exists(),'HANDOFF missing')
    expect((Path(project)/'MANIFEST.json').exists(),'MANIFEST missing')

def gp01(td):
    p=Path(td)/'project'; init(p,'gp01')
    select(p,'начать новое исследование с нуля','UC01')
    rs0=load(p/'RUN_STATE.json'); expect(rs0['next_use_case_id']=='UC01','UC01 not selected')
    outcome(p,'UC01','initialized','UC03','2026-10-01T00:01:00+00:00')
    rs=load(p/'RUN_STATE.json'); expect(rs['next_task_id']=='M01','first task pointer not preserved into UC03')
    run_tool(ROOT/'TOOLS/validate_project.py',p)
    return ['UC01','UC03']

def gp02(td):
    baseline=Path(td)/'baseline'; init(baseline,'baseline')
    # Make the baseline a real checkpointed project.
    checkpoint(baseline,'2026-09-30T20:00:00+00:00')
    cyc=Path(td)/'cycle'; run_tool(ROOT/'TOOLS/bootstrap_cycle.py','-o',cyc,baseline)
    p=cyc/'PROJECT'; select(p,'продолжи прошлое исследование из старого архива','UC02',{'baseline_supplied':True})
    inv=load(cyc/'INVENTORY.json'); expect(len(inv['inputs'])==1,'baseline inventory missing')
    idx=load(p/'PROJECT_INDEX.json'); expect(idx['artifacts']['workbook']=='research.xlsx','bad workbook pointer')
    expect((p/'research.xlsx').exists(),'bootstrap workbook missing')
    run_tool(ROOT/'TOOLS/validate_project.py',p)
    outcome(p,'UC02','baseline_ready','UC03','2026-10-01T00:02:00+00:00')
    return ['UC02','UC03']

def gp03(td):
    p=Path(td)/'project'; init(p,'gp03'); select(p,'собери programming jobs и выясни за какие небольшие задачи платят','UC06')
    r=p/'RESULTS'; r.mkdir()
    save(r/'raw_tasks.json',{'tasks':[{'id':'j1','title':'Fix Python script'},{'id':'j2','title':'Small API integration'}]})
    outcome(p,'UC06','observations_collected','UC07','2026-10-01T01:00:00+00:00')
    save(r/'normalized.json',{'service_units':['Python bug fixing','Small API integration']})
    outcome(p,'UC07','normalized','UC08','2026-10-01T01:01:00+00:00')
    save(r/'measurement.json',{'metric':'payout','unit':'USD','observations':[25,80]})
    outcome(p,'UC08','measurement_complete','UC14','2026-10-01T01:02:00+00:00')
    save(r/'decision.json',{'status':'updated','note':'synthetic golden-path decision'})
    outcome(p,'UC14','decision_updated','UC17','2026-10-01T01:03:00+00:00')
    checkpoint(p,'2026-10-01T01:04:00+00:00')
    for f in ['raw_tasks.json','normalized.json','measurement.json','decision.json']: expect((r/f).exists(),f'{f} missing')
    return ['UC06','UC07','UC08','UC14','UC17']

def gp04(td):
    p=Path(td)/'project'; init(p,'gp04'); select(p,'что изменилось с вчера по известному направлению','UC09')
    start=ROOT/'TOOLS/start_daily_run.py'; rec=ROOT/'TOOLS/record_observation.py'; finish=ROOT/'TOOLS/finish_daily_run.py'
    run_tool(start,p,'--run-id','day1','--method-id','m1','--method-version','1','--scope-fingerprint','scope','--source-route','routeA','--now','2026-09-30T10:00:00+00:00')
    run_tool(rec,p,'--entity-id','e1','--canonical-key','e1','--class','seen','--state','active','--source-id','src','--payload-json','{"price":10}','--now','2026-09-30T10:01:00+00:00')
    run_tool(finish,p,'--coverage','complete','--now','2026-09-30T11:00:00+00:00')
    run_tool(start,p,'--run-id','day2','--method-id','m1','--method-version','1','--scope-fingerprint','scope','--source-route','routeA','--now','2026-10-01T10:00:00+00:00')
    run_tool(rec,p,'--entity-id','e1','--canonical-key','e1','--class','seen','--state','active','--source-id','src','--payload-json','{"price":20}','--now','2026-10-01T10:01:00+00:00')
    run_tool(rec,p,'--entity-id','e2','--canonical-key','e2','--class','seen','--state','active','--source-id','src','--payload-json','{"price":5}','--now','2026-10-01T10:02:00+00:00')
    run_tool(finish,p,'--coverage','complete','--now','2026-10-01T11:00:00+00:00')
    diff=json.loads(run_tool(ROOT/'TOOLS/build_daily_diff.py',p,'--current-run','day2','--previous-run','day1').stdout)
    expect(diff['comparison_status']=='comparable','runs not comparable')
    expect(diff['changed_entity_ids']==['e1'],f'expected e1 changed: {diff}')
    expect(diff['new_entity_ids']==['e2'],f'expected e2 new: {diff}')
    expect(diff['confirmed_closed_ids']==[],f'false closure: {diff}')
    outcome(p,'UC09','changes_built','UC17','2026-10-01T11:01:00+00:00'); checkpoint(p,'2026-10-01T11:02:00+00:00')
    return ['UC09','UC17']

def gp05(td):
    p=Path(td)/'project'; init(p,'gp05'); select(p,'добавь этот источник в реестр источников','UC15')
    sr=load(p/'SOURCE_REGISTRY.json'); sr['sources'].append({'source_id':'SRC-GP','canonical_name':'Golden Path Forum','source_role':'discovery','current_priority':'P2','current_status':'active','discovered_via_source_ids':[],'discovery_route_ids':['golden_path']}); save(p/'SOURCE_REGISTRY.json',sr)
    run_tool(ROOT/'TOOLS/validate_project.py',p)
    expect(load(p/'SOURCE_REGISTRY.json')['sources'][0]['source_id']=='SRC-GP','source not persisted')
    outcome(p,'UC15','sources_updated','UC17','2026-10-01T12:00:00+00:00'); checkpoint(p,'2026-10-01T12:01:00+00:00')
    return ['UC15','UC17']

def gp06(td):
    p=Path(td)/'project'; init(p,'gp06'); select(p,'измени метод исследования; для этого нужна миграция проекта','UC16')
    outcome(p,'UC16','migration_required','UC20','2026-10-01T13:00:00+00:00')
    # Model a project still carrying the immediately previous system contract.
    for fn in ['STATE.json','RUN_STATE.json']:
        x=load(p/fn); x['system_version']='1.10.0'; save(p/fn,x)
    run_tool(ROOT/'TOOLS/migrate_project.py',p,'--apply')
    expect(load(p/'STATE.json')['system_version']=='1.11.0','state not migrated')
    expect(load(p/'RUN_STATE.json')['system_version']=='1.11.0','run state not migrated')
    run_tool(ROOT/'TOOLS/validate_project.py',p)
    outcome(p,'UC20','migrated','UC03','2026-10-01T13:01:00+00:00')
    return ['UC16','UC20','UC03']

FUNCS={'GP01':gp01,'GP02':gp02,'GP03':gp03,'GP04':gp04,'GP05':gp05,'GP06':gp06}

def run_one(gpid):
    spec=next((x for x in REG['paths'] if x['id']==gpid),None)
    if not spec: raise GPError(f'unknown golden path {gpid}')
    with tempfile.TemporaryDirectory(prefix=f'{gpid.lower()}-') as td:
        seq=FUNCS[gpid](td)
    expect(seq==spec['expected_use_case_sequence'],f'{gpid}: expected sequence {spec["expected_use_case_sequence"]}, got {seq}')
    return {'id':gpid,'status':'pass','sequence':seq}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--path',action='append'); ap.add_argument('--json',action='store_true'); ap.add_argument('--workers',type=int,default=3); args=ap.parse_args()
    ids=args.path or [x['id'] for x in REG['paths'] if x.get('release_gate')]
    results=[]; failed=[]
    def wrapped(gpid):
        try: return run_one(gpid)
        except Exception as e: return {'id':gpid,'status':'fail','error':str(e)}
    if len(ids)==1:
        raw=[wrapped(ids[0])]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex:
            raw=list(ex.map(wrapped,ids))
    for r in raw:
        gpid=r['id']; results.append(r)
        if r['status']=='fail':
            failed.append(gpid)
            if not args.json: print(f'FAIL {gpid}: {r.get("error")}')
        elif not args.json: print(f'PASS {gpid}: {" -> ".join(r["sequence"])}')
    out={'registry_version':REG['registry_version'],'system_version':REG['system_version'],'passed':len(results)-len(failed),'failed':len(failed),'results':results}
    if args.json: print(json.dumps(out,ensure_ascii=False,indent=2))
    else: print(f'GOLDEN PATH GATE: {"OK" if not failed else "FAIL"} — {out["passed"]}/{len(results)} passed')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
