"""Affected headless regression only. Never creates a desktop window."""
from pathlib import Path
import argparse,hashlib,importlib,json,os,platform,sys,time,unittest,uuid
import runtime
ROOT=runtime.ROOT
class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[]
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'id':test.id(),'status':'PASS'})
    def addError(self,test,err):super().addError(test,err);self.cases.append({'id':test.id(),'status':'ERROR'})
    def addFailure(self,test,err):super().addFailure(test,err);self.cases.append({'id':test.id(),'status':'FAIL'})
    def addSkip(self,test,reason):super().addSkip(test,reason);self.cases.append({'id':test.id(),'status':'SKIP','reason':reason})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--integration-only',action='store_true');parser.add_argument('--case',action='append');args=parser.parse_args()
    modules=[('first_bank','test_first_bank')]
    if not args.integration_only and not args.case:modules += [('draft_authoring','test_authoring'),('local_ui','test_ui'),('local_command_adapter','test_commands'),('bank_read_api','test_reads'),('lexical_search','test_search')]
    suite=unittest.TestSuite()
    for folder,name in modules:
        sys.path.insert(0,str(ROOT/'EXPERIMENTS'/folder));m=importlib.import_module(name);suite.addTests([m.Tests(n) for n in args.case] if args.case else unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
    started=time.monotonic();result=unittest.TextTestRunner(verbosity=1,resultclass=Evidence).run(suite)
    files=[]
    for folder in ['first_bank','draft_authoring','local_command_adapter','bank_read_api']:
        files.extend(x for x in (ROOT/'EXPERIMENTS'/folder).iterdir() if x.suffix in ['.py','.json'] and x.name not in ['ISSUES.json','LOCAL_RESULTS.json','NATIVE_RESULTS.json'])
    report={'record_kind':'first_bank_headless_runtime_evidence','at':runtime.im.now(),'platform':platform.platform(),'python':sys.version,'sqlite':runtime.sqlite3.sqlite_version,'elapsed_seconds':round(time.monotonic()-started,3),'success':result.wasSuccessful(),'tests_run':result.testsRun,'skips':len(result.skipped),'cases':result.cases,'source_sha256':{x.relative_to(ROOT).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in files},'limitations':['Owned synthetic roots only; actual config and user visual acceptance separate','No main desktop window created or automated','Original native secure reader symlink blockers not overridden','No full R1/research/provider/hardware/restore/release acceptance']}
    folder=Path(__file__).parent/'evidence';folder.mkdir(exist_ok=True);path=folder/(('NATIVE' if os.name=='nt' else 'LOCAL')+'_'+uuid.uuid4().hex+'.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'success':report['success'],'tests_run':report['tests_run'],'skips':report['skips'],'report':str(path)}));return 0 if result.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
