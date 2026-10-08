"""Independent structural/authority review; not milestone or runtime acceptance."""
from pathlib import Path
import json,re,hashlib,collections,datetime
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda n:json.loads((R/n).read_bytes())
results=[]
def check(name,fn):
 try:detail=fn();results.append({'id':name,'status':'PASS','detail':detail})
 except Exception as e:results.append({'id':name,'status':'FAIL','detail':type(e).__name__+':'+str(e)})
req=load('DRAFT_NOTES/REQUIREMENTS_MAP.json');plan=load('PLANNING/REQUIREMENTS_RELEASE_MAP.json');rs={x['id']:x for x in req['requirements']};ps={x['requirement_id']:x for x in plan['requirements']};ms={x['id']:x for x in plan['milestones']}
def parity():
 assert len(rs)==len(req['requirements'])==115==len(ps)==len(plan['requirements']);assert rs.keys()==ps.keys()
 for k in rs:assert rs[k]['status']==ps[k]['classification'] and rs[k]['statement']==ps[k]['statement_snapshot'],k
 assert len([x for x in rs.values() if x['status']=='MVP_REQUIRED'])==11
 assert rs['OPP-017']['status']=='TARGET_REQUIRED' and ps['OPP-017']['slices'][-1]['milestone']=='R7'
 return {'requirements':115,'MVP':11,'OPP_017_preserved_TARGET':True}
check('C-01_REQUIREMENT_PARITY',parity)
def graphs():
 for fields in [('dependencies',),('dependencies','sequencing_after')]:
  seen=set();visiting=set()
  def visit(k):
   assert k in ms and k not in visiting,('unknown_or_cycle',k)
   if k in seen:return
   visiting.add(k)
   for f in fields:
    vals=ms[k].get(f) or [];vals=vals if isinstance(vals,list) else [vals]
    for v in vals:visit(v)
   visiting.remove(k);seen.add(k)
  for k in ms:visit(k)
 return {'milestones':len(ms),'dependency_and_sequence_DAG':True}
check('C-02_MILESTONE_DAGS',graphs)
def staging():
 expected=[('2.0.0-alpha.1',None),('2.0.0-alpha.2','0.1.0'),('2.0.0','0.2.0'),('2.0.1','1.0.0'),('2.1.0','1.1.0'),('2.2.0','1.2.0'),('2.3.0','1.3.0'),('2.4.0','1.4.0'),('2.5.0','1.5.0')]
 assert [(ms['R'+str(i)]['system_version'],ms['R'+str(i)]['application_version']) for i in range(9)]==expected
 assert plan['mvp_checkpoint']['milestone']=='R2' and set(plan['mvp_checkpoint']['required_ids'])=={k for k,v in rs.items() if v['status']=='MVP_REQUIRED'}
 for x in ps.values():
  for s in x.get('slices',[]):
   m=ms[s['milestone']];assert s['system_version']==m['system_version'] and s['application_version']==m['application_version']
   if x['classification']=='MVP_REQUIRED':assert int(s['milestone'][1:])<=2
 return {'R1_partial_R2_full_R3_stable':True,'later_TARGET_not_MVP':True}
check('C-03_VERSION_AND_MVP_BOUNDARIES',staging)
def inventory():
 tri=load('DRAFT_NOTES/BACKLOG_TRIAGE.json');prop=load('DRAFT_NOTES/NORMALIZATION_PROPOSALS.json');assert len(tri['items'])==159 and len(prop['entries'])==45
 ids=[x.get('proposal_id',x.get('id')) for x in prop['entries']];assert len(set(ids))==45
 return {'backlog_preserved':159,'proposal_records':45,'blanket_adoption':False}
check('C-04_BACKLOG_AND_PROPOSALS',inventory)
def cards():
 card=[];missing=[];badref=[];allowed=set(rs)|{x['id'] for x in plan['supplemental_planning_items']}
 for p in (R/'PLANNING/WORK_ITEMS').glob('*.json'):
  d=json.loads(p.read_bytes())
  if d.get('record_kind')!='vnext_development_work_item':continue
  card.append({'path':p.relative_to(R).as_posix(),'task_id':d['task_id'],'status':d['status']})
  for n in d.get('required_inputs',[]):
   if not (R/n).is_file():missing.append((p.name,n))
  for k in d.get('requirement_refs',[]):
   if k not in allowed:badref.append((p.name,k))
 assert not missing,missing;assert not badref,badref;assert len({c['task_id'] for c in card})==len(card)
 state=(R/'PLANNING/SESSION_STATE.md').read_text();ptr=re.findall(r'^CURRENT_WORK_ITEM: \[([^]]+)\]\(([^)]+)\)',state,re.M);assert len(ptr)==1;target=R/'PLANNING'/ptr[0][1];d=json.loads(target.read_bytes());assert d['status']=='prepared_after_independent_card_review'
 return {'cards':card,'one_current_pointer':ptr[0][1],'all_inputs_exist':True}
check('C-05_CARD_INPUTS_AND_AUTHORITY',cards)
def schema():
 d=load('PLANNING/CONTRACTS/BANK_SCHEMA_COMPATIBILITY.json');s=load('PLANNING/CONTRACTS/BANK_TYPES.schema.json');assert set(d['profiles']['R1']['write_types'])=={'Asset','Entity','Annotation','Collection'}
 assert set(d['profiles']['R1']['read_types'])==set(d['profiles']['R1']['write_types']);assert 'Source' in s['$defs'] and 'Source' not in d['profiles']['R1']['write_types']
 ddl=(R/'PLANNING/CONTRACTS/LOCAL_STORAGE_SCHEMA.sql').read_text();assert 'object_type TEXT NOT NULL,' in ddl and "object_type IN (" not in ddl
 return {'R1_four_types_Source_R2':True,'physical_metadata_not_closed_to_domain_enum':True,'full_R2_domain_compatibility':False}
check('C-06_EXTENSIBILITY_BOUNDARIES',schema)
def scenario():
 sce=load('PLANNING/SOLUTION_EVOLUTION_SCENARIO_2026-10-07.json');gold=(R/'DRAFT_NOTES/09_GOLDEN_SCENARIOS.md').read_text();assert 'GSU15' in gold
 for k,m in [('MVP-001','R1'),('MVP-005','R2'),('TGT-015','R4'),('TGT-020','R5'),('TGT-024','R7'),('TGT-007','R8')]:assert m in [s['milestone'] for s in ps[k]['slices']]
 return {'algorithm_theory_storage_R1_research_R2_counterevidence_R4_temporal_R5_packs_R7_Watch_R8':True,'actual_research_Watch_implemented':False}
check('C-07_TARGET_SCENARIO_TO_PLAN',scenario)
def decisions():
 d=load('PLANNING/USER_DECISIONS_BANK_SCOPE_2026-10-06_141538.json');assert len(d['decisions'])==3 and all(not x['blocking_user_answer'] for x in d['decisions'])
 cur=req['current_strategy']['user_scope_decision_checkpoint'];assert not cur['secret_use_planned'] and not cur['additional_AI_providers_currently_planned'] and not cur['PC_off_access_required_for_current_MVP'] and cur['ideas_and_analysis_may_be_nonpublic']
 udp=load('PLANNING/USER_DELIVERY_PRIORITY_2026-10-07.json');assert udp['decision_id']=='UDP-20261007-01'
 return {'three_answers_not_reopened':True,'no_all_ideas_public_inference':True,'current_chat_first_Bank_choice_additive_not_retroactive':True}
check('C-08_USER_INTENT_AND_TRIGGER_BOUNDARIES',decisions)
def scopes():
 for n in ['PLANNING/WORK_ITEMS/R1_DRAFT_AUTHORING_RECEIPT.json','PLANNING/WORK_ITEMS/R1_OBJECT_AUTHORING_CARD_REVIEW_RECEIPT.json']:
  d=load(n);assert d.get('release_acceptance') is False and d.get('production_runtime_acceptance') is False
 c=load('PLANNING/WORK_ITEMS/R1_OBJECT_AUTHORING.json');assert all(x['status']=='pending_runtime_implementation' for x in c['acceptance_checks']) and not c['new_editor_runtime_implemented']
 return {'component_completion_not_whole_release':True,'object_card_11_checks_pending':True}
check('C-09_COMPLETION_SCOPES',scopes)
def source():
 pf=load('EXPERIMENTS/full_target_review/20261008_033045/NATIVE_PREFLIGHT.json');assert not pf['prior_guard_drift'] and pf['prior_guard_count']==353 and pf['baseline_matches'] and pf['baseline_count']==264
 relevant=[]
 for n,v in pf['inventory'].items():
  if '/VERSION_PLAN_APPLY_HISTORY/' in n or '/WORKFLOW_APPLY_HISTORY/' in n or '/TEST_HISTORY/' in n or n.startswith('freelance_research_system_feature_architecture_red_tests/'):continue
  if n.startswith(('PLANNING/','DRAFT_NOTES/')) or (n.startswith('EXPERIMENTS/') and n.endswith(('.py','.sql')) and '/completed_work_review/' not in n):relevant.append(n);assert (R/n).is_file() and sha((R/n).read_bytes())==v['sha256'],n
 return {'authoritative_current_mirror_files':len(relevant),'fresh_native_prior_guard353_baseline264':True}
check('C-10_FRESH_SOURCE_IDENTITY',source)
ledger=load('DRAFT_NOTES/REVIEW/FINDINGS.json');byid={x['id']:x for x in ledger['findings']}
stale=[]
for k,now,evidence in [('RVP-001','Initial local-file transport and SQLite/BLOB backend selected; GitHub auxiliary, full topology not closed.','PLANNING/USER_DECISIONS_BANK_SCOPE_2026-10-06_141538.json / CONTRACTS/LOCAL_STORAGE_DECISION.md'),('RVP-002','R2 full MVP and R3 stable checkpoint explicitly mapped,115requirements staged.','PLANNING/REQUIREMENTS_RELEASE_MAP.json'),('FPR-20261006-U04','Indexed fields/extraction/oracle already defined and implemented in scoped native search; full release still open.','PLANNING/WORK_ITEMS/R1_LEXICAL_SEARCH_RECEIPT.json')]:
 x=byid[k];stale.append({'id':k,'current_classification':x.get('current_classification'),'last_recorded_status':x.get('review_status'),'actual_later_evidence':now,'evidence':evidence})
report={'record_kind':'full_target_review_document_checks','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':results,'success':all(x['status']=='PASS' for x in results),'observed_ledger_drift':stale,'release_acceptance':False,'limitations':['Structured parity does not prove all broad statements operationally covered. Goals/remainder assessed separately.','Historical reports/checkpoint hashes are snapshots; they are not required to equal later intentionally modified documents.','Source payloads/typed constraints and Windows guards need fresh runtime review as well.']}
(OUT/'DOCUMENT_CHECKS_LOCAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'success':report['success'],'checks':len(results),'failed':[x for x in results if x['status']!='PASS'],'stale_candidates':stale},ensure_ascii=False))
