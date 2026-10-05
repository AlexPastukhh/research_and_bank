import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PhaseRecordTests(unittest.TestCase):
    def test_phase_records_validate(self):
        p=subprocess.run([sys.executable,str(ROOT/'TOOLS/validate_phase_records.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+'\n'+p.stderr)
    def test_phase_qa_view_parity(self):
        p=subprocess.run([sys.executable,str(ROOT/'TOOLS/generate_phase_qa_view.py'),'--check'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+'\n'+p.stderr)
if __name__=='__main__': unittest.main()
