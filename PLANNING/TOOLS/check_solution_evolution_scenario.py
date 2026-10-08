"""Independent synthetic domain conformance; not a Bank/runtime/research acceptance."""
from pathlib import Path
import argparse,base64,copy,hashlib,importlib.util,json
def run(root):
 p=root/'PLANNING/TOOLS/check_bank_contracts.py';spec=importlib.util.spec_from_file_location('scenario_bank_contracts',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 fixture=json.loads((root/'PLANNING/SCENARIOS/SOLUTION_EVOLUTION_FIXTURE.json').read_text(encoding='utf-8'))
 initial=fixture['initial'];new=fixture['recheck'];cases=[]
 def case(name,action):action();cases.append({'id':name,'observed':'PASS'})
 def reject(docs,code,accepted=()):
  try:m.validate_documents(docs,accepted=accepted)
  except m.ContractError as e:assert str(e)==code,(code,str(e))
  else:raise AssertionError('EXPECTED_REJECTION:'+code)
 def domains():
  m.validate_documents(initial);assert {d['data']['entity_kind'] for d in initial if d['object_type']=='Entity'}=={'problem','algorithm','theory'}
 case('SE1_GENERIC_PROBLEM_ALGORITHM_THEORY',domains)
 def originals():
  for d in [*initial,*new]:
   if d['object_type']=='Asset':
    s=d['data']['storage'];b=base64.b64decode(fixture['original_payloads_base64'][s['file_path']]);assert len(b)==s['byte_length'] and hashlib.sha256(b).hexdigest()==s['sha256']
 case('SE2_EXACT_THEORY_SOURCE_PAYLOAD_DESCRIPTORS',originals)
 def history():
  before=json.dumps(initial,sort_keys=True);m.validate_documents(new,accepted=initial);assert json.dumps(initial,sort_keys=True)==before
  oldnote=next(x for x in initial if x['object_type']=='Annotation' and x['object_id']==new[2]['object_id']);assert oldnote['revision_id']!=new[2]['revision_id'];assert {tuple(sorted(x.items())) for x in new[2]['provenance']['derived_from']} >= {tuple(sorted({k:oldnote[k] for k in ['object_type','object_id','revision_id']}.items()))}
 case('SE3_REASSESSMENT_RETAINS_OLD_PINNED_REVISION',history)
 def ai_boundary():
  ai=next(x for x in initial if x['title']=='LLM-only hypothesis and theory');assert ai['object_type']=='Annotation' and ai['provenance']['origin_kind']=='ai_authored';assert ai['provenance']['source_ref'] is None and ai['provenance']['source_locator'] is None and ai['data']['author']['model'] is None
  bad=copy.deepcopy(ai);bad['provenance']['origin_kind']='external_capture';reject([bad],'OBJECT_SCHEMA',initial[:4])
 case('SE4_AI_AUTHORED_IS_NOT_RAW_SOURCE',ai_boundary)
 def closed_schema():
  bad=copy.deepcopy(initial[1]);bad['data']['complexity']={'time':'O(1)'};reject([bad],'OBJECT_SCHEMA',[initial[3]])
  bad=copy.deepcopy(initial[1]);bad['object_type']='Algorithm';reject([bad],'OBJECT_SCHEMA',[initial[3]])
 case('SE5_UNSUPPORTED_STRUCTURED_FIELDS_TYPES_EXPLICIT',closed_schema)
 def wrong_ref():
  bad=copy.deepcopy(initial[4]);bad['data']['targets'][0]['object_type']='Asset';reject([bad],'REFERENCE_TYPE_MISMATCH',initial[:4])
 case('SE6_TYPED_TARGET_MISMATCH_REJECTED',wrong_ref)
 def causal_cycle():
  bad=copy.deepcopy(new[2]);bad['provenance']['derived_from']=[{k:bad[k] for k in ['object_type','object_id','revision_id']}];reject([*new[:2],bad,new[3]],'DERIVATION_CYCLE',initial)
 case('SE7_DERIVATION_SELF_REFERENCE_REJECTED',causal_cycle)
 def version_boundary():
  bad=copy.deepcopy(initial[1]);bad['schema']='bank-entity/2';reject([bad],'OBJECT_SCHEMA',[initial[3]])
 case('SE8_UNKNOWN_SCHEMA_VERSION_REJECTED',version_boundary)
 return {'record_kind':'solution_evolution_static_conformance','status':'PASS','tests_run':len(cases),'cases':cases,'fixture_sha256':hashlib.sha256((root/'PLANNING/SCENARIOS/SOLUTION_EVOLUTION_FIXTURE.json').read_bytes()).hexdigest(),'schema_sha256':hashlib.sha256((root/'PLANNING/CONTRACTS/BANK_TYPES.schema.json').read_bytes()).hexdigest(),'existing_contract_helper_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':fixture['meaning_limit'],'full_scenario_runtime_accepted':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=ap.parse_args();print(json.dumps(run(a.root),ensure_ascii=False))
