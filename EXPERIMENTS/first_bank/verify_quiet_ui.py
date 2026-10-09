"""Focused UI regressions; no visible desktop window is opened."""
from pathlib import Path
import hashlib,json,os,platform,sys,time,unittest,uuid
import runtime,test_quiet_ui,test_first_bank
from verify import Evidence

def main():
    paths=['EXPERIMENTS/first_bank/'+n for n in ['app.py','integration.py','runtime.py','test_quiet_ui.py','verify_quiet_ui.py','test_first_bank.py']]
    paths+=['EXPERIMENTS/object_authoring/runtime/'+n for n in ['object_ui.py','object_model.py','object_authoring.py']]
    paths+=['EXPERIMENTS/draft_authoring/'+n for n in ['authoring_ui.py','authoring_presenter.py']]
    def hashes():return {n:hashlib.sha256((runtime.ROOT/n).read_bytes()).hexdigest() for n in paths}
    before=hashes();suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_quiet_ui.Tests)
    if os.name=='nt':suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test_quiet_ui.NativeLayout))
    names=['test_10_observer_second_process_and_pinned_selection','test_11_busy_disconnect_stale_generation_decrease_close','test_12_single_worker_visible_rebuild_then_search_readonly','test_22_index_recovery_clears_only_owned_error_notice']
    suite.addTests(test_first_bank.Tests(n) for n in names)
    start=time.monotonic();result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(suite);after=hashes()
    report={'record_kind':'quiet_bank_ui_focused_evidence','at':runtime.im.now(),'platform':platform.platform(),'python':sys.version,'tests_run':result.testsRun,'success':result.wasSuccessful() and before==after,'skips':len(result.skipped),'elapsed_seconds':round(time.monotonic()-start,3),'same_source_throughout_run':before==after,'source_sha256':before,'cases':result.cases,'limitations':['No main desktop window opened or automated','Native layout checks use an owned withdrawn Tk window; visible layout and flicker require user confirmation','No user Bank/config/cache is modified by tests','Full FUB10 and OBJ10/OBJ11 acceptance remains pending']}
    folder=Path(__file__).parent/'rechecks/20261009_flicker/evidence';folder.mkdir(parents=True,exist_ok=True);p=folder/(('NATIVE' if os.name=='nt' else 'LOCAL')+'_'+uuid.uuid4().hex+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'success':report['success'],'tests_run':result.testsRun,'skips':report['skips'],'report':str(p)}));return 0 if report['success'] else 1
if __name__=='__main__':sys.exit(main())
