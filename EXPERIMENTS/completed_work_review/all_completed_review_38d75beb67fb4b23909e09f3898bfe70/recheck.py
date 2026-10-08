"""Read-only source review; tests mutate only owned synthetic roots and review evidence."""
from pathlib import Path
import argparse,base64,copy,datetime,hashlib,importlib,json,os,platform,re,shutil,sqlite3,subprocess,sys,time,unittest,uuid

def digest(raw):return hashlib.sha256(raw).hexdigest()
def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);ap.add_argument('--metadata',required=True)
a=ap.parse_args();root=Path(a.root).absolute();out=Path(a.out).absolute();out.mkdir(parents=True,exist_ok=True)
meta=json.loads(Path(a.metadata).read_text(encoding='utf-8'))
before={n:digest((root/n).read_bytes()) for n in meta['files']}
assert before=={n:m['sha256'] for n,m in meta['files'].items()},'SOURCE_DRIFT_BEFORE_RECHECK'
for folder in ['secure_intake','sqlite_importer','bank_read_api','lexical_search','local_command_adapter','package_producer','local_ui']:
    sys.path.insert(0,str(root/'EXPERIMENTS'/folder))
sys.path.insert(0,str(root/'PLANNING/TOOLS'))
cases=[];groups=[];start=time.monotonic()
class Evidence(unittest.TextTestResult):
    def record(self,test,status,detail=None):
        cases.append({'id':test.id(),'observed':status,**({'detail':detail} if detail else {})})
        (out/'PROGRESS.json').write_text(dump({'platform':platform.platform(),'completed':len(cases),'last':test.id(),'failures':sum(c['observed']!='PASS' for c in cases),'elapsed_seconds':round(time.monotonic()-start,2)}),encoding='utf-8')
    def addSuccess(self,t):super().addSuccess(t);self.record(t,'PASS')
    def addFailure(self,t,e):super().addFailure(t,e);self.record(t,'FAIL',self._exc_info_to_string(e,t))
    def addError(self,t,e):super().addError(t,e);self.record(t,'ERROR',self._exc_info_to_string(e,t))
    def addSkip(self,t,why):super().addSkip(t,why);self.record(t,'SKIP',why)
    def addSubTest(self,t,sub,e):
        super().addSubTest(t,sub,e)
        if e:self.record(sub,'FAIL',self._exc_info_to_string(e,t))

specs=[('test_release_plan','ReleasePlanTests'),('test_inventory','InventoryTests'),('test_bank_contracts','Tests'),('test_bank_queries','QueryContractTests')]
if os.name=='nt':specs.append(('test_reader','Tests'))
specs += [(m,'Tests') for m in ['test_importer','test_reads','test_search','test_commands','test_producer','test_ui']]
for name,cls in specs:
    module=importlib.import_module(name)
    if name=='test_ui':module.__file__=str(out/'test_ui.py') # capture destination only; desktop/process source remains actual
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(getattr(module,cls))
    if name=='test_ui' and os.name=='nt':
        suite.addTests(module.NativeUI(n) for n in sorted(dir(module.NativeUI)) if n.startswith('ui_'))
    print('GROUP_START',name,suite.countTestCases(),flush=True)
    result=unittest.TextTestRunner(verbosity=0,resultclass=Evidence).run(suite)
    groups.append({'module':name,'tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors)})
    print('GROUP_DONE',json.dumps(groups[-1]),flush=True)

import reader as transport,importer as im,bank_read as reads,search as lexical
import test_importer as fixtures
probes=[]
def probe(name,function):
    t=time.monotonic()
    try:value=function();probes.append({'id':name,**value,'elapsed_seconds':round(time.monotonic()-t,3)})
    except Exception as e:probes.append({'id':name,'status':'PROBE_ERROR','exception':type(e).__name__,'detail':str(e)[:600]})
    print('PROBE',json.dumps(probes[-1],ensure_ascii=False),flush=True)

def parser_integer():
    raw=b'{"n":'+b'1'*5000+b'}'
    try:transport.strict_json(raw,16384,16);observed='unexpected_accept'
    except transport.Rejected as e:observed='structured_rejection:'+str(e)
    except Exception as e:observed='uncaught_'+type(e).__name__
    return {'status':'CONFIRMED_DEFECT' if observed=='uncaught_ValueError' else 'COUNTEREVIDENCE','raw_bytes':len(raw),'observed':observed,'interpreter_digit_limit':sys.get_int_max_str_digits()}
probe('PARSER_LONG_INTEGER',parser_integer)

def native_packet_integer():
    import test_reader as tr
    f=tr.Tests('test_01_supported_fixture_snapshot_lifetime');f.setUp()
    try:
        marker=(b'{"protocol":"local-bank-intake/1","transaction_id":"'+f.tx.encode()+b'","manifest_byte_length":'+b'1'*5000+b',"manifest_sha256":"'+b'0'*64+b'"}')
        (f.p/'READY.json').write_bytes(marker)
        try:
            result=f.read();observed=result.status+'/'+result.code
            if result.snapshot:result.snapshot.close()
        except Exception as e:observed='uncaught_'+type(e).__name__
        return {'status':'CONFIRMED_DEFECT' if observed=='uncaught_ValueError' else 'COUNTEREVIDENCE','ready_bytes':len(marker),'observed':observed,'staging_empty':list(f.stage.iterdir())==[]}
    finally:f.tearDown()
if os.name=='nt':probe('NATIVE_READY_LONG_INTEGER',native_packet_integer)

def grant_world(p):
    cp=subprocess.run(['icacls',str(p),'/grant','*S-1-1-0:(F)'],capture_output=True,text=True,timeout=10)
    assert cp.returncode==0,'ICACLS_GRANT_FAILED:'+cp.stderr
def file_acl(p):
    with im.native.Handle(p) as h:
        sddl=im.native.security_sddl(h)
        try:im.native.verify_private_acl(h);rejected=False
        except im.native.SafetyError:rejected=True
    return sddl,rejected
def database_acl():
    f=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');f.setUp()
    try:
        grant_world(f.store.db);sddl,refused=file_acl(f.store.db)
        with im.native.configured_root(f.root):root_still_private=True
        try:c=f.store._connect(False);c.close();observed='STORE_ACCEPTS_NONPRIVATE_DB'
        except Exception as e:observed='refused:'+type(e).__name__
        cache_root=f.temp/'cache';fixtures.private(cache_root)
        api=lexical.SearchAPI(f.root,cache_root);built=api.rebuild();api.close()
        cache_file=cache_root/'search-cache.sqlite3';grant_world(cache_file);cache_sddl,cache_refused=file_acl(cache_file)
        with lexical.Cache(cache_root,f.root,lexical.SearchAPI(f.root,cache_root).limits) as cache:
            try:c=cache.connect(lexical.Budget(cache.limits));c.close();cache_observed='CACHE_ACCEPTS_NONPRIVATE_FILE'
            except Exception as e:cache_observed='refused:'+type(e).__name__
        return {'status':'CONFIRMED_DEFECT' if refused and observed=='STORE_ACCEPTS_NONPRIVATE_DB' else 'COUNTEREVIDENCE','configured_root_private':root_still_private,'file_guard_refuses':refused,'observed':observed,'file_sddl':sddl,'cache_build':built['status'],'cache_file_guard_refuses':cache_refused,'cache_observed':cache_observed,'cache_file_sddl':cache_sddl,'boundary':'Only owner-created synthetic files had Everyone ACE added; no real Bank/account/global policy modified. Other-user actual impersonation not performed.'}
    finally:f.tearDown()
if os.name=='nt':probe('NATIVE_DATABASE_AND_CACHE_FILE_ACL',database_acl)

def payload_acl():
    import test_reader as tr
    f=tr.Tests('test_01_supported_fixture_snapshot_lifetime');f.setUp()
    try:
        grant_world(f.p/'payload.bin');sddl,refused=file_acl(f.p/'payload.bin')
        result=f.read()
        if result.snapshot:result.snapshot.close()
        return {'status':'CONFIRMED_DEFECT' if refused and result.status=='VERIFIED_TRANSPORT' else 'COUNTEREVIDENCE','file_guard_refuses':refused,'observed':result.status+'/'+result.code,'file_sddl':sddl,'configured_package_private':True,'transport_only':True}
    finally:f.tearDown()
if os.name=='nt':probe('NATIVE_INTAKE_PAYLOAD_FILE_ACL',payload_acl)

def reference_work():
    f=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');f.setUp()
    try:
        refs=[]
        for i in range(3):
            b=fixtures.Bundle();op,d=b.doc('Asset');b.m['transaction_id']=str(uuid.uuid4());oid=str(uuid.uuid4());rid=str(uuid.uuid4());op.update(object_id=oid,revision_id=rid,base_revision_id=None);d.update(object_id=oid,revision_id=rid,title='Reference-work original '+str(i));d['provenance']['derived_from']=[]
            path=d['data']['storage']['file_path'];raw=bytes([65+i])*1048576;d['data']['storage'].update(byte_length=len(raw),sha256=im.sha(raw));b.m['operations']=[op];b.files={op['document_path']:im.encoded(d),path:raw}
            result=f.save(b);assert result.state=='ACCEPTED',result
            refs.append({k:d[k] for k in ['object_type','object_id','revision_id']})
        template=fixtures.Bundle();old_op,old_doc=template.doc('Annotation');batch=fixtures.Bundle();batch.m['transaction_id']=str(uuid.uuid4());batch.m['operations']=[];batch.files={}
        for i in range(64):
            d=copy.deepcopy(old_doc);d.update(object_id=str(uuid.uuid4()),revision_id=str(uuid.uuid4()),title='Reference note '+str(i));d['data']['targets']=copy.deepcopy(refs);d['provenance']['derived_from']=[]
            path='objects/note-'+str(i)+'.json';op={**old_op,'object_id':d['object_id'],'revision_id':d['revision_id'],'base_revision_id':None,'document_path':path};batch.m['operations'].append(op);batch.files[path]=im.encoded(d)
        bytes_read=0;blob_reads=0;commit_checks=0;old_verify=f.store._verify_blob;old_commit=f.store._verify_commit
        def verify(c,row,cap,collect=False):
            nonlocal bytes_read,blob_reads
            bytes_read+=row[2];blob_reads+=1;return old_verify(c,row,cap,collect)
        def check(c,seq):
            nonlocal commit_checks
            commit_checks+=1;return old_commit(c,seq)
        f.store._verify_blob=verify;f.store._verify_commit=check
        incoming=sum(len(b) for b in batch.files.values());t=time.monotonic();result=f.save(batch);elapsed=time.monotonic()-t
        return {'status':'CONFIRMED_WORK_AMPLIFICATION','observed':result.state,'notes':64,'distinct_old_commits':3,'references_per_note':3,'commit_verifications':commit_checks,'retained_blob_reads':blob_reads,'retained_bytes_verified':bytes_read,'incoming_payload_bytes':incoming,'amplification':round(bytes_read/incoming,1),'import_elapsed_seconds':round(elapsed,3),'old_original_bytes_each':1048576,'per_request_retained_work_budget_present':False,'interpretation':'Measured redundant historical work, not a measured universal latency threshold or corruption. Three commits cycle through a two-entry cache; importer has no elapsed/aggregate-retained-byte budget.'}
    finally:f.tearDown()
probe('REFERENCE_VERIFICATION_WORK',reference_work)

def independent_document_checks():
    registry=json.loads((root/'DRAFT_NOTES/REQUIREMENTS_MAP.json').read_text());plan=json.loads((root/'PLANNING/REQUIREMENTS_RELEASE_MAP.json').read_text());reqs=registry['requirements'];mapped=plan['requirements']
    ids=[r['id'] for r in reqs];mapids=[r['requirement_id'] for r in mapped];assert len(ids)==len(set(ids))==115;assert set(ids)==set(mapids) and len(mapids)==115
    milestones={m['id']:m for m in plan['milestones']};visiting=set();visited=set()
    def visit(n):
        assert n in milestones
        if n in visited:return
        assert n not in visiting,'MILESTONE_CYCLE'
        visiting.add(n)
        for predecessor in milestones[n]['dependencies']:visit(predecessor)
        visiting.remove(n);visited.add(n)
    for n in milestones:visit(n)
    triage=json.loads((root/'DRAFT_NOTES/BACKLOG_TRIAGE.json').read_text());assert len(triage['items'])==159 and len({i['backlog_id'] for i in triage['items']})==159
    proposals=json.loads((root/'DRAFT_NOTES/NORMALIZATION_PROPOSALS.json').read_text());assert len(proposals['entries'])==45
    cards=[];missing=[]
    for p in (root/'PLANNING/WORK_ITEMS').glob('*.json'):
        c=json.loads(p.read_text())
        if c.get('record_kind')!='vnext_development_work_item':continue
        cards.append({'path':p.relative_to(root).as_posix(),'id':c['task_id'],'status':c['status']})
        for n in c.get('required_inputs',[]):
            if not (root/n).is_file():missing.append({'card':c['task_id'],'input':n})
        for q in c.get('pre_execution_questions',[]):
            assert not(q.get('blocking_user_answer') and q.get('status') in ['pending','proposal_review_pending']), 'UNANSWERED_BLOCKING_USER_QUESTION'
        if c['status']=='completed':
            assert all(k.get('status')=='PASS' for k in c['acceptance_checks']),p.name
            assert (root/c['completion_receipt']).is_file(),p.name
    state=(root/'PLANNING/SESSION_STATE.md').read_text();assert state.count('CURRENT_WORK_ITEM:')==1
    match=re.search(r'CURRENT_WORK_ITEM: \[[^]]+\]\(([^)]+)\)',state);current=json.loads((root/'PLANNING'/match[1]).read_text());assert current['status']!='completed'
    return {'status':'PASS' if not missing or os.name!='nt' else 'INPUTS_MISSING','requirements':115,'backlog':159,'proposals':45,'pending_proposals':sum(p['state']=='pending_not_adopted' for p in proposals['entries']),'milestone_dependency_cycles':False,'cards':cards,'missing_inputs':missing,'missing_input_interpretation':'Local source mirror excludes accepted baseline files; Windows checks actual repository inputs.','current_work_item':current['task_id'],'full_release_accepted':False}
probe('INDEPENDENT_DOCUMENT_INVARIANTS',independent_document_checks)

after={n:digest((root/n).read_bytes()) for n in meta['files']};assert before==after,'SOURCE_CHANGED_BY_RECHECK'
captures=[]
if os.name=='nt':captures=importlib.import_module('test_ui').CAPTURES
report={'record_kind':'completed_work_independent_recheck','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'elapsed_seconds':round(time.monotonic()-start,3),'groups':groups,'tests_run':sum(g['tests_run'] for g in groups),'regression_success':all(g['success'] and g['skipped']==0 for g in groups),'cases':cases,'independent_probes':probes,'source_unchanged':True,'source_sha256':after,'native_ui_captures':captures,'limitations':['Existing regression suites are repeated checks, not independent proof by themselves. Additional independent adversarial probes and document invariants provide counterexamples.','Native ACL probes add Everyone ACE only to owned temporary files; effective access by a separate user token was not tested.','No real Bank/user import/install/provider/network/physical power loss/full-release acceptance.','Measured reference amplification demonstrates redundant work, not a universal real-workload latency estimate.']}
target=out/('REGRESSION_NATIVE.json' if os.name=='nt' else 'REGRESSION_LOCAL.json');target.write_text(dump(report),encoding='utf-8');assert json.loads(target.read_text())==report
print('FINAL',json.dumps({'path':str(target),'tests':report['tests_run'],'regression_success':report['regression_success'],'independent_probes':len(probes),'source_unchanged':True,'report_sha256':digest(target.read_bytes())}),flush=True)
