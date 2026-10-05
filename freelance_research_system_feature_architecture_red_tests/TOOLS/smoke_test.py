#!/usr/bin/env python3
import tempfile,subprocess,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
 p=subprocess.run([sys.executable,*map(str,a)],capture_output=True,text=True)
 if p.returncode: raise SystemExit(p.stdout+'\n'+p.stderr)
 return p
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'p'; run(ROOT/'TOOLS/init_project.py',p,'smoke'); run(ROOT/'TOOLS/validate_project.py',p)
 run(ROOT/'TOOLS/start_daily_run.py',p,'--run-id','r1','--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','a','--now','2026-10-01T00:00:00+00:00')
 run(ROOT/'TOOLS/record_observation.py',p,'--entity-id','e1','--canonical-key','k','--class','seen','--state','active','--source-id','src','--payload-json','{"v":1}','--now','2026-10-01T00:01:00+00:00')
 run(ROOT/'TOOLS/finish_daily_run.py',p,'--coverage','complete','--now','2026-10-01T01:00:00+00:00'); run(ROOT/'TOOLS/checkpoint_project.py',p,'--now','2026-10-01T02:00:00+00:00'); run(ROOT/'TOOLS/validate_project.py',p)
print('SMOKE TEST: OK')
