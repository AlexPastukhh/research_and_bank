#!/usr/bin/env python3
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'REFERENCE/PHASE_ACCEPTANCE_QA.md'

def render():
    stage=json.loads((ROOT/'STAGE_STATUS.json').read_text(encoding='utf-8'))
    lines=['# Phase Acceptance — Questions & Answers','',
           'This is a generated human view. Canonical question/answer records live under `AUDIT/PHASE_EXECUTION_RECORDS/`. Questions are captured before execution (or explicitly marked retrospective for completed legacy phases); answers are added after implementation and before acceptance.','',
           '| Phase | Status | Capture | Questions | Answered | Unresolved blocking | Record |','|---:|---|---|---:|---:|---:|---|']
    recs=[]
    for ph in stage['phases']:
        p=ROOT/ph['question_record']; rec=json.loads(p.read_text(encoding='utf-8')); recs.append(rec)
        qs=rec['pre_execution_questions']+rec['emergent_questions']; amap={a['question_id']:a for a in rec['post_execution_answers']}
        answered=sum(1 for q in qs if q['id'] in amap and amap[q['id']]['status'] in ('answered','not_applicable'))
        unresolved=sum(1 for q in qs if q['blocking'] and (q['id'] not in amap or amap[q['id']]['status'] not in ('answered','not_applicable')))
        lines.append(f"| {rec['phase']} | {rec['lifecycle_status']} | {rec['question_capture_mode']} | {len(qs)} | {answered} | {unresolved} | `{ph['question_record']}` |")
    for rec in recs:
        lines += ['',f"## Phase {rec['phase']} — {rec['phase_name']}",'',f"Status: **{rec['lifecycle_status']}**. Capture: `{rec['question_capture_mode']}`.",'']
        amap={a['question_id']:a for a in rec['post_execution_answers']}
        allq=rec['pre_execution_questions']+rec['emergent_questions']
        for q in allq:
            origin='pre-execution' if q['origin']=='pre_execution_planning' else q['origin'].replace('_',' ')
            lines += [f"### {q['id']} — {q['question']}",'',f"- Why it mattered: {q['why_it_matters']}",f"- Blocking: **{'yes' if q['blocking'] else 'no'}**",f"- Origin: `{origin}`"]
            ans=amap.get(q['id'])
            if ans:
                lines += [f"- Answer status: **{ans['status']}**",f"- Answer: {ans['answer']}",f"- Decision: {ans['decision']}",f"- Acceptance impact: {ans['acceptance_impact']}",f"- Evidence: "+(', '.join(f'`{x}`' for x in ans['evidence_refs']) if ans['evidence_refs'] else '—')]
            else:
                lines += ['- Answer status: **pending**','- Answer: —','- Decision: —','- Acceptance impact: unresolved until execution/acceptance']
            lines.append('')
        if rec.get('acceptance_link'):
            lines.append(f"Acceptance review: `{rec['acceptance_link']}`")
    return '\n'.join(lines).rstrip()+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); text=render()
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8')!=text:
            print('PHASE Q&A VIEW PARITY: FAIL'); return 1
        print('PHASE Q&A VIEW PARITY: OK'); return 0
    OUT.write_text(text,encoding='utf-8'); print('PHASE Q&A VIEW GENERATED'); return 0
if __name__=='__main__': raise SystemExit(main())
