"""Owned publication integration; Linux fixture evidence is separate from native NTFS."""
from pathlib import Path
from contextlib import ExitStack
import copy,errno,json,os,platform,shutil,socket,sqlite3,subprocess,sys,threading,unittest,uuid
from unittest.mock import patch
import producer as app
sys.path.insert(0,str(app.ROOT/'EXPERIMENTS/local_command_adapter'))
import test_commands as ct
fx=ct.fixtures
class Tests(unittest.TestCase):
    def setUp(self):
        self.h=ct.Tests('test_01_actual_cli_save_receipt_four_reads_rebuild_search');self.h.setUp();self.f=self.h.f;self.source=self.f.temp/'source';fx.private(self.source);self.tx=self.f.bundle.m['transaction_id']
    def tearDown(self):self.h.tearDown()
    def draft(self,b=None):
        b=(b or self.f.bundle).clone();p=self.source/b.m['transaction_id'];fx.private(p);d={**b.m,'protocol':'local-bank-draft/1','files':list(b.files)}
        for n,raw in {**b.files,'DRAFT.json':app.encoded(d)}.items():
            q=p/n
            for parent in reversed(q.parent.parents):
                if parent.is_relative_to(p) and not parent.exists():fx.private(parent)
            if not q.parent.exists():fx.private(q.parent)
            q.write_bytes(raw)
            if os.name!='nt':q.chmod(0o600)
        return b,p,d
    def publisher(self,**kw):return app.Publisher(self.f.intake,self.source,_portable_fixture=os.name!='nt',**kw)
    def runpub(self,tx=None,action='publish',**kw):return self.publisher(**kw).execute(action,tx or self.tx)
    def good(self,b=None):
        b,p,d=self.draft(b);r=self.runpub(b.m['transaction_id']);self.assertEqual(r['status'],'PUBLISHED',r);self.assertFalse(r['Bank_accepted']);self.assertEqual(self.h.count(),0);return b,p,r
    def bytes_at(self,p):return {q.relative_to(p).as_posix():q.read_bytes() for q in p.rglob('*') if q.is_file()}
    def cli(self,action,tx=None,phase=None,extra=None):
        cmd=[sys.executable,'-X','utf8',str(Path(__file__)),'--producer-cli'] if os.name!='nt' or phase else [sys.executable,'-X','utf8',str(Path(app.__file__))]
        if phase:cmd+=['--phase',phase]
        cmd+=[action,'--intake-root',str(self.f.intake),'--source-root',str(self.source),'--transaction-id',tx or self.tx];cmd+=extra or []
        return subprocess.run(cmd,capture_output=True,timeout=25)
    def rejected(self,r):self.assertIn(r['status'],['REJECTED','IO_ERROR','INTEGRITY_ERROR','CONFLICT'],r);self.assertFalse(r['Bank_accepted']);self.assertEqual(self.h.count(),0)
    def test_01_default_cli_producer_save_receipt_reads_search(self):
        b,p,d=self.draft();out=self.cli('publish');self.assertEqual(out.returncode,0,out.stderr+out.stdout);r=json.loads(out.stdout);self.assertFalse(r['Bank_accepted']);self.assertEqual(self.h.count(),0)
        out=self.h.cli('save',tx=self.tx);self.assertEqual(out.returncode,0,out.stdout);receipt=json.loads(out.stdout)['receipt'];self.assertEqual(receipt['manifest_sha256'],r['manifest_sha256']);self.assertEqual(self.h.query(self.h.receipt())['data']['receipt'],receipt)
        for kind in ['Asset','Entity','Annotation','Collection']:
            out=self.h.cli('query',app.encoded(self.h.q(kind,'collection.get' if kind=='Collection' else 'bank.get')));self.assertEqual(out.returncode,0,out.stdout);self.assertEqual(json.loads(out.stdout)['data']['document'],b.doc(kind)[1])
        self.assertEqual(self.h.cli('rebuild-search').returncode,0);self.assertGreater(self.h.query(self.h.searchq())['data']['total_matches'],0)
    def test_02_exact_bytes_manifest_ids_and_independent_hash_oracle(self):
        b,p,r=self.good();dest=self.f.intake/self.tx;mraw=(dest/'manifest.json').read_bytes();m=json.loads(mraw)
        self.assertEqual({k:v for k,v in m.items() if k not in ['protocol','files']},{k:v for k,v in b.m.items() if k not in ['protocol','files']});self.assertEqual(m['files'],[{'path':n,'byte_length':len(b.files[n]),'sha256':app.im.sha(b.files[n])} for n in sorted(b.files)])
        self.assertEqual(mraw,json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode());self.assertEqual(r['manifest_sha256'],app.im.sha(mraw))
        for n,raw in b.files.items():self.assertEqual((dest/n).read_bytes(),raw)
        self.assertEqual((dest/'READY.json').read_bytes(),app.encoded({'protocol':'local-bank-intake/1','transaction_id':self.tx,'manifest_byte_length':len(mraw),'manifest_sha256':app.im.sha(mraw)}));self.assertFalse((dest/'READY.pending').exists())
    def test_03_repeat_and_reordered_draft_never_rewrites_published(self):
        b,p,r=self.good();dest=self.f.intake/self.tx;before=self.bytes_at(dest);d=json.loads((p/'DRAFT.json').read_bytes());d['files'].reverse();(p/'DRAFT.json').write_text(json.dumps(d,indent=2));out=self.runpub();self.assertEqual(out['status'],'ALREADY_PUBLISHED',out);self.assertEqual(out['manifest_sha256'],r['manifest_sha256']);self.assertEqual(before,self.bytes_at(dest))
    def test_04_changed_same_transaction_conflict_preserves_all_bytes(self):
        b,p,r=self.good();dest=self.f.intake/self.tx;before=self.bytes_at(dest);op,d=b.doc('Annotation');d['data']['body']='changed';(p/op['document_path']).write_bytes(app.encoded(d));out=self.runpub();self.assertEqual(out['status'],'CONFLICT',out);self.assertEqual(before,self.bytes_at(dest))
    def test_05_inspect_after_source_removed_no_bank_claim(self):
        b,p,r=self.good();shutil.rmtree(self.source);out=app.Publisher(self.f.intake,_portable_fixture=os.name!='nt').execute('inspect',self.tx);self.assertEqual(out['status'],'PUBLISHED',out);self.assertEqual(out['manifest_sha256'],r['manifest_sha256']);self.assertFalse(out['Bank_accepted']);self.assertEqual(self.h.count(),0)
    def test_06_missing_and_incomplete_do_not_repair(self):
        b,p,d=self.draft();self.assertEqual(self.runpub(action='inspect')['status'],'NOT_FOUND');dest=self.f.intake/self.tx;fx.private(dest);(dest/'owned.txt').write_bytes(b'keep');before=self.bytes_at(dest);self.assertEqual(self.runpub()['status'],'INCOMPLETE');self.assertEqual(self.runpub(action='inspect')['status'],'INCOMPLETE');self.assertEqual(before,self.bytes_at(dest));self.rejected(self.runpub(action='resume'));self.assertEqual(before,self.bytes_at(dest))
    def test_07_pending_complete_explicit_resume_only(self):
        b,p,d=self.draft()
        def hook(n,v):
            if n=='before_move':raise OSError(errno.EIO,'owned fault')
        self.assertEqual(self.runpub(_hook=hook)['status'],'IO_ERROR');dest=self.f.intake/self.tx;before=self.bytes_at(dest);self.assertIn('READY.pending',before);self.assertEqual(self.runpub()['status'],'INCOMPLETE');self.assertEqual(before,self.bytes_at(dest));out=self.runpub(action='resume');self.assertEqual(out['status'],'PUBLISHED',out);after=self.bytes_at(dest);self.assertEqual(after.pop('READY.json'),before.pop('READY.pending'));self.assertEqual(after,before)
    def test_08_partial_resume_rejected_bytes_preserved(self):
        b,p,d=self.draft()
        def hook(n,v):
            if n=='copy_chunk':raise OSError(errno.ENOSPC,'owned no disk fill')
        self.assertEqual(self.runpub(_hook=hook)['status'],'IO_ERROR');dest=self.f.intake/self.tx;before=self.bytes_at(dest);self.assertNotIn('READY.json',before);self.rejected(self.runpub(action='resume'));self.assertEqual(before,self.bytes_at(dest))
    def test_09_pending_changed_input_conflict_without_rename(self):
        b,p,d=self.draft()
        def hook(n,v):
            if n=='before_move':raise OSError()
        self.runpub(_hook=hook);dest=self.f.intake/self.tx;before=self.bytes_at(dest);op,d=b.doc('Annotation');d['data']['body']='different pending';(p/op['document_path']).write_bytes(app.encoded(d));self.assertEqual(self.runpub(action='resume')['status'],'CONFLICT');self.assertEqual(before,self.bytes_at(dest))
    def test_10_invalid_schema_identity_date_before_target_creation(self):
        for change in [lambda d:d.update(protocol='bad'),lambda d:d.update(transaction_id=str(uuid.uuid4())),lambda d:d.update(created_at='bad'),lambda d:d.update(extra=True)]:
            b=fx.Bundle.entity();b,p,d=self.draft(b);change(d);(p/'DRAFT.json').write_bytes(app.encoded(d));self.rejected(self.runpub(b.m['transaction_id']));self.assertFalse((self.f.intake/b.m['transaction_id']).exists())
    def test_11_strict_json_duplicate_nan_utf8_depth_before_copy(self):
        b,p,d=self.draft()
        for raw in [b'{"a":1,"a":2}',b'NaN',b'\xff',b'['*66+b']'*66]:
            (p/'DRAFT.json').write_bytes(raw);self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_12_invalid_paths_case_ads_reserved_escape_before_copy(self):
        b,p,d=self.draft()
        for name in ['../outside','/absolute','C:/absolute','a:b','Upper.json','nul.txt','a\\b','draft.json','manifest.json','READY.json']:
            d['files']=[name];(p/'DRAFT.json').write_bytes(app.encoded(d));self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_13_duplicate_files_operations_and_directory_collision(self):
        b,p,d=self.draft();original=copy.deepcopy(d)
        for change in [lambda d:d['files'].append(d['files'][0]),lambda d:d['operations'].append(d['operations'][0]),lambda d:d['files'].extend(['x','x/y'])]:
            d=copy.deepcopy(original);change(d);(p/'DRAFT.json').write_bytes(app.encoded(d));self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_14_source_extra_missing_file_not_published(self):
        b,p,d=self.draft();extra=p/'extra.txt';extra.write_bytes(b'x');self.rejected(self.runpub());extra.unlink();(p/d['files'][0]).unlink();self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_15_domain_and_asset_descriptor_rejected_before_copy(self):
        for kind,change in [('Annotation',lambda d:d.update(schema='bank.types/999')),('Entity',lambda d:d.update(object_id=str(uuid.uuid4()))),('Asset',lambda d:d['data']['storage'].update(sha256='0'*64))]:
            b=fx.Bundle();b.m['transaction_id']=str(uuid.uuid4());b.edit(kind,change);b,p,d=self.draft(b);self.rejected(self.runpub(b.m['transaction_id']));self.assertFalse((self.f.intake/b.m['transaction_id']).exists())
    def test_16_external_refs_and_cas_app_owns_acceptance(self):
        b=fx.Bundle.entity();b.edit('Entity',lambda d:d['data'].update(asset_refs=[{'object_type':'Asset','object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4())}]));b,p,r=self.good(b);out=self.h.c.save('bank.save',b.m['transaction_id']);self.assertEqual(out['status'],'REJECTED',out);self.assertEqual(self.h.count(),0);self.assertEqual(self.runpub(b.m['transaction_id'],action='inspect')['status'],'PUBLISHED')
    def test_17_limits_draft_work_metadata_time_directories(self):
        b,p,d=self.draft()
        for limits in [{'draft_bytes':1},{'work_bytes':1},{'metadata_bytes':1},{'elapsed_ms':-1},{'directories':0}]:
            self.rejected(self.runpub(_limits=limits));self.assertFalse((self.f.intake/self.tx).exists())
    def test_18_source_hardlink_rejected_no_target(self):
        b,p,d=self.draft();os.link(p/d['files'][0],self.f.temp/'alias');self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_19_target_hardlink_and_tamper_inspect_never_ok(self):
        b,p,r=self.good();dest=self.f.intake/self.tx;n=next(iter(b.files));os.link(dest/n,self.f.temp/'alias');self.rejected(self.runpub(action='inspect'));(self.f.temp/'alias').unlink();(dest/n).write_bytes(b'bad');self.rejected(self.runpub(action='inspect'))
    def test_20_root_overlap_relative_missing_no_autocreation(self):
        b,p,d=self.draft()
        for intake,source in [(self.source,self.source),(Path('relative'),self.source),(self.f.intake,self.f.temp/'absent')]:
            r=app.Publisher(intake,source,_portable_fixture=os.name!='nt').execute('publish',self.tx);self.rejected(r)
        self.assertFalse((self.f.temp/'absent').exists());self.assertFalse((self.f.intake/self.tx).exists())
    def test_21_source_mutation_denied_native_or_caught_fixture(self):
        b,p,d=self.draft();n=d['files'][0];blocked=[]
        def hook(event,v):
            if event=='source_validated':
                try:(p/n).write_bytes(b'mutated')
                except OSError:blocked.append(True)
        out=self.runpub(_hook=hook)
        if os.name=='nt':self.assertTrue(blocked);self.assertEqual(out['status'],'PUBLISHED',out)
        else:self.rejected(out);self.assertFalse((self.f.intake/self.tx/'READY.json').exists())
    def test_22_target_tamper_pre_move_audit_refuses(self):
        b,p,d=self.draft()
        def hook(event,base):
            if event=='before_move':(base/d['files'][0]).write_bytes(b'tamper')
        self.rejected(self.runpub(_hook=hook));self.assertFalse((self.f.intake/self.tx/'READY.json').exists())
    def test_23_root_rename_lease_denied_or_checked_no_escape(self):
        b,p,d=self.draft();alias=self.f.temp/'moved-intake';blocked=[]
        def hook(event,v):
            if event=='before_move':
                try:self.f.intake.rename(alias)
                except OSError:blocked.append(True)
        out=self.runpub(_hook=hook)
        if os.name=='nt':self.assertTrue(blocked);self.assertEqual(out['status'],'PUBLISHED',out)
        else:self.rejected(out);alias.rename(self.f.intake);self.assertFalse((self.f.intake/self.tx/'READY.json').exists())
    def test_24_native_junction_or_fixture_symlink_refused(self):
        b,p,d=self.draft();alias=self.f.temp/'source-alias'
        if os.name=='nt':
            r=subprocess.run(['cmd','/c','mklink','/J',str(alias),str(self.source)],capture_output=True,timeout=10);self.assertEqual(r.returncode,0,r.stderr)
        else:alias.symlink_to(self.source,target_is_directory=True)
        try:self.rejected(app.Publisher(self.f.intake,alias,_portable_fixture=os.name!='nt').execute('publish',self.tx));self.assertFalse((self.f.intake/self.tx).exists())
        finally:alias.rmdir() if os.name=='nt' else alias.unlink()
    def test_25_actual_no_replace_move_collision_preserves_both(self):
        folder=self.f.temp/'move';fx.private(folder);(folder/'READY.pending').write_bytes(b'new');(folder/'READY.json').write_bytes(b'old')
        with self.assertRaises(OSError):app.io.move_no_replace(folder/'READY.pending',folder/'READY.json')
        self.assertEqual((folder/'READY.pending').read_bytes(),b'new');self.assertEqual((folder/'READY.json').read_bytes(),b'old')
    def test_26_fault_flush_no_complete_marker(self):
        b,p,d=self.draft()
        with patch.object(app.io.File,'flush',side_effect=OSError(errno.ENOSPC,'owned flush fault')):self.assertEqual(self.runpub()['status'],'IO_ERROR')
        self.assertFalse((self.f.intake/self.tx/'READY.json').exists());self.assertEqual(self.runpub()['status'],'INCOMPLETE')
    def test_27_cancel_before_and_unknown_after_move_inspect(self):
        for phase in ['before_move','after_move']:
            b=fx.Bundle.entity();b,p,d=self.draft(b)
            def hook(n,v):
                if n==phase:raise KeyboardInterrupt()
            out=self.runpub(b.m['transaction_id'],_hook=hook);self.assertEqual(out['status'],'CANCELLED' if phase=='before_move' else 'UNKNOWN',out);self.assertIsNone(out['published']);out=self.runpub(b.m['transaction_id'],action='inspect');self.assertEqual(out['status'],'INCOMPLETE' if phase=='before_move' else 'PUBLISHED',out)
    def test_28_post_move_io_unknown_recover_same_identity(self):
        b,p,d=self.draft()
        def hook(n,v):
            if n=='after_move':raise OSError('Must not echo payload')
        out=self.runpub(_hook=hook);self.assertEqual(out['status'],'UNKNOWN',out);self.assertNotIn('echo',json.dumps(out));self.assertEqual(self.runpub(action='inspect')['status'],'PUBLISHED');self.assertEqual(self.runpub()['status'],'ALREADY_PUBLISHED')
    def test_29_actual_owned_process_death_publication_boundaries(self):
        for phase in ['directory_created','before_move','after_move']:
            b=fx.Bundle.entity();b,p,d=self.draft(b);tx=b.m['transaction_id'];out=self.cli('publish',tx=tx,phase=phase);self.assertEqual(out.returncode,71,out.stderr);state=self.runpub(tx,action='inspect')['status'];self.assertEqual(state,'PUBLISHED' if phase=='after_move' else 'INCOMPLETE')
            if phase=='directory_created':self.rejected(self.runpub(tx,action='resume'))
            elif phase=='before_move':self.assertEqual(self.runpub(tx,action='resume')['status'],'PUBLISHED')
            else:self.assertEqual(self.runpub(tx)['status'],'ALREADY_PUBLISHED')
    def test_30_reader_before_publication_and_two_publishers(self):
        b,p,d=self.draft();entered=threading.Event();release=threading.Event();results=[]
        def hook(n,v):
            if n=='before_move':entered.set();self.assertTrue(release.wait(8))
        thread=threading.Thread(target=lambda:results.append(self.runpub(_hook=hook)));thread.start()
        try:
            self.assertTrue(entered.wait(8));self.assertEqual(self.runpub()['status'],'INCOMPLETE');r=(app.reader.read_package if os.name=='nt' else ct.portable_read)(self.f.intake,self.tx,self.f.stage,policy_bytes=self.f.c.policy.raw,schema=self.f.c.env);self.assertNotEqual(r.status,'VERIFIED_TRANSPORT');self.assertEqual(self.h.count(),0)
        finally:release.set();thread.join(10)
        self.assertFalse(thread.is_alive());self.assertEqual(results[0]['status'],'PUBLISHED',results);self.assertEqual(self.runpub()['status'],'ALREADY_PUBLISHED');self.assertEqual(self.h.c.save('bank.save',self.tx)['status'],'ACCEPTED')
    def test_31_update_old_pinned_and_replay_after_restart(self):
        b,p,r=self.good();first=self.h.cli('save',tx=self.tx);self.assertEqual(first.returncode,0,first.stdout);old=self.h.query(self.h.q())['data']['ref'];new=fx.Bundle('continuation');new,p,d=self.draft(new);tx=new.m['transaction_id'];self.assertEqual(self.runpub(tx)['status'],'PUBLISHED');self.assertEqual(self.h.cli('save',tx=tx).returncode,0);q=self.h.q();q['selector']={'mode':'pinned','revision_id':old['revision_id']};out=self.h.cli('query',app.encoded(q));self.assertEqual(json.loads(out.stdout)['data']['ref'],old);self.assertEqual(json.loads(self.h.cli('save',tx=self.tx).stdout)['status'],'REPLAY');self.assertEqual(self.h.count(),2)
    def test_32_actual_closed_stdout_inspect_then_receipt(self):
        b,p,d=self.draft();cmd=[sys.executable,'-X','utf8',str(Path(__file__)),'--producer-cli'] if os.name!='nt' else [sys.executable,'-X','utf8',str(Path(app.__file__))];cmd+=['publish','--intake-root',str(self.f.intake),'--source-root',str(self.source),'--transaction-id',self.tx];proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);proc.stdout.close();err=proc.stderr.read();proc.stderr.close();proc.wait(timeout=25);self.assertEqual(proc.returncode,4,err);self.assertEqual(self.runpub(action='inspect')['status'],'PUBLISHED');self.assertEqual(self.h.c.save('bank.save',self.tx)['status'],'ACCEPTED');self.assertEqual(self.h.query(self.h.receipt())['status'],'OK')
    def test_33_output_cap_returns_unknown_after_move_bounded(self):
        b,p,d=self.draft();out=self.runpub(_limits={'response_bytes':100});self.assertEqual(out['status'],'UNKNOWN',out);self.assertLessEqual(len(app.encoded(out)),8192);self.assertEqual(self.runpub(action='inspect')['status'],'PUBLISHED')
    def test_34_no_network_no_allocator_no_bank_mutation_and_closed_cli(self):
        b,p,d=self.draft()
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No network')),patch.object(uuid,'uuid4',side_effect=AssertionError('IDs supplied')),patch.object(app.im.Store,'initialize',side_effect=AssertionError('No initialize')):out=self.runpub();self.assertEqual(out['status'],'PUBLISHED',out)
        self.assertEqual(self.h.count(),0);out=self.cli('publish',extra=['--sql','PRIVATE_PAYLOAD']);self.assertEqual(out.returncode,2);self.assertNotIn(b'PRIVATE_PAYLOAD',out.stdout+out.stderr)
    def test_35_actual_sparse_file_cap_and_descriptor_count_before_copy(self):
        b,p,d=self.draft();name=next(n for n in d['files'] if not any(o['document_path']==n for o in d['operations']))
        with (p/name).open('r+b') as f:f.truncate(self.f.c.policy['file_bytes']+1)
        self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists());d['files']=['x'+str(i) for i in range(129)];(p/'DRAFT.json').write_bytes(app.encoded(d));self.rejected(self.runpub());self.assertFalse((self.f.intake/self.tx).exists())
    def test_36_invalid_action_identity_before_any_directory_io(self):
        pub=self.publisher()
        with patch.object(app.io,'Directory',side_effect=AssertionError('No I/O')):
            for action,tx in [('bad',self.tx),('publish','../bad'),('publish',None),('publish',True)]:self.assertEqual(pub.execute(action,tx)['status'],'REJECTED')
    def test_37_move_busy_preserves_pending_explicit_retry(self):
        b,p,d=self.draft()
        with patch.object(app.io,'move_no_replace',side_effect=OSError(errno.EBUSY,'owned move busy')):out=self.runpub()
        self.assertEqual(out['status'],'RETRYABLE_BUSY',out);dest=self.f.intake/self.tx;before=self.bytes_at(dest);self.assertNotIn('READY.json',before);self.assertIn('READY.pending',before);self.assertEqual(self.runpub(action='resume')['status'],'PUBLISHED')
class Evidence(ct.Evidence):pass
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--producer-cli':
        args=sys.argv[2:];phase=None
        if args[:1]==['--phase']:phase=args[1];args=args[2:]
        if phase:
            original=app.Publisher
            class FaultPublisher(original):
                def __init__(self,*a,**k):
                    def hook(n,v):
                        if n==phase:os._exit(71)
                    super().__init__(*a,**k,_hook=hook)
            app.Publisher=FaultPublisher
        sys.exit(app.main(args,_portable_fixture=os.name!='nt'))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));folder=Path(__file__).parent;at=app.im.now();name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';report={'record_kind':'synthetic_R1_package_producer_evidence','at':at,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'transport':'actual Windows native handles/NTFS/default CLI' if os.name=='nt' else 'trusted Linux portable publication fixture only','tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'source_sha256':{n:app.im.sha((folder/n).read_bytes()) for n in ['producer.py','producer_io.py','test_producer.py','draft.schema.json','result.schema.json','LIMITS.json']},'limitations':['Prepared synthetic drafts only, no real Bank/install/editor/UI/release acceptance','Portable fixture cannot prove Windows ACL/NTFS/atomic publication','Trusted owner/operator/code/root parents; no malicious admin or same-owner adversary resistance','Process death and FlushFileBuffers/MoveFileExW tests do not prove physical power-loss durability','Existing incomplete package never repaired or automatically removed; explicit matching pending resume only','Publication is not Bank acceptance; external refs/CAS and durable accepted receipts belong to app']}
    p=folder/name
    if p.exists():h=folder/'TEST_HISTORY';h.mkdir(exist_ok=True);shutil.copyfile(p,h/(name+'-'+uuid.uuid4().hex+'.json'))
    p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');p=folder/'ISSUES.json';issues=json.loads(p.read_text(encoding='utf-8'));known={i['id']:i for i in issues['issues']}
    for c in report['cases']:
        iid='PUB-TEST-'+c['id'];i=known.get(iid)
        if c['observed']=='FAIL':
            if i is None:i={'id':iid,'title':'Publication assertion '+c['id'],'history':[]};issues['issues'].append(i);known[iid]=i
            i['status']='open';i['history'].append({'at':at,'status':'open','evidence':name,'detail':c['detail']})
        elif i and i['status']=='open':i['status']='resolved_local' if os.name!='nt' else 'resolved_native';i['history'].append({'at':at,'status':i['status'],'evidence':name,'note':'Same-source rerun passes; prior failure retained.'})
    p.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':result.bad,'report':str(folder/name)}),flush=True);sys.exit(not result.wasSuccessful())
