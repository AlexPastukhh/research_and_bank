"""Owned headless card-review proofs. No first-Bank runtime implementation."""
from pathlib import Path
from contextlib import closing
import codecs, copy, datetime, hashlib, importlib.util, json, os, socket, sqlite3, sys, time, unittest, uuid
from unittest.mock import patch
from jsonschema import Draft202012Validator, FormatChecker

O = Path(__file__).resolve().parent
R = O.parents[3]
spec = importlib.util.spec_from_file_location('prior_target_counterprobes', O.parent/'TARGET_COUNTERPROBES_V2.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
A = old.A
ATTEMPT_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema', 'type':'object', 'additionalProperties':False,
 'required':['protocol','attempt_id','transaction_id','manifest_sha256','recorded_at','outcome','code','canonical_receipt'],
 'properties':{
  'protocol':{'const':'local-bank-attempt/1'},
  'attempt_id':{'type':'string','format':'uuid'},
  'transaction_id':{'type':['string','null'],'format':'uuid'},
  'manifest_sha256':{'anyOf':[{'type':'null'},{'type':'string','pattern':'^[0-9a-f]{64}$'}]},
  'recorded_at':{'type':'string','format':'date-time'},
  'outcome':{'enum':['ACCEPTED','REPLAY','CONFLICT','REJECTED','INCOMPLETE','INTEGRITY_ERROR','UNKNOWN','IO_ERROR','RETRYABLE_BUSY','CANCELLED','READY_NOT_PUBLISHED']},
  'code':{'type':'string','pattern':'^[A-Z][A-Z0-9_]{0,127}$'},
  'canonical_receipt':{'type':['object','null']}
 }
}
# Schema is a private design oracle, not an adopted runtime contract. Semantic
# validation of an optional canonical receipt remains Contracts.envelope's job.
v = Draft202012Validator(ATTEMPT_SCHEMA, format_checker=FormatChecker())
observed = {}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def token(c):
 row = c.execute('SELECT commit_sequence,commit_id FROM commits ORDER BY commit_sequence DESC LIMIT 1').fetchone()
 return tuple(row) if row else (0,None)
def append_owned(db, record):
 v.validate(record)
 raw=A.encoded(record)
 with closing(sqlite3.connect(db)) as c:
  c.execute('INSERT INTO attempt_receipts(attempt_id,transaction_id,manifest_sha256,recorded_at,receipt_blob) VALUES(?,?,?,?,?)',
   tuple(record[k] for k in ['attempt_id','transaction_id','manifest_sha256','recorded_at'])+(raw,))
  c.commit()
 return raw
def record(tx, outcome='UNKNOWN'):
 return {'protocol':'local-bank-attempt/1','attempt_id':str(uuid.uuid4()),'transaction_id':tx,
 'manifest_sha256':None,'recorded_at':A.utc(),'outcome':outcome,'code':'OWNED_OUTPUT_UNCERTAIN','canonical_receipt':None}

class NewProofs(unittest.TestCase):
 def test_05_legacy_v1_sealed_input_survives_external_original_removal(self):
  with old.fixture() as h:
   p=h.prepare('file'); before=h.snapshot(p['transaction_id']); doc=h.doc(p)
   h.original.unlink(); reopened=h.workspace().inspect(p['transaction_id'])
   self.assertEqual(reopened,p); self.assertEqual(h.snapshot(p['transaction_id']),before)
   self.assertEqual(doc['data']['storage']['media_type'],'application/octet-stream')
   intent=json.loads((h.roots['authoring']/p['transaction_id']/'INTENT.json').read_bytes())
   self.assertEqual(intent['profile']['policy_version'],'r1-authoring/1')
   observed['legacy_profile']={'exact_reopen':True,'profile':'r1-authoring/1','future_v2_must_preserve_v1':True}
 def test_06_streaming_UTF8_design_oracle_preserves_bytes_and_rejects_invalid(self):
  raw=b'\xef\xbb\xbf'+ 'Теория 🙂\r\nAlgorithm'.encode('utf8')
  d=codecs.getincrementaldecoder('utf-8')('strict'); text=''.join(d.decode(raw[i:i+1]) for i in range(len(raw)))+d.decode(b'',final=True)
  self.assertEqual(text.encode('utf8'),raw)
  d=codecs.getincrementaldecoder('utf-8')('strict');d.decode(b'prefix\xe2')
  with self.assertRaises(UnicodeDecodeError):d.decode(b'',final=True)
  with self.assertRaises(UnicodeDecodeError):codecs.getincrementaldecoder('utf-8')('strict').decode(b'\xff',final=True)
  observed['UTF8_oracle']={'split_multibyte_BOM_CRLF_exact':True,'invalid_or_incomplete_rejected':True,'new_authoring_not_implemented':True}
 def test_07_unknown_is_not_a_canonical_Bank_receipt(self):
  with old.fixture() as h:
   tx=str(uuid.uuid4()); canonical=h.h.f.store._receipt('INCOMPLETE','OWNED_INCOMPLETE',str(uuid.uuid4()),tx)
   A.im.Contracts().envelope(canonical)
   bad=copy.deepcopy(canonical);bad['status']='UNKNOWN'
   with self.assertRaises(Exception):A.im.Contracts().envelope(bad)
   private=record(tx);v.validate(private);self.assertIsNone(private['canonical_receipt'])
   observed['canonical_boundary']={'UNKNOWN_rejected_by_existing_canonical_schema':True,'private_design_envelope_required':True}
 def test_08_existing_attempt_table_reopens_and_is_immutable_without_DDL_change(self):
  with old.fixture() as h:
   db=h.h.f.store.db
   with closing(sqlite3.connect(db)) as c: before=c.execute('SELECT type,name,sql FROM sqlite_schema ORDER BY type,name').fetchall();t=token(c)
   rec=record(str(uuid.uuid4()));raw=append_owned(db,rec)
   with closing(sqlite3.connect(db)) as c:
    self.assertEqual(c.execute('SELECT receipt_blob FROM attempt_receipts WHERE attempt_id=?',(rec['attempt_id'],)).fetchone()[0],raw)
    self.assertEqual(token(c),t);self.assertEqual(c.execute('SELECT type,name,sql FROM sqlite_schema ORDER BY type,name').fetchall(),before)
    with self.assertRaises(sqlite3.IntegrityError):c.execute('UPDATE attempt_receipts SET recorded_at=? WHERE attempt_id=?',('bad',rec['attempt_id']))
    c.rollback()
    with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM attempt_receipts WHERE attempt_id=?',(rec['attempt_id'],))
    c.rollback()
   observed['physical_reuse']={'append_reopen_exact':True,'immutable':True,'no_DDL_change':True,'does_not_change_commit_token':True,'prototype_only':True}
 def test_09_accepted_truth_is_separate_from_later_unknown_or_failed_diagnostic(self):
  with old.fixture() as h:
   p,s=old.create(h,{'kind':'note','title':'Accepted theory','body':'Exact retained truth'})
   rec=record(p['transaction_id']);rec['manifest_sha256']='f'*64;append_owned(h.h.f.store.db,rec)
   q=h.backend.base.dispatch('receipt',{'transaction_id':p['transaction_id'],'expected_manifest_sha256':p['manifest_sha256']})
   self.assertEqual(q['data']['receipt'],s['receipt']);self.assertEqual(q['data']['latest_diagnostic_attempt'],{'availability':'not_recorded_by_current_writer'})
   schema=json.loads((R/'EXPERIMENTS/bank_read_api/result.schema.json').read_bytes());bad=copy.deepcopy(q)
   bad['data']['latest_diagnostic_attempt']={'availability':'available','attempt':rec}
   self.assertTrue(list(Draft202012Validator(schema).iter_errors(bad)))
   observed['reader_extension']={'accepted_unchanged':True,'current_placeholder_explicit':True,'app_result_schema_extension_required':True}
 def test_10_compact_commit_token_detects_save_while_diagnostics_do_not(self):
  with old.fixture() as h:
   db=h.h.f.store.db
   with closing(sqlite3.connect(db)) as c:before=token(c)
   p,s=old.create(h,{'kind':'url','title':'External locator','uri':'https://example.invalid/theory'})
   with closing(sqlite3.connect(db)) as c:after=token(c)
   self.assertNotEqual(before,after);self.assertEqual(after[1],s['receipt']['commit_id'])
   append_owned(db,record(p['transaction_id']))
   with closing(sqlite3.connect(db)) as c:self.assertEqual(token(c),after)
   observed['visibility_signal']={'compact_commit_token_changes':True,'diagnostic_only_append_ignored':True,'future_observer_needs_root_generation_and_no_recovery':True,'observer_UI_not_implemented':True}

if __name__=='__main__':
 start=time.monotonic()
 sources={p.relative_to(R).as_posix():digest(p) for top in ['draft_authoring','local_ui','local_command_adapter','sqlite_importer','bank_read_api','lexical_search','package_producer','secure_intake'] for p in (R/'EXPERIMENTS'/top).iterdir() if p.suffix in ['.py','.sql'] or p.name=='LIMITS.json'}
 suite=unittest.TestSuite(old.Tests(n) for n in ['test_01_supported_plaintext_file_authoring_search_gap','test_03_external_app_save_and_manual_UI_refresh_only','test_04_incomplete_attempt_diagnostic_not_retained','test_06_exact_replay_accepted_receipt_survives_journal_damage'])
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NewProofs))
 with patch.object(socket.socket,'connect',side_effect=AssertionError('No network in owned review proof')):
  result=unittest.TextTestRunner(verbosity=2).run(suite)
 unchanged=all(digest(R/n)==h for n,h in sources.items())
 report={'record_kind':'first_bank_card_existing_contract_proofs','review_id':'FBCR-20261008-01','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':sys.platform,'success':result.wasSuccessful() and unchanged,'tests_run':result.testsRun,'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),'source_unchanged':unchanged,'source_sha256':sources,'probe_sha256':digest(Path(__file__)),'observed':{**old.observed,**observed},'elapsed_seconds':time.monotonic()-start,'limitations':['Existing contracts and owned design oracles only; new first-Bank features NOT implemented or accepted','No Tk instance/window/capture, real Bank/setup, network, privilege change or full release acceptance','Native Windows capability proof only when platform win32; portable result does not replace native guards']}
 (O/('CONTRACT_PROBES_NATIVE.json' if os.name=='nt' else 'CONTRACT_PROBES_LOCAL.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('FINAL',json.dumps({k:report[k] for k in ['success','tests_run','skipped','failures','errors','source_unchanged','elapsed_seconds']}),flush=True)
 sys.exit(0 if report['success'] else 1)
