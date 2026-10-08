"""Mandatory native synthetic tests; no Bank, network, global settings or unrelated processes."""
import base64, copy, ctypes, datetime, errno, hashlib, json, os, platform, queue, shutil, sqlite3, subprocess, sys, tempfile, threading, time, unittest, uuid
from pathlib import Path
from unittest.mock import patch
import reader as r
import win32_io as n
ROOT=r.ROOT
POLICY=(ROOT/'PLANNING/CONTRACTS/LOCAL_INTAKE_LIMITS.json').read_bytes()
SCHEMA=json.loads((ROOT/'PLANNING/CONTRACTS/LOCAL_WRITE_ENVELOPE.schema.json').read_text(encoding='utf-8'))
def raw(obj):return json.dumps(obj,separators=(',',':'),ensure_ascii=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='bank-secure-test-'));self.intake=self.temp/'intake';self.stage=self.temp/'stage'
        n.private_directory(self.intake);n.private_directory(self.stage);self.tx=str(uuid.uuid4());self.p=self.intake/self.tx;n.private_directory(self.p)
        self.m={'protocol':r.PROTOCOL,'transaction_id':self.tx,'command':'commit_revisions','intent':'independent_save','created_at':'2026-10-06T00:00:00Z','producer':{'name':'synthetic-test','version':'1'},'operations':[],'files':[]}
        self.add('document.json',b'{"body":"fixture"}',True);self.add('payload.bin',b'hello');self.publish()
    def tearDown(self):shutil.rmtree(self.temp)
    def add(self,name,b,document=False):
        p=self.p/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        self.m['files'].append({'path':name,'byte_length':len(b),'sha256':sha(b)})
        if document:self.m['operations'].append({'object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4()),'base_revision_id':None,'type':'Annotation','schema_ref':'annotation/1','document_path':name})
    def publish(self,manifest=None,ready=None):
        b=raw(self.m) if manifest is None else manifest;(self.p/'manifest.json').write_bytes(b)
        ready=raw({'protocol':r.PROTOCOL,'transaction_id':self.tx,'manifest_byte_length':len(b),'manifest_sha256':sha(b)}) if ready is None else ready
        (self.p/'READY.json').write_bytes(ready)
    def read(self,**kw):return r.read_package(self.intake,self.tx,self.stage,policy_bytes=kw.pop('policy_bytes',POLICY),schema=SCHEMA,**kw)
    def policy(self,**limits):
        p=json.loads(POLICY);p['limits'].update(limits);return raw(p)
    def reject(self,code=None,**kw):
        result=self.read(**kw);self.assertEqual(result.status,'REJECTED',result.code);self.assertIsNone(result.snapshot)
        if code:self.assertEqual(result.code,code)
        self.assertEqual(list(self.stage.iterdir()),[]);return result
    def fingerprint(self):return {p.relative_to(self.p).as_posix():sha(p.read_bytes()) for p in self.p.rglob('*') if p.is_file()}
    def success(self,**kw):
        x=self.read(**kw);self.assertEqual(x.status,'VERIFIED_TRANSPORT',x.code);self.assertIsNotNone(x.snapshot);return x.snapshot
    def test_01_supported_fixture_snapshot_lifetime(self):
        index=json.loads((ROOT/'PLANNING/CONTRACTS/BANK_TYPE_EXAMPLES/INDEX.json').read_text())
        entry=index['fixtures'][0] if isinstance(index,dict) and 'fixtures' in index else None
        # Exact accepted static fixture, not the intentionally domain-invalid transport helper.
        fixture=next((ROOT/'PLANNING/CONTRACTS/BANK_TYPE_EXAMPLES/create').iterdir())
        shutil.rmtree(self.p);self.tx=fixture.name;self.p=self.intake/self.tx;n.private_directory(self.p);shutil.copytree(fixture,self.p,dirs_exist_ok=True)
        before=self.fingerprint()
        with patch.object(sqlite3,'connect',side_effect=AssertionError('Bank access forbidden')):
            s=self.success();self.assertEqual(s.policy_bytes,POLICY)
            self.assertEqual(s.manifest_bytes,(self.p/'manifest.json').read_bytes());self.assertEqual(s.ready_bytes,(self.p/'READY.json').read_bytes())
            expected={f: (self.p/f).read_bytes() for f in s.files}
            # Source handles closed, snapshot remains independent after actual source rewrite.
            for f in expected:(self.p/f).write_bytes(b'changed after successful read')
            for f,b in expected.items():self.assertEqual(b''.join(s.iter_bytes(f)),b)
            s.close();self.assertEqual(list(self.stage.iterdir()),[])
            with self.assertRaisesRegex(r.Rejected,'SNAPSHOT_CLOSED'):list(s.iter_bytes(next(iter(expected))))
        self.assertTrue(before)
    def test_02_continuation_without_history_or_database(self):
        fixture=next((ROOT/'PLANNING/CONTRACTS/BANK_TYPE_EXAMPLES/continuation').iterdir())
        shutil.rmtree(self.p);self.tx=fixture.name;self.p=self.intake/self.tx;n.private_directory(self.p);shutil.copytree(fixture,self.p,dirs_exist_ok=True)
        with patch.object(sqlite3,'connect',side_effect=AssertionError('Bank access forbidden')):
            with self.success() as s:
                manifest=json.loads(s.manifest_bytes);self.assertTrue(any(op['base_revision_id'] for op in manifest['operations']))
                for name in s.files:self.assertEqual(b''.join(s.iter_bytes(name)),(self.p/name).read_bytes())
                self.assertEqual(s.status,'VERIFIED_TRANSPORT');self.assertFalse(hasattr(s,'receipt'))
    def test_03_missing_and_pending_ready(self):
        (self.p/'READY.json').unlink()
        for pending in [False,True]:
            if pending:(self.p/'READY.pending').write_bytes(b'in progress')
            result=self.read();self.assertEqual(result.status,'INCOMPLETE');self.assertIsNone(result.snapshot);self.assertEqual(list(self.stage.iterdir()),[])
    def test_04_invalid_existing_markers(self):
        for b in [b'{',b'{}',b'\xef\xbb\xbf{}',b'{"x":1,"x":2}',b'{"x":NaN}',b'\xff']:
            with self.subTest(marker=b):(self.p/'READY.json').write_bytes(b);self.reject()
    def test_05_marker_manifest_bindings(self):
        self.publish();ready=json.loads((self.p/'READY.json').read_bytes())
        for key,value in [('transaction_id',str(uuid.uuid4())),('manifest_sha256','0'*64),('manifest_byte_length',1),('protocol','invalid')]:
            with self.subTest(field=key):other=dict(ready);other[key]=value;(self.p/'READY.json').write_bytes(raw(other));self.reject()
        self.m['transaction_id']=str(uuid.uuid4());self.publish();self.reject('TRANSACTION_ID_MISMATCH')
    def test_06_missing_tampered_and_extra_entries(self):
        original=(self.p/'manifest.json').read_bytes();(self.p/'manifest.json').unlink();self.reject('MISSING_MANIFEST');self.publish(manifest=original)
        b=(self.p/'payload.bin').read_bytes();(self.p/'payload.bin').unlink();self.reject();(self.p/'payload.bin').write_bytes(b'jello');self.reject('FILE_INTEGRITY');(self.p/'payload.bin').write_bytes(b)
        for name,directory in [('extra.bin',False),('empty',True),('READY.pending',False)]:
            p=self.p/name;p.mkdir() if directory else p.write_bytes(b'x');self.reject();p.rmdir() if directory else p.unlink()
    def test_07_paths_and_collisions(self):
        original=copy.deepcopy(self.m)
        for path in ['../escape','a/../escape','payload.bin:ads','CON.txt','NUL','com1.bin','A.json','ready.json','a\\b.json','a//b.json']:
            with self.subTest(path=path):self.m=copy.deepcopy(original);self.m['files'][1]['path']=path;self.publish();self.reject()
        self.m=copy.deepcopy(original);self.m['files'].append(dict(self.m['files'][1]));self.publish();self.reject('DUPLICATE_FILE')
        self.m=copy.deepcopy(original);self.m['operations'].append(dict(self.m['operations'][0]));self.publish();self.reject('DUPLICATE_DOCUMENT')
    def test_08_real_payload_symlink_and_hardlink(self):
        outside=self.temp/'outside';outside.write_bytes(b'hello');p=self.p/'payload.bin';p.unlink();os.symlink(outside,p);self.reject();p.unlink()
        os.link(outside,p);self.reject('HARDLINK');p.unlink();self.assertEqual(outside.read_bytes(),b'hello')
    def test_09_real_directory_symlink_and_junction(self):
        target=self.temp/'target';target.mkdir();(target/'payload.bin').write_bytes(b'hello')
        self.m['files'][1]['path']='nested/payload.bin';self.publish();(self.p/'payload.bin').unlink();link=self.p/'nested'
        os.symlink(target,link,target_is_directory=True);self.reject('REPARSE_POINT');link.unlink()
        cp=subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(target)],capture_output=True,text=True,timeout=5);self.assertEqual(cp.returncode,0,cp.stderr)
        self.reject('REPARSE_POINT');os.rmdir(link);self.assertEqual((target/'payload.bin').read_bytes(),b'hello')
    def test_10_root_reparse_and_overlap(self):
        link=self.temp/'intake-link';os.symlink(self.intake,link,target_is_directory=True)
        x=r.read_package(link,self.tx,self.stage,policy_bytes=POLICY,schema=SCHEMA);self.assertEqual(x.status,'REJECTED');self.assertEqual(x.code,'REPARSE_ROOT_OR_PARENT');link.unlink()
        x=r.read_package(self.intake,self.tx,self.intake,policy_bytes=POLICY,schema=SCHEMA);self.assertEqual(x.code,'ROOT_OVERLAP')
        for root in [Path('relative'),Path(r'\\server\share')]:
            x=r.read_package(root,self.tx,self.stage,policy_bytes=POLICY,schema=SCHEMA);self.assertEqual(x.status,'REJECTED')
    def test_11_broad_acl_rejected(self):
        bad=self.temp/'broad';sid=n.current_sid();sd=n.C.c_void_p();n.checked(n.sddl_sd('O:'+sid+'D:P(A;OICI;FA;;;WD)(A;OICI;FA;;;'+sid+')',1,n.C.byref(sd),None))
        try:
            sa=n.SecurityAttributes(n.C.sizeof(n.SecurityAttributes),sd,False);n.checked(n.mkdir_native(n.extended(bad),n.C.byref(sa)))
        finally:n.local_free(sd)
        x=r.read_package(bad,self.tx,self.stage,policy_bytes=POLICY,schema=SCHEMA);self.assertEqual(x.status,'REJECTED');self.assertEqual(x.code,'UNTRUSTED_DACL')
    def test_12_opened_payload_and_markers_cannot_swap(self):
        blocked=[]
        def hook(event,name):
            if event=='file_opened' and name=='payload.bin':
                for p in [self.p/'payload.bin',self.p/'READY.json',self.p/'manifest.json',self.p]:
                    try:os.rename(p,str(p)+'.swap')
                    except OSError:blocked.append(str(p))
                    else:self.fail('native held path unexpectedly renamed')
                try:(self.p/'payload.bin').write_bytes(b'evil!')
                except OSError:blocked.append('write')
                else:self.fail('native held payload unexpectedly written')
        with self.success(_hook=hook) as s:self.assertEqual(b''.join(s.iter_bytes('payload.bin')),b'hello')
        self.assertEqual(len(blocked),5)
    def test_13_actual_preopen_replacement_detected(self):
        changed=[]
        def hook(event,name):
            if event=='inventory_checked':
                p=self.p/'payload.bin';p.unlink();p.write_bytes(b'evil!');changed.append(True)
        self.reject('FILE_INTEGRITY',_hook=hook);self.assertEqual(changed,[True])
    def test_14_midcopy_extra_entry_detected(self):
        def hook(event,name):
            if event=='payload_chunk' and name=='payload.bin':(self.p/'extra.bin').write_bytes(b'created during copy')
        self.reject(_hook=hook)
    def test_15_snapshot_write_and_rename_blocked(self):
        with self.success() as s:
            path=next(s._directory.iterdir())
            with self.assertRaises(OSError):path.write_bytes(b'changed')
            with self.assertRaises(OSError):os.rename(path,path.with_suffix('.changed'))
            with self.assertRaises(OSError):os.rename(s._directory,s._directory.with_name('renamed'))
            self.assertEqual(b''.join(s.iter_bytes('payload.bin')),b'hello')
    def test_16_strict_json_and_depth(self):
        for b in [b'{"a":1,"a":2}',b'NaN',b'Infinity',b'-Infinity',b'1e999',b'"\\ud800"',b'\xff',b'\xef\xbb\xbf{}']:
            with self.subTest(value=b),self.assertRaises(r.Rejected):r.strict_json(b,1000,64)
        self.assertEqual(r.strict_json(b'{"a":"\\\"{[}\\\\"}',1000,1),{'a':'"{[}\\'})
        self.assertEqual(r.strict_json(b'['*64+b'0'+b']'*64,1000,64),json.loads(b'['*64+b'0'+b']'*64))
        with self.assertRaisesRegex(r.Rejected,'JSON_DEPTH'):r.strict_json(b'['*65+b'0'+b']'*65,1000,64)
    def test_17_document_invalid_json_rejected(self):
        for b in [b'{',b'{"x":NaN}',b'{"x":1,"x":2}',b'\xff',b'\xef\xbb\xbf{}',b'['*65+b'0'+b']'*65]:
            with self.subTest(value=b):
                (self.p/'document.json').write_bytes(b);self.m['files'][0].update(byte_length=len(b),sha256=sha(b));self.publish();self.reject()
    def test_18_ready_actual_default_byte_boundary(self):
        b=(self.p/'READY.json').read_bytes();cap=r.Policy(POLICY)['ready_bytes'];(self.p/'READY.json').write_bytes(b+b' '*(cap-len(b)))
        with self.success():pass
        with (self.p/'READY.json').open('ab') as f:f.write(b' ')
        self.reject('LIMIT_EXCEEDED')
    def test_19_manifest_actual_default_byte_boundary(self):
        b=raw(self.m);cap=r.Policy(POLICY)['manifest_bytes'];self.publish(manifest=b+b' '*(cap-len(b)))
        with self.success():pass
        self.publish(manifest=b+b' '*(cap+1-len(b)));self.reject('LIMIT_EXCEEDED')
    def test_20_document_actual_default_byte_boundary(self):
        cap=r.Policy(POLICY)['object_json_bytes'];b=b'"'+b'x'*(cap-2)+b'"';(self.p/'document.json').write_bytes(b);self.m['files'][0].update(byte_length=cap,sha256=sha(b));self.publish()
        with self.success():pass
        b+=b' ';(self.p/'document.json').write_bytes(b);self.m['files'][0].update(byte_length=len(b),sha256=sha(b));self.publish();self.reject('LIMIT_EXCEEDED')
    def test_21_default_file_count_boundary(self):
        for i in range(126):self.add('f'+str(i)+'.bin',b'')
        self.publish()
        with self.success():pass
        self.add('one-too-many.bin',b'');self.publish();self.reject('LIMIT_EXCEEDED')
    def test_22_default_operation_count_boundary(self):
        (self.p/'payload.bin').unlink();self.m['files'].pop()
        for i in range(127):self.add('d'+str(i)+'.json',b'{}',True)
        self.publish()
        with self.success():pass
        # 129 operations against <=128 file descriptors, counts checked pre-schema/precopy.
        self.m['operations'].append(copy.deepcopy(self.m['operations'][0]));self.publish();self.reject('LIMIT_EXCEEDED')
    def fill(self,name,length):
        chunk=b'x'*1048576;p=self.p/name;digest=hashlib.sha256()
        with p.open('wb') as f:
            remaining=length
            while remaining:b=chunk[:min(len(chunk),remaining)];f.write(b);digest.update(b);remaining-=len(b)
        return {'path':name,'byte_length':length,'sha256':digest.hexdigest()}
    def test_23_actual_64m_file_boundary(self):
        cap=r.Policy(POLICY)['file_bytes'];self.m['files'][1]=self.fill('payload.bin',cap);self.publish()
        with self.success() as s:self.assertEqual(sum(map(len,s.iter_bytes('payload.bin'))),cap)
        with (self.p/'payload.bin').open('ab') as f:f.write(b'x')
        self.reject('LIMIT_EXCEEDED')
    def test_24_actual_256m_package_boundary(self):
        cap=r.Policy(POLICY)['package_bytes'];fmax=r.Policy(POLICY)['file_bytes']
        if shutil.disk_usage(self.temp).free<3*cap:raise AssertionError('NOT_VERIFIED: insufficient owned temporary capacity for exact real boundary')
        (self.p/'payload.bin').unlink();self.m['files'].pop()
        for i in range(4):self.m['files'].append({'path':'large'+str(i)+'.bin','byte_length':fmax,'sha256':'0'*64})
        # Hashes have constant width; converge decimal byte-count/marker overhead before writing.
        for _ in range(8):
            self.publish();overhead=len((self.p/'READY.json').read_bytes())+len((self.p/'manifest.json').read_bytes())+self.m['files'][0]['byte_length']
            last=cap-overhead-3*fmax;self.m['files'][-1]['byte_length']=last
        for i in range(4):self.m['files'][i+1]=self.fill('large'+str(i)+'.bin',self.m['files'][i+1]['byte_length'])
        self.publish();total=sum(f['byte_length'] for f in self.m['files'])+sum((self.p/x).stat().st_size for x in ['READY.json','manifest.json']);self.assertEqual(total,cap)
        with self.success() as s:self.assertEqual(sum(x[0] for x in s.files.values())+len(s.ready_bytes)+len(s.manifest_bytes),cap)
        self.m['files'][-1]['byte_length']+=1;self.publish();self.reject('LIMIT_EXCEEDED')
    def test_25_actual_size_cannot_lie_and_small_chunks(self):
        self.m['files'][1]['byte_length']=1;self.publish();self.reject('FILE_INTEGRITY')
        self.m['files'][1]['byte_length']=5;self.publish();reads=[];original=n.Handle.read
        def record(handle,size):reads.append(size);return original(handle,size)
        with patch.object(n.Handle,'read',record):
            with self.success(policy_bytes=self.policy(blob_chunk_bytes=3)) as s:self.assertEqual(b''.join(s.iter_bytes('payload.bin')),b'hello')
        self.assertTrue(reads);self.assertLessEqual(max(reads),3)
    def test_26_read_write_enospc_cancel_cleanup_and_retry(self):
        before=self.fingerprint()
        for event,error in [('read_chunk',errno.EIO),('before_stage_write',errno.EIO),('before_stage_write',errno.ENOSPC)]:
            def hook(name,value):
                if name==event:raise OSError(error,'injected bounded fixture fault')
            result=self.read(_hook=hook);self.assertEqual(result.status,'IO_ERROR');self.assertIsNone(result.snapshot);self.assertEqual(list(self.stage.iterdir()),[]);self.assertEqual(self.fingerprint(),before)
            # Closed source handles, no previous success token; original retry remains possible.
            os.rename(self.p/'payload.bin',self.p/'check.bin');os.rename(self.p/'check.bin',self.p/'payload.bin')
        cancelled=[False]
        def hook(event,name):
            if event=='payload_chunk':cancelled[0]=True
        result=self.read(cancel=lambda:cancelled[0],_hook=hook);self.assertEqual(result.status,'CANCELLED');self.assertIsNone(result.snapshot);self.assertEqual(list(self.stage.iterdir()),[]);self.assertEqual(self.fingerprint(),before)
        with self.success() as s:self.assertEqual(s.transaction_id,self.tx)
    def test_27_owned_child_interruption_orphan_and_restart(self):
        before=self.fingerprint();child=self.temp/'child.py'
        child.write_text('import sys,threading\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nimport reader\ndef hook(event,name):\n if event=="payload_chunk":\n  print("PAUSED",flush=True);threading.Event().wait(15)\nx=reader.read_package(Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4]),_hook=hook)\nprint(x.status,flush=True)\n',encoding='utf-8')
        q=queue.Queue();p=subprocess.Popen([sys.executable,str(child),str(Path(r.__file__).parent),str(self.intake),self.tx,str(self.stage)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        def listen():
            for line in p.stdout:q.put(line.strip())
        thread=threading.Thread(target=listen,daemon=True);thread.start()
        try:self.assertEqual(q.get(timeout=8),'PAUSED');p.terminate();p.wait(timeout=5)
        finally:
            if p.poll() is None:p.kill();p.wait(timeout=5)
            thread.join(timeout=2);p.stdout.close()
        orphans=list(self.stage.iterdir());self.assertEqual(len(orphans),1);self.assertTrue(list(orphans[0].iterdir()));self.assertEqual(self.fingerprint(),before)
        # Process death releases locks, but an orphan's existence grants no snapshot/readiness.
        with self.success() as s:self.assertNotEqual(s._directory,orphans[0]);self.assertEqual(s.transaction_id,self.tx)
        self.assertEqual(list(self.stage.iterdir()),orphans)
        shutil.rmtree(orphans[0]);self.assertEqual(list(self.stage.iterdir()),[])
    def test_28_invalid_trusted_policy_and_transaction(self):
        for value in [True,0,-1,65]:
            with self.subTest(depth=value),self.assertRaises(r.Rejected):r.Policy(self.policy(json_container_depth=value))
        obj=json.loads(POLICY);obj['limits']['unknown']=1
        with self.assertRaises(r.Rejected):r.Policy(raw(obj))
        old=self.tx;self.tx='../outside';self.reject('INVALID_TRANSACTION_ID');self.tx=old
    def test_29_root_parent_reparse_and_parent_swap(self):
        link=self.temp/'parent-link';os.symlink(self.intake,link,target_is_directory=True)
        x=r.read_package(link/self.tx,self.tx,self.stage,policy_bytes=POLICY,schema=SCHEMA);self.assertEqual(x.code,'REPARSE_ROOT_OR_PARENT');link.unlink()
        self.add('nested/data.bin',b'x');self.publish();blocked=[]
        def hook(event,name):
            if event=='inventory_checked':
                try:os.rename(self.p/'nested',self.p/'moved')
                except OSError:blocked.append(True)
                else:self.fail('locked parent moved')
        with self.success(_hook=hook):pass
        self.assertEqual(blocked,[True])

class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[];self.bad=set()
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'id':test._testMethodName,'expected':'all assertions/mandatory cases pass','observed':'PASS'})
    def addFailure(self,test,err):super().addFailure(test,err);self.bad.add(test._testMethodName);self.cases.append({'id':test._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(err,test)})
    def addError(self,test,err):super().addError(test,err);self.bad.add(test._testMethodName);self.cases.append({'id':test._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(err,test)})
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err:self.bad.add(test._testMethodName);self.cases.append({'id':test._testMethodName,'subcase':str(subtest),'observed':'FAIL','detail':self._exc_info_to_string(err,test)})
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    now=datetime.datetime.now(datetime.timezone.utc).isoformat();folder=Path(__file__).parent
    report={'record_kind':'native_synthetic_secure_reader_evidence','at':now,'platform':platform.platform(),'python':sys.version,'executable':sys.executable,'tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'scope':'synthetic transport only; actual local NTFS links/ACL/sharing, exact default byte/count boundaries, deterministic mutation/fault and owned child interruption; no live Bank','limitations':['No administrator/authorized owner or hostile in-process protection','Trusted root parents/configuration','No hardware power-loss or real producer READY publication','No importer/domain/CAS/SQLite/runtime acceptance'],'source_sha256':{p.name:sha(p.read_bytes()) for p in [folder/'reader.py',folder/'win32_io.py',folder/'test_reader.py']}}
    old=folder/'TEST_RESULTS.json'
    if old.exists():
        hist=folder/'TEST_HISTORY';hist.mkdir(exist_ok=True);shutil.copyfile(old,hist/('run-'+str(uuid.uuid4())+'.json'))
    old.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    logpath=folder/'ISSUES.json';log=json.loads(logpath.read_text(encoding='utf-8'));known={x['id']:x for x in log['issues']}
    for name in sorted(result.bad):
        iid='SI-TEST-'+name;entry=known.get(iid)
        if entry is None:entry={'id':iid,'title':'Mandatory native case failed: '+name,'status':'open','history':[]};log['issues'].append(entry)
        entry['status']='open';entry['history'].append({'at':now,'status':'open','evidence':'TEST_RESULTS.json','detail':next(x['detail'] for x in result.cases if x['id']==name and x['observed']=='FAIL')})
    for entry in log['issues']:
        if entry['id'].startswith('SI-TEST-') and entry['status']=='open' and entry['id'][8:] not in result.bad:
            entry['status']='resolved';entry['history'].append({'at':now,'status':'resolved','evidence':'TEST_RESULTS.json','note':'Mandatory case rerun passed; prior failure retained in TEST_HISTORY.'})
    logpath.write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'failed_cases':sorted(result.bad),'report':str(old)}),flush=True)
    sys.exit(not result.wasSuccessful())
