"""Entrypoint integration; native uses real secure transport, portable fixture only."""
from pathlib import Path
from contextlib import closing
import copy,errno,json,os,platform,shutil,socket,sqlite3,subprocess,sys,unittest,uuid
from unittest.mock import patch
import commands as app
sys.path.insert(0,str(app.ROOT/'EXPERIMENTS/sqlite_importer'))
import test_importer as fixtures
OriginalStore=app.im.Store
class PortableStore(OriginalStore):
    def __init__(self,*a,**kw):kw.setdefault('_snapshot_type',fixtures.FixtureSnapshot);super().__init__(*a,**kw)
def portable_read(intake,tx,stage,*,policy_bytes,schema):
    # Independent bounded bytes/inventory fixture; no Windows confinement claim.
    policy=app.im.reader.Policy(policy_bytes);p=Path(intake)/tx
    try:
        if not(p/'READY.json').exists():return app.im.reader.Result('INCOMPLETE','READY_NOT_PUBLISHED')
        def small(path,cap):
            if path.stat().st_size>cap:raise app.im.reader.Rejected('LIMIT_EXCEEDED')
            return path.read_bytes()
        readyraw=small(p/'READY.json',policy['ready_bytes']);ready=app.im.reader.strict_json(readyraw,policy['ready_bytes'],64);raw=small(p/'manifest.json',policy['manifest_bytes']);m=app.im.reader.strict_json(raw,policy['manifest_bytes'],64)
        for x in [ready,m]:app.im.Contracts().envelope(x)
        if ready['transaction_id']!=tx or m['transaction_id']!=tx or ready['manifest_byte_length']!=len(raw) or ready['manifest_sha256']!=app.im.sha(raw):raise app.im.reader.Rejected('MANIFEST_INTEGRITY')
        if len(m['operations'])>policy['operations'] or len(m['files'])>policy['files']:raise app.im.reader.Rejected('LIMIT_EXCEEDED')
        files={};total=len(raw)+len(readyraw)
        for f in m['files']:
            name=app.im.reader.valid_path(f['path']);path=p/name
            if path.is_symlink() or path.stat().st_nlink!=1:raise app.im.reader.Rejected('HARDLINK')
            b=small(path,policy['file_bytes']);total+=len(b)
            if len(b)!=f['byte_length'] or app.im.sha(b)!=f['sha256']:raise app.im.reader.Rejected('FILE_INTEGRITY')
            files[name]=b
        if total>policy['package_bytes']:raise app.im.reader.Rejected('LIMIT_EXCEEDED')
        actual={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file()}
        if actual!=set(files)|{'manifest.json','READY.json'}:raise app.im.reader.Rejected('INVENTORY_MISMATCH')
        b=fixtures.Bundle();b.m=m;b.files=files;s=fixtures.FixtureSnapshot(b,policy_bytes);s.manifest_bytes=raw;s.ready_bytes=readyraw;s.manifest_sha256=app.im.sha(raw);return app.im.reader.Result('VERIFIED_TRANSPORT','OK',s)
    except app.im.reader.Rejected as e:return app.im.reader.Result('REJECTED',str(e))
    except OSError:return app.im.reader.Result('IO_ERROR','STORAGE_IO_ERROR')
def portable_patch():
    if os.name!='nt':app.im.Store=PortableStore;app.im.reader.read_package=portable_read

class Tests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');self.f.setUp();self.cache=self.f.temp/'cache';fixtures.private(self.cache);self.outputs=self.f.temp/'output';fixtures.private(self.outputs);self.clients=[];self.snapshots=[];self.c=self.open()
    def tearDown(self):
        for c in self.clients:c.close()
        self.f.tearDown()
    def open(self,**kw):
        def tracked(*a,**k):
            r=(app.im.reader.read_package if os.name=='nt' else portable_read)(*a,**k)
            if r.snapshot:self.snapshots.append(r.snapshot)
            return r
        kw.setdefault('_transport',tracked)
        if os.name!='nt':kw.setdefault('_store_factory',PortableStore)
        c=app.Controller(self.f.root,intake_root=self.f.intake,stage_root=self.f.stage,cache_root=self.cache,output_root=self.outputs,**kw);self.clients.append(c);return c
    def publish(self,b=None,root=None):
        b=(b or self.f.bundle).clone().refresh();p=(root or self.f.intake)/b.m['transaction_id'];fixtures.private(p)
        for name,raw in {**b.files,'manifest.json':b.manifest,'READY.json':b.ready}.items():
            q=p/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
        return b,p
    def saved(self,b=None,client=None,operation='bank.save'):
        b,p=self.publish(b);r=(client or self.c).save(operation,b.m['transaction_id']);self.assertEqual(r['status'],'ACCEPTED',r);self.assertEqual(r['receipt']['manifest_sha256'],app.im.sha(b.manifest));self.assertEqual(r['cleanup_status'],'complete');self.assertFalse(list(self.f.stage.iterdir()));self.assertTrue((p/'READY.json').exists());return b,r
    def q(self,kind='Annotation',op='bank.get',bundle=None):
        b=bundle or self.f.bundle;_,d=b.doc(kind);q={'protocol':app.read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':op,'object_type':kind,'object_id':d['object_id']}
        if op in ['bank.get','collection.get']:q['selector']={'mode':'current'}
        elif op=='bank.original':q['revision_id']=d['revision_id']
        elif op=='bank.history':q.update(snapshot_sequence=None,limit=1,offset=0)
        return q
    def receipt(self,b=None):return {'protocol':app.read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'receipt.get','transaction_id':(b or self.f.bundle).m['transaction_id'],'expected_manifest_sha256':None}
    def searchq(self):return {'protocol':app.read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'bank.search','object_types':['Asset','Entity','Annotation','Collection'],'fields':['title','body','content'],'query':'synthetic','revisions_mode':'current','snapshot_sequence':None,'limit':10,'offset':0}
    def query(self,q,client=None):return (client or self.c).query(app.im.encoded(q))
    def count(self):return self.f.count()[0]
    def assert_error(self,r,code):self.assertEqual(r['status'],'ERROR',r);self.assertEqual(r['code'],code,r);self.assertNotIn('data',r)
    def args(self):return ['--bank-root',str(self.f.root),'--intake-root',str(self.f.intake),'--stage-root',str(self.f.stage),'--cache-root',str(self.cache),'--output-root',str(self.outputs)]
    def cli(self,action,raw=None,tx=None,phase=None,extra=None):
        command=[sys.executable,'-X','utf8',str(Path(__file__)),'--cli'] if os.name!='nt' or phase else [sys.executable,'-X','utf8',str(Path(app.__file__))]
        if phase:command+=['--phase',phase]
        command+=[action,*self.args()]
        if tx:command+=['--transaction-id',tx]
        command+=extra or [];return subprocess.run(command,input=raw,capture_output=True,timeout=25)
    def test_01_actual_cli_save_receipt_four_reads_rebuild_search(self):
        b,p=self.publish();r=self.cli('save',tx=b.m['transaction_id']);self.assertEqual(r.returncode,0,r.stderr);receipt=json.loads(r.stdout)['receipt'];self.assertEqual(self.count(),1)
        for kind in ['Asset','Entity','Annotation','Collection']:
            q=self.q(kind,'collection.get' if kind=='Collection' else 'bank.get');r=self.cli('query',app.im.encoded(q));self.assertEqual(r.returncode,0,r.stdout);data=json.loads(r.stdout)['data'];self.assertEqual(data['document'],b.doc(kind)[1])
        r=self.cli('query',app.im.encoded(self.receipt()));self.assertEqual(json.loads(r.stdout)['data']['receipt'],receipt)
        self.assertEqual(self.cli('rebuild-search').returncode,0);r=self.cli('query',app.im.encoded(self.searchq()));self.assertEqual(r.returncode,0,r.stdout);self.assertGreater(json.loads(r.stdout)['data']['total_matches'],0)
    def test_02_actual_cli_original_retained_after_intake_removal(self):
        b,r=self.saved();shutil.rmtree(self.f.intake/b.m['transaction_id']);q=self.q('Asset','bank.original');p=self.cli('query',app.im.encoded(q));self.assertEqual(p.returncode,0,p.stderr);data=json.loads(p.stdout)['data'];out=Path(data['original']['path']);raw=out.read_bytes();self.assertEqual(app.im.sha(raw),data['original']['sha256']);self.assertEqual(raw,b.files[b.doc('Asset')[1]['data']['storage']['file_path']])
    def test_03_actual_cli_update_old_pinned_reopen_replay_after_update(self):
        b,r=self.saved();old=self.query(self.q())['data']['ref'];new,p=self.publish(fixtures.Bundle('continuation'));self.assertEqual(self.cli('save',tx=new.m['transaction_id']).returncode,0);self.assertEqual(self.count(),2)
        q=self.q();q['selector']={'mode':'pinned','revision_id':old['revision_id']};p=self.cli('query',app.im.encoded(q));self.assertEqual(json.loads(p.stdout)['data']['ref'],old);replay=self.cli('save',tx=b.m['transaction_id']);self.assertEqual(replay.returncode,0);self.assertEqual(json.loads(replay.stdout)['status'],'REPLAY');self.assertEqual(self.count(),2);self.assertEqual(self.query(self.receipt())['data']['receipt'],r['receipt'])
    def test_04_collection_only_alias_keeps_members(self):
        self.saved();b=self.f.bundle.clone().revision('Collection');b,p=self.publish(b);r=self.cli('collection-save',tx=b.m['transaction_id']);self.assertEqual(r.returncode,0,r.stdout);self.assertEqual(json.loads(r.stdout)['operation'],'collection.save');self.assertEqual(self.query(self.q('Collection','collection.get',b))['data']['document']['data']['members'],b.doc('Collection')[1]['data']['members'])
    def test_05_collection_mixed_rejected_before_import_no_partial(self):
        b,p=self.publish()
        with patch.object(OriginalStore,'import_snapshot',side_effect=AssertionError('Must not import')):r=self.c.save('collection.save',b.m['transaction_id'])
        self.assertEqual(r['status'],'REJECTED',r);self.assertEqual(r['code'],'COLLECTION_ONLY_REQUIRED');self.assertEqual(self.count(),0);self.assertFalse(list(self.f.stage.iterdir()))
    def test_06_domain_schema_rejected_without_mutation(self):
        b=self.f.bundle.clone().edit('Annotation',lambda d:d.update(schema='bank.types/999'));b,p=self.publish(b);r=self.c.save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'REJECTED',r);self.assertEqual(self.count(),0)
    def test_07_same_transaction_changed_hash_conflict_retains_original(self):
        b,r=self.saved();p=self.f.intake/b.m['transaction_id'];shutil.rmtree(p);changed,p=self.publish(b.clone().edit('Annotation',lambda d:d['data'].update(body='Different')));out=self.c.save('bank.save',b.m['transaction_id']);self.assertEqual(out['status'],'CONFLICT',out);self.assertEqual(out['code'],'TRANSACTION_ID_REUSED');self.assertEqual(self.count(),1);self.assertEqual(self.query(self.receipt())['data']['receipt'],r['receipt'])
    def test_08_multiobject_stale_base_atomic(self):
        self.saved();b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4())
        for o in b.m['operations']:
            d=json.loads(b.files[o['document_path']]);o['base_revision_id']=o['revision_id'];o['revision_id']=str(uuid.uuid4());d['revision_id']=o['revision_id'];b.files[o['document_path']]=app.im.encoded(d)
        b.m['operations'][-1]['base_revision_id']=str(uuid.uuid4());b,p=self.publish(b);r=self.c.save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'CONFLICT',r);self.assertEqual(self.count(),1)
    def test_09_invalid_identity_and_operation_before_io(self):
        with patch.object(self.c,'transport',side_effect=AssertionError('No I/O')):
            for tx in [None,True,'../bank','A'*36]:r=self.c.save('bank.save',tx);self.assertEqual(r['status'],'REJECTED');self.assertIsNone(r['transaction_id'])
            self.assertEqual(self.c.save('bad',str(uuid.uuid4()))['status'],'REJECTED')
        self.assertEqual(self.count(),0)
    def test_10_absolute_disjoint_roots_before_transport(self):
        b,p=self.publish()
        for role,path in [('stage',self.f.root/'stage'),('cache',self.f.intake),('output',Path('relative'))]:
            c=self.open();c.roots[role]=path
            with patch.object(c,'transport',side_effect=AssertionError('No intake')):r=c.save('bank.save',b.m['transaction_id'])
            self.assertEqual(r['status'],'IO_ERROR',r)
        self.assertEqual(self.count(),0)
    def test_11_actual_hardlink_payload_refused(self):
        b,p=self.publish();name=next(iter(b.files));os.link(p/name,self.f.temp/'alias');r=self.c.save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'REJECTED',r);self.assertEqual(self.count(),0)
    def test_12_incomplete_tampered_extra_truncated_not_accepted(self):
        for case in ['missing_ready','tamper','extra','truncated']:
            b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4());b,p=self.publish(b)
            if case=='missing_ready':(p/'READY.json').unlink()
            elif case=='tamper':(p/next(iter(b.files))).write_bytes(b'bad')
            elif case=='extra':(p/'extra.txt').write_bytes(b'bad')
            else:(p/'manifest.json').write_bytes(b'{')
            r=self.c.save('bank.save',b.m['transaction_id']);self.assertIn(r['status'],['INCOMPLETE','REJECTED']);self.assertEqual(self.count(),0)
    def test_13_transport_descriptor_limit_no_partial(self):
        b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4());b.refresh();b.m['files'][0]['byte_length']=self.f.c.policy['file_bytes']+1;raw=app.im.encoded(b.m);ready=app.im.encoded({'protocol':app.im.reader.PROTOCOL,'transaction_id':b.m['transaction_id'],'manifest_byte_length':len(raw),'manifest_sha256':app.im.sha(raw)});p=self.f.intake/b.m['transaction_id'];fixtures.private(p);(p/'manifest.json').write_bytes(raw);(p/'READY.json').write_bytes(ready);r=self.c.save('bank.save',b.m['transaction_id']);self.assertIn(r['status'],['REJECTED','IO_ERROR']);self.assertEqual(self.count(),0)
    def test_14_absent_bank_not_initialized_no_transport(self):
        b,p=self.publish();c=self.open();c.roots['bank']=self.f.temp/'absent'
        with patch.object(c,'transport',side_effect=AssertionError('No intake')):r=c.save('bank.save',b.m['transaction_id'])
        self.assertNotIn(r['status'],['ACCEPTED','REPLAY','UNKNOWN']);self.assertFalse(c.roots['bank'].exists())
    def test_15_existing_bank_busy_retryable_exit_mapping(self):
        b,p=self.publish();lock=sqlite3.connect(self.f.store.db,isolation_level=None);lock.execute('BEGIN EXCLUSIVE')
        try:r=self.c.save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'RETRYABLE_BUSY',r);self.assertEqual(app.exit_code(r),3)
        finally:lock.close()
        self.assertEqual(self.count(),0)
    def test_16_reader_io_cancelled_preserved_no_fabricated_receipt(self):
        for state in ['IO_ERROR','CANCELLED']:
            c=self.open(_transport=lambda *a,**k:app.im.reader.Result(state,'STORAGE_IO_ERROR' if state=='IO_ERROR' else 'CANCELLED'));r=c.save('bank.save',str(uuid.uuid4()));self.assertEqual(r['status'],state);self.assertIsNone(r['receipt']);self.assertIsNone(r['manifest_sha256'])
    def test_17_real_importer_fault_states_and_unknown_receipt_recovery(self):
        for state in ['IO_ERROR','CANCELLED','UNKNOWN']:
            b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4());b,p=self.publish(b)
            def factory(*a,**kw):
                def hook(name,value):
                    if name==('after_commit' if state=='UNKNOWN' else 'before_commit'):
                        if state=='CANCELLED':raise app.im.Cancelled()
                        raise OSError(errno.EIO,'Payload must not leak')
                s=(OriginalStore if os.name=='nt' else PortableStore)(*a,**kw,_hook=hook)
                if state=='UNKNOWN':s.get_receipt=lambda *a,**k:(_ for _ in ()).throw(OSError(errno.EIO,'Recovery hidden'))
                return s
            c=self.open(_store_factory=factory);r=c.save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],state,r);self.assertIsNone(r['receipt']);self.assertNotIn('Payload',json.dumps(r))
            if state=='UNKNOWN':self.assertEqual(self.query(self.receipt(b))['status'],'OK');self.assertEqual(self.c.save('bank.save',b.m['transaction_id'])['status'],'REPLAY')
        self.assertEqual(self.count(),1)
    def test_18_after_import_response_failure_unknown_then_original_receipt(self):
        def hook(name,value):
            if name=='after_import':raise OSError('Do not expose body')
        b,p=self.publish();r=self.open(_hook=hook).save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'UNKNOWN',r);self.assertIsNone(r['receipt']);self.assertEqual(self.count(),1);self.assertEqual(self.query(self.receipt())['data']['receipt']['status'],'ACCEPTED');self.assertEqual(self.c.save('bank.save',b.m['transaction_id'])['status'],'REPLAY')
    def test_19_interrupt_before_and_after_import_closes_snapshot(self):
        for phase in ['before_import','after_import']:
            b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4());b,p=self.publish(b)
            def hook(name,value):
                if name==phase:raise KeyboardInterrupt()
            r=self.open(_hook=hook).save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'CANCELLED' if phase=='before_import' else 'UNKNOWN');self.assertFalse(list(self.f.stage.iterdir()))
        self.assertEqual(self.count(),1)
    def test_20_cleanup_failure_does_not_negate_known_acceptance(self):
        def transport(*a,**kw):
            r=(app.im.reader.read_package if os.name=='nt' else portable_read)(*a,**kw);close=r.snapshot.close
            def fail():close();raise OSError('Cleanup issue')
            r.snapshot.close=fail;return r
        b,p=self.publish();r=self.open(_transport=transport).save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'ACCEPTED',r);self.assertEqual(r['cleanup_status'],'failed');self.assertEqual(r['diagnostic'],'SNAPSHOT_CLEANUP_FAILED');self.assertEqual(self.count(),1);self.assertFalse(list(self.f.stage.iterdir()))
    def test_21_result_output_limit_after_commit_unknown_not_rejected(self):
        b,p=self.publish();r=self.open(_limits={'save_response_bytes':100}).save('bank.save',b.m['transaction_id']);self.assertEqual(r['status'],'UNKNOWN',r);self.assertEqual(self.count(),1);self.assertEqual(self.query(self.receipt())['status'],'OK')
    def test_22_actual_owned_process_death_before_after_commit_restart(self):
        for phase in ['before_commit','after_commit']:
            b=self.f.bundle.clone();b.m['transaction_id']=str(uuid.uuid4())
            if phase=='after_commit':b=fixtures.Bundle.entity()
            b,p=self.publish(b);r=self.cli('save',tx=b.m['transaction_id'],phase=phase);self.assertEqual(r.returncode,71 if phase=='before_commit' else 72,r.stderr)
            q=self.query(self.receipt(b));self.assertEqual(q['status'],'ERROR' if phase=='before_commit' else 'OK',q)
            out=self.cli('save',tx=b.m['transaction_id']);self.assertEqual(out.returncode,0,out.stdout);self.assertEqual(json.loads(out.stdout)['status'],'ACCEPTED' if phase=='before_commit' else 'REPLAY')
        self.assertEqual(self.count(),2)
    def test_23_closed_read_queries_identity_and_limits(self):
        self.saved();q=self.q();q['arbitrary_path']='data';self.assert_error(self.query(q),'INVALID_REQUEST')
        for raw in [b'NaN',b'{"a":1,"a":2}',b'\xff',b'['*18+b']'*18,b'x'*16385]:self.assertEqual(self.c.query(raw)['status'],'ERROR')
        q=self.searchq();q['limit']=True;self.assert_error(self.query(q),'INVALID_REQUEST');q=self.searchq();q['query']=' '*5;self.assert_error(self.query(q),'INVALID_REQUEST');q=self.q();q['operation']='bank.save';self.assert_error(self.query(q),'UNSUPPORTED_MODE')
    def test_24_history_snapshot_paging_cli_restart(self):
        self.saved();self.saved(fixtures.Bundle('continuation'));q=self.q(op='bank.history');r=self.cli('query',app.im.encoded(q));first=json.loads(r.stdout);self.assertEqual(first['status'],'OK');q.update(snapshot_sequence=first['snapshot_sequence'],offset=1);r=self.cli('query',app.im.encoded(q));second=json.loads(r.stdout);self.assertEqual(second['snapshot_sequence'],2);self.assertNotEqual(first['data']['revisions'][0]['ref'],second['data']['revisions'][0]['ref'])
    def test_25_no_save_index_coupling_stale_missing_profile_and_corruption(self):
        with patch.object(app.search.SearchAPI,'rebuild',side_effect=AssertionError('Explicit only')):self.saved()
        self.assert_error(self.query(self.searchq()),'INDEX_UNAVAILABLE');self.assertEqual(self.c.rebuild()['status'],'BUILT');self.saved(fixtures.Bundle('continuation'));self.assert_error(self.query(self.searchq()),'INDEX_NOT_READY');self.assertEqual(self.c.rebuild()['status'],'BUILT')
        with sqlite3.connect(self.cache/'search-cache.sqlite3') as c:c.execute("UPDATE generation SET unicode_version='bad'")
        self.assert_error(self.query(self.searchq()),'INDEX_PROFILE_MISMATCH');self.assertEqual(self.c.rebuild()['status'],'BUILT');(self.cache/'search-cache.sqlite3').write_bytes(b'bad');self.assert_error(self.query(self.searchq()),'INDEX_UNAVAILABLE');self.assertEqual(self.count(),2)
    def test_26_export_response_failure_no_unpublished_files(self):
        self.saved();c=self.open(_read_limits={'response_bytes':100});self.assert_error(self.query(self.q('Asset','bank.original'),c),'LIMIT_EXCEEDED');self.assertFalse(list(self.outputs.iterdir()))
    def test_27_closed_controller_and_missing_role_no_initialization(self):
        b,p=self.publish();self.c.close();self.assertNotIn(self.c.save('bank.save',b.m['transaction_id'])['status'],['ACCEPTED','REPLAY']);self.assert_error(self.query(self.q()),'BANK_UNAVAILABLE');c=self.open();c.roots['stage']=None;self.assertEqual(c.save('bank.save',b.m['transaction_id'])['status'],'IO_ERROR');self.assertEqual(self.count(),0)
    def test_28_no_network_fetch_and_locators_metadata_only(self):
        self.saved()
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No network')):self.assertEqual(self.query(self.q())['status'],'OK');self.assertEqual(self.c.rebuild()['status'],'BUILT');self.assertEqual(self.query(self.searchq())['status'],'OK')
    def test_29_actual_cli_unknown_arguments_bounded_no_payload_echo(self):
        r=self.cli('query',extra=['--sql','PRIVATE_PAYLOAD']);self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout),{'status':'ERROR','code':'INVALID_CLI'});self.assertNotIn(b'PRIVATE_PAYLOAD',r.stdout+r.stderr)
    def test_30_actual_closed_stdout_exit_unknown_receipt_recovery(self):
        b,p=self.publish();cmd=[sys.executable,'-X','utf8',str(Path(__file__)),'--cli'] if os.name!='nt' else [sys.executable,'-X','utf8',str(Path(app.__file__))];cmd+=['save',*self.args(),'--transaction-id',b.m['transaction_id']];proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);proc.stdout.close();err=proc.stderr.read();proc.stderr.close();proc.wait(timeout=25);self.assertEqual(proc.returncode,4,err);self.assertEqual(self.query(self.receipt())['status'],'OK');self.assertEqual(self.count(),1)

class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[];self.bad=[]
    def addSuccess(self,t):super().addSuccess(t);self.cases.append({'id':t._testMethodName,'expected':'entrypoint integration assertions pass','observed':'PASS'})
    def failure(self,t,e):self.bad.append(t._testMethodName);self.cases.append({'id':t._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(e,t)})
    def addFailure(self,t,e):super().addFailure(t,e);self.failure(t,e)
    def addError(self,t,e):super().addError(t,e);self.failure(t,e)
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--cli':
        portable_patch();args=sys.argv[2:]
        if args[:1]==['--phase']:
            phase=args[1];args=args[2:];base=app.im.Store
            class FaultStore(base):
                def __init__(self,*a,**k):
                    def hook(name,value):
                        if name==phase:os._exit(71 if phase=='before_commit' else 72)
                    super().__init__(*a,**k,_hook=hook)
            app.im.Store=FaultStore
        sys.exit(app.main(args))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));folder=Path(__file__).parent;at=app.im.now();name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';report={'record_kind':'synthetic_R1_local_command_adapter_evidence','at':at,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'snapshot_adapter':'actual Windows secure reader handles' if os.name=='nt' else 'bounded portable fixture only','tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'source_sha256':{p.name:app.im.sha(p.read_bytes()) for p in [folder/'commands.py',folder/'test_commands.py',folder/'save_result.schema.json',folder/'LIMITS.json']},'limitations':['Synthetic private existing Bank; no user import/install/UI/producer publication/release','Portable fixture transport is not native NTFS confinement evidence','Trusted code/operator/owner/root parents; previous components unchanged','Owned process-death tests are not physical power loss; orphan stage remains quarantined until explicit maintenance']}
    p=folder/name
    if p.exists():h=folder/'TEST_HISTORY';h.mkdir(exist_ok=True);shutil.copyfile(p,h/(name+'-'+uuid.uuid4().hex+'.json'))
    p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');p=folder/'ISSUES.json';issues=json.loads(p.read_text(encoding='utf-8'));known={i['id']:i for i in issues['issues']}
    for c in report['cases']:
        iid='CMD-TEST-'+c['id'];i=known.get(iid)
        if c['observed']=='FAIL':
            if i is None:i={'id':iid,'title':'Integration assertion '+c['id'],'history':[]};issues['issues'].append(i);known[iid]=i
            i['status']='open';i['history'].append({'at':at,'status':'open','evidence':name,'detail':c['detail']})
        elif i and i['status']=='open':i['status']='resolved_local' if os.name!='nt' else 'resolved_native';i['history'].append({'at':at,'status':i['status'],'evidence':name,'note':'Rerun passed; previous failure retained.'})
    p.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':result.bad,'report':str(folder/name)}),flush=True);sys.exit(not result.wasSuccessful())
