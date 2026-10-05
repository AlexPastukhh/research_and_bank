#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter
import argparse,json
ROOT=Path(__file__).resolve().parents[1]

def classify(root, ref):
    p=root/ref
    if p.exists():
        if ref.startswith('METHOD/'): return 'method'
        if ref.startswith('TOOLS/'): return 'tool'
        if ref.startswith('CORE/SCHEMAS/'): return 'schema'
        if ref.startswith('CORE/'): return 'core_contract'
        if ref.startswith('AUDIT/'): return 'audit'
        if ref.startswith('REFERENCE/'): return 'reference'
        return 'system_file'
    if ref.endswith(('.json','.jsonl')) or any(x in ref.lower() for x in ['registry','ledger']) or ref in {'RawTasks','Measurements','ClaimLedger','OpportunityEconomics','SourceInbox','ApplicationsTests','PracticalTests'}:
        return 'project_runtime_artifact'
    return 'logical_capability'

def load_phase_records():
    out={}
    for p in sorted((ROOT/'AUDIT/PHASE_EXECUTION_RECORDS').glob('PHASE*_EXECUTION_RECORD.json')):
        r=json.loads(p.read_text(encoding='utf-8')); out[r['phase']]=r
    return out

def qstats(rec):
    qs=rec.get('pre_execution_questions',[])+rec.get('emergent_questions',[])
    amap={a['question_id']:a for a in rec.get('post_execution_answers',[])}
    answered=sum(1 for q in qs if q['id'] in amap and amap[q['id']].get('status') in ('answered','not_applicable'))
    unresolved=sum(1 for q in qs if q.get('blocking') and (q['id'] not in amap or amap[q['id']].get('status') not in ('answered','not_applicable')))
    return len(qs),answered,unresolved

def build():
    spec=json.loads((ROOT/'CORE/SYSTEM_SPEC.json').read_text())
    ucr=json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text())
    gpr=json.loads((ROOT/'CORE/GOLDEN_PATH_REGISTRY.json').read_text())
    axes=json.loads((ROOT/'AUDIT/AUDIT_AXES.json').read_text())
    budget=json.loads((ROOT/'CORE/ARCHITECTURE_BUDGET.json').read_text())
    ms=json.loads((ROOT/'CORE/SYSTEM_MAP_SPEC.json').read_text())
    products=json.loads((ROOT/'CORE/RESULT_PRODUCT_CONTRACTS.json').read_text())
    stage=json.loads((ROOT/'STAGE_STATUS.json').read_text())
    phase_records=load_phase_records()
    nodes={}; edges=[]
    def node(i,**kw): nodes.setdefault(i,{'id':i}).update({k:v for k,v in kw.items() if v is not None})
    node('SYSTEM',type='system',label='Freelance Opportunity Research System',version=spec['system_version'],layer='root')
    for role,rel in spec.get('canonical_artifacts',{}).items():
        node(rel,type='canonical_artifact',label=rel,role=role,layer='control_plane',exists=(True if rel in ms.get('outputs',[]) else (ROOT/rel).exists())); edges.append({'from':'SYSTEM','to':rel,'type':'owns','label':role})
    for u in ucr['use_cases']:
        uid=u['id']; node(uid,type='use_case',label=f"{uid} {u['name']}",group=u['group'],interaction_type=u['interaction_type'],execution_owner=u['execution_owner'],action_class=u['action_class'],layer='use_case_control')
        edges.append({'from':'CORE/USE_CASE_REGISTRY.json','to':uid,'type':'declares'})
        node(u['workflow'],type='workflow',label=u['workflow'],layer='workflow',exists=(ROOT/u['workflow']).exists()); edges.append({'from':uid,'to':u['workflow'],'type':'procedure'})
        for ref in u['reads']: node(ref,type=classify(ROOT,ref),label=ref,layer='dependency'); edges.append({'from':uid,'to':ref,'type':'reads'})
        for ref in u['writes']: node(ref,type=classify(ROOT,ref),label=ref,layer='runtime_data'); edges.append({'from':uid,'to':ref,'type':'writes'})
        for ref in u['capabilities']: node(ref,type=classify(ROOT,ref),label=ref,layer='capabilities'); edges.append({'from':uid,'to':ref,'type':'uses_capability'})
        for tr in u['transitions']:
            if tr.get('to'): edges.append({'from':uid,'to':tr['to'],'type':'transition','label':tr['outcome']})
    for pname,pdef in products['products'].items():
        node('RESULT:'+pname,type='result_product_contract',label=pname,layer='result_contracts',status=products.get('implementation_status','contract_only'),purpose=pdef.get('purpose'))
        edges.append({'from':'CORE/RESULT_PRODUCT_CONTRACTS.json','to':'RESULT:'+pname,'type':'declares'})
    for u in ucr['use_cases']:
        if u.get('interaction_type')=='query':
            for out in u.get('outputs',[]):
                if out.get('type') in products['products']: edges.append({'from':u['id'],'to':'RESULT:'+out['type'],'type':'returns'})
    for gp in gpr['paths']:
        gid=gp['id']; node(gid,type='golden_path',label=f"{gid} {gp['name']}",layer='assurance',release_gate=gp.get('release_gate')); edges.append({'from':'CORE/GOLDEN_PATH_REGISTRY.json','to':gid,'type':'declares'})
        prev=gid
        for i,uid in enumerate(gp['expected_use_case_sequence']): edges.append({'from':prev,'to':uid,'type':'golden_step','label':str(i+1)}); prev=uid
    for a in axes['axes']:
        node(a['id'],type='audit_axis',label=f"{a['id']} {a['name']}",layer='assurance',release_gate=a.get('release_gate')); edges.append({'from':'AUDIT/AUDIT_AXES.json','to':a['id'],'type':'declares'})
    for ph in stage.get('phases',[]):
        rec=phase_records.get(ph['phase'],{}); total,answered,unresolved=qstats(rec)
        pid=f"PHASE:{ph['phase']}"; node(pid,type='development_phase',label=f"Phase {ph['phase']} — {ph['name']}",layer='development_status',status=ph['status'],acceptance_review=ph.get('acceptance_review'),question_record=ph.get('question_record'),questions=total,answered_questions=answered,unresolved_blocking_questions=unresolved); edges.append({'from':'SYSTEM','to':pid,'type':'development_status','label':ph['status']})
        if ph.get('question_record'):
            qid=f"PHASEQA:{ph['phase']}"; node(qid,type='phase_execution_record',label=f"Phase {ph['phase']} Questions & Answers",layer='assurance',record=ph['question_record'],capture_mode=rec.get('question_capture_mode'),questions=total,answered=answered,unresolved_blocking=unresolved); edges.append({'from':pid,'to':qid,'type':'records_questions'})
    planned=ms.get('planned_overlay',{}); proj=planned.get('result_projection_layer',{})
    if proj:
        node('PLANNED:ResultProjectionLayer',type='logical_capability',label='Result Projection Layer',layer='planned_result_projection',status=proj.get('status','planned'))
        for prod in proj.get('products',[]):
            if 'RESULT:'+prod in nodes: edges.append({'from':'PLANNED:ResultProjectionLayer','to':'RESULT:'+prod,'type':'produces'})
    for s in planned.get('ui_surfaces',[]):
        sid='UI:'+s['name']; node(sid,type='ui_surface',label=s['name'],layer='planned_ui',status='prototype_requirement')
        for q in s.get('query_use_cases',[]): edges.append({'from':sid,'to':q,'type':'invokes'})
        for c in s.get('command_actions',[]): edges.append({'from':sid,'to':c,'type':'invokes'})
    graph={'generated_from_system_version':spec['system_version'],'acceptance_model_version':stage.get('acceptance_model_version'),'development_status':stage,'use_case_registry_version':ucr['registry_version'],'use_case_contract_version':ucr.get('contract_version'),'golden_path_registry_version':gpr['registry_version'],'system_map_version':ms['system_map_version'],'architecture_budget':budget,'nodes':sorted(nodes.values(),key=lambda x:x['id']),'edges':edges}
    return graph,ucr,gpr,axes,ms,phase_records

def render_files():
    graph,ucr,gpr,axes,ms,phase_records=build(); stage=graph['development_status']; groups=Counter(u['group'] for u in ucr['use_cases']); interactions=Counter(u['interaction_type'] for u in ucr['use_cases']); owners=Counter(u['execution_owner'] for u in ucr['use_cases'])
    mermaid=f'''flowchart TB\n  USER[User / Agent / Future UI]\n  ROUTER[Use Case Registry\\n{len(ucr['use_cases'])} implemented UCs]\n  COMMAND[Command UCs]\n  ORCH[Orchestration UCs]\n  DATA[State + append-only truth]\n  PROJ[PLANNED Result Projection Layer]\n  QUERY[Implemented Query UCs\\nUC21-UC25]\n  UI[Prototype UI surfaces]\n  ASSURE[AX01-AX26 + Golden Paths + Acceptance Q&A + Map parity]\n  USER --> ROUTER\n  ROUTER --> COMMAND\n  ROUTER --> ORCH\n  COMMAND --> DATA\n  ORCH --> DATA\n  DATA --> PROJ\n  PROJ --> QUERY\n  QUERY --> UI\n  QUERY --> USER\n  UI --> COMMAND\n  ASSURE -. validates .-> ROUTER\n  ASSURE -. validates .-> DATA\n  ASSURE -. validates .-> QUERY\n'''
    lines=['# System Map — current implementation + planned result/query overlay','',f"Generated from system **{graph['generated_from_system_version']}**, Use Case Registry **{ucr['registry_version']}**, contract **{ucr.get('contract_version')}**, Golden Path Registry **{gpr['registry_version']}**, acceptance model **{graph.get('acceptance_model_version')}**.",'','## 1. High-level architecture','','```mermaid',mermaid.rstrip(),'```','','## 2. Implemented use-case topology','',f"Implemented UCs: **{len(ucr['use_cases'])}**. Groups: "+', '.join(f'`{k}`={v}' for k,v in sorted(groups.items()))+'. Interactions: '+', '.join(f'`{k}`={v}' for k,v in sorted(interactions.items()))+'. Execution owners: '+', '.join(f'`{k}`={v}' for k,v in sorted(owners.items()))+'.','', '| UC | Group | Interaction | Execution owner | Inputs | Outputs | Reads | Writes | Capabilities | Next |','|---|---|---|---|---:|---:|---:|---:|---:|---|']
    for u in ucr['use_cases']:
        targets=sorted({t['to'] for t in u['transitions'] if t.get('to')}); lines.append(f"| {u['id']} {u['name']} | {u['group']} | {u['interaction_type']} | `{u['execution_owner']}` | {len(u['inputs'])} | {len(u['outputs'])} | {len(u['reads'])} | {len(u['writes'])} | {len(u['capabilities'])} | {', '.join(targets) or 'terminal'} |")
    lines += ['','## 3. Current Golden Paths','']+[f"- **{p['id']} {p['name']}**: `"+' → '.join(p['expected_use_case_sequence'])+'`' for p in gpr['paths']]
    lines += ['','## 4. Result/query plane','','UC21–UC25 are implemented as **read-only query contracts** in Phase 2. Their typed result-product contracts exist, while projection/build execution remains planned for Phase 3.','']
    for u in ucr['use_cases']:
        if u.get('interaction_type')=='query': lines.append(f"- `{u['id']} {u['name']}` → `{u['outputs'][0]['type']}`; writes={len(u['writes'])}; UI: {', '.join(u['ui_surfaces']) or '—'}")
    lines += ['','Projection backend status: `'+ms['planned_overlay']['result_projection_layer']['status']+'`.','','## 5. UI composition overlay','']
    for s in ms['planned_overlay']['ui_surfaces']: lines.append(f"- **{s['name']}** → queries {', '.join(s['query_use_cases']) or '—'}; command actions {', '.join(s['command_actions']) or '—'}")
    lines += ['','## 6. Assurance and map maintenance','',f"- Audit axes: **{len(axes['axes'])}** (`AX01–AX26`).",f"- Golden Paths: **{len(gpr['paths'])}**.",'- Acceptance uses explicit phase criteria **plus** pre-execution/emergent questions and post-execution answers.','- `REFERENCE/SYSTEM_MAP.*` and `REFERENCE/PHASE_ACCEPTANCE_QA.md` are generated views, never independent contracts.','- AX20/AX24 fail if regeneration differs from committed generated views.','','## 7. Phase acceptance questions & answers','',f"Acceptance model: **{stage.get('acceptance_model_version','unknown')}**. Canonical records: `AUDIT/PHASE_EXECUTION_RECORDS/`. Generated view: `REFERENCE/PHASE_ACCEPTANCE_QA.md`.",'','| Phase | Status | Questions | Answered | Unresolved blocking |','|---:|---|---:|---:|---:|']
    for ph in stage.get('phases',[]):
        total,answered,unresolved=qstats(phase_records.get(ph['phase'],{})); lines.append(f"| {ph['phase']} | {ph['status']} | {total} | {answered} | {unresolved} |")
    lines += ['','## 8. Development plan','','See `REFERENCE/DEVELOPMENT_PLAN_vNext.md`. Phase 2 implements UC21–UC25 query contracts and command/query boundaries. Phase 3 questions are already captured prospectively; result projection builders remain planned.','']
    return {'REFERENCE/SYSTEM_MAP.json':json.dumps(graph,ensure_ascii=False,indent=2)+'\n','REFERENCE/SYSTEM_MAP.mmd':mermaid,'REFERENCE/SYSTEM_MAP.md':'\n'.join(lines)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); files=render_files(); bad=[]
    for rel,text in files.items():
        p=ROOT/rel
        if a.check:
            if not p.exists() or p.read_text(encoding='utf-8')!=text: bad.append(rel)
        else: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')
    if bad: print('SYSTEM MAP PARITY: FAIL — '+', '.join(bad)); return 1
    print('SYSTEM MAP PARITY: OK' if a.check else 'SYSTEM MAP GENERATED'); return 0
if __name__=='__main__': raise SystemExit(main())
