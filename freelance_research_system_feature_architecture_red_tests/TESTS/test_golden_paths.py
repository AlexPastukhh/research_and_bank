import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class GoldenPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=json.loads((ROOT/'CORE/GOLDEN_PATH_REGISTRY.json').read_text(encoding='utf-8'))
    def test_registry_ids_and_files(self):
        ids=[x['id'] for x in self.reg['paths']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(ids,[f'GP{i:02d}' for i in range(1,7)])
        for x in self.reg['paths']:
            self.assertTrue((ROOT/x['workflow']).exists())
            self.assertTrue(x['expected_use_case_sequence'])
            self.assertTrue(x['assertions'])
    def test_release_gate_paths_execute(self):
        p=subprocess.run([sys.executable,str(ROOT/'TOOLS/run_golden_paths.py'),'--json'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+'\n'+p.stderr)
        data=json.loads(p.stdout); self.assertEqual(data['failed'],0); self.assertEqual(data['passed'],6)
if __name__=='__main__': unittest.main()
