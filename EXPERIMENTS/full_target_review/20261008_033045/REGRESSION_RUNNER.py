"""Isolated same-source evidence; never rewrites historical component reports."""
from pathlib import Path
import argparse,datetime,hashlib,importlib,json,os,platform,sys,time,unittest
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--out',required=True);a=p.parse_args();root=Path(a.root).resolve();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
for f in ['secure_intake','sqlite_importer','bank_read_api','lexical_search','local_command_adapter','package_producer','local_ui','draft_authoring']:sys.path.insert(0,str(root/'EXPERIMENTS'/f))
sys.path.insert(0,str(root/'PLANNING/TOOLS'))
sha=lambda b:hashlib.sha256(b).hexdigest();dump=lambda d:json.dumps(d,ensure_ascii=False,indent=2)+'\n'
source={p.relative_to(root).as_posix():sha(p.read_bytes()) for folder in ['secure_intake','sqlite_importer','bank_read_api','lexical_search','local_command_adapter','package_producer','local_ui','draft_authoring'] for p in (root/'EXPERIMENTS'/folder).iterdir() if p.is_file() and p.suffix in ['.py','.sql','.json'] and (p.suffix!='.json' or p.name in ['LIMITS.json','WORK_LIMITS.json'] or p.name.endswith('.schema.json'))}
cases=[];groups=[];start=time.monotonic()
class Evidence(unittest.TextTestResult):
    def record(self,t,status,detail=None):
        cases.append({'id':t.id(),'status':status,**({'detail':detail} if detail else {})});(out/'PROGRESS.json').write_text(dump({'completed':len(cases),'last':t.id(),'last_status':status,'nonpass':sum(x['status'] not in ['PASS','SKIP_PLATFORM'] for x in cases),'elapsed_seconds':round(time.monotonic()-start,2)}),encoding='utf-8')
    def addSuccess(self,t):super().addSuccess(t);self.record(t,'PASS')
    def addFailure(self,t,e):super().addFailure(t,e);self.record(t,'FAIL',self._exc_info_to_string(e,t))
    def addError(self,t,e):
        super().addError(t,e);detail=self._exc_info_to_string(e,t)
        blocked=os.name=='nt' and t.id() in ['test_reader.Tests.test_08_symlink_file','test_reader.Tests.test_09_symlink_directory','test_reader.Tests.test_10_symlink_root_parent','test_reader.Tests.test_29_ready_symlink'] and '1314' in detail
        # Classify by actual original case name below if the known names differ.
        if os.name=='nt' and t.id().startswith('test_reader.Tests.test_') and t._testMethodName.split('_')[1] in ['08','09','10','29'] and '1314' in detail:blocked=True
        self.record(t,'BLOCKED_FIXTURE_WIN1314' if blocked else 'ERROR',detail)
    def addSkip(self,t,why):super().addSkip(t,why);self.record(t,'SKIP_PLATFORM',why)
    def addSubTest(self,t,sub,e):
        super().addSubTest(t,sub,e)
        if e:self.record(sub,'FAIL',self._exc_info_to_string(e,t))
specs=[('test_release_plan','ReleasePlanTests'),('test_inventory','InventoryTests'),('test_bank_contracts','Tests'),('test_bank_queries','QueryContractTests')]
if os.name=='nt':specs.append(('test_reader','Tests'))
specs.extend((m,'Tests') for m in ['test_importer','test_reads','test_search','test_commands','test_producer','test_ui','test_review_fixes','test_authoring'])
for name,cls in specs:
    mod=importlib.import_module(name)
    if name=='test_ui':mod.CAPTURE_ROOT=out/'NATIVE_SCREENSHOTS_UI'
    if name=='test_authoring':mod.PROOF_ROOT=out/'AUTHORING_CAPTURES'
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(getattr(mod,cls))
    if name in ['test_ui','test_authoring'] and os.name=='nt':suite.addTests(mod.NativeUI(n) for n in sorted(dir(mod.NativeUI)) if n.startswith('ui_'))
    print('GROUP_START',name,suite.countTestCases(),flush=True);result=unittest.TextTestRunner(verbosity=0,resultclass=Evidence).run(suite);groups.append({'module':name,'tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors)});print('GROUP_DONE',json.dumps(groups[-1]),flush=True)
after={n:sha((root/n).read_bytes()) for n in source};assert after==source,'SOURCE_CHANGED_DURING_TESTS'
failed=[x for x in cases if x['status'] in ['FAIL','ERROR']];blocked=[x for x in cases if x['status'].startswith('BLOCKED')];count=lambda status:sum(x['status']==status for x in cases)
report={'record_kind':'full_target_review_current_regression','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'python':sys.version,'sqlite':__import__('sqlite3').sqlite_version,'status':'FAILED' if failed else ('PASS_WITH_EXPLICIT_CAPABILITY_BLOCKERS' if blocked else 'PASS'),'tests_run':sum(x['tests_run'] for x in groups),'passed':count('PASS'),'skipped_platform':count('SKIP_PLATFORM'),'blocked_fixture':len(blocked),'cases':cases,'groups':groups,'source_sha256':source,'source_unchanged_during_tests':True,'measurements':sys.modules['test_review_fixes'].MEASUREMENTS,'native_window_captures':{'local_ui':sys.modules['test_ui'].CAPTURES,'draft_authoring':sys.modules['test_authoring'].CAPTURES},'elapsed_seconds':round(time.monotonic()-start,2),'production_or_full_release_accepted':False,'limitations':['Owned synthetic roots and fixtures only','Original Win1314 symlink cases remain blockers rather than PASS','Generated mapped UI events/captures are not physical human/a11y acceptance','No hardware/power-loss/real Bank/deploy/OS-privilege changes']}
name='REGRESSION_NATIVE.json' if os.name=='nt' else 'REGRESSION_LOCAL.json';(out/name).write_text(dump(report),encoding='utf-8');print('FINAL',json.dumps({k:report[k] for k in ['status','tests_run','passed','skipped_platform','blocked_fixture','elapsed_seconds','measurements']}),flush=True);sys.exit(1 if failed else 0)
