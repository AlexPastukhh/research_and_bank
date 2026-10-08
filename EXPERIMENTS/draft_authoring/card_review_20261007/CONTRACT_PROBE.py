"""Independent authoring-card contract probes; no authoring implementation."""
from pathlib import Path
import argparse,copy,json,hashlib,sys,uuid,datetime,errno
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--out',required=True);a=p.parse_args()
root=Path(a.root).resolve();sys.path.insert(0,str(root/'EXPERIMENTS/package_producer'))
import test_producer as t
app=t.app;fx=t.fx;cases=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
def record(name,fn):
 value=fn();cases.append({'id':name,'status':'PASS','observed':value})
def kind_profile(kind):
 h=t.Tests('test_01_default_cli_producer_save_receipt_reads_search');h.setUp()
 try:
  b=fx.Bundle();base_kind='Annotation' if kind=='note' else 'Asset';op,doc=b.doc(base_kind)
  oid,rid,tx=[str(uuid.uuid4()) for _ in range(3)];timestamp='2026-10-07T15:50:00Z'
  op.update(object_id=oid,revision_id=rid,base_revision_id=None);doc.update(object_id=oid,revision_id=rid,revision_created_at=timestamp,title='Owned '+kind)
  doc['provenance'].update(origin_kind='unknown',source_locator=None,captured_at=None,source_ref=None,derived_from=[])
  raw=b'owned binary\x00\xff';payload='payload/original.bin'
  if kind=='file':doc['data']={'storage':{'mode':'bytes','file_path':payload,'byte_length':len(raw),'sha256':sha(raw),'media_type':'application/octet-stream','original_filename':'owned.bin'}}
  elif kind=='url':doc['data']={'storage':{'mode':'locator','uri':'https://example.invalid/algorithm?v=1','label':None}};doc['provenance'].update(origin_kind='user_capture',source_locator=doc['data']['storage']['uri'],captured_at=timestamp)
  else:doc['data']={'kind':'note','content_format':'plain_text','body':'Algorithm + theory; epistemic status unchanged.','author':{'kind':'unknown','identity':None,'model':None},'targets':[]}
  b.m.update(transaction_id=tx,created_at=timestamp,producer={'name':'authoring-card-review','version':'1'});b.m['operations']=[op];b.files={op['document_path']:app.encoded(doc)}
  if kind=='file':b.files[payload]=raw
  _,source,draft=h.draft(b);before={n:(source/n).read_bytes() for n in draft['files']};published=h.runpub(tx);assert published['status']=='PUBLISHED',published
  manifest_bytes=(h.f.intake/tx/'manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
  assert all((h.f.intake/tx/n).read_bytes()==data for n,data in before.items());assert manifest['operations']==[op]
  accepted=h.h.c.save('bank.save',tx);assert accepted['status']=='ACCEPTED',accepted
  replay=h.h.c.save('bank.save',tx);assert replay['status']=='REPLAY' and replay['receipt']['commit_id']==accepted['receipt']['commit_id']
  assert h.h.count()==1
  if kind=='file':assert b''.join(h.f.store.read_original(tx,payload))==raw
  return {'canonical_type':base_kind,'base_revision_id':None,'targets':doc['data'].get('targets'),'transaction_id':tx,'document_sha256':sha(before[op['document_path']]),'manifest_sha256':sha(manifest_bytes),'publication':'PUBLISHED','save':'ACCEPTED','retry':'REPLAY','portable_fixture_not_native':sys.platform!='win32'}
 finally:h.tearDown()
for kind in ['file','url','note']:record('PROFILE_'+kind.upper(),lambda kind=kind:kind_profile(kind))
def producer_case(name):
 h=t.Tests(name);h.setUp()
 try:getattr(h,name)();return {'existing_case':name,'actual_contract_assertions_executed':True}
 finally:h.tearDown()
for name in ['test_07_pending_complete_explicit_resume_only','test_08_partial_resume_rejected_bytes_preserved','test_14_source_extra_missing_file_not_published','test_04_changed_same_transaction_conflict_preserves_all_bytes']:
 record('CONTRACT_'+name,lambda name=name:producer_case(name))
def journal_is_not_payload():
 h=t.Tests('test_14_source_extra_missing_file_not_published');h.setUp()
 try:
  b,source,d=h.draft();(source/'INTENT.json').write_bytes(b'{}');r=h.runpub();assert r['status']=='REJECTED' and r['code']=='EXTRA_FILE',r
  assert not(h.f.intake/h.tx).exists();return {'publication':r['status'],'code':r['code'],'Bank_commits':h.h.count(),'journal_must_be_outside_source_tx':True}
 finally:h.tearDown()
record('JOURNAL_INSIDE_SOURCE_REJECTED',journal_is_not_payload)
def note_provenance():
 contracts=app.im.Contracts();b=fx.Bundle();_,d=b.doc('Annotation');d['data']['targets']=[];d['provenance']['source_ref']=None;d['provenance']['derived_from']=[]
 for author,origin in [('user','user_authored'),('ai','ai_authored'),('unknown','unknown')]:
  d['data']['author']={'kind':author,'identity':None,'model':None};d['provenance']['origin_kind']=origin;contracts.schema(d)
 d['data']['author']['kind']='user';d['provenance']['origin_kind']='ai_authored'
 try:contracts.schema(d)
 except app.im.Problem as e:assert e.code=='OBJECT_SCHEMA'
 else:raise AssertionError('False provenance accepted')
 return {'standalone_note_valid':True,'unknown_identity_and_model_valid':True,'false_user_AI_origin_rejected':True}
record('EXPLICIT_NOTE_PROVENANCE',note_provenance)
def ui_context_does_not_reset_itself():
 sys.path.insert(0,str(root/'EXPERIMENTS/local_ui'));import presenter
 m=presenter.Model();old,new=[str(uuid.uuid4()) for _ in range(2)]
 m.begin('save',{'transaction_id':old},'Bank');m.finish({'status':'ACCEPTED','code':'OK','transaction_id':old})
 m.begin('prepare',{'transaction_id':new},'Bank');m.finish({'status':'PREPARED','code':'READY','transaction_id':new})
 assert m.save['transaction_id']==old and m.save['status']=='ACCEPTED'
 return {'old_transaction_status_retained':True,'requires_authoring_context_isolation':True,'authoring_UI_not_implemented':True}
record('BASE_MODEL_CONTEXT_REQUIRES_ISOLATION',ui_context_does_not_reset_itself)
source_paths=['PLANNING/CONTRACTS/BANK_TYPES.schema.json','PLANNING/CONTRACTS/BANK_SCHEMA_COMPATIBILITY.json','PLANNING/CONTRACTS/LOCAL_INTAKE_LIMITS.json','EXPERIMENTS/package_producer/draft.schema.json','EXPERIMENTS/package_producer/producer.py','EXPERIMENTS/package_producer/producer_io.py','EXPERIMENTS/package_producer/test_producer.py','EXPERIMENTS/sqlite_importer/importer.py','EXPERIMENTS/local_command_adapter/commands.py','EXPERIMENTS/local_ui/presenter.py']
report={'record_kind':'authoring_card_independent_contract_probe','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','cases':cases,'passed':len(cases),'source_sha256':{n:sha((root/n).read_bytes()) for n in source_paths},'limitations':['Review probes exercise existing contracts and independent profile samples; no authoring UI/workspace/journal implementation tested','Local run uses explicit synthetic fixture adapters; no Windows source guard or hardware durability claim'],'authoring_runtime_accepted':False}
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'status':report['status'],'passed':report['passed']}))
