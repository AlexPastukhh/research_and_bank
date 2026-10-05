#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
try:
    import jsonschema
except Exception as e:
    print('PHASE Q&A VALIDATION: FAIL — jsonschema unavailable:',e); raise SystemExit(1)

schema=json.loads((ROOT/'CORE/SCHEMAS/PHASE_EXECUTION_RECORD_SCHEMA.json').read_text(encoding='utf-8'))
stage=json.loads((ROOT/'STAGE_STATUS.json').read_text(encoding='utf-8'))
plan=(ROOT/'REFERENCE/DEVELOPMENT_PLAN_vNext.md').read_text(encoding='utf-8')
records={}
for p in sorted((ROOT/'AUDIT/PHASE_EXECUTION_RECORDS').glob('PHASE*_EXECUTION_RECORD.json')):
    rec=json.loads(p.read_text(encoding='utf-8'))
    try: jsonschema.Draft202012Validator(schema).validate(rec)
    except Exception as e: errors.append(f'{p.relative_to(ROOT)} schema: {e}'); continue
    ph=rec['phase']
    if ph in records: errors.append(f'duplicate phase record {ph}')
    records[ph]=rec
    qlist=rec['pre_execution_questions']+rec['emergent_questions']
    qids=[q['id'] for q in qlist]
    if len(qids)!=len(set(qids)): errors.append(f'phase {ph}: duplicate question IDs')
    amap={a['question_id']:a for a in rec['post_execution_answers']}
    if len(amap)!=len(rec['post_execution_answers']): errors.append(f'phase {ph}: duplicate answers')
    unknown=sorted(set(amap)-set(qids))
    if unknown: errors.append(f'phase {ph}: answers for unknown questions {unknown}')
    # Plan must visibly carry every question ID and exact question text.
    for q in qlist:
        marker=f"**{q['id']}** — {q['question']}"
        if marker not in plan: errors.append(f'phase {ph}: plan missing question {q["id"]}')
    # Accepted phases require answers to all blocking questions, and evidence for answered blocking questions.
    if rec['lifecycle_status']=='accepted':
        for q in qlist:
            if not q['blocking']: continue
            ans=amap.get(q['id'])
            if not ans: errors.append(f'phase {ph}: accepted with unanswered blocking {q["id"]}'); continue
            if ans['status'] not in ('answered','not_applicable'): errors.append(f'phase {ph}: blocking {q["id"]} status={ans["status"]}')
            if ans['status']=='answered' and not ans['evidence_refs']: errors.append(f'phase {ph}: blocking {q["id"]} lacks evidence')
            for ref in ans.get('evidence_refs',[]):
                # Allow logical directory refs (e.g. USE_CASES), otherwise require path existence.
                if '/' in ref or '.' in Path(ref).name:
                    if not (ROOT/ref).exists(): errors.append(f'phase {ph}: evidence ref missing {ref}')
    # Planned phases should have prospective questions before implementation and no fabricated answers.
    if rec['lifecycle_status']=='planned':
        if rec['question_capture_mode']!='prospective': errors.append(f'phase {ph}: planned record must be prospective')
        if not rec['pre_execution_questions']: errors.append(f'phase {ph}: planned phase has no pre-execution questions')
        if rec['post_execution_answers']: errors.append(f'phase {ph}: planned phase already has post-execution answers')

for ph in stage.get('phases',[]):
    n=ph['phase']
    if n not in records: errors.append(f'missing phase execution record {n}')
    else:
        rec=records[n]
        if rec['phase_name']!=ph['name']: errors.append(f'phase {n}: name mismatch with STAGE_STATUS')
        if rec['lifecycle_status']!=ph['status']: errors.append(f'phase {n}: status mismatch record={rec["lifecycle_status"]} stage={ph["status"]}')
        expected=f'AUDIT/PHASE_EXECUTION_RECORDS/PHASE{n}_EXECUTION_RECORD.json'
        if ph.get('question_record')!=expected: errors.append(f'phase {n}: STAGE_STATUS question_record mismatch')

if errors:
    print('PHASE Q&A VALIDATION: FAIL')
    for e in errors: print('-',e)
    raise SystemExit(1)
print(f'PHASE Q&A VALIDATION: OK — {len(records)} phase records; accepted phases have no unresolved blocking questions')
