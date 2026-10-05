#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from common import load_json, save_json
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--now'); args=ap.parse_args(); p=Path(args.project).resolve(); now=args.now or datetime.now(timezone.utc).isoformat()
rs=load_json(p/'RUN_STATE.json'); st=load_json(p/'STATE.json'); rs['status']='checkpointed'; rs['last_updated']=now; st['last_checkpoint']=now
save_json(p/'RUN_STATE.json',rs); save_json(p/'STATE.json',st)
hand={'schema_version':'1.0','system_version':'1.11.0','checkpointed_at':now,'next_use_case_id':rs.get('next_use_case_id'),'next_task_id':rs.get('next_task_id'),'next_question':rs.get('next_question'),'next_task_inputs':rs.get('next_task_inputs',[])}
save_json(p/'HANDOFF.json',hand); (p/'SESSION_CHECKPOINT.md').write_text(f"# Session Checkpoint\n\n- at: {now}\n- next use case: {hand['next_use_case_id']}\n- next task: {hand['next_task_id']}\n- next question: {hand['next_question']}\n",encoding='utf-8')
import subprocess,sys; subprocess.check_call([sys.executable,str(ROOT/'TOOLS/build_manifest.py'),str(p)])
print('CHECKPOINT OK')
