"""Integrated synthetic tests. Linux fixture adapters do not claim Windows handle evidence."""
from pathlib import Path
import copy,datetime,errno,hashlib,json,os,platform,shutil,sqlite3,subprocess,sys,tempfile,threading,time,unittest,uuid
from unittest.mock import patch
import importer as im
ROOT=im.ROOT
class Bundle:
    def __init__(self,kind='create'):
        index=json.loads((ROOT/'PLANNING/CONTRACTS/BANK_TYPE_EXAMPLES/INDEX.json').read_text(encoding='utf-8-sig'));folder=ROOT/index['examples'][kind]['path'];self.m=json.loads((folder/'manifest.json').read_bytes());self.files={f['path']:(folder/f['path']).read_bytes() for f in self.m['files']}
    def clone(self):return copy.deepcopy(self)
    def refresh(self):
        self.m['files']=[{'path':n,'byte_length':len(b),'sha256':im.sha(b)} for n,b in self.files.items()];self.manifest=im.encoded(self.m);self.ready=im.encoded({'protocol':im.reader.PROTOCOL,'transaction_id':self.m['transaction_id'],'manifest_byte_length':len(self.manifest),'manifest_sha256':im.sha(self.manifest)});return self
    def doc(self,kind):
        op=next(o for o in self.m['operations'] if o['type']==kind);return op,json.loads(self.files[op['document_path']])
    def edit(self,kind,func):
        op,d=self.doc(kind);func(d);self.files[op['document_path']]=im.encoded(d);return self
    def revision(self,kind='Annotation'):
        self.m['transaction_id']=str(uuid.uuid4());op,d=self.doc(kind);base=op['revision_id'];op['base_revision_id']=base;op['revision_id']=str(uuid.uuid4());d['revision_id']=op['revision_id'];self.m['operations']=[op];self.files={op['document_path']:im.encoded(d)};return self
    @classmethod
    def entity(cls,previous=None):
        b=cls();op,d=b.doc('Entity');oid=str(uuid.uuid4());rid=str(uuid.uuid4());d.update(object_id=oid,revision_id=rid,title='Synthetic history');d['data']['asset_refs']=[];d['provenance']['derived_from']=[] if previous is None else [{'object_type':'Entity','object_id':previous['object_id'],'revision_id':previous['revision_id']}];op.update(object_id=oid,revision_id=rid,base_revision_id=None);b.m['transaction_id']=str(uuid.uuid4());b.m['operations']=[op];b.files={op['document_path']:im.encoded(d)};return b
class FixtureSnapshot:
    status='VERIFIED_TRANSPORT'
    def __init__(self,b,policy):
        b.refresh();self.manifest_bytes=b.manifest;self.ready_bytes=b.ready;self.policy_bytes=policy;self.transaction_id=b.m['transaction_id'];self.manifest_sha256=im.sha(b.manifest);self._data=dict(b.files);self.files={n:(len(raw),im.sha(raw)) for n,raw in self._data.items()};self.closed=False
    def iter_bytes(self,name):
        if self.closed:raise im.reader.Rejected('SNAPSHOT_CLOSED')
        chunk=im.reader.Policy(self.policy_bytes)['blob_chunk_bytes']
        for i in range(0,len(self._data[name]),chunk):yield self._data[name][i:i+chunk]
    def close(self):self.closed=True
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
def private(p):
    if os.name=='nt':im.native.private_directory(p)
    else:p.mkdir(mode=0o700)
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='bank-importer-test-'));self.root=self.temp/'store';private(self.root);self.intake=self.temp/'intake';private(self.intake);self.stage=self.temp/'stage';private(self.stage);self.snapshots=[];self.stores=[];self.bundle=Bundle();self.c=im.Contracts();self.store=self.open_store();self.store.initialize()
    def tearDown(self):
        for s in self.snapshots:s.close()
        for store in self.stores:store.close()
        shutil.rmtree(self.temp)
    def open_store(self,**kw):
        if os.name!='nt':kw.setdefault('_snapshot_type',FixtureSnapshot)
        store=im.Store(self.root,contracts=self.c,**kw);self.stores.append(store);return store
    def snapshot(self,b=None):
        b=(b or self.bundle).clone().refresh()
        if os.name=='nt':
            # A repeated producer ID is copied into a fresh trusted temporary intake root, never overwrites the other snapshot's source.
            ir=self.temp/('intake-'+uuid.uuid4().hex);private(ir);p=ir/b.m['transaction_id'];private(p)
            for name,raw in {**b.files,'manifest.json':b.manifest,'READY.json':b.ready}.items():
                q=p/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
            x=im.reader.read_package(ir,b.m['transaction_id'],self.stage);self.assertEqual(x.status,'VERIFIED_TRANSPORT',x.code);s=x.snapshot;s._fixture_input=p
        else:s=FixtureSnapshot(b,self.c.policy.raw)
        self.snapshots.append(s);return s
    def save(self,b=None,store=None):
        snapshot=self.snapshot(b)
        try:return (store or self.store).import_snapshot(snapshot)
        finally:snapshot.close()
    def count(self):
        c=sqlite3.connect(self.store.db)
        try:return tuple(c.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['commits','files','revisions','accepted_receipts'])
        finally:c.close()
    def accepted(self,b=None):
        result=self.save(b);self.assertEqual(result.state,'ACCEPTED',result);self.assertEqual(result.receipt['status'],'ACCEPTED');self.c.envelope(result.receipt);return result
    def unchanged_error(self,b,state='REJECTED',code=None):
        before=self.count();r=self.save(b);self.assertEqual(r.state,state,r)
        if code:self.assertEqual(r.code,code)
        self.assertEqual(self.count(),before);return r
    def test_01_supported_atomic_reopen_original_receipt(self):
        result=self.accepted();self.assertEqual(self.count(),(1,5,4,1));self.assertEqual(self.store.get_receipt(self.bundle.m['transaction_id']),result.receipt)
        other=self.open_store()
        for name,raw in self.bundle.files.items():self.assertEqual(b''.join(other.read_original(self.bundle.m['transaction_id'],name)),raw)
    def test_02_exact_replay_zero_new_rows(self):
        original=self.accepted();before=self.count();replay=self.save();self.assertEqual(replay.state,'REPLAY');self.assertEqual(self.count(),before);self.assertEqual(replay.receipt['commit_id'],original.receipt['commit_id']);self.assertNotEqual(replay.receipt['attempt_id'],original.receipt['attempt_id']);self.assertEqual(self.store.get_receipt(self.bundle.m['transaction_id']),original.receipt)
    def test_03_same_transaction_changed_hash_conflict(self):
        original=self.accepted();changed=self.bundle.clone().edit('Annotation',lambda d:d['data'].update(body='Changed exact manifest'))
        self.unchanged_error(changed,'CONFLICT','TRANSACTION_ID_REUSED');self.assertEqual(self.store.get_receipt(self.bundle.m['transaction_id']),original.receipt)
    def test_04_continuation_accepted_history(self):
        self.accepted();self.accepted(Bundle('continuation'));self.assertEqual(self.count(),(2,6,5,2))
    def test_05_replay_after_later_head_change(self):
        original=self.accepted();self.accepted(Bundle('continuation'));before=self.count();replay=self.save();self.assertEqual(replay.state,'REPLAY');self.assertEqual(replay.receipt['commit_id'],original.receipt['commit_id']);self.assertEqual(self.count(),before)
    def test_06_revision_id_reuse_new_transaction(self):
        self.accepted();b=self.bundle.clone();b.m['transaction_id']=str(uuid.uuid4());self.unchanged_error(b,'CONFLICT','REVISION_ID_REUSED')
    def test_07_multiobject_stale_base_rolls_back_everything(self):
        self.accepted();b=self.bundle.clone();b.m['transaction_id']=str(uuid.uuid4())
        for op in b.m['operations']:
            d=json.loads(b.files[op['document_path']]);op['base_revision_id']=op['revision_id'];op['revision_id']=str(uuid.uuid4());d['revision_id']=op['revision_id'];b.files[op['document_path']]=im.encoded(d)
        b.m['operations'][-1]['base_revision_id']=str(uuid.uuid4());self.unchanged_error(b,'CONFLICT','STALE_BASE')
    def test_08_wrong_object_base_and_type_stability(self):
        self.accepted();b=self.bundle.clone().revision();b.m['operations'][0]['base_revision_id']=self.bundle.m['operations'][0]['revision_id'];self.unchanged_error(b,'CONFLICT','STALE_BASE')
        b=Bundle.entity();op,d=b.doc('Entity');annotation_op,_=self.bundle.doc('Annotation');op['object_id']=annotation_op['object_id'];op['base_revision_id']=annotation_op['revision_id'];d['object_id']=op['object_id'];b.files[op['document_path']]=im.encoded(d);self.unchanged_error(b,'CONFLICT','OBJECT_TYPE_CHANGED')
    def test_09_asset_binding_path_length_hash(self):
        for key,value in [('sha256','0'*64),('byte_length',1),('file_path','files/missing.bin')]:
            with self.subTest(field=key):self.unchanged_error(self.bundle.clone().edit('Asset',lambda d:d['data']['storage'].update({key:value})),'REJECTED','ASSET_DESCRIPTOR_MISMATCH')
    def test_10_r1_intent_and_source_type_gate(self):
        b=self.bundle.clone();b.m['intent']='tracked_research';self.unchanged_error(b,'REJECTED','UNSUPPORTED_INTENT')
        self.unchanged_error(Bundle('source_boundary'),'REJECTED')
    def test_11_envelope_document_identity_and_schema(self):
        for change in [lambda d:d.update(object_id=str(uuid.uuid4())),lambda d:d.update(schema='bank-annotation/99'),lambda d:d.update(extra='unknown')]:
            with self.subTest(change=change):self.unchanged_error(self.bundle.clone().edit('Annotation',change))
    def test_12_unresolved_wrong_type_provenance(self):
        for change in [lambda d:d['data']['targets'][0].update(revision_id=str(uuid.uuid4())),lambda d:d['data']['targets'][0].update(object_type='Entity'),lambda d:d['provenance'].update(origin_kind='derived',derived_from=[])]:
            with self.subTest(change=change):self.unchanged_error(self.bundle.clone().edit('Annotation',change))
    def test_13_in_package_derivation_cycle(self):
        b=self.bundle.clone();aop,ad=b.doc('Asset');eop,ed=b.doc('Entity');ad['provenance']['derived_from']=[{'object_type':'Entity','object_id':ed['object_id'],'revision_id':ed['revision_id']}];ed['provenance']['derived_from']=[{'object_type':'Asset','object_id':ad['object_id'],'revision_id':ad['revision_id']}];b.files[aop['document_path']]=im.encoded(ad);b.files[eop['document_path']]=im.encoded(ed);self.unchanged_error(b,'REJECTED','DERIVATION_CYCLE')
    def test_14_unicode_byte_limits_exact_and_above(self):
        b=Bundle.entity();b.edit('Entity',lambda d:d.update(title='é'*2048));self.accepted(b)
        b=Bundle.entity();b.edit('Entity',lambda d:d.update(title='é'*2048+'x'));self.unchanged_error(b,'REJECTED','TEXT_LIMIT')
        b=self.bundle.clone().edit('Annotation',lambda d:d['data'].update(body='é'*524289));self.unchanged_error(b,'REJECTED','TEXT_LIMIT')
    def test_15_locator_is_metadata_without_fetch(self):
        b=self.bundle.clone().edit('Asset',lambda d:d['data'].update(storage={'mode':'locator','uri':'https://invalid.example/never-fetch','label':None}));b.files.pop('files/report.md')
        with patch('urllib.request.urlopen',side_effect=AssertionError('no fetch')):self.accepted(b)
        b=self.bundle.clone().edit('Asset',lambda d:d['data'].update(storage={'mode':'locator','uri':'https://invalid.example/'+('x'*8192),'label':None}));b.files.pop('files/report.md');self.unchanged_error(b,'REJECTED','TEXT_LIMIT')
    def test_16_invalid_fake_and_closed_snapshot(self):
        out=self.store.import_snapshot(object());self.assertEqual(out.state,'REJECTED');self.assertIsNone(out.receipt['transaction_id'])
        s=self.snapshot();s.close();out=self.store.import_snapshot(s);self.assertEqual(out.state,'REJECTED');self.assertEqual(self.count(),(0,0,0,0))
    def test_17_before_copy_write_enospc_cancel_rollbacks(self):
        for event,number in [('incoming_validated',errno.EIO),('before_blob_write',errno.EIO),('blob_chunk',errno.ENOSPC),('before_commit',errno.EIO)]:
            def hook(name,value):
                if name==event:raise OSError(number,'owned fixture injected fault')
            with self.subTest(event=event):
                store=self.open_store(_hook=hook);out=self.save(store=store);self.assertEqual(out.state,'IO_ERROR');self.assertIsNone(out.receipt);self.assertEqual(self.count(),(0,0,0,0))
        flag=[False]
        def hook(name,value):
            if name=='blob_chunk':flag[0]=True
        store=self.open_store(_hook=hook,_cancel=lambda:flag[0]);out=self.save(store=store);self.assertEqual(out.state,'CANCELLED');self.assertEqual(self.count(),(0,0,0,0));self.accepted()
    def test_18_fault_after_commit_recovers_original(self):
        def hook(name,value):
            if name=='after_commit':raise OSError(errno.EIO,'return channel fault')
        store=self.open_store(_hook=hook);out=self.save(store=store);self.assertEqual(out.state,'ACCEPTED');self.assertEqual(self.count(),(1,5,4,1));self.assertEqual(self.store.get_receipt(self.bundle.m['transaction_id']),out.receipt)
    def test_19_unknown_commit_recovery_unavailable(self):
        class Uncertain(im.Store):
            def _commit(self,c):super()._commit(c);raise OSError(errno.EIO,'unknown response after actual commit')
            def get_receipt(self,*a):raise OSError(errno.EIO,'owned simulated recovery unavailable')
        kw={'_snapshot_type':FixtureSnapshot} if os.name!='nt' else {};store=Uncertain(self.root,contracts=self.c,**kw);self.stores.append(store);out=self.save(store=store);self.assertEqual(out.state,'UNKNOWN');self.assertIsNone(out.receipt);self.assertEqual(self.count(),(1,5,4,1));self.assertEqual(self.save().state,'REPLAY')
    def test_20_lock_contention_retryable_and_bounded(self):
        c=sqlite3.connect(self.store.db,isolation_level=None);c.execute('BEGIN IMMEDIATE');start=time.monotonic()
        try:out=self.save();self.assertEqual(out.state,'RETRYABLE_BUSY');self.assertIsNone(out.receipt);self.assertLess(time.monotonic()-start,3)
        finally:c.execute('ROLLBACK');c.close()
        self.accepted()
    def test_21_two_writers_one_stale_whole_command(self):
        self.accepted();base=Bundle('continuation');b1=base.clone();b2=base.clone();b2.m['transaction_id']=str(uuid.uuid4());op,d=b2.doc('Annotation');op['revision_id']=str(uuid.uuid4());d['revision_id']=op['revision_id'];b2.files[op['document_path']]=im.encoded(d)
        snaps=[self.snapshot(b1),self.snapshot(b2)];stores=[self.open_store(),self.open_store()];barrier=threading.Barrier(2);outputs=[];errors=[]
        def run(i):
            try:barrier.wait(timeout=3);outputs.append(stores[i].import_snapshot(snaps[i]))
            except BaseException as e:errors.append(str(e))
        threads=[threading.Thread(target=run,args=(i,)) for i in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=6);self.assertFalse(t.is_alive())
        self.assertEqual(errors,[]);self.assertEqual(sorted(x.state for x in outputs),['ACCEPTED','CONFLICT']);self.assertEqual(self.count(),(2,6,5,2))
    def test_22_old_blob_write_forbidden_by_app_capability(self):
        self.accepted();c=self.store._connect(True);c.execute('BEGIN IMMEDIATE')
        try:
            old=c.execute('SELECT file_id FROM files LIMIT 1').fetchone()[0];session=im._WriteSession(c,2,self.c.policy,lambda *x:None)
            with self.assertRaisesRegex(im.Problem,'OLD_BLOB_WRITE_FORBIDDEN'):session.write(old,[b'x'],1,im.sha(b'x'))
        finally:c.execute('ROLLBACK');c.close()
        for name,raw in self.bundle.files.items():self.assertEqual(b''.join(self.store.read_original(self.bundle.m['transaction_id'],name)),raw)
    def test_23_sql_immutability_and_read_only_api(self):
        self.accepted();c=self.store._connect(True)
        try:
            for t in ['commits','files','revisions','accepted_receipts','attempt_receipts']:
                # An empty attempt table still has the required trigger; insert a diagnostic fixture first.
                if t=='attempt_receipts':c.execute('INSERT INTO attempt_receipts VALUES(?,?,?,?,?)',(str(uuid.uuid4()),None,None,im.now(),b'{}'))
                with self.subTest(table=t),self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM '+t)
        finally:c.close()
        c=self.store._connect(False)
        try:
            with self.assertRaises(sqlite3.OperationalError):c.execute('CREATE TABLE forbidden(x)')
        finally:c.close()
    def test_24_corrupt_retained_blob_blocks_replay_and_read(self):
        self.accepted();c=sqlite3.connect(self.store.db,isolation_level=None);fid=c.execute("SELECT file_id FROM files WHERE path='files/report.md'").fetchone()[0]
        with c.blobopen('files','file_blob',fid,readonly=False) as b:b.write(b'!')
        c.close();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR',out);self.assertNotEqual(out.receipt['status'],'REPLAY');self.assertEqual(self.count(),(1,5,4,1))
        with self.assertRaises(im.Problem):list(self.store.read_original(self.bundle.m['transaction_id'],'files/report.md'))
    def test_25_unknown_existing_format_untouched(self):
        bad=self.temp/'bad';private(bad);db=bad/'bank.sqlite';c=sqlite3.connect(db);c.execute('CREATE TABLE foreign_data(x)');c.commit();c.close();before=db.read_bytes();store=im.Store(bad,contracts=self.c,_snapshot_type=FixtureSnapshot if os.name!='nt' else im.reader.Snapshot);self.stores.append(store)
        out=store.import_snapshot(self.snapshot());self.assertEqual(out.state,'INTEGRITY_ERROR');self.assertEqual(db.read_bytes(),before)
        with self.assertRaises(im.Problem):store.initialize()
        self.assertEqual(db.read_bytes(),before)
    def test_26_known_headers_wrong_schema_untouched(self):
        c=sqlite3.connect(self.store.db);c.execute('DROP TRIGGER files_no_delete');c.commit();c.close();before=self.store.db.read_bytes();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR');self.assertEqual(self.store.db.read_bytes(),before)
    def child(self,phase,bundle=None):
        b=(bundle or self.bundle).clone().refresh();packet=self.temp/'child_bundle.json';packet.write_text(json.dumps({'m':b.m,'files':{n:raw.hex() for n,raw in b.files.items()}}),encoding='utf-8')
        q=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(self.root),str(packet),phase],capture_output=True,text=True,timeout=15);return q
    def test_27_owned_process_death_before_commit_recovery(self):
        q=self.child('before_commit');self.assertEqual(q.returncode,17,q.stdout+q.stderr);self.assertIsNone(self.store.get_receipt(self.bundle.m['transaction_id']));self.assertEqual(self.count(),(0,0,0,0));self.accepted()
    def test_28_owned_process_death_after_commit_before_return(self):
        q=self.child('after_commit');self.assertEqual(q.returncode,18,q.stdout+q.stderr);self.assertEqual(self.count(),(1,5,4,1));receipt=self.store.get_receipt(self.bundle.m['transaction_id']);self.assertEqual(receipt['status'],'ACCEPTED');self.assertEqual(self.save().state,'REPLAY')
    def test_29_read_after_intake_removed(self):
        s=self.snapshot();out=self.store.import_snapshot(s);self.assertEqual(out.state,'ACCEPTED')
        if os.name=='nt':shutil.rmtree(s._fixture_input)
        else:s._data.clear()
        for name,raw in self.bundle.files.items():self.assertEqual(b''.join(self.store.read_original(self.bundle.m['transaction_id'],name)),raw)
    def test_30_retained_receipt_hash_mismatch_and_missing(self):
        self.accepted();self.assertIsNone(self.store.get_receipt(str(uuid.uuid4())))
        with self.assertRaisesRegex(im.Problem,'TRANSACTION_HASH_MISMATCH'):self.store.get_receipt(self.bundle.m['transaction_id'],'0'*64)
    def test_31_long_causal_history_targeted_no_recursive_traversal(self):
        prev=None
        for _ in range(1100):
            b=Bundle.entity(prev);self.accepted(b);_,prev=b.doc('Entity')
        self.accepted(Bundle.entity(prev));self.assertEqual(self.count(),(1101,1101,1101,1101))
    def test_32_header_config_foreign_keys_and_exact_schema(self):
        c=self.store._connect(True)
        try:
            for pragma,value in [('journal_mode','delete'),('synchronous',3),('foreign_keys',1),('trusted_schema',0),('read_uncommitted',0),('application_id',1380076337),('user_version',1)]:self.assertEqual(c.execute('PRAGMA '+pragma).fetchone()[0],value)
            self.assertTrue(c.getconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE));self.assertEqual(im.Contracts.catalog_of(c),self.c.catalog);self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        finally:c.close()
    def test_33_commit_busy_is_retryable_no_success(self):
        self.accepted();b=Bundle('continuation');c=sqlite3.connect(self.store.db,isolation_level=None);c.execute('BEGIN');c.execute('SELECT * FROM commits').fetchone()
        try:out=self.save(b);self.assertEqual(out.state,'RETRYABLE_BUSY',out);self.assertIsNone(out.receipt);self.assertEqual(self.count(),(1,5,4,1))
        finally:c.execute('ROLLBACK');c.close()
        self.accepted(b)
    def test_34_cancel_after_commit_does_not_mislabel_retained_success(self):
        flag=[False]
        def hook(name,value):
            if name=='after_commit':flag[0]=True
        store=self.open_store(_hook=hook,_cancel=lambda:flag[0]);out=self.save(store=store);self.assertEqual(out.state,'ACCEPTED',out);self.assertEqual(self.count(),(1,5,4,1))
    def test_35_retained_malformed_document_is_integrity_error(self):
        self.accepted();c=sqlite3.connect(self.store.db,isolation_level=None);fid=c.execute("SELECT file_id FROM files WHERE path LIKE 'objects/%' LIMIT 1").fetchone()[0]
        with c.blobopen('files','file_blob',fid,readonly=False) as b:b.write(b'!')
        c.close();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR',out)
    def test_36_incomplete_initialization_not_accepted(self):
        root=self.temp/'new-init';private(root);q=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--init-child',str(root)],capture_output=True,text=True,timeout=10);self.assertEqual(q.returncode,19,q.stdout+q.stderr)
        kw={'_snapshot_type':FixtureSnapshot} if os.name!='nt' else {};store=im.Store(root,contracts=self.c,**kw);self.stores.append(store);out=store.import_snapshot(self.snapshot());self.assertNotEqual(out.state,'ACCEPTED');self.assertFalse((root/'bank.sqlite').read_bytes()[:16]==b'SQLite format 3\x00' and out.state=='REPLAY')

    def large(self,length):
        b=self.bundle.clone();payload=b'x'*length;b.files['files/report.md']=payload;b.edit('Asset',lambda d:d['data']['storage'].update(byte_length=length,sha256=im.sha(payload)));return b
    def test_37_real_64m_blob_stream_exact_original(self):
        b=self.large(67108864);self.accepted(b);count=0;h=hashlib.sha256()
        for raw in self.store.read_original(b.m['transaction_id'],'files/report.md'):self.assertLessEqual(len(raw),1048576);h.update(raw);count+=len(raw)
        self.assertEqual(count,67108864);self.assertEqual(h.hexdigest(),im.sha(b.files['files/report.md']))
    def test_38_real_sqlite_full_owned_db_page_limit(self):
        class Limited(im.Store):
            def _connect(self,write=False):
                c=super()._connect(write)
                if write:c.execute('PRAGMA max_page_count='+str(c.execute('PRAGMA page_count').fetchone()[0]+4))
                return c
        kw={'_snapshot_type':FixtureSnapshot} if os.name!='nt' else {};store=Limited(self.root,contracts=self.c,**kw);self.stores.append(store);out=self.save(self.large(2*1048576),store);self.assertEqual(out.state,'IO_ERROR',out);self.assertEqual(out.code,'SQLITE_FULL');self.assertEqual(self.count(),(0,0,0,0))
    def test_39_hot_journal_spill_recovered_without_external_sql(self):
        b=self.large(4*1048576);q=self.child('before_commit',b);self.assertEqual(q.returncode,17,q.stdout+q.stderr)
        # Store is the first reader after real cache spill and child death, no helper opens SQLite first.
        self.assertIsNone(self.store.get_receipt(b.m['transaction_id']));self.assertEqual(self.count(),(0,0,0,0));self.accepted(b)
    def test_40_corrupt_canonical_receipt_is_integrity_error(self):
        self.accepted();c=sqlite3.connect(self.store.db,isolation_level=None)
        with c.blobopen('accepted_receipts','receipt_blob',1,readonly=False) as b:b.write(b'!')
        c.close();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR',out);self.assertNotEqual(out.receipt['status'],'REPLAY')
    def test_41_domain_error_receipt_keeps_verified_transaction(self):
        b=self.bundle.clone();b.m['intent']='tracked_research';out=self.save(b);self.assertEqual(out.state,'REJECTED');self.assertEqual(out.receipt['transaction_id'],b.m['transaction_id']);self.assertEqual(out.receipt['manifest_sha256'],im.sha(b.refresh().manifest))
    def test_42_db_link_alias_rejected(self):
        # Arrange aliases while the protected root lease is closed; Windows
        # forbids link creation through leased parent directories. Reacquire
        # the actual root protection before exercising each rejection.
        target=self.temp/'original-db';self.store.close();shutil.copyfile(self.store.db,target);self.store.db.unlink();os.link(target,self.store.db)
        self.store=self.open_store();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR');self.assertEqual(out.code,'UNTRUSTED_DB_FILE')
        self.store.close();self.store.db.unlink()
        if os.name=='nt':
            # Actual NTFS reparse alias without changing OS symlink privileges.
            destination=self.temp/'junction-target';destination.mkdir()
            made=subprocess.run(['cmd','/c','mklink','/J',str(self.store.db),str(destination)],capture_output=True,text=True,timeout=10)
            self.assertEqual(made.returncode,0,made.stdout+made.stderr);self.assertTrue(self.store.db.lstat().st_file_attributes&0x400)
        else:os.symlink(target,self.store.db)
        self.store=self.open_store();out=self.save();self.assertEqual(out.state,'INTEGRITY_ERROR');self.assertEqual(out.code,'UNTRUSTED_DB_FILE')
        self.store.close()
        if os.name=='nt':os.rmdir(self.store.db)
        else:self.store.db.unlink()
        shutil.copyfile(target,self.store.db)

class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[];self.bad=set()
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'id':test._testMethodName,'expected':'all integration assertions pass','observed':'PASS'})
    def fail(self,test,err):
        self.bad.add(test._testMethodName);self.cases.append({'id':test._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(err,test)})
    def addFailure(self,test,err):super().addFailure(test,err);self.fail(test,err)
    def addError(self,test,err):super().addError(test,err);self.fail(test,err)
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err:self.fail(test,err)

def child():
    phase=sys.argv[4];root=Path(sys.argv[2]);p=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8-sig'));b=Bundle();b.m=p['m'];b.files={n:bytes.fromhex(raw) for n,raw in p['files'].items()}
    def hook(name,value):
        if name==phase:os._exit(17 if phase=='before_commit' else 18)
    kw={'_snapshot_type':FixtureSnapshot} if os.name!='nt' else {}
    with im.Store(root,_hook=hook,**kw) as store:
        if os.name=='nt':
            with tempfile.TemporaryDirectory(prefix='bank-import-child-',dir=root.parent) as t:
                t=Path(t);ir=t/'intake';sr=t/'stage';private(ir);private(sr);pack=ir/b.m['transaction_id'];private(pack);b.refresh()
                for name,raw in {**b.files,'READY.json':b.ready,'manifest.json':b.manifest}.items():q=pack/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
                out=store.import_package(ir,b.m['transaction_id'],sr);print(out,flush=True)
        else:out=store.import_snapshot(FixtureSnapshot(b,store.contracts.policy.raw));print(out,flush=True)
    raise RuntimeError('Owned child did not reach required interruption phase')
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child':child();sys.exit()
    if len(sys.argv)>1 and sys.argv[1]=='--init-child':
        def hook(name,value):
            if name=='init_before_commit':os._exit(19)
        with im.Store(Path(sys.argv[2]),_hook=hook) as store:store.initialize()
        raise RuntimeError('Owned init child did not reach phase')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));folder=Path(__file__).parent;now=im.now()
    report={'record_kind':'synthetic_whole_command_importer_evidence','at':now,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'snapshot_adapter':'actual Windows secure reader handles' if os.name=='nt' else 'trusted immutable portable fixture (no Windows confinement claim)','tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'source_sha256':{p.name:im.sha(p.read_bytes()) for p in [folder/'importer.py',folder/'test_importer.py']},'limitations':['Synthetic temporary DB only; no installed Bank/UI/search','No hardware/VFS power-loss or real private deployment acceptance','Trusted roots/parents/current owner/app configuration','Faults use injected own I/O errors/process exits; no disk filling or unrelated process termination']}
    name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';p=folder/name
    if p.exists():hist=folder/'TEST_HISTORY';hist.mkdir(exist_ok=True);shutil.copyfile(p,hist/(name+'-'+uuid.uuid4().hex+'.json'))
    p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    p=folder/'ISSUES.json';log=json.loads(p.read_text(encoding='utf-8-sig'));known={x['id']:x for x in log['issues']}
    for test in result.bad:
        iid='DB-TEST-'+test;x=known.get(iid)
        if x is None:x={'id':iid,'title':'Integration assertion failed: '+test,'status':'open','history':[]};log['issues'].append(x)
        x['status']='open';x['history'].append({'at':now,'status':'open','evidence':name,'detail':next(c['detail'] for c in result.cases if c['id']==test and c['observed']=='FAIL')})
    for x in log['issues']:
        if x['id'].startswith('DB-TEST-') and x['status']=='open' and x['id'][8:] not in result.bad:x['status']='resolved';x['history'].append({'at':now,'status':'resolved','evidence':name,'note':'Integration case rerun passed; prior failure retained in TEST_HISTORY.'})
    p.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':sorted(result.bad),'report':str(folder/name)}),flush=True);sys.exit(not result.wasSuccessful())
