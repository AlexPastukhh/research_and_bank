"""Independent adversarial regressions for AWR fixes; owned synthetic roots only."""
from pathlib import Path
import copy,json,os,sqlite3,subprocess,sys,time,unittest,uuid
ROOT=Path(__file__).resolve().parents[2]
for folder in ['secure_intake','sqlite_importer','bank_read_api','lexical_search','local_command_adapter','local_ui']:
    sys.path.insert(0,str(ROOT/'EXPERIMENTS'/folder))
import importer as im,test_importer as fx,reader,bank_read as read,search,commands,presenter
MEASUREMENTS=[]
class Tests(unittest.TestCase):
    def setUp(self):
        self.f=fx.Tests('test_01_supported_atomic_reopen_original_receipt');self.f.setUp()
    def tearDown(self):self.f.tearDown()
    def limited(self,**limits):return self.f.open_store(_work_limits=limits)
    def refs_batch(self,size=1048576):
        refs=[]
        for i in range(3):
            b=fx.Bundle();op,d=b.doc('Asset');b.m['transaction_id']=str(uuid.uuid4());oid=str(uuid.uuid4());rid=str(uuid.uuid4());op.update(object_id=oid,revision_id=rid,base_revision_id=None);d.update(object_id=oid,revision_id=rid,title='Old original '+str(i));d['provenance']['derived_from']=[];path=d['data']['storage']['file_path'];raw=bytes([65+i])*size;d['data']['storage'].update(byte_length=size,sha256=im.sha(raw));b.m['operations']=[op];b.files={op['document_path']:im.encoded(d),path:raw};self.assertEqual(self.f.save(b).state,'ACCEPTED');refs.append(read.ref(d))
        template=fx.Bundle();op,old=template.doc('Annotation');batch=fx.Bundle();batch.m['transaction_id']=str(uuid.uuid4());batch.m['operations']=[];batch.files={}
        for i in range(64):
            d=copy.deepcopy(old);d.update(object_id=str(uuid.uuid4()),revision_id=str(uuid.uuid4()),title='New note '+str(i));d['data']['targets']=copy.deepcopy(refs);d['provenance']['derived_from']=[];path='objects/note-'+str(i)+'.json';batch.m['operations'].append({**op,'object_id':d['object_id'],'revision_id':d['revision_id'],'base_revision_id':None,'document_path':path});batch.files[path]=im.encoded(d)
        return batch
    def test_01_numeric_json_boundary_codes(self):
        for raw,code in [(b'{"n":'+b'1'*5000+b'}','INVALID_JSON'),(b'{"a":1,"a":2}','DUPLICATE_JSON_KEY'),(b'{"a":NaN}','NONFINITE_JSON'),(b'{"a":"\\ud800"}','INVALID_JSON'),(b'[[[0]]]','JSON_DEPTH'),(b'\xef\xbb\xbf{}','JSON_BOM')]:
            with self.subTest(code=code):
                with self.assertRaisesRegex(reader.Rejected,'^'+code+'$'):reader.strict_json(raw,16384,2)
    def test_02_invalid_trusted_policy_before_resources(self):
        before=list(self.f.stage.iterdir())
        with self.assertRaisesRegex(reader.ConfigurationError,'^INVALID_POLICY$'):reader.read_package(self.f.intake,self.f.bundle.m['transaction_id'],self.f.stage,policy_bytes=b'{"n":'+b'1'*5000+b'}')
        self.assertEqual(list(self.f.stage.iterdir()),before)
    @unittest.skipUnless(os.name=='nt','Actual Windows transport only')
    def test_03_real_ready_manifest_document_long_integer_no_stage(self):
        import test_reader as tr
        for place in ['READY','manifest','document']:
            f=tr.Tests('test_01_supported_fixture_snapshot_lifetime');f.setUp()
            try:
                huge=b'{"n":'+b'1'*5000+b'}'
                if place=='READY':(f.p/'READY.json').write_bytes(huge)
                elif place=='manifest':f.publish(manifest=huge)
                else:
                    (f.p/'document.json').write_bytes(huge);f.m['files'][0].update(byte_length=len(huge),sha256=im.sha(huge));f.publish()
                result=f.read();self.assertEqual((result.status,result.code),('REJECTED','INVALID_JSON'));self.assertEqual(list(f.stage.iterdir()),[])
            finally:f.tearDown()
    @unittest.skipUnless(os.name=='nt','Actual Windows ACL fixtures only')
    def test_04_individual_intake_acl_entries_refused(self):
        import test_reader as tr
        for place in ['READY.json','manifest.json','payload.bin','document.json','nested','nested/payload.bin']:
            f=tr.Tests('test_01_supported_fixture_snapshot_lifetime');f.setUp()
            try:
                if place.startswith('nested'):f.add('nested/payload.bin',b'private payload');f.publish()
                target=f.p/place;before=f.fingerprint();self.grant(target);result=f.read();self.assertEqual((result.status,result.code),('REJECTED','UNTRUSTED_DACL'));self.assertEqual(f.fingerprint(),before);self.assertEqual(list(f.stage.iterdir()),[])
            finally:f.tearDown()
    def grant(self,p):
        cp=subprocess.run(['icacls',str(p),'/grant','*S-1-1-0:(F)'],capture_output=True,timeout=10);self.assertEqual(cp.returncode,0)
    @unittest.skipUnless(os.name=='nt','Actual Windows file guards only')
    def test_05_database_acl_rejects_save_read_and_receipt(self):
        self.assertEqual(self.f.save().state,'ACCEPTED');before=self.f.store.db.read_bytes();self.grant(self.f.store.db)
        out=self.f.save();self.assertNotIn(out.state,['ACCEPTED','REPLAY']);self.assertEqual(self.f.store.db.read_bytes(),before)
        with self.assertRaises(im.native.SafetyError):self.f.store.get_receipt(self.f.bundle.m['transaction_id'])
        with read.ReadAPI(self.f.root) as api:
            d=self.f.bundle.doc('Annotation')[1];out=api.execute(im.encoded({'protocol':read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'bank.get','object_type':d['object_type'],'object_id':d['object_id'],'selector':{'mode':'current'}}));self.assertEqual(out['status'],'ERROR');self.assertNotIn('data',out)
    @unittest.skipUnless(os.name=='nt','Actual Windows sidecar file guards only')
    def test_06_preexisting_sidecar_acl_or_link_checked_before_connect(self):
        for kind in ['acl','hardlink','wal']:
            suffix='-wal' if kind=='wal' else '-journal';p=Path(str(self.f.store.db)+suffix)
            if kind=='hardlink':
                self.f.store.close();target=self.f.temp/'hardlink-original';target.write_bytes(b'alias');os.link(target,p);self.f.store=self.f.open_store()
            else:p.write_bytes(b'preexisting unsafe fixture')
            if kind=='acl':self.grant(p)
            before=p.read_bytes();db=self.f.store.db.read_bytes();out=self.f.save();self.assertNotIn(out.state,['ACCEPTED','REPLAY']);self.assertEqual(p.read_bytes(),before);self.assertEqual(self.f.store.db.read_bytes(),db);p.unlink()
    @unittest.skipUnless(os.name=='nt','Actual Windows cache file guards only')
    def test_07_cache_and_existing_cache_journal_acl_refused(self):
        self.f.save();cache=self.f.temp/'cache';im.native.private_directory(cache)
        with search.SearchAPI(self.f.root,cache) as api:
            self.assertEqual(api.rebuild()['status'],'BUILT');p=cache/'search-cache.sqlite3';before=p.read_bytes();self.grant(p);self.assertEqual(api.rebuild()['status'],'ERROR');self.assertEqual(p.read_bytes(),before)
            cp=subprocess.run(['icacls',str(p),'/remove:g','*S-1-1-0'],capture_output=True,timeout=10);self.assertEqual(cp.returncode,0)
            j=Path(str(p)+'-journal');j.write_bytes(b'unsafe journal');self.grant(j);before=j.read_bytes();self.assertEqual(api.rebuild()['status'],'ERROR');self.assertEqual(j.read_bytes(),before)
    def test_08_three_old_commits_once_compact_bounded(self):
        batch=self.refs_batch();calls=[];blob=[];summaries=[];store=self.f.store;old=store._verify_commit;oldblob=store._verify_blob
        def verify(c,seq,**kw):
            calls.append(seq);result=old(c,seq,**kw)
            if kw.get('_compact'):summaries.extend(result[1].values());self.assertTrue(all(set(d)=={'revision_id','object_type'} for d in result[1].values()))
            return result
        def b(c,row,cap,collect=False):blob.append(row[2]);return oldblob(c,row,cap,collect)
        store._verify_commit=verify;store._verify_blob=b;start=time.monotonic();out=self.f.save(batch);seconds=time.monotonic()-start
        self.assertEqual(out.state,'ACCEPTED');self.assertEqual(len(calls),3);self.assertEqual(len(set(calls)),3);self.assertEqual(len(blob),6);self.assertLess(sum(blob),4*1048576);self.assertEqual(len(summaries),3)
        MEASUREMENTS.append({'scenario':'64x3 refs','commit_checks':len(calls),'retained_bytes':sum(blob),'blob_reads':len(blob),'elapsed_seconds':seconds,'incoming_bytes':sum(map(len,batch.files.values()))})
    def test_09_new_import_budget_rejects_rolls_back_exact_retry(self):
        batch=self.refs_batch();before=self.f.count();out=self.f.save(batch,self.limited(retained_bytes=1024));self.assertEqual((out.state,out.code),('REJECTED','RETAINED_WORK_LIMIT'));self.assertEqual(out.receipt['status'],'REJECTED');self.assertEqual(self.f.count(),before);self.assertEqual(self.f.save(batch).state,'ACCEPTED')
    def test_10_accepted_retry_limit_not_corruption_or_false_rejection(self):
        self.f.save();out=self.f.save(store=self.limited(retained_bytes=1));self.assertEqual((out.state,out.code),('IO_ERROR','RETAINED_WORK_LIMIT'));self.assertIsNone(out.receipt);self.assertEqual(self.f.count(),(1,5,4,1));self.assertEqual(self.f.save().state,'REPLAY')
    def test_11_commit_summary_metadata_elapsed_caps(self):
        batch=self.refs_batch();before=self.f.count()
        for limits in [{'commits':1},{'summary_bytes':1},{'metadata_bytes':1}]:
            with self.subTest(limits=limits):
                out=self.f.save(batch,self.limited(**limits));self.assertEqual((out.state,out.code),('REJECTED','RETAINED_WORK_LIMIT'));self.assertEqual(self.f.count(),before)
        store=self.limited(elapsed_ms=1)
        def expire(name,value):
            if name=='retained_work_checkpoint':store._work.get().start-=1
        store._hook=expire;out=self.f.save(batch,store);self.assertEqual((out.state,out.code),('REJECTED','RETAINED_WORK_LIMIT'));self.assertEqual(self.f.count(),before)
    def test_12_corrupt_original_not_skipped_by_cached_summaries(self):
        batch=self.refs_batch();before=self.f.count();c=sqlite3.connect(self.f.store.db);row=c.execute('SELECT file_id FROM files WHERE byte_length=1048576 LIMIT 1').fetchone()
        with c.blobopen('files','file_blob',row[0],readonly=False) as b:b.write(b'changed')
        c.commit();c.close();out=self.f.save(batch);self.assertEqual((out.state,out.code),('INTEGRITY_ERROR','RETAINED_BLOB_HASH'));self.assertEqual(self.f.count(),before)
    def test_13_cancel_retained_chunk_rolls_back(self):
        batch=self.refs_batch(2097152);before=self.f.count();cancelled=[];store=self.limited()
        def hook(name,value):
            if name=='retained_work_checkpoint' and store._work.get().bytes>=1048576:cancelled.append(True)
        store._hook=hook;store._cancel=lambda:bool(cancelled);out=self.f.save(batch,store);self.assertEqual(out.state,'CANCELLED');self.assertEqual(self.f.count(),before)
    def test_14_failure_after_commit_unknown_then_actual_receipt_replay(self):
        for error in [im.WorkLimit,im.Cancelled]:
            b=fx.Bundle.entity();b.m['transaction_id']=str(uuid.uuid4());store=self.limited()
            def uncertain(c):c.execute('COMMIT');raise error()
            store._commit=uncertain;out=self.f.save(b,store);self.assertEqual(out.state,'UNKNOWN');self.assertIsNone(out.receipt);self.assertEqual(self.f.store.get_receipt(b.m['transaction_id'])['status'],'ACCEPTED');self.assertEqual(self.f.save(b).state,'REPLAY')
    def test_15_retained_read_limit_error_no_partial_success(self):
        self.f.save();api=read.ReadAPI(self.f.root)
        original=read.ReadSession.__enter__
        def fail(session):raise im.WorkLimit()
        try:
            read.ReadSession.__enter__=fail;out=api.execute(im.encoded({'protocol':read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'receipt.get','transaction_id':self.f.bundle.m['transaction_id'],'expected_manifest_sha256':None}));self.assertEqual((out['status'],out['code']),('ERROR','LIMIT_EXCEEDED'));self.assertNotIn('data',out)
        finally:read.ReadSession.__enter__=original;api.close()
    def test_16_controller_config_error_and_limit_ui_are_truthful(self):
        import test_commands as ct
        h=ct.Tests('test_01_actual_cli_save_receipt_four_reads_rebuild_search');h.setUp()
        try:
            def invalid(*a,**kw):raise reader.ConfigurationError('INVALID_POLICY')
            controller=h.open(_transport=invalid);out=controller.save('bank.save',h.f.bundle.m['transaction_id']);self.assertEqual((out['status'],out['code']),('IO_ERROR','INVALID_POLICY'));self.assertIsNone(out['receipt'])
        finally:h.tearDown()
        text=presenter.render({'status':'IO_ERROR','code':'RETAINED_WORK_LIMIT'});self.assertIn('не означает',text);self.assertIn('ID не менять',text)
    def test_17_non_utf8_real_subprocess_bytes_capture_diagnostic(self):
        cp=subprocess.run([sys.executable,'-c',"import sys;sys.stdout.buffer.write(bytes([164])*12000)"],capture_output=True,timeout=10);self.assertEqual(cp.returncode,0);self.assertIsInstance(cp.stdout,bytes);text=fx.cmd_diagnostic(cp.stdout,cp.stderr);self.assertEqual(len(text),8192);self.assertIn('\ufffd',text)
    def test_18_current_max_file_profile_save_replay_original(self):
        b=self.f.large(67108864);start=time.monotonic();out=self.f.save(b);self.assertEqual(out.state,'ACCEPTED');self.assertEqual(self.f.save(b).state,'REPLAY');op,d=b.doc('Asset');path=d['data']['storage']['file_path'];size=sum(map(len,self.f.store.read_original(b.m['transaction_id'],path)));self.assertEqual(size,67108864);MEASUREMENTS.append({'scenario':'current64MiB file save/replay/original','bytes':size,'elapsed_seconds':time.monotonic()-start})
    def test_19_near_256mib_package_with_multiple_max_files(self):
        b=self.f.large(67108864);raw=b'Z'*67108864;b.files['files/extra-one.bin']=raw;b.files['files/extra-two.bin']=raw;b.files['files/extra-three.bin']=raw[:-131072];b.refresh();total=len(b.manifest)+len(b.ready)+sum(map(len,b.files.values()));self.assertLessEqual(total,268435456);self.assertGreater(total,267000000);start=time.monotonic();self.assertEqual(self.f.save(b).state,'ACCEPTED');self.assertEqual(self.f.save(b).state,'REPLAY');MEASUREMENTS.append({'scenario':'near256MiB package/4 large files save/replay','package_bytes':total,'elapsed_seconds':time.monotonic()-start})
