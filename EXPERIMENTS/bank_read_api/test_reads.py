"""Owned synthetic actual SQLite tests; Windows uses real secure-reader handles."""
from pathlib import Path
from contextlib import closing
import copy,gc,hashlib,json,os,platform,shutil,sqlite3,subprocess,sys,time,unittest,uuid
from unittest.mock import patch
import bank_read as api
sys.path.insert(0,str(api.ROOT/'EXPERIMENTS/sqlite_importer'))
import test_importer as fixtures

class Tests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');self.f.setUp();self.outputs=self.f.temp/'exports';fixtures.private(self.outputs);self.clients=[];self.client=self.open()
    def tearDown(self):
        for c in self.clients:c.close()
        self.f.tearDown()
    def open(self,**kw):
        c=api.ReadAPI(self.f.root,self.outputs,contracts=self.f.c,**kw);self.clients.append(c);return c
    def request(self,kind='Annotation',op='bank.get',bundle=None):
        b=bundle or self.f.bundle;o,d=b.doc(kind);q={'protocol':api.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':op,'object_type':kind,'object_id':d['object_id']}
        if op in ['bank.get','collection.get']:q['selector']={'mode':'current'}
        elif op=='bank.original':q['revision_id']=d['revision_id']
        elif op=='bank.history':q.update(snapshot_sequence=None,limit=2,offset=0)
        return q
    def receipt_request(self,bundle=None):return {'protocol':api.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'receipt.get','transaction_id':(bundle or self.f.bundle).m['transaction_id'],'expected_manifest_sha256':None}
    def run_query(self,q,client=None):
        result=(client or self.client).execute(api.im.encoded(q));self.assertIsNone(next(self.client.result_validator.iter_errors(result),None));return result
    def ok(self,q,client=None):
        result=self.run_query(q,client);self.assertEqual(result['status'],'OK',result);return result
    def error(self,q,code,client=None):
        result=self.run_query(q,client);self.assertEqual(result['status'],'ERROR',result);self.assertEqual(result['code'],code,result);self.assertNotIn('data',result);return result
    def corrupt(self,table,column,rowid):
        with closing(sqlite3.connect(self.f.store.db,isolation_level=None)) as c:
            with c.blobopen(table,column,rowid,readonly=False) as b:b.write(b'!')
    def remove_intake(self):
        # Native fixture snapshots used distinct private intake roots. Remove
        # those actual package sources, not just the unused base intake folder.
        for snapshot in self.f.snapshots:
            p=getattr(snapshot,'_fixture_input',None)
            if p is not None and p.parent.exists():shutil.rmtree(p.parent)
        if self.f.intake.exists():shutil.rmtree(self.f.intake)
    def test_01_empty_missing_no_initialization(self):
        self.error(self.request(),'OBJECT_NOT_FOUND');self.error(self.receipt_request(),'RECEIPT_NOT_FOUND')
        other=self.f.temp/'missing';c=api.ReadAPI(other);self.error(self.request(),'BANK_UNAVAILABLE',c);c.close();self.assertFalse(other.exists())
    def test_02_save_receipt_current_four_types_exact_documents(self):
        accepted=self.f.accepted()
        for kind in ['Asset','Entity','Annotation','Collection']:
            r=self.ok(self.request(kind));_,d=self.f.bundle.doc(kind);self.assertEqual(r['data']['document'],d);self.assertEqual(r['data']['ref'],api.ref(d));self.assertEqual(r['snapshot_sequence'],1)
        r=self.ok(self.receipt_request());self.assertEqual(r['data']['receipt'],accepted.receipt);self.assertEqual(r['data']['latest_diagnostic_attempt'],{'availability':'not_recorded_by_current_writer'})
    def test_03_update_old_pinned_after_intake_removed_restart(self):
        self.f.accepted();q=self.request();old=self.ok(q)['data'];self.f.accepted(fixtures.Bundle('continuation'));new=self.ok(q)['data'];self.assertNotEqual(old['ref'],new['ref'])
        q['selector']={'mode':'pinned','revision_id':old['ref']['revision_id']};self.assertEqual(self.ok(q,self.open())['data'],old)
        self.remove_intake();self.assertEqual(self.ok(q)['data']['document'],old['document'])
    def test_04_pinned_missing_wrong_object_type_never_fallback(self):
        self.f.accepted();q=self.request();q['selector']={'mode':'pinned','revision_id':str(uuid.uuid4())};self.error(q,'REVISION_NOT_FOUND')
        q['selector']['revision_id']=self.f.bundle.doc('Asset')[1]['revision_id'];self.error(q,'REVISION_NOT_FOUND');q=self.request();q['object_type']='Entity';self.error(q,'TYPE_MISMATCH')
        q['object_id']=str(uuid.uuid4());self.error(q,'OBJECT_NOT_FOUND')
    def test_05_closed_schema_numeric_types_identity_preserved(self):
        q=self.request(op='bank.history')
        for changes in [{'extra':1},{'limit':True},{'limit':1.0},{'snapshot_sequence':False},{'offset':-1},{'offset':10001},{'limit':101}]:
            x=copy.deepcopy(q);x.update(changes);r=self.error(x,'INVALID_REQUEST');self.assertEqual(r['request_id'],q['request_id'])
        x=self.request();x['protocol']='local-bank-query/2';self.error(x,'UNSUPPORTED_PROTOCOL');x=self.request();x['object_type']='Source';self.error(x,'UNSUPPORTED_TYPE');x=self.request();x['operation']=[];self.error(x,'UNSUPPORTED_MODE')
        x=self.request();x['selector']={'mode':'latest'};self.error(x,'INVALID_REQUEST')
    def test_06_strict_json_utf8_duplicates_depth_and_byte_limits(self):
        for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'\xff',b'\xef\xbb\xbf{}',b'{"x":"\\ud800"}',b'[]']:
            r=self.client.execute(raw);self.assertEqual(r['code'],'INVALID_REQUEST',r);self.assertNotIn('data',r)
        for raw in [b' '*16385,b'['*17+b'0'+b']'*17]:self.assertEqual(self.client.execute(raw)['code'],'LIMIT_EXCEEDED')
        q=self.request();raw=api.im.encoded(q);r=self.client.execute(raw+b' '*(16384-len(raw)));self.assertEqual(r['code'],'OBJECT_NOT_FOUND')
    def test_07_search_explicitly_unsupported_without_db(self):
        q={'protocol':api.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'bank.search','query':'hello','object_types':['Asset'],'fields':['title'],'revisions_mode':'current','snapshot_sequence':None,'limit':5,'offset':0};self.error(q,'UNSUPPORTED_MODE')
    def test_08_collection_order_pinned_members_not_new_head(self):
        self.f.accepted();q=self.request('Collection','collection.get');before=self.ok(q)['data'];self.f.accepted(fixtures.Bundle('continuation'));after=self.ok(q)['data'];self.assertEqual(before['document'],after['document']);self.assertEqual(before['member_statuses'],after['member_statuses']);self.assertTrue(all(x['availability']=='available' for x in after['member_statuses']))
    def test_09_collection_missing_member_visible_without_omission(self):
        self.f.accepted();new=self.f.bundle.clone().revision('Collection');self.f.accepted(new);member=new.doc('Collection')[1]['data']['members'][0]
        with closing(sqlite3.connect(self.f.store.db,isolation_level=None)) as c:
            trigger=c.execute("SELECT sql FROM sqlite_schema WHERE name='revisions_no_delete'").fetchone()[0];c.execute('DROP TRIGGER revisions_no_delete');c.execute('DELETE FROM revisions WHERE revision_id=?',(member['revision_id'],));c.execute(trigger)
        r=self.ok(self.request('Collection','collection.get',new));self.assertEqual(r['data']['document']['data']['members'][0],member);self.assertEqual(r['data']['member_statuses'][0]['availability'],'revision_not_found')
    def test_10_history_stable_explicit_snapshot_after_update(self):
        self.f.accepted();b=fixtures.Bundle('continuation');self.f.accepted(b);q=self.request(op='bank.history');q['limit']=1;first=self.ok(q);self.assertTrue(first['data']['has_more']);self.assertEqual(first['snapshot_sequence'],2)
        b=b.clone().revision();self.f.accepted(b);q.update(snapshot_sequence=2,offset=first['data']['next_offset']);second=self.ok(q);self.assertEqual(second['snapshot_sequence'],2);self.assertEqual(second['data']['revisions'][0]['ref']['revision_id'],self.f.bundle.doc('Annotation')[1]['revision_id']);self.assertFalse(second['data']['has_more'])
    def test_11_history_invalid_snapshot_empty_page_and_limits(self):
        self.f.accepted();q=self.request(op='bank.history');q['snapshot_sequence']=2;self.error(q,'SNAPSHOT_NOT_AVAILABLE');q['snapshot_sequence']=0;self.error(q,'OBJECT_NOT_FOUND');q.update(snapshot_sequence=None,offset=10000);r=self.ok(q);self.assertEqual(r['data']['revisions'],[]);self.assertFalse(r['data']['has_more'])
    def test_12_history_accepted_time_not_producer_time(self):
        self.f.accepted();self.f.accepted(fixtures.Bundle('continuation'));r=self.ok(self.request(op='bank.history'));self.assertEqual([x['commit_sequence'] for x in r['data']['revisions']],[2,1]);self.assertTrue(all(x['accepted_at'].endswith('Z') for x in r['data']['revisions']))
    def test_13_original_exact_private_owned_output_after_source_removal(self):
        self.f.accepted();self.remove_intake();q=self.request('Asset','bank.original');result=self.ok(q);out=result['data']['original'];raw=Path(out['path']).read_bytes();self.assertEqual(raw,self.f.bundle.files['files/report.md']);self.assertEqual(hashlib.sha256(raw).hexdigest(),out['sha256']);self.assertEqual(len(raw),out['byte_length']);self.assertTrue(Path(out['path']).is_relative_to(self.outputs));self.assertEqual(result['data']['availability'],'bytes');self.assertEqual(out['rendering'],'opaque_bytes_no_execution')
        self.client.close();self.assertEqual(Path(out['path']).read_bytes(),raw)
    def test_14_original_locator_metadata_never_fetches(self):
        b=self.f.bundle.clone().edit('Asset',lambda d:d['data'].update(storage={'mode':'locator','uri':'https://invalid.example/private?x=1','label':None}));self.f.accepted(b)
        with patch.object(api.Exporter,'create',side_effect=AssertionError('No bytes export')):
            r=self.ok(self.request('Asset','bank.original',b));self.assertEqual(r['data']['availability'],'locator_only');self.assertEqual(r['data']['uri'],'https://invalid.example/private?x=1');self.assertNotIn('original',r['data']);self.assertEqual(list(self.outputs.iterdir()),[])
    def test_15_original_destination_in_request_is_rejected(self):
        self.f.accepted();q=self.request('Asset','bank.original');q['destination']=str(self.f.temp/'caller.bin');self.error(q,'INVALID_REQUEST');self.assertFalse((self.f.temp/'caller.bin').exists())
    def test_16_corrupt_original_no_success_no_partial_export(self):
        self.f.accepted()
        with closing(sqlite3.connect(self.f.store.db)) as c:fid=c.execute("SELECT file_id FROM files WHERE path='files/report.md'").fetchone()[0]
        self.corrupt('files','file_blob',fid);self.error(self.request('Asset','bank.original'),'INTEGRITY_ERROR');self.assertEqual(list(self.outputs.iterdir()),[]);self.error(self.receipt_request(),'INTEGRITY_ERROR')
    def test_17_corrupt_document_and_receipt_no_cache_success(self):
        self.f.accepted();q=self.request();self.ok(q)
        with closing(sqlite3.connect(self.f.store.db)) as c:fid=c.execute('SELECT file_id FROM files WHERE path=?',(self.f.bundle.doc('Annotation')[0]['document_path'],)).fetchone()[0]
        self.corrupt('files','file_blob',fid);self.error(q,'INTEGRITY_ERROR')
    def test_18_canonical_receipt_corruption_blocks_detail(self):
        self.f.accepted();self.corrupt('accepted_receipts','receipt_blob',1);self.error(self.request(),'INTEGRITY_ERROR')
    def test_19_receipt_hash_mismatch_not_failed_attempt(self):
        self.f.accepted();q=self.receipt_request();q['expected_manifest_sha256']='0'*64;self.error(q,'TRANSACTION_HASH_MISMATCH');q['expected_manifest_sha256']=api.im.sha(self.f.bundle.refresh().manifest);self.ok(q)
    def test_20_busy_bounded_visible_not_empty(self):
        c=sqlite3.connect(self.f.store.db,isolation_level=None);c.execute('BEGIN EXCLUSIVE');start=time.monotonic()
        try:self.error(self.request(),'BANK_BUSY');self.assertLess(time.monotonic()-start,3)
        finally:c.execute('ROLLBACK');c.close()
        self.error(self.request(),'OBJECT_NOT_FOUND')
    def test_21_read_connection_authority_no_write_and_bytes_unchanged(self):
        self.f.accepted();before=self.f.store.db.read_bytes()
        with api.im.Store(self.f.root,contracts=self.f.c) as s:
            with api.ReadSession(s,api.Budget(self.client.limits)) as session:
                for sql in ['DELETE FROM commits','CREATE TABLE bad(x)','ATTACH DATABASE ":memory:" AS bad','PRAGMA writable_schema=ON']:
                    with self.assertRaises(sqlite3.DatabaseError):session.c.execute(sql)
        for q in [self.request(),self.request(op='bank.history'),self.receipt_request()]:self.ok(q)
        self.assertEqual(before,self.f.store.db.read_bytes())
    def test_22_export_failure_owned_cleanup_and_no_db_changes(self):
        self.f.accepted();before=self.f.store.db.read_bytes()
        def fail(name,value):
            if name=='export_chunk':raise OSError('Synthetic owned ENOSPC')
        unraisable=[]
        with patch.object(sys,'unraisablehook',unraisable.append):
            self.error(self.request('Asset','bank.original'),'BANK_UNAVAILABLE',self.open(_hook=fail));gc.collect()
        self.assertEqual(unraisable,[]);self.assertEqual(list(self.outputs.iterdir()),[]);self.assertEqual(before,self.f.store.db.read_bytes())
    def test_23_response_and_verification_budgets_no_truncation(self):
        self.f.accepted();q=self.request();self.error(q,'LIMIT_EXCEEDED',self.open(_limits={'response_bytes':300}));self.error(q,'LIMIT_EXCEEDED',self.open(_limits={'stored_bytes_per_request':1}));self.error(q,'LIMIT_EXCEEDED',self.open(_limits={'stored_metadata_bytes_per_request':1}));self.error(q,'LIMIT_EXCEEDED',self.open(_limits={'elapsed_ms':0}))
    def test_24_unknown_schema_not_defaulted(self):
        self.f.accepted();contracts=api.im.Contracts();contracts.allowed=set();self.error(self.request(),'UNSUPPORTED_SCHEMA',api.ReadAPI(self.f.root,contracts=contracts))
    def test_25_foreign_db_untouched(self):
        self.f.store.close();self.f.store.db.write_bytes(b'foreign-format');before=self.f.store.db.read_bytes();self.error(self.request(),'INTEGRITY_ERROR');self.assertEqual(self.f.store.db.read_bytes(),before)
    def test_26_output_root_overlap_and_broad_acl_rejected(self):
        self.f.accepted();c=api.ReadAPI(self.f.root,self.f.root);self.error(self.request('Asset','bank.original'),'BANK_UNAVAILABLE',c);c.close()
        broad=self.f.temp/'broad';broad.mkdir(mode=0o777);os.chmod(broad,0o777)
        if os.name=='nt':
            changed=subprocess.run(['icacls',str(broad),'/grant','*S-1-1-0:(OI)(CI)R'],capture_output=True,timeout=10);self.assertEqual(changed.returncode,0,changed.stdout+changed.stderr)
        c=api.ReadAPI(self.f.root,broad);self.error(self.request('Asset','bank.original'),'BANK_UNAVAILABLE',c);c.close();self.assertEqual(list(broad.iterdir()),[])
    def test_27_protected_export_live_native_mutation_denied(self):
        self.f.accepted();r=self.ok(self.request('Asset','bank.original'));p=Path(r['data']['original']['path'])
        if os.name=='nt':
            with self.assertRaises(OSError):p.write_bytes(b'tampered')
            with self.assertRaises(OSError):p.unlink()
            with api.im.native.Handle(p) as handle:api.im.native.verify_private_acl(handle)
        else:self.assertEqual(stat_mode(p),0o600);self.assertEqual(stat_mode(p.parent),0o700)
    def test_28_cli_restart_json_exchange_and_persistent_original(self):
        self.f.accepted();command=[sys.executable,str(Path(api.__file__)),'--bank-root',str(self.f.root),'--output-root',str(self.outputs)]
        for q in [self.request(),self.request('Asset','bank.original')]:
            p=subprocess.run(command,input=api.im.encoded(q),capture_output=True,timeout=15);self.assertEqual(p.returncode,0,p.stderr.decode(errors='replace'));r=json.loads(p.stdout);self.assertEqual(r['status'],'OK');self.assertEqual(r['request_id'],q['request_id'])
            if q['operation']=='bank.original':self.assertEqual(Path(r['data']['original']['path']).read_bytes(),self.f.bundle.files['files/report.md'])
        p=subprocess.run(command,input=b'{"bad":1}',capture_output=True,timeout=15);self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['code'],'UNSUPPORTED_PROTOCOL')
    def test_29_indexed_long_history_page_bounded_to_requested_rows(self):
        self.f.accepted();b=self.f.bundle
        for _ in range(220):b=b.clone().revision();self.f.accepted(b)
        q=self.request(op='bank.history');q.update(offset=200,limit=3);seen=[];original=api.ReadSession.document
        def counted(session,row):seen.append(row[0]);return original(session,row)
        with patch.object(api.ReadSession,'document',counted):r=self.ok(q)
        self.assertEqual(len(r['data']['revisions']),3);self.assertEqual(len(seen),3)
        with closing(sqlite3.connect(self.f.store.db)) as c:
            plan=c.execute('EXPLAIN QUERY PLAN SELECT revision_id FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 4 OFFSET 200',(q['object_id'],221)).fetchall();self.assertIn('revisions_object_history',str(plan));self.assertNotIn('USE TEMP B-TREE',str(plan))
    def test_30_original_real_64m_stream_limit_and_exact_hash(self):
        b=self.f.large(67108864);self.f.accepted(b);r=self.ok(self.request('Asset','bank.original',b));out=r['data']['original'];self.assertEqual(out['byte_length'],67108864)
        h=hashlib.sha256()
        with Path(out['path']).open('rb') as f:
            while raw:=f.read(1048576):h.update(raw)
        self.assertEqual(h.hexdigest(),out['sha256'])
    def test_31_collection_member_budget_explicit_error(self):
        self.f.accepted();self.error(self.request('Collection','collection.get'),'LIMIT_EXCEEDED',self.open(_limits={'member_count':0}))
    def test_32_current_snapshot_concurrent_writer_cannot_change_result(self):
        self.f.accepted();seen=[]
        def hook(name,value):
            if name=='snapshot_selected':
                # DELETE journal reader lock prevents later writer COMMIT; read stays at sequence1.
                out=self.f.save(fixtures.Bundle('continuation'));seen.append(out.state)
        r=self.ok(self.request(),self.open(_hook=hook));self.assertEqual(r['snapshot_sequence'],1);self.assertEqual(r['data']['ref']['revision_id'],self.f.bundle.doc('Annotation')[1]['revision_id']);self.assertEqual(seen,['RETRYABLE_BUSY']);self.f.accepted(fixtures.Bundle('continuation'))
    def test_33_sql_work_budget_interrupts_own_query(self):
        budget=api.Budget({**self.client.limits,'sqlite_vm_steps':1000})
        with api.im.Store(self.f.root,contracts=self.f.c) as store:
            with api.ReadSession(store,budget) as s:
                with self.assertRaises(sqlite3.OperationalError):s.c.execute('WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<100000) SELECT sum(x) FROM n').fetchone()
        self.assertTrue(budget.exceeded)
    def test_34_no_unrelated_blob_read_for_detail(self):
        self.f.accepted();old=api.ReadSession.file_chunks;paths=[]
        def watch(s,f,*args,**kw):paths.append(f[1]);yield from old(s,f,*args,**kw)
        with patch.object(api.ReadSession,'file_chunks',watch):self.ok(self.request())
        self.assertEqual(paths,[self.f.bundle.doc('Annotation')[0]['document_path']])
    def test_35_export_collision_does_not_overwrite_existing(self):
        self.f.accepted();export_id=str(uuid.uuid4());directory=self.outputs/export_id;fixtures.private(directory);p=directory/'original.bin';p.write_bytes(b'keep')
        with patch.object(api.uuid,'uuid4',return_value=uuid.UUID(export_id)):self.error(self.request('Asset','bank.original'),'BANK_UNAVAILABLE')
        self.assertEqual(p.read_bytes(),b'keep')
    def test_36_closed_api_never_reads_or_exports(self):
        self.f.accepted();self.client.close();self.error(self.request(),'BANK_UNAVAILABLE');self.assertEqual(list(self.outputs.iterdir()),[])
    def test_37_empty_original_valid_hash(self):
        b=self.f.large(0);self.f.accepted(b);r=self.ok(self.request('Asset','bank.original',b));p=Path(r['data']['original']['path']);self.assertEqual(p.read_bytes(),b'');self.assertEqual(r['data']['original']['sha256'],hashlib.sha256(b'').hexdigest())
    def test_38_output_response_limit_reclaims_unpublished_export(self):
        self.f.accepted();self.error(self.request('Asset','bank.original'),'LIMIT_EXCEEDED',self.open(_limits={'response_bytes':300}));self.assertEqual(list(self.outputs.iterdir()),[])
    def test_39_file_locator_never_reads_target(self):
        target=self.f.temp/'unrelated.txt';target.write_bytes(b'not imported');b=self.f.bundle.clone().edit('Asset',lambda d:d['data'].update(storage={'mode':'locator','uri':target.as_uri(),'label':'metadata only'}));self.f.accepted(b);original=Path.open
        def guarded(p,*args,**kw):
            if p==target:raise AssertionError('Locator must not fetch target')
            return original(p,*args,**kw)
        with patch.object(Path,'open',guarded):r=self.ok(self.request('Asset','bank.original',b));self.assertEqual(r['data']['availability'],'locator_only')
    def test_40_returned_document_mutation_cannot_change_bank(self):
        self.f.accepted();q=self.request();r=self.ok(q);r['data']['document']['title']='caller mutation';self.assertNotEqual(self.ok(q)['data']['document']['title'],'caller mutation')
    def test_41_first_read_recovers_owned_hot_journal_after_child_death(self):
        b=self.f.large(4*1048576);child=self.f.child('before_commit',b);self.assertEqual(child.returncode,17,child.stdout+child.stderr)
        # No helper/SQLite query precedes the read API after interrupted spill.
        self.error(self.receipt_request(b),'RECEIPT_NOT_FOUND');self.error(self.request(),'OBJECT_NOT_FOUND');self.f.accepted(b);self.ok(self.request())
    def test_42_errors_never_echo_request_content_or_paths(self):
        q=self.request();q['selector']['content']='synthetic-private-request-text';r=self.error(q,'INVALID_REQUEST');raw=api.im.encoded(r);self.assertNotIn(b'synthetic-private-request-text',raw);self.assertNotIn(str(self.f.temp).encode(),raw);self.assertLessEqual(len(r['message'].encode()),8192)

def stat_mode(p):return p.stat().st_mode&0o777
class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[];self.bad=set()
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'id':test._testMethodName,'expected':'all integration assertions pass','observed':'PASS'})
    def failed(self,test,err):self.bad.add(test._testMethodName);self.cases.append({'id':test._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(err,test)})
    def addFailure(self,test,err):super().addFailure(test,err);self.failed(test,err)
    def addError(self,test,err):super().addError(test,err);self.failed(test,err)
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));folder=Path(__file__).parent;at=api.im.now();report={'record_kind':'synthetic_R1_read_API_evidence','at':at,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'snapshot_adapter':'actual Windows secure reader handles' if os.name=='nt' else 'trusted portable fixture only','tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'source_sha256':{p.name:api.im.sha(p.read_bytes()) for p in [folder/'bank_read.py',folder/'test_reads.py',folder/'result.schema.json',folder/'LIMITS.json']},'limitations':['Synthetic private owned resources only, no real Bank/UI/search/release','Trusted app/operator config/current owner/root parents','No hardware/private deployment acceptance','Exports protected during API context; later CLI consumers verify returned hash/size']}
    name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';p=folder/name
    if p.exists():h=folder/'TEST_HISTORY';h.mkdir(exist_ok=True);shutil.copyfile(p,h/(name+'-'+uuid.uuid4().hex+'.json'))
    p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');p=folder/'ISSUES.json';issues=json.loads(p.read_text(encoding='utf-8'));known={i['id']:i for i in issues['issues']}
    for case in result.cases:
        iid='READ-TEST-'+case['id'];i=known.get(iid)
        if case['observed']=='FAIL':
            if i is None:i={'id':iid,'title':'Integration assertion: '+case['id'],'history':[]};issues['issues'].append(i)
            i['status']='open';i['history'].append({'at':at,'status':'open','evidence':name,'detail':case['detail']})
        elif i and i['status']=='open':i['status']='resolved';i['history'].append({'at':at,'status':'resolved','evidence':name,'note':'Integration rerun passed; previous failure retained.'})
    p.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':sorted(result.bad),'report':str(folder/name)}),flush=True);sys.exit(not result.wasSuccessful())
