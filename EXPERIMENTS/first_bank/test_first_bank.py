"""Headless cross-seam and counterexample tests, owned synthetic roots only."""
from pathlib import Path
import codecs,copy,hashlib,json,os,sqlite3,subprocess,sys,time,unittest,uuid
from unittest.mock import patch
import integration as i
import runtime,attempts
p=i.p;a=p.a;im=a.im
sys.path.insert(0,str(runtime.ROOT/'EXPERIMENTS/draft_authoring'))
import test_authoring as creation
class Tests(unittest.TestCase):
    def setUp(self):
        self.f=creation.Tests('test_01_all_kinds_independent_exact_oracle_bank_discovery_detail_original');self.f.setUp();self.roots=self.f.roots;self.temp=self.f.h.f.temp;self.w=self.f.w
        kw={}
        if os.name!='nt':kw={'_portable_fixture':True,'_controller_kwargs':{'_transport':creation.old.ct.portable_read,'_store_factory':creation.old.ct.PortableStore},'_publisher_kwargs':{'_portable_fixture':True}}
        self.backend=i.Backend(self.roots,context='owned-test-bank',**kw)
    def tearDown(self):self.f.tearDown()
    def prepare(self,path=None,**kw):
        data={'kind':'file','title':'Interior content proof','path':str(path)} if path else {'kind':'note','title':'Owned note','body':'A separate exact note'}
        out=self.w.prepare({**data,**kw});self.assertEqual(out['status'],'PREPARED',out);return out
    def save(self,out):
        pub=self.backend.dispatch('publish',{'transaction_id':out['transaction_id']});self.assertIn(pub['status'],['PUBLISHED','ALREADY_PUBLISHED'],pub)
        saved=self.backend.dispatch('save',{'transaction_id':out['transaction_id']});self.assertIn(saved['status'],['ACCEPTED','REPLAY'],saved);return saved
    def query(self,out):return self.backend.dispatch('receipt',{'transaction_id':out['transaction_id'],'expected_manifest_sha256':out['manifest_sha256']})
    def search(self,word,fields=['content']):return self.backend.dispatch('search',{'object_types':['Asset','Annotation'],'fields':fields,'query':word,'revisions_mode':'current'})
    def test_01_utf8_split_bom_crlf_exact_export_interior_search(self):
        raw=b'\xef\xbb\xbfhead\r\n'+('🙂 Привет\r\ninteriorterm\r\n').encode();path=self.temp/'material.TXT';path.write_bytes(raw)
        w=a.Workspace(self.roots,_portable_fixture=os.name!='nt',_limits={'chunk_bytes':2});out=w.prepare({'kind':'file','title':'No query term here','path':str(path)});self.assertEqual(out['status'],'PREPARED',out)
        self.assertEqual(self.f.doc(out)['data']['storage']['media_type'],'text/plain');path.unlink();self.save(out)
        self.assertEqual(self.backend.dispatch('rebuild',{})['status'],'BUILT')
        found=self.search('interiorterm');self.assertEqual(found['status'],'OK',found);self.assertEqual([x['ref'] for x in found['data']['hits']],[out['ref']])
        exported=self.backend.dispatch('export',{'ref':out['ref']});self.assertEqual(Path(exported['data']['original']['path']).read_bytes(),raw)
    def test_02_invalid_utf8_partial_no_acceptance_explicit_new_binary(self):
        path=self.temp/'invalid.md';path.write_bytes(b'bad\xff');bad=self.w.prepare({'kind':'file','title':'Invalid text','path':str(path)});self.assertEqual(bad['code'],'INVALID_UTF8');self.assertEqual(bad['status'],'INCOMPLETE');self.assertFalse((self.roots['authoring']/bad['transaction_id']/'SEAL.json').exists());self.assertEqual(self.w.inspect(bad['transaction_id'])['code'],'INPUT_NOT_SEALED')
        out=self.prepare(path,input_mode='binary');self.assertNotEqual(out['transaction_id'],bad['transaction_id']);self.save(out);self.assertEqual(self.f.doc(out)['data']['storage']['media_type'],'application/octet-stream')
        path.write_bytes(b'final\xe2\x82');self.assertEqual(self.w.prepare({'kind':'file','title':'Truncated final codepoint','path':str(path)})['code'],'INVALID_UTF8')
    def test_03_explicit_other_suffix_and_4m_boundary_honest_coverage(self):
        for n in [4*1024*1024,4*1024*1024+1]:
            path=self.temp/(str(n)+'.other');path.write_bytes(b' '* (n-16)+b'edgeword        ');out=self.prepare(path,input_mode='utf8_text');self.save(out)
        self.assertEqual(self.backend.dispatch('rebuild',{})['status'],'BUILT');found=self.search('edgeword');self.assertEqual(found['status'],'OK',found);self.assertEqual(found['data']['total_matches'],1);self.assertIn('size_limit',json.dumps(found['data']['coverage']))
        path=self.temp/'large.txt'
        with path.open('wb') as f:f.truncate(64*1024*1024+1)
        out=self.w.prepare({'kind':'file','title':'Too large','path':str(path)});self.assertEqual(out['code'],'AUTHORING_INPUT_LIMIT');self.assertIsNone(out['transaction_id'])
    def test_04_v1_frozen_exact_reopen_publish_replay_after_source_removed(self):
        for phase in ['seal_published','draft_published']:
            def hook(n,v):
                if n==phase:raise OSError('owned crash checkpoint')
            old=a.Workspace(self.roots,_portable_fixture=os.name!='nt',_limits={'policy_version':'r1-authoring/1'},_hook=hook);path=self.temp/(phase+'.txt');raw=b'old v1 binary\r\n';path.write_bytes(raw)
            out=old.prepare({'kind':'file','title':'Legacy title','path':str(path)});tx=out['transaction_id'];before=self.f.snapshot(tx);path.unlink()
            inspected=self.w.inspect(tx,finish=True);self.assertEqual(inspected['status'],'PREPARED',inspected);d=self.f.doc(inspected)
            self.assertEqual(d['provenance']['producer'],{'name':'research-bank-authoring','version':'1'});self.assertEqual(d['data']['storage']['media_type'],'application/octet-stream');intent=json.loads((self.roots['authoring']/tx/'INTENT.json').read_bytes());self.assertNotIn('input_mode',intent['fields']);self.assertEqual(intent['profile']['policy_version'],'r1-authoring/1')
            for name,h in before.items():
                if not name.endswith('DRAFT.pending'):self.assertEqual(a.sha((self.temp/name).read_bytes()),h)
            self.save(inspected);self.assertEqual(self.save(inspected)['status'],'REPLAY');self.assertEqual(self.w.inspect(tx),inspected)
    def test_05_attempt_failure_survives_reopen_receipt_not_found_not_failed(self):
        tx=str(uuid.uuid4());creation.old.fx.private(self.roots['intake']/tx);result=self.backend.dispatch('save',{'transaction_id':tx});self.assertEqual(result['status'],'INCOMPLETE',result);self.assertEqual(result['diagnostic_attempt']['availability'],'available')
        r=attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':tx});self.assertEqual(r['data']['items'][0]['status'],result['status']);self.assertEqual(r['data']['items'][0]['code'],result['code']);receipt=self.backend.dispatch('receipt',{'transaction_id':tx});self.assertEqual(receipt['code'],'RECEIPT_NOT_FOUND')
    def test_06_canonical_acceptance_preserved_when_diagnostic_write_fails(self):
        out=self.prepare();pub=self.backend.dispatch('publish',{'transaction_id':out['transaction_id']});self.assertEqual(pub['status'],'PUBLISHED')
        def failure(*args,**kw):return {'availability':'unavailable','code':'ATTEMPT_NOT_RECORDED'}
        with patch.object(attempts,'record',side_effect=failure):saved=self.backend.dispatch('save',{'transaction_id':out['transaction_id']})
        self.assertEqual(saved['status'],'ACCEPTED');self.assertEqual(saved['diagnostic_attempt']['code'],'ATTEMPT_NOT_RECORDED');self.assertEqual(self.query(out)['data']['receipt']['status'],'ACCEPTED')
    def test_07_private_unknown_and_wrong_hash_attempt_separate_from_receipt(self):
        out=self.prepare();self.save(out);tx=out['transaction_id']
        for state,code in [('UNKNOWN','OUTPUT_OUTCOME_UNCERTAIN'),('REJECTED','TRANSACTION_HASH_MISMATCH')]:
            r=attempts.record(self.roots['bank'],{'transaction_id':tx,'manifest_sha256':'f'*64,'status':state,'code':code,'receipt':None});self.assertEqual(r['availability'],'available')
        receipt=self.query(out);self.assertEqual(receipt['status'],'OK',receipt);self.assertEqual(receipt['data']['receipt']['manifest_sha256'],out['manifest_sha256']);latest=receipt['data']['latest_diagnostic_attempt'];self.assertEqual(latest['attempt']['status'],'REJECTED');self.assertEqual(latest['attempt']['manifest_sha256'],'f'*64)
    def test_08_attempt_scan_exhaustion_and_cursor_not_false_absence(self):
        target=str(uuid.uuid4());other=str(uuid.uuid4());a1=attempts.record(self.roots['bank'],{'transaction_id':target,'status':'UNKNOWN','code':'OWNED_UNKNOWN','receipt':None})
        for _ in range(3):attempts.record(self.roots['bank'],{'transaction_id':other,'status':'UNKNOWN','code':'OWNED_UNKNOWN','receipt':None})
        with attempts.connection(self.roots['bank']) as (store,c):
            r=attempts.scan(c,store.contracts,target,scan_limit=2);self.assertEqual(r['availability'],'incomplete_scan');self.assertTrue(r['next_before_rowid']);r2=attempts.scan(c,store.contracts,target,before=r['next_before_rowid'],scan_limit=2);self.assertEqual(r2['items'][0]['attempt_id'],a1['attempt_id'])
    def test_09_attempt_row_corruption_future_format_and_immutable_append(self):
        tx=str(uuid.uuid4())
        with attempts.connection(self.roots['bank'],True) as (_,c):
            d={'protocol':'future/99'};c.execute('INSERT INTO attempt_receipts VALUES(?,?,?,?,?)',(str(uuid.uuid4()),tx,None,im.now(),im.encoded(d)))
            with self.assertRaises(sqlite3.IntegrityError):c.execute('UPDATE attempt_receipts SET recorded_at=?',('changed',))
        self.assertEqual(attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':tx})['data']['availability'],'unavailable')
    def test_10_observer_second_process_and_pinned_selection(self):
        old=self.prepare();self.save(old);model=p.Model();model.rows['Bank']=[{'ref':old['ref'],'title':'Old'}];model.select('Bank',0);model.pages['History']={'snapshot_sequence':1};model.rows['Search']=[{'ref':old['ref']}]
        flow=i.Flow(self.backend.context,self.backend.identity);initial=self.backend.dispatch('observe',{});flow.apply('observe',initial);flow.refresh_pending=False;flow.rebuild_pending=False
        out=self.prepare();self.backend.dispatch('publish',{'transaction_id':out['transaction_id']})
        code="import sys,json,os;sys.path.insert(0,sys.argv[1]);import integration as i;import test_first_bank as t;kw={};\nif os.name!='nt':kw={'_portable_fixture':True,'_controller_kwargs':{'_transport':t.creation.old.ct.portable_read,'_store_factory':t.creation.old.ct.PortableStore},'_publisher_kwargs':{'_portable_fixture':True}}\nb=i.Backend(json.loads(sys.argv[2]),**kw);r=b.dispatch('save',{'transaction_id':sys.argv[3]});print(json.dumps(r));sys.exit(0 if r['status']=='ACCEPTED' else 2)"
        child=subprocess.run([sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent),json.dumps({k:str(v) for k,v in self.roots.items()}),out['transaction_id']],capture_output=True,timeout=30);self.assertEqual(child.returncode,0,child.stdout+child.stderr)
        observed=self.backend.dispatch('observe',{});flow.apply('observe',observed);self.assertTrue(flow.refresh_pending);self.assertTrue(flow.rebuild_pending);self.assertEqual(flow.next()[0],'list');self.assertEqual(model.selected,old['ref']);self.assertEqual(model.pages['History']['snapshot_sequence'],1);self.assertEqual(model.rows['Search'][0]['ref'],old['ref'])
    def test_11_busy_disconnect_stale_generation_decrease_close(self):
        flow=i.Flow('one','root');r={'status':'OK','context':'one','root_generation':'root','token':[2,str(uuid.uuid4())],'identity':[1,2,'x'],'cache_ready':True};flow.apply('observe',r);flow.refresh_pending=False
        flow.apply('observe',{**r,'context':'old','token':[7,str(uuid.uuid4())]});self.assertEqual(flow.token,r['token'])
        flow.apply('observe',{'status':'ERROR','context':'one','root_generation':'root','code':'BANK_BUSY'});self.assertEqual(flow.token,r['token']);self.assertIn('прежние',flow.notice)
        flow.apply('observe',r);self.assertFalse(flow.disconnected);self.assertNotIn('недоступен',flow.notice)
        flow.apply('observe',{**r,'token':[1,str(uuid.uuid4())]});self.assertTrue(flow.refresh_pending);flow.search({'query':'later'});flow.close();self.assertIsNone(flow.next())
        with im.Store(self.roots['bank']) as store:
            c=store._connect(True);c.execute('BEGIN EXCLUSIVE')
            try:self.assertEqual(i.observe(self.roots['bank'],'one')['status'],'ERROR')
            finally:c.close()
    def test_12_single_worker_visible_rebuild_then_search_readonly(self):
        out=self.prepare(body='notebodyterm');self.save(out);flow=i.Flow(self.backend.context,self.backend.identity);flow.refresh_pending=False;flow.rebuild_pending=True;flow.search({'query':'notebodyterm','fields':['body'],'object_types':['Annotation'],'revisions_mode':'current'})
        action,args,tab=flow.next();self.assertEqual(action,'rebuild');bridge=p.base.Bridge(self.backend);self.assertTrue(bridge.submit(action,args));self.assertFalse(bridge.submit('observe',{}));end=time.monotonic()+10
        result=None
        while result is None and time.monotonic()<end:result=bridge.poll();time.sleep(.01)
        self.assertIsNotNone(result);flow.apply(action,result);self.assertTrue(flow.index_ready);action,args,_=flow.next();before=(self.roots['bank']/'bank.sqlite').read_bytes();result=self.backend.dispatch(action,args);self.assertEqual(result['data']['total_matches'],1);self.assertEqual((self.roots['bank']/'bank.sqlite').read_bytes(),before)
    def test_22_index_recovery_clears_only_owned_error_notice(self):
        flow=i.Flow('one','root');observed={'status':'OK','context':'one','root_generation':'root','token':[1,str(uuid.uuid4())],'identity':[1,2,'x'],'cache_ready':True}
        flow.apply('observe',observed)
        flow.apply('observe',{**observed,'token':[2,str(uuid.uuid4())]});bank_notice=flow.notice
        self.assertIn('обновился',bank_notice)
        flow.apply('rebuild',{'status':'ERROR','code':'OWNED_TRANSIENT_FAILURE'});self.assertIn('Поиск пока недоступен',flow.notice);self.assertIn(bank_notice,flow.notice)
        flow.apply('rebuild',{'status':'BUILT','code':'INDEX_BUILT'});self.assertTrue(flow.index_ready);self.assertEqual(flow.notice,bank_notice)
        flow.apply('rebuild',{'status':'ERROR','code':'OWNED_TRANSIENT_FAILURE'})
        flow.apply('observe',{'status':'ERROR','context':'one','root_generation':'root','code':'BANK_BUSY'});self.assertIn('Bank недоступен',flow.notice)
        flow.apply('rebuild',{'status':'BUILT','code':'INDEX_BUILT'});self.assertNotIn('Поиск пока недоступен',flow.notice);self.assertIn('Bank недоступен',flow.notice)
        flow.apply('observe',observed);self.assertFalse(flow.disconnected);bank_notice=flow.notice
        flow.apply('rebuild',{'status':'ERROR','code':'OWNED_TRANSIENT_FAILURE'})
        flow.apply('observe',{**observed,'context':'stale'});self.assertIn('Поиск пока недоступен',flow.notice)
        flow.apply('observe',{**observed,'cache_ready':False});self.assertIn('Поиск пока недоступен',flow.notice)
        flow.apply('observe',observed);self.assertTrue(flow.index_ready);self.assertEqual(flow.notice,bank_notice)
    def test_13_setup_retry_never_reset_unknown_or_partial_db(self):
        base=self.temp/'first-setup';r=runtime.setup(base,portable=os.name!='nt');self.assertEqual(r['status'],'READY');original=(base/'config.json').read_bytes();self.assertEqual(runtime.setup(base,portable=os.name!='nt')['code'],'CONFIG_REOPENED');self.assertEqual((base/'config.json').read_bytes(),original)
        other=self.temp/'partial'
        def crash(n,v):
            if n=='db_verified':raise OSError('owned stop')
        with self.assertRaises(OSError):runtime.setup(other,portable=os.name!='nt',hook=crash)
        self.assertFalse((other/'config.json').exists());db=(other/'bank/bank.sqlite').read_bytes();runtime.setup(other,portable=os.name!='nt');self.assertEqual((other/'bank/bank.sqlite').read_bytes(),db)
        broken=self.temp/'unknown';runtime.io.mkdir(broken);runtime.io.mkdir(broken/'bank');(broken/'bank/bank.sqlite').write_bytes(b'unknown data')
        with self.assertRaises(Exception):runtime.setup(broken,portable=os.name!='nt')
        self.assertEqual((broken/'bank/bank.sqlite').read_bytes(),b'unknown data');self.assertFalse((broken/'config.json').exists())
    def test_14_setup_crashes_roots_config_db_before_commit(self):
        for phase in ['root_created','config_pending','init_before_commit']:
            base=self.temp/('crash-'+phase)
            def crash(n,v):
                if n==phase:raise OSError('owned interruption')
            with self.assertRaises(OSError):runtime.setup(base,portable=os.name!='nt',hook=crash)
            self.assertFalse((base/'config.json').exists())
            if phase=='init_before_commit':
                before=(base/'bank/bank.sqlite').read_bytes()
                with self.assertRaises(Exception):runtime.setup(base,portable=os.name!='nt')
                self.assertEqual((base/'bank/bank.sqlite').read_bytes(),before)
            else:self.assertEqual(runtime.setup(base,portable=os.name!='nt')['status'],'READY')
    def test_15_verified_backup_reopen_exact_retained_original(self):
        out=self.prepare();self.save(out);before=(self.roots['bank']/'bank.sqlite').read_bytes();r=runtime.safeguard(self.roots,portable=os.name!='nt');self.assertEqual(r['status'],'OK',r);self.assertEqual(r['verified_commits'],1);self.assertEqual(r['sha256'],a.sha(Path(r['path']).read_bytes()));self.assertEqual((self.roots['bank']/'bank.sqlite').read_bytes(),before)
        with im.Store(Path(r['path']).parent) as copy:self.assertEqual(copy.get_receipt(out['transaction_id'])['manifest_sha256'],out['manifest_sha256'])
    def test_16_rejected_roots_config_no_lazy_creation_and_attempt_query(self):
        absent=self.temp/'absent'
        with self.assertRaises(Exception):runtime.load(absent,portable=os.name!='nt')
        self.assertFalse(absent.exists());overlap={**self.roots,'authoring':self.roots['source']}
        with self.assertRaises(Exception):runtime.validate_roots(overlap,portable=os.name!='nt')
        q={'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':str(uuid.uuid4()),'extra':True};self.assertEqual(attempts.query(self.roots['bank'],q)['status'],'ERROR')

    def test_17_real_attempt_io_busy_size_and_interrupt_failure_after_accept(self):
        out=self.prepare();saved=self.save(out);tx=out['transaction_id']
        def fail(n,v):raise OSError('owned diagnostic failure')
        self.assertEqual(attempts.record(self.roots['bank'],saved,_hook=fail)['code'],'ATTEMPT_NOT_RECORDED')
        def interrupt(n,v):raise KeyboardInterrupt()
        self.assertEqual(attempts.record(self.roots['bank'],saved,_hook=interrupt)['code'],'ATTEMPT_NOT_RECORDED')
        with patch.object(attempts,'CAP',8):self.assertEqual(attempts.record(self.roots['bank'],saved)['code'],'ATTEMPT_NOT_RECORDED')
        with im.Store(self.roots['bank']) as store:
            c=store._connect(True);c.execute('BEGIN EXCLUSIVE')
            try:self.assertEqual(attempts.record(self.roots['bank'],saved)['code'],'ATTEMPT_NOT_RECORDED')
            finally:c.close()
        self.assertEqual(self.query(out)['data']['receipt']['status'],'ACCEPTED')
    def test_18_known_legacy_attempt_and_mismatched_row_detected(self):
        tx=str(uuid.uuid4())
        with attempts.connection(self.roots['bank'],True) as (store,c):
            d=store._receipt('REJECTED','OWNED_REJECTED',str(uuid.uuid4()),tx)
            c.execute('INSERT INTO attempt_receipts VALUES(?,?,?,?,?)',(*[d[k] for k in ['attempt_id','transaction_id','manifest_sha256','recorded_at']],im.encoded(d)))
        r=attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':tx});self.assertEqual(r['data']['items'][0]['canonical_receipt'],d)
        with attempts.connection(self.roots['bank'],True) as (store,c):
            c.execute('INSERT INTO attempt_receipts VALUES(?,?,?,?,?)',(str(uuid.uuid4()),tx,None,im.now(),im.encoded(d)))
        self.assertEqual(attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':tx})['data']['availability'],'unavailable')
    def test_19_process_death_after_commit_before_diagnostic_exact_recovery(self):
        out=self.prepare();self.backend.dispatch('publish',{'transaction_id':out['transaction_id']})
        code="import sys,json,os;sys.path.insert(0,sys.argv[1]);import integration as i;import test_first_bank as t;kw={};\nif os.name!='nt':kw={'_portable_fixture':True,'_controller_kwargs':{'_transport':t.creation.old.ct.portable_read,'_store_factory':t.creation.old.ct.PortableStore},'_publisher_kwargs':{'_portable_fixture':True}}\ndef hook(n,v):\n if n=='after_import':os._exit(73)\nkw.setdefault('_controller_kwargs',{})['_hook']=hook\nb=i.Backend(json.loads(sys.argv[2]),**kw);b.dispatch('save',{'transaction_id':sys.argv[3]})"
        child=subprocess.run([sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent),json.dumps({k:str(v) for k,v in self.roots.items()}),out['transaction_id']],capture_output=True,timeout=30);self.assertEqual(child.returncode,73,child.stdout+child.stderr)
        receipt=self.query(out);self.assertEqual(receipt['status'],'OK',receipt);self.assertEqual(receipt['data']['receipt']['status'],'ACCEPTED');self.assertEqual(receipt['data']['latest_diagnostic_attempt']['availability'],'not_recorded');self.assertEqual(self.save(out)['status'],'REPLAY')
    def test_20_passive_observer_does_not_recover_hot_journal(self):
        out=self.prepare();self.save(out);root=self.roots['bank'];before=(root/'bank.sqlite').read_bytes()
        code="import sys,os;sys.path.insert(0,sys.argv[1]);import integration as i;store=i.im.Store(sys.argv[2]);c=store._connect(True);c.execute('PRAGMA cache_size=10');c.execute('BEGIN IMMEDIATE');c.execute(\"INSERT INTO attempt_receipts VALUES('pending',NULL,NULL,'pending',zeroblob(1000000))\");os._exit(73)"
        child=subprocess.run([sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent),str(root)],capture_output=True,timeout=20);self.assertEqual(child.returncode,73,child.stdout+child.stderr);journal=root/'bank.sqlite-journal';self.assertTrue(journal.exists());j=journal.read_bytes();db=(root/'bank.sqlite').read_bytes()
        r=i.observe(root,'owned-test-bank');self.assertEqual(r['status'],'ERROR',r);self.assertEqual(journal.read_bytes(),j);self.assertEqual((root/'bank.sqlite').read_bytes(),db)
        receipt=self.query(out);self.assertEqual(receipt['status'],'OK',receipt);self.assertEqual((root/'bank.sqlite').read_bytes(),before)
    def test_21_production_scan_bound_and_missing_dependency_no_setup(self):
        target=str(uuid.uuid4())
        with attempts.connection(self.roots['bank'],True) as (_,c):
            c.execute('BEGIN IMMEDIATE')
            for _ in range(4097):
                d={'protocol':attempts.PROTOCOL,'attempt_id':str(uuid.uuid4()),'transaction_id':str(uuid.uuid4()),'manifest_sha256':None,'recorded_at':im.now(),'status':'UNKNOWN','code':'OWNED_UNKNOWN','canonical_receipt':None}
                c.execute('INSERT INTO attempt_receipts VALUES(?,?,?,?,?)',(*[d[k] for k in ['attempt_id','transaction_id','manifest_sha256','recorded_at']],im.encoded(d)))
            c.execute('COMMIT')
        r=attempts.query(self.roots['bank'],{'protocol':attempts.QUERY,'operation':'attempt.get','transaction_id':target});self.assertEqual(r['data']['availability'],'incomplete_scan');self.assertIsNotNone(r['data']['next_before_rowid'])
        absent=self.temp/'missing-dependency'
        with patch.object(runtime,'preflight',side_effect=ImportError('owned missing dependency')):
            with self.assertRaises(ImportError):runtime.setup(absent,portable=os.name!='nt')
        self.assertFalse(absent.exists())
if __name__=='__main__':unittest.main()
