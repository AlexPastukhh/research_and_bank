#!/usr/bin/env python3
import argparse, shutil, zipfile, tempfile, json, sys
from pathlib import Path
from common import load_json, save_json
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('-o','--output',required=True); ap.add_argument('inputs',nargs='+'); args=ap.parse_args(); out=Path(args.output).resolve()
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True); baseline=out/'BASELINE'; baseline.mkdir(); inventory=[]
for raw in args.inputs:
    p=Path(raw).resolve()
    if p.is_dir():
        dst=baseline/p.name; shutil.copytree(p,dst); inventory.append({'input':str(p),'type':'directory','stored':str(dst.relative_to(out))})
    elif zipfile.is_zipfile(p):
        dst=baseline/(p.stem+'_unzipped'); dst.mkdir();
        with zipfile.ZipFile(p) as z: z.extractall(dst)
        inventory.append({'input':str(p),'type':'zip','stored':str(dst.relative_to(out))})
    else:
        dst=baseline/p.name; shutil.copy2(p,dst); inventory.append({'input':str(p),'type':'file','stored':str(dst.relative_to(out))})
# initialize cycle project directly from templates
subprocess=None
import subprocess as sp
sp.check_call([sys.executable,str(ROOT/'TOOLS/init_project.py'),str(out/'PROJECT'),'continuation-cycle'])
# set route to UC02
rs=load_json(out/'PROJECT/RUN_STATE.json'); rs['next_use_case_id']='UC02'; rs['next_task_id']='BOOT-01'; rs['next_question']='Reconstruct the supplied baseline and build a minimal DeltaPlan.'; rs['next_task_inputs']=[x['stored'] for x in inventory]; save_json(out/'PROJECT/RUN_STATE.json',rs)
(out/'INVENTORY.json').write_text(json.dumps({'inputs':inventory},indent=2)+'\n')
print(f'BOOTSTRAP OK {out}')
