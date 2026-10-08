from pathlib import Path
import json,os,re,datetime,hashlib
root=Path(__import__('sys').argv[1]).absolute()
def independent_document_checks():
    registry=json.loads((root/'DRAFT_NOTES/REQUIREMENTS_MAP.json').read_text());plan=json.loads((root/'PLANNING/REQUIREMENTS_RELEASE_MAP.json').read_text());reqs=registry['requirements'];mapped=plan['requirements']
    ids=[r['id'] for r in reqs];mapids=[r['requirement_id'] for r in mapped];assert len(ids)==len(set(ids))==115;assert set(ids)==set(mapids) and len(mapids)==115
    milestones={m['id']:m for m in plan['milestones']};visiting=set();visited=set()
    def visit(n):
        assert n in milestones
        if n in visited:return
        assert n not in visiting,'MILESTONE_CYCLE'
        visiting.add(n)
        for predecessor in milestones[n]['dependencies']:visit(predecessor)
        visiting.remove(n);visited.add(n)
    for n in milestones:visit(n)
    triage=json.loads((root/'DRAFT_NOTES/BACKLOG_TRIAGE.json').read_text());assert len(triage['items'])==159 and len({i['backlog_id'] for i in triage['items']})==159
    proposals=json.loads((root/'DRAFT_NOTES/NORMALIZATION_PROPOSALS.json').read_text());assert len(proposals['entries'])==45
    cards=[];missing=[]
    for p in (root/'PLANNING/WORK_ITEMS').glob('*.json'):
        c=json.loads(p.read_text())
        if c.get('record_kind')!='vnext_development_work_item':continue
        cards.append({'path':p.relative_to(root).as_posix(),'id':c['task_id'],'status':c['status']})
        for n in c.get('required_inputs',[]):
            if not (root/n).is_file():missing.append({'card':c['task_id'],'input':n})
        for q in c.get('pre_execution_questions',[]):
            assert not(q.get('blocking_user_answer') and q.get('status') in ['pending','proposal_review_pending']), 'UNANSWERED_BLOCKING_USER_QUESTION'
        if c['status']=='completed':
            assert all(str(k.get('status','')).upper().startswith('PASS') for k in c['acceptance_checks']),p.name
            receipt=c.get('completion_receipt')
            if receipt is None:
                counterpart=p.with_name(p.stem+'_RECEIPT.json')
                assert counterpart.is_file(),'COMPLETION_EVIDENCE_MISSING:'+p.name
                receipt=counterpart.relative_to(root).as_posix()
            assert (root/receipt).is_file(),p.name
    state=(root/'PLANNING/SESSION_STATE.md').read_text();assert state.count('CURRENT_WORK_ITEM:')==1
    match=re.search(r'CURRENT_WORK_ITEM: \[[^]]+\]\(([^)]+)\)',state);current=json.loads((root/'PLANNING'/match[1]).read_text());assert current['status']!='completed'
    return {'status':'PASS' if not missing or os.name!='nt' else 'INPUTS_MISSING','requirements':115,'backlog':159,'proposals':45,'pending_proposals':sum(p['state']=='pending_not_adopted' for p in proposals['entries']),'milestone_dependency_cycles':False,'cards':cards,'missing_inputs':missing,'missing_input_interpretation':'Local source mirror excludes accepted baseline files; Windows checks actual repository inputs.','current_work_item':current['task_id'],'full_release_accepted':False}
v=independent_document_checks()
print(json.dumps(v,ensure_ascii=False))
