"""Current-source local/native evidence. This runner never opens a desktop window."""
from pathlib import Path
import argparse, hashlib, json, os, platform, sqlite3, sys, time, unittest, uuid
import object_authoring as o
import test_objects

class Evidence(unittest.TextTestResult):
    def __init__(self, *a, **kw): super().__init__(*a, **kw); self.cases = []
    def addSuccess(self, test): super().addSuccess(test); self.cases.append({'id': test.id(), 'status': 'PASS'})
    def addFailure(self, test, err): super().addFailure(test, err); self.cases.append({'id': test.id(), 'status': 'FAIL'})
    def addError(self, test, err): super().addError(test, err); self.cases.append({'id': test.id(), 'status': 'ERROR'})
    def addSkip(self, test, reason): super().addSkip(test, reason); self.cases.append({'id': test.id(), 'status': 'SKIP', 'reason': reason})

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--early', action='store_true'); args = parser.parse_args()
    names = [n for n in unittest.defaultTestLoader.getTestCaseNames(test_objects.Tests) if n.startswith('test_obj')]
    if args.early: names = [n for n in names if n.startswith(('test_obj02_', 'test_obj03_', 'test_obj07_', 'test_obj08_', 'test_obj09_'))]
    roots = ['object_authoring/runtime', 'first_bank', 'draft_authoring', 'local_command_adapter', 'package_producer', 'bank_read_api']
    files = [p for name in roots for p in (o.ROOT / 'EXPERIMENTS' / name).glob('*') if p.suffix in ['.py', '.json']]
    before = {p.relative_to(o.ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    suite = unittest.TestSuite(test_objects.Tests(n) for n in names); started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2, resultclass=Evidence).run(suite)
    after = {p.relative_to(o.ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    same_source = before == after
    report = {'record_kind': 'object_authoring_headless_evidence', 'at': o.a.utc(), 'stage': 'early_G1_G2' if args.early else 'full_object_headless',
      'platform': platform.platform(), 'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'success': result.wasSuccessful() and same_source,
      'tests_run': result.testsRun, 'skips': len(result.skipped), 'elapsed_seconds': round(time.monotonic()-started, 3), 'cases': result.cases,
      'source_sha256': before, 'same_source_throughout_run': same_source,
      'user_gui_accepted': False, 'actual_user_bank_changed': False, 'limitations': ['Owned synthetic inputs and roots', 'Manual GUI acceptance remains separate', 'Original reader Win1314 blockers remain', 'No full R1/research/release acceptance']}
    folder = Path(__file__).parent.parent / 'implementation' / 'evidence'; folder.mkdir(parents=True, exist_ok=True)
    path = folder / (('NATIVE' if os.name == 'nt' else 'LOCAL') + '_' + uuid.uuid4().hex + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'success': report['success'], 'tests_run': report['tests_run'], 'skips': report['skips'], 'report': str(path)}))
    return 0 if result.wasSuccessful() else 1
if __name__ == '__main__': sys.exit(main())
