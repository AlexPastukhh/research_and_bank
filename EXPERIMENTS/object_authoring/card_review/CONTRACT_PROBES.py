"""Independent card probes of existing contracts; no new authoring runtime."""
from pathlib import Path
import argparse,copy,hashlib,json,os,platform,re,socket,sqlite3,sys,unittest,uuid,datetime
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'EXPERIMENTS/package_producer'),str(ROOT/'EXPERIMENTS/draft_authoring'),str(ROOT/'PLANNING/TOOLS')]
import test_producer as tp,producer,authoring as a,test_authoring as ta,check_bank_contracts as c
fx=tp.fx
ref=lambda d:{k:d[k] for k in ['object_type','object_id','revision_id']}
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
def revision(bundle,kind,payload=True):
 b=bundle.clone();op,d=b.doc(kind);base=d['revision_id'];rid=str(uuid.uuid4());tx=str(uuid.uuid4());stamp=utc()
 op.update(base_revision_id=base,revision_id=rid)
 d.update(revision_id=rid,revision_created_at=stamp,title='Revised '+kind)
 b.m.update(transaction_id=tx,created_at=stamp,operations=[op])
 b.files={op['document_path']:producer.encoded(d)}
 if kind=='Asset' and d['data']['storage']['mode']=='bytes' and payload:
  n=d['data']['storage']['file_path'];b.files[n]=bundle.files[n]
 return b
class Harness:
 def __enter__(self):
  self.h=tp.Tests('test_01_default_cli_producer_save_receipt_reads_search');self.h.setUp();return self.h
 def __exit__(self,*_):self.h.tearDown()
def publish(h,b):
 before=h.h.count();b,source,draft=h.draft(b);published=h.runpub(b.m['transaction_id'])
 assert published['status']=='PUBLISHED' and not published['Bank_accepted']
 assert h.h.count()==before
 return b,source,published
def save(h,b):
 b,source,published=publish(h,b)
 result=h.h.c.save('bank.save',b.m['transaction_id']);assert result['status']=='ACCEPTED',result
 return b,result
class Probes(unittest.TestCase):
 def test_01_universal_entity_schema_exact_fields(self):
  b=fx.Bundle();_,d=b.doc('Entity');d['data']['asset_refs']=[];d['provenance']['derived_from']=[]
  for kind in ['problem','algorithm','theory']:
   x=copy.deepcopy(d);x['data']['entity_kind']=kind;c.validate_documents([x])
  for change in [lambda x:x['data'].update(entity_kind='source'),lambda x:x['data'].update(complexity='O(n)'),lambda x:x.update(schema='bank-entity/99')]:
   x=copy.deepcopy(d);change(x)
   with self.assertRaises(c.ContractError):c.validate_documents([x])
 def test_02_collection_cycles_are_flat_refs_not_derivation(self):
  b=fx.Bundle();_,d=b.doc('Collection');one=copy.deepcopy(d);two=copy.deepcopy(d)
  for x in [one,two]:
   x.update(object_id=str(uuid.uuid4()),revision_id=str(uuid.uuid4()));x['provenance']['derived_from']=[]
  one['data']['members']=[ref(two)];two['data']['members']=[ref(one)]
  c.validate_documents([one,two])
  one['provenance'].update(origin_kind='derived',derived_from=[ref(two)])
  two['provenance'].update(origin_kind='derived',derived_from=[ref(one)])
  with self.assertRaisesRegex(c.ContractError,'DERIVATION_CYCLE'):c.validate_documents([one,two])
 def test_03_duplicate_means_exact_pin_different_revisions_allowed(self):
  b=fx.Bundle();_,asset=b.doc('Asset');new=copy.deepcopy(asset);new['revision_id']=str(uuid.uuid4());_,collection=b.doc('Collection');collection['provenance']['derived_from']=[]
  collection['data']['members']=[ref(new),ref(asset)]
  c.validate_documents([collection],accepted=[asset,new])
  collection['data']['members'].append(ref(asset))
  with self.assertRaises(c.ContractError):c.validate_documents([collection],accepted=[asset,new])
 def test_04_existing_creation_workspace_is_not_an_update_editor(self):
  h=ta.Tests('test_01_all_kinds_independent_exact_oracle_bank_discovery_detail_original');h.setUp()
  try:
   f=h.fields()
   for more in [{'object_id':str(uuid.uuid4())},{'base_revision_id':str(uuid.uuid4())},{'targets':[]},{'kind':'entity'}]:
    result=h.w.prepare({**f,**more});self.assertEqual(result['status'],'REJECTED');self.assertIsNone(result['transaction_id'])
   result=h.w.prepare(f);self.assertEqual(result['status'],'PREPARED')
   draft=json.loads((h.roots['source']/result['transaction_id']/'DRAFT.json').read_bytes())
   self.assertIsNone(draft['operations'][0]['base_revision_id'])
  finally:h.tearDown()
 def test_05_publication_does_not_validate_external_bank_refs(self):
  with Harness() as h:
   b=fx.Bundle.entity();b.edit('Entity',lambda d:d['data'].update(asset_refs=[{'object_type':'Asset','object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4())}]))
   b,p,pub=publish(h,b);self.assertEqual(pub['status'],'PUBLISHED');self.assertFalse(pub['Bank_accepted'])
   result=h.h.c.save('bank.save',b.m['transaction_id']);self.assertEqual(result['status'],'REJECTED',result);self.assertEqual(h.h.count(),0)
 def test_06_all_four_types_update_stable_id_and_old_pinned_read(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle())
   for kind in ['Asset','Entity','Annotation','Collection']:
    new,result=save(h,revision(old,kind));old_op,old_doc=old.doc(kind);new_op,new_doc=new.doc(kind)
    self.assertEqual(old_doc['object_id'],new_doc['object_id']);self.assertNotEqual(old_doc['revision_id'],new_doc['revision_id']);self.assertEqual(new_op['base_revision_id'],old_doc['revision_id'])
    q=h.h.q(kind,'collection.get' if kind=='Collection' else 'bank.get',new);self.assertEqual(h.h.query(q)['data']['document'],new_doc)
    q['selector']={'mode':'pinned','revision_id':old_doc['revision_id']};self.assertEqual(h.h.query(q)['data']['document'],old_doc)
    self.assertEqual(h.h.query(h.h.receipt(new))['data']['receipt'],result['receipt'])
   self.assertEqual(h.h.count(),5)
 def test_07_same_base_race_stale_conflict_keeps_draft_and_head(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle());winner=revision(old,'Entity');loser=revision(old,'Entity')
   winner,p,wpub=publish(h,winner);loser,lp,lpub=publish(h,loser);before=h.bytes_at(lp)
   accepted=h.h.c.save('bank.save',winner.m['transaction_id']);self.assertEqual(accepted['status'],'ACCEPTED',accepted)
   result=h.h.c.save('bank.save',loser.m['transaction_id']);self.assertEqual(result['status'],'CONFLICT',result);self.assertEqual(result['code'],'STALE_BASE')
   self.assertEqual(h.bytes_at(lp),before);self.assertEqual(h.h.count(),2)
   self.assertEqual(h.h.query(h.h.q('Entity',bundle=winner))['data']['ref'],ref(winner.doc('Entity')[1]))
   same=h.h.c.save('bank.save',loser.m['transaction_id']);self.assertEqual(same['code'],'STALE_BASE');self.assertEqual(h.h.count(),2)
 def test_08_rebase_under_published_transaction_is_content_conflict(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle());edit=revision(old,'Entity');edit,p,pub=publish(h,edit);ready=h.bytes_at(h.f.intake/edit.m['transaction_id'])
   draft=json.loads((p/'DRAFT.json').read_bytes());draft['operations'][0]['base_revision_id']=str(uuid.uuid4());(p/'DRAFT.json').write_bytes(producer.encoded(draft))
   result=h.runpub(edit.m['transaction_id']);self.assertIn(result['status'],['CONFLICT','REJECTED']);self.assertFalse(result['Bank_accepted'])
   self.assertEqual(h.bytes_at(h.f.intake/edit.m['transaction_id']),ready);self.assertEqual(h.h.count(),1)
 def test_09_asset_metadata_revision_requires_recaptured_exact_payload(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle());bad=revision(old,'Asset',payload=False);bad,p,d=h.draft(bad)
   result=h.runpub(bad.m['transaction_id']);self.assertEqual(result['status'],'REJECTED',result);self.assertFalse((h.f.intake/bad.m['transaction_id']).exists());self.assertEqual(h.h.count(),1)
   good,_=save(h,revision(old,'Asset'));_,od=old.doc('Asset');_,nd=good.doc('Asset');self.assertEqual(od['data']['storage'],nd['data']['storage'])
   for b in [old,good]:
    got=h.h.query(h.h.q('Asset','bank.original',b));self.assertEqual(got['status'],'OK',got);o=got['data']['original'];raw=Path(o['path']).read_bytes();n=b.doc('Asset')[1]['data']['storage']['file_path']
    self.assertEqual(raw,b.files[n]);self.assertEqual(hashlib.sha256(raw).hexdigest(),o['sha256'])
 def test_10_collection_order_and_both_historical_versions_survive_reopen(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle());newnote,_=save(h,revision(old,'Annotation'));changed=revision(old,'Collection')
   newref=ref(newnote.doc('Annotation')[1]);oldref=ref(old.doc('Annotation')[1])
   changed.edit('Collection',lambda d:d['data'].update(members=[newref,oldref]));changed,_=save(h,changed)
   client=h.h.open();q=h.h.q('Collection','collection.get',changed);actual=h.h.query(q,client)['data']['document']['data']['members'];self.assertEqual(actual,[newref,oldref])
   q['selector']={'mode':'pinned','revision_id':old.doc('Collection')[1]['revision_id']}
   self.assertEqual(h.h.query(q,client)['data']['document'],old.doc('Collection')[1])
 def test_11_targeted_note_and_explicit_author_consistency(self):
  with Harness() as h:
   old,_=save(h,fx.Bundle());target=ref(old.doc('Entity')[1]);note=revision(old,'Annotation')
   note.edit('Annotation',lambda d:d['data'].update(targets=[target]));note,_=save(h,note)
   got=h.h.query(h.h.q('Annotation',bundle=note));self.assertEqual(got['data']['document']['data']['targets'],[target])
   bad=revision(note,'Annotation');bad.edit('Annotation',lambda d:(d['data']['author'].update(kind='ai'),d['provenance'].update(origin_kind='user_authored')))
   bad,p,d=h.draft(bad);result=h.runpub(bad.m['transaction_id']);self.assertEqual(result['status'],'REJECTED');self.assertEqual(h.h.count(),2)
 def test_12_shared_workspace_lock_and_exact_root_contract(self):
  h=ta.Tests('test_01_all_kinds_independent_exact_oracle_bank_discovery_detail_original');h.setUp()
  try:
   extra=h.h.f.temp/'object-authoring';fx.private(extra)
   result=a.Workspace({**h.roots,'object_authoring':extra},_portable_fixture=os.name!='nt').prepare(h.fields())
   self.assertEqual(result['code'],'INVALID_ROOT_CONFIGURATION');self.assertIsNone(result['transaction_id'])
   with h.w.session():
    with self.assertRaises((a.io.Refused,OSError)) as caught:
     with a.io.WorkspaceLock(h.roots['authoring']/'LOCK'):pass
    error=caught.exception
    self.assertTrue(getattr(error,'code',None)=='AUTHORING_BUSY' or getattr(error,'winerror',None) in [32,33] or getattr(error,'errno',None) in [11,16],str(error))
   with a.io.WorkspaceLock(h.roots['authoring']/'LOCK'):pass
  finally:h.tearDown()
class Evidence(unittest.TextTestResult):
 def __init__(self,*args,**kw):super().__init__(*args,**kw);self.rows=[]
 def addSuccess(self,t):super().addSuccess(t);self.rows.append({'id':t._testMethodName,'observed':'PASS'})
 def addFailure(self,t,e):super().addFailure(t,e);self.rows.append({'id':t._testMethodName,'observed':'FAIL','traceback':self._exc_info_to_string(e,t)})
 def addError(self,t,e):super().addError(t,e);self.rows.append({'id':t._testMethodName,'observed':'ERROR','traceback':self._exc_info_to_string(e,t)})
def main():
 p=argparse.ArgumentParser();p.add_argument('--token',required=True);args=p.parse_args();assert re.fullmatch('[0-9a-f]{32}',args.token)
 out=Path(__file__).parent/('CONTRACT_PROBES_'+('NATIVE' if os.name=='nt' else 'LOCAL')+'_'+args.token+'.json');assert not out.exists()
 card=json.loads((ROOT/'PLANNING/WORK_ITEMS/R1_OBJECT_AUTHORING_CARD_REVIEW.json').read_bytes())
 paths=card['required_inputs']+[Path(__file__).relative_to(ROOT).as_posix(),'EXPERIMENTS/draft_authoring/test_authoring.py','EXPERIMENTS/package_producer/test_producer.py','EXPERIMENTS/local_command_adapter/commands.py','EXPERIMENTS/sqlite_importer/importer.py','EXPERIMENTS/bank_read_api/bank_read.py','EXPERIMENTS/draft_authoring/authoring_io.py','PLANNING/TOOLS/check_bank_contracts.py','PLANNING/CONTRACTS/LOCAL_INTAKE_LIMITS.json']
 hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sorted(set(paths))}
 with patch.object(socket.socket,'connect',side_effect=AssertionError('NETWORK_FORBIDDEN')):
  result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Probes))
 assert hashes=={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in hashes}
 d={'record_kind':'object_authoring_card_contract_probes','at':utc(),'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'success':result.wasSuccessful(),'tests_run':result.testsRun,'skipped':len(result.skipped),'cases':result.rows,'source_sha256':hashes,'limitations':['Review-only probes execute existing components on owned synthetic resources; no new editor runtime or real Bank installation','POSIX runs inject explicit existing fixture adapters; native runs use existing default controller/native guards','No generated editor GUI, hardware/a11y/full R0/R1/MVP acceptance or original4 Win1314 fixture resolution']}
 b=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
 with out.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert out.read_bytes()==b;print('FINAL',json.dumps({'success':d['success'],'tests_run':d['tests_run'],'skipped':d['skipped'],'report':str(out),'sha256':hashlib.sha256(b).hexdigest()}))
 return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())

