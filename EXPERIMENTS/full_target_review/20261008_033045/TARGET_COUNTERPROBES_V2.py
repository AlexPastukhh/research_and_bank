"""Independent target-oriented evidence over owned fixtures; no network/user data."""
from pathlib import Path
from contextlib import contextmanager, closing
import json,os,sys,uuid,sqlite3,socket,time,hashlib,datetime,unittest
from unittest.mock import patch
R=Path(__file__).resolve().parents[3];O=Path(__file__).parent
sys.path.insert(0,str(R/'EXPERIMENTS/draft_authoring'))
import test_authoring as fx
A=fx.a
@contextmanager
def fixture():
 h=fx.Tests('test_01_all_kinds_independent_exact_oracle_bank_discovery_detail_original');h.setUp()
 try:yield h
 finally:h.tearDown()
def create(h,fields):
 p=h.w.prepare(fields);assert p['status']=='PREPARED',p
 published=h.backend.dispatch('publish',{'transaction_id':p['transaction_id']});assert published['status']=='PUBLISHED',published
 saved=h.backend.dispatch('save',{'transaction_id':p['transaction_id']});assert saved['status']=='ACCEPTED',saved
 assert saved['receipt']['committed']==[{'object_id':p['ref']['object_id'],'revision_id':p['ref']['revision_id']}]
 return p,saved
def get(h,ref):return h.backend.base.dispatch('detail',{'ref':ref})
def search(h,term,field,kind):
 b=h.backend.base.dispatch('rebuild',{});assert b['status']=='BUILT',b
 return h.backend.base.dispatch('search',{'query':term,'fields':[field],'revisions_mode':'current','object_types':[kind]})
def count(h,table):
 assert table in ['commits','revisions','attempt_receipts']
 path=h.h.f.store.db;assert path.is_file()
 with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as c:return c.execute('SELECT count(*) FROM '+table).fetchone()[0]
observed={}
class Tests(unittest.TestCase):
 def test_01_supported_plaintext_file_authoring_search_gap(self):
  with fixture() as h:
   path=h.h.f.temp/'algorithm.txt';raw=b'quicksorttargetomega unique theory';path.write_bytes(raw)
   p,s=create(h,{'kind':'file','title':'Algorithm file','path':str(path)});d=get(h,p['ref']);self.assertEqual(d['status'],'OK');self.assertEqual(d['data']['document']['data']['storage']['media_type'],'application/octet-stream')
   exp=h.backend.base.dispatch('export',{'ref':p['ref']});self.assertEqual(Path(exp['data']['original']['path']).read_bytes(),raw)
   q=search(h,'quicksorttargetomega','content','Asset');self.assertEqual(q['status'],'OK');self.assertEqual(q['data']['total_matches'],0);self.assertEqual(q['data']['coverage']['unsupported_media'],1)
   fn=search(h,'algorithm','filename','Asset');self.assertEqual([x['ref'] for x in fn['data']['hits']],[p['ref']])
   from test_importer import Bundle
   control=Bundle();op,cd=control.doc('Asset');cp=cd['data']['storage']['file_path'];control.files[cp]=raw;cd['data']['storage'].update(media_type='text/plain',byte_length=len(raw),sha256=hashlib.sha256(raw).hexdigest());control.files[op['document_path']]=A.encoded(cd)
   self.assertEqual(h.h.f.save(control).state,'ACCEPTED');cq=search(h,'quicksorttargetomega','content','Asset');self.assertEqual([x['ref'] for x in cq['data']['hits']],[{'object_type':'Asset','object_id':cd['object_id'],'revision_id':cd['revision_id']}])
   observed['plaintext_creation']={'positive_control_same_UTF8_text_plain_hit':True,'saved':True,'exact_original':True,'media_type':'application/octet-stream','content_search_expected_for_text_plain':1,'actual_content_matches':0,'coverage':q['data']['coverage'],'filename_search':True,'classification':'first-use integration gap; earlier creation-only binary contract itself not disproved'}
 def test_02_note_supported_text_full_search_and_preview(self):
  with fixture() as h:
   body='Theorytargetomega '+('Text paragraph. '*8000);p,s=create(h,{'kind':'note','title':'Theory note','body':body,'author_kind':'user','identity':'synthetic owner'});d=get(h,p['ref']);self.assertEqual(d['data']['document']['data']['body'],body)
   q=search(h,'Theorytargetomega','body','Annotation');self.assertEqual([x['ref'] for x in q['data']['hits']],[p['ref']]);self.assertIn('сокращён',fx.p.base.display(d))
   observed['note_text']={'full_body_bytes':len(body.encode()),'actual_pinned_hit':p['ref'],'display_limited_explicitly':True}
 def test_03_external_app_save_and_manual_UI_refresh_only(self):
  with fixture() as h:
   model=fx.p.base.Model();req={'protocol':fx.p.base.discovery.PROTOCOL,'object_types':fx.p.base.TYPES,'snapshot_sequence':None,'after_object_id':None,'limit':10};self.assertTrue(model.begin('list',req,'Bank'));model.finish(h.backend.base.dispatch('list',req));self.assertEqual(model.rows['Bank'],[])
   p,s=create(h,{'kind':'note','title':'External saved','body':'Exact saved'});self.assertEqual(model.rows['Bank'],[]);fresh=h.backend.base.dispatch('list',req);self.assertEqual([x['ref'] for x in fresh['items']],[p['ref']])
   self.assertTrue(model.begin('list',req,'Bank'));model.finish(fresh);self.assertEqual([x['ref'] for x in model.rows['Bank']],[p['ref']])
   observed['external_save_UI']={'accepted_through_app':True,'fresh_query_sees_record':True,'existing_UI_rows_refresh_only_when_list_action_finishes':True,'classification':'remaining R1 automatic external-change visibility; no false current full-R1 claim'}
 def test_04_incomplete_attempt_diagnostic_not_retained(self):
  with fixture() as h:
   tx=str(uuid.uuid4());A.io.mkdir(h.roots['intake']/tx)
   first=h.backend.base.dispatch('save',{'transaction_id':tx});self.assertEqual(first['status'],'INCOMPLETE');self.assertIsNotNone(first['receipt']);self.assertEqual(count(h,'attempt_receipts'),0)
   q=h.backend.base.dispatch('receipt',{'transaction_id':tx});self.assertEqual(q['status'],'ERROR');self.assertEqual(q['code'],'RECEIPT_NOT_FOUND');self.assertEqual(count(h,'commits'),0)
   observed['incomplete_attempt']={'immediate_status':first['status'],'diagnostic_code':first['code'],'persistent_attempt_rows':0,'receipt_after_reopen':q['code'],'classification':'existing planned failed-attempt/restart UX remainder; not lost accepted data'}
 def test_05_locator_get_does_not_fetch_and_note_unknown_not_raw(self):
  with fixture() as h:
   p,s=create(h,{'kind':'url','title':'Retained URL','uri':'https://example.invalid/new-theory'});o=h.backend.base.dispatch('export',{'ref':p['ref']});self.assertEqual(o['data']['availability'],'locator_only');self.assertNotIn('original',o['data'])
   n,s=create(h,{'kind':'note','title':'LLM reasoning','body':'Maybe another method','author_kind':'ai','model':'synthetic-model'});d=get(h,n['ref'])['data']['document'];self.assertEqual(d['provenance']['origin_kind'],'ai_authored');self.assertIsNone(d['provenance']['source_ref']);self.assertEqual(d['data']['targets'],[])
   observed['epistemic']={'URL_is_locator_not_source_capture':True,'AI_annotation_not_raw':True,'no_fake_Source_Run':True}
 def test_06_exact_replay_accepted_receipt_survives_journal_damage(self):
  with fixture() as h:
   p,s=create(h,{'kind':'note','title':'Immutable proof','body':'Exactly retained'});before=count(h,'commits');(h.roots['authoring']/p['transaction_id']/'SEAL.json').write_bytes(b'broken journal')
   r=h.backend.dispatch('receipt',{'transaction_id':p['transaction_id'],'expected_manifest_sha256':p['manifest_sha256']});self.assertEqual(r['data']['receipt']['commit_id'],s['receipt']['commit_id']);repeat=h.backend.dispatch('save',{'transaction_id':p['transaction_id']});self.assertEqual(repeat['status'],'REPLAY');self.assertEqual(count(h,'commits'),before)
   observed['receipt_truth']={'actual_accepted_receipt_survives_local_journal_damage':True,'replay_zero_duplicate':True}
 def test_07_first_variant_workspace_quota_is_not_global_Bank_limit(self):
  with fixture() as h:
   w=h.workspace(_limits={'intents':1});first=w.prepare({'kind':'note','title':'One','body':'One'});self.assertEqual(first['status'],'PREPARED');p=h.backend.dispatch('publish',{'transaction_id':first['transaction_id']});self.assertEqual(p['status'],'PUBLISHED');self.assertEqual(h.backend.dispatch('save',{'transaction_id':first['transaction_id']})['status'],'ACCEPTED')
   second=w.prepare({'kind':'note','title':'Two','body':'Two'});self.assertEqual(second['code'],'AUTHORING_WORKSPACE_LIMIT');self.assertIsNone(second['transaction_id']);self.assertEqual(count(h,'commits'),1);self.assertEqual(get(h,first['ref'])['status'],'OK')
   observed['quota']={'accepted_intents_count_toward_workspace_quota':True,'profile_refusal_not_Bank_capacity_claim':True,'explicit_maintenance_needed_at_real_quota_trigger':True}
 def test_08_byte_limit_policy_is_frozen_and_semantic_revision_not_persistent_properties(self):
  with fixture() as h:
   p,s=create(h,{'kind':'note','title':'Frozen bytes','body':'Exact text'});intent=json.loads((h.roots['authoring']/p['transaction_id']/'INTENT.json').read_bytes());self.assertEqual(intent['profile']['policy_version'],'r1-authoring/1');self.assertEqual(intent['profile']['body_utf8_bytes'],1048576)
   initial=get(h,p['ref']);self.assertEqual(initial['data']['document']['object_id'],p['ref']['object_id']);self.assertEqual(count(h,'revisions'),1)
   observed['version_boundaries']={'frozen_intent_profile':True,'stable_pin':True,'editor_runtime_pending':True,'new_domain_structured_fields_need_reviewed_schema_profile':True}
if __name__=='__main__':
 start=time.monotonic();sources={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for top in ['draft_authoring','local_ui','local_command_adapter','sqlite_importer','bank_read_api','lexical_search','package_producer','secure_intake'] for p in(R/'EXPERIMENTS'/top).iterdir() if p.suffix in ['.py','.sql'] or p.name=='LIMITS.json'}
 with patch.object(socket.socket,'connect',side_effect=AssertionError('No external network')):result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in sources.items())
 report={'record_kind':'independent_full_target_counterprobes','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':sys.platform,'success':result.wasSuccessful(),'tests_run':result.testsRun,'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),'observed_target_limitations_and_passed_invariants':observed,'source_sha256':sources,'source_unchanged':True,'counterprobe_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-start,'limitations':['Owned synthetic data, actual default Windows guards only on Windows; portable fixture on POSIX','These assertions establish actual limitations too; success is not a claim that first-use gaps are fixed or all target goals achieved','No real Bank/install/import/OS privileges/provider/research/Watch or complete release acceptance']}
 name='COUNTERPROBES_NATIVE_V2.json' if os.name=='nt' else 'COUNTERPROBES_LOCAL_V2.json';(O/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('FINAL',json.dumps({k:report[k] for k in ['success','tests_run','skipped','failures','errors','elapsed_seconds']}),flush=True);sys.exit(not result.wasSuccessful())
