"""Owned synthetic authoring integration, real process exits and mapped native GUI."""
from pathlib import Path
import copy,json,os,platform,shutil,socket,sqlite3,subprocess,sys,threading,time,unittest,uuid
from unittest.mock import patch
import authoring as a
import authoring_presenter as p
import authoring_ui
sys.path.insert(0,str(a.ROOT/'EXPERIMENTS/local_ui'))
import test_ui as old,window_capture

class Tests(unittest.TestCase):
    def setUp(self):
        self.h=old.Tests('test_01_empty_existing_bank_discovery_zero');self.h.setUp();self.roots={**self.h.roots,'authoring':self.h.f.temp/'authoring'};old.fx.private(self.roots['authoring']);self.w=self.workspace();self.backend=self.make_backend();self.original=self.h.f.temp/'owned-original.dat';self.raw=b'Owned algorithm bytes\x00\xff\r\n';self.original.write_bytes(self.raw)
    def tearDown(self):self.h.tearDown()
    def workspace(self,**kw):return a.Workspace(self.roots,_portable_fixture=os.name!='nt',**kw)
    def make_backend(self,**kw):
        if os.name!='nt':kw.setdefault('_controller_kwargs',{'_transport':old.ct.portable_read,'_store_factory':old.ct.PortableStore});kw.setdefault('_publisher_kwargs',{'_portable_fixture':True})
        return p.Backend(self.roots,_portable_fixture=os.name!='nt',**kw)
    def fields(self,kind='note',**kw):return {'kind':kind,'title':'Algorithm proof title',**({'path':str(self.original)} if kind=='file' else {'uri':'https://example.invalid/algorithms'} if kind=='url' else {'body':'A theory with exact \r\ntext, 🙂, <script>plain</script>'}),**kw}
    def prepare(self,kind='note',**kw):
        out=self.w.prepare(self.fields(kind,**kw));self.assertEqual(out['status'],'PREPARED',out);return out
    def execute(self,action,out,**kw):return self.backend.dispatch(action,{'transaction_id':out['transaction_id'],**kw})
    def save(self,out):
        pub=self.execute('publish',out);self.assertIn(pub['status'],['PUBLISHED','ALREADY_PUBLISHED'],pub);self.assertEqual(pub['manifest_sha256'],out['manifest_sha256']);saved=self.execute('save',out);self.assertIn(saved['status'],['ACCEPTED','REPLAY'],saved);return saved
    def doc(self,out):return json.loads((self.roots['source']/out['transaction_id']/'docs/object.json').read_bytes())
    def snapshot(self,tx):return {str(f.relative_to(self.h.f.temp)):a.sha(f.read_bytes()) for k in ['source','authoring','intake'] for f in (self.roots[k]/tx).rglob('*') if f.is_file()}
    def test_01_all_kinds_independent_exact_oracle_bank_discovery_detail_original(self):
        for kind in ['file','url','note']:
            out=self.prepare(kind);d=self.doc(out);tx=out['transaction_id'];intent=json.loads((self.roots['authoring']/tx/'INTENT.json').read_bytes());self.assertEqual(len({tx,d['object_id'],d['revision_id']}),3);self.assertEqual(out['ref'],p.base.read.ref(d));self.assertEqual(d['revision_created_at'],intent['created_at']);self.assertEqual(d['title'],self.fields(kind)['title']);self.assertFalse(out['Bank_accepted']);self.assertEqual(self.h.h.h.count(),['file','url','note'].index(kind))
            if kind=='file':
                s=d['data']['storage'];self.assertEqual(s['byte_length'],len(self.raw));self.assertEqual(s['sha256'],a.sha(self.raw));self.assertEqual(s['media_type'],'application/octet-stream');self.assertEqual(s['original_filename'],self.original.name);self.assertEqual(d['provenance']['origin_kind'],'unknown');self.assertEqual((self.roots['source']/tx/'payload/original.bin').read_bytes(),self.raw)
            elif kind=='url':self.assertEqual(d['data']['storage']['uri'],self.fields(kind)['uri']);self.assertEqual(d['provenance']['source_locator'],self.fields(kind)['uri']);self.assertIn('без скачивания',p.display(out))
            else:self.assertEqual(d['data']['body'],self.fields(kind)['body']);self.assertEqual(d['data']['targets'],[]);self.assertEqual(d['data']['author'],{'kind':'unknown','identity':None,'model':None});self.assertEqual(d['provenance']['origin_kind'],'unknown')
            self.save(out);q=self.backend.dispatch('detail',{'ref':out['ref']});self.assertEqual(q['status'],'OK',q);self.assertEqual(q['data']['document'],d);page=self.backend.dispatch('list',self.h.q());self.assertIn(out['ref'],[x['ref'] for x in page['items']])
            if kind=='file':
                exported=self.backend.dispatch('export',{'ref':out['ref']});self.assertEqual(exported['status'],'OK',exported);self.assertEqual(Path(exported['data']['original']['path']).read_bytes(),self.raw)
    def test_02_explicit_authorship_and_formats_no_inference(self):
        for author,origin in [('user','user_authored'),('ai','ai_authored'),('unknown','unknown')]:
            out=self.prepare(author_kind=author,identity='Declared' if author!='unknown' else None,model='Declared model' if author=='ai' else None,content_format='markdown');d=self.doc(out);self.assertEqual(d['data']['author']['kind'],author);self.assertEqual(d['provenance']['origin_kind'],origin);self.assertEqual(d['data']['content_format'],'markdown');self.save(out)
    def test_03_input_boundaries_empty_utf8_no_truncation_no_allocation(self):
        for f in [self.fields(title=''),self.fields(body=''),self.fields(body='🙂'*262145),self.fields(title='🙂'*1025),self.fields('url',uri='javascript:alert(1)'),self.fields(extra=True),self.fields(author_kind='inferred'),self.fields(identity='x'*4097)]:
            out=self.w.prepare(f);self.assertEqual(out['status'],'REJECTED',out);self.assertIsNone(out['transaction_id']);self.assertEqual(self.w.listing()['items'],[])
        exact='x'*1048576;out=self.prepare(body=exact);self.assertEqual(self.doc(out)['data']['body'],exact);self.assertIn('body',out['preview']['truncated_fields']);self.save(out)
    def test_04_json_escaping_effective_document_budget_before_intent(self):
        w=self.workspace(_limits={'document_bytes':3000});out=w.prepare(self.fields(body='\x01'*600));self.assertEqual(out['status'],'REJECTED');self.assertEqual(out['code'],'AUTHORING_INPUT_LIMIT');self.assertIsNone(out['transaction_id']);self.assertEqual(w.listing()['items'],[])
    def test_05_sealed_reopen_original_removed_ids_time_profile_unchanged(self):
        out=self.prepare('file');before=self.snapshot(out['transaction_id']);self.original.unlink();reopened=self.workspace().inspect(out['transaction_id']);self.assertEqual(reopened,out);self.assertEqual(self.snapshot(out['transaction_id']),before);self.save(reopened);self.assertEqual(self.h.h.h.count(),1)
    def test_06_unsealed_partial_never_recopies_changed_original(self):
        def hook(n,v):
            if n=='capture_chunk':raise OSError('Owned interrupted capture')
        out=self.workspace(_hook=hook,_limits={'chunk_bytes':4}).prepare(self.fields('file'));tx=out['transaction_id'];self.assertEqual(out['status'],'INCOMPLETE');before=self.snapshot(tx);self.original.write_bytes(b'changed');self.assertEqual(self.w.inspect(tx,finish=True)['code'],'INPUT_NOT_SEALED');self.assertEqual(self.snapshot(tx),before);self.assertEqual(self.h.h.h.count(),0);new=self.prepare('file');self.assertNotEqual(new['transaction_id'],tx)
    def test_07_seal_boundary_finish_exact_no_overwrite(self):
        def hook(n,v):
            if n=='seal_published':raise OSError('Owned seal interruption')
        out=self.workspace(_hook=hook).prepare(self.fields());tx=out['transaction_id'];self.assertTrue(out['sealed_input_may_exist']);self.assertEqual(self.w.inspect(tx)['status'],'SEALED');done=self.w.inspect(tx,finish=True);self.assertEqual(done['status'],'PREPARED',done);before=self.snapshot(tx);self.assertEqual(self.w.inspect(tx,finish=True),done);self.assertEqual(self.snapshot(tx),before);self.save(done)
    def test_08_actual_child_process_exit_at_every_preparation_checkpoint(self):
        phases=['intent_published_pending','intent_published','source_created','capture_chunk','original_flushed','document_flushed','draft_flushed','seal_published_pending','seal_published','draft_published']
        for phase in phases:
            checkpoint=self.h.f.temp/('child-checkpoint-'+phase+'.json');code="import pathlib,sys,json,os;sys.path.insert(0,sys.argv[1]);import authoring as a;roots=json.loads(sys.argv[2]);phase=sys.argv[3];checkpoint=pathlib.Path(sys.argv[4]);fields=json.loads(sys.argv[5]);\ndef hook(n,v):\n if n==phase:\n  s=str(v);p=pathlib.Path(s);tx=s if a.reader.UUID.fullmatch(s) else next(x.name for x in [p,*p.parents] if a.reader.UUID.fullmatch(x.name));checkpoint.write_bytes(json.dumps({'transaction_id':tx,'phase':n}).encode());os._exit(73)\nw=a.Workspace(roots,_portable_fixture=os.name!='nt',_hook=hook,_limits={'chunk_bytes':4});print(w.prepare(fields));"
            run=subprocess.run([sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent),json.dumps({k:str(v) for k,v in self.roots.items()}),phase,str(checkpoint),json.dumps(self.fields('file'))],capture_output=True,timeout=20);self.assertEqual(run.returncode,73,run.stdout+run.stderr);tx=json.loads(checkpoint.read_bytes())['transaction_id'];end=time.monotonic()+3
            while True:
                inspected=self.w.inspect(tx)
                if inspected['status']!='RETRYABLE_BUSY' or time.monotonic()>end:break
                time.sleep(.01)
            expected='SEALED' if phase=='seal_published' else 'PREPARED' if phase=='draft_published' else 'INCOMPLETE';self.assertEqual(inspected['status'],expected,(phase,inspected));before=self.snapshot(tx)
            if expected=='SEALED':self.assertEqual(self.w.inspect(tx,finish=True)['status'],'PREPARED')
            elif expected=='INCOMPLETE':self.assertEqual(self.w.inspect(tx,finish=True)['status'],'INCOMPLETE');self.assertEqual(self.snapshot(tx),before)
            self.assertEqual(self.h.h.h.count(),0)
    def test_09_cancel_before_intent_during_capture_after_seal(self):
        self.assertEqual(self.w.prepare(self.fields(),cancel=lambda:True)['status'],'CANCELLED');cancel=threading.Event()
        def hook(n,v):
            if n=='capture_chunk':cancel.set()
        out=self.workspace(_hook=hook,_limits={'chunk_bytes':4}).prepare(self.fields('file'),cancel=cancel.is_set);self.assertEqual(out['status'],'INCOMPLETE');self.assertEqual(self.w.inspect(out['transaction_id'])['code'],'INPUT_NOT_SEALED');cancel.clear()
        def sealed(n,v):
            if n=='seal_published':cancel.set()
        out=self.workspace(_hook=sealed).prepare(self.fields(),cancel=cancel.is_set);self.assertEqual(out['status'],'PREPARED',out)
    def test_10_quotas_scan_page_output_time_work_no_gc(self):
        out=self.prepare();before=self.snapshot(out['transaction_id'])
        for limit in [{'intents':1},{'workspace_bytes_including_managed_source':1},{'workspace_scan_entries':1},{'capture_elapsed_ms':0},{'work_bytes':0}]:
            rejected=self.workspace(_limits=limit).prepare(self.fields());self.assertIsNone(rejected['transaction_id'],rejected);self.assertIn(rejected['status'],['REJECTED','CANCELLED']);self.assertEqual(self.snapshot(out['transaction_id']),before)
        self.prepare('url');w=self.workspace(_limits={'page_items':1});first=w.listing();self.assertEqual(len(first['items']),1);self.assertTrue(first['has_more']);second=w.listing(first['next_after']);self.assertEqual(len(second['items']),1);self.assertFalse(second['has_more']);self.assertNotEqual(first['items'][0]['transaction_id'],second['items'][0]['transaction_id']);self.assertEqual(self.workspace(_limits={'per_request_output_bytes':1}).listing()['code'],'AUTHORING_RESULT_LIMIT')
    def test_11_corrupt_intent_seal_payload_draft_extra_entry_rejected(self):
        for path in ['authoring/INTENT.json','authoring/SEAL.json','source/DRAFT.json','source/docs/object.json','source/payload/original.bin','source/extra.bin']:
            out=self.prepare('file');role,relative=path.split('/',1);f=self.roots[role]/out['transaction_id']/relative
            if f.exists():f.write_bytes(f.read_bytes()+b' ')
            else:f.write_bytes(b'foreign')
            self.assertNotEqual(self.w.inspect(out['transaction_id'])['status'],'PREPARED',path);self.assertNotIn(self.execute('publish',out)['status'],['PUBLISHED','ALREADY_PUBLISHED']);self.assertEqual(self.h.h.h.count(),0)
    def test_12_source_missing_root_overlap_link_and_file_size_refusals(self):
        for source in [self.h.f.temp/'absent',self.roots['source']/'owned.bin',Path('relative')]:
            if source.is_absolute() and source.parent==self.roots['source']:source.write_bytes(self.raw)
            out=self.w.prepare(self.fields('file',path=str(source)));self.assertIsNone(out['transaction_id']);self.assertEqual(out['status'],'REJECTED',out)
        link=self.h.f.temp/'hardlink';os.link(self.original,link)
        try:self.assertEqual(self.w.prepare(self.fields('file'))['status'],'REJECTED')
        finally:link.unlink()
        with self.original.open('r+b') as f:f.truncate(64*1024*1024+1)
        out=self.w.prepare(self.fields('file'));self.assertEqual(out['code'],'AUTHORING_INPUT_LIMIT');self.assertIsNone(out['transaction_id'])
    def test_13_portable_source_change_detected_and_no_source_mutation(self):
        if os.name=='nt':
            with self.original.open('r+b') as f:
                out=self.w.prepare(self.fields('file'));self.assertEqual(out['status'],'RETRYABLE_BUSY');self.assertEqual(out['code'],'AUTHORING_BUSY');self.assertIsNone(out['transaction_id'])
        else:
            def hook(n,v):
                if n=='capture_chunk':self.original.write_bytes(b'changed')
            out=self.workspace(_hook=hook,_limits={'chunk_bytes':4}).prepare(self.fields('file'));self.assertEqual(out['status'],'INCOMPLETE');self.assertFalse((self.roots['authoring']/out['transaction_id']/'SEAL.json').exists())
    def test_14_real_workspace_lock_busy_then_released(self):
        with a.io.WorkspaceLock(self.roots['authoring']/'LOCK'):
            out=self.w.prepare(self.fields());self.assertEqual(out['status'],'RETRYABLE_BUSY',out);self.assertIsNone(out['transaction_id']);self.assertEqual(self.backend.dispatch('save',{'transaction_id':str(uuid.uuid4())})['status'],'RETRYABLE_BUSY')
        self.prepare()
    def test_15_publication_partial_vs_ready_pending_same_ids(self):
        for stop in ['copy_chunk','before_move','after_move']:
            previous_count=self.h.h.h.count();out=self.prepare();tx=out['transaction_id']
            def hook(n,v):
                if n==stop:raise OSError('Owned publication interruption')
            kw=copy.copy(self.backend.base.pkw);kw['_hook']=hook;b=self.make_backend(_publisher_kwargs=kw);first=b.dispatch('publish',{'transaction_id':tx});self.assertNotEqual(first['status'],'PUBLISHED');self.assertEqual(self.h.h.h.count(),previous_count);again=self.execute('resume',out)
            if stop=='copy_chunk':self.assertNotIn(again['status'],['PUBLISHED','ALREADY_PUBLISHED']);self.assertEqual(again['code'],'PENDING_NOT_COMPLETE')
            else:self.assertIn(again['status'],['PUBLISHED','ALREADY_PUBLISHED'],again);self.save(out)
    def test_16_actual_unknown_receipt_exact_replay_even_after_journal_damage(self):
        out=self.prepare();tx=out['transaction_id'];self.execute('publish',out)
        def hook(n,v):
            if n=='after_import':raise OSError('Owned output loss')
        kw=copy.copy(self.backend.base.ckw);kw['_hook']=hook;b=self.make_backend(_controller_kwargs=kw);lost=b.dispatch('save',{'transaction_id':tx});self.assertEqual(lost['status'],'UNKNOWN',lost);self.assertEqual(self.h.h.h.count(),1);(self.roots['authoring']/tx/'SEAL.json').write_bytes(b'broken');self.assertEqual(self.w.inspect(tx)['status'],'INCOMPLETE');r=self.execute('receipt',out,expected_manifest_sha256=out['manifest_sha256']);self.assertEqual(r['status'],'OK',r);self.assertEqual(r['data']['receipt']['transaction_id'],tx);self.assertEqual(self.execute('save',out)['status'],'REPLAY');self.assertEqual(self.h.h.h.count(),1)
    def test_17_retained_limit_does_not_reject_accepted_retry(self):
        out=self.prepare();self.save(out)
        def limited(root,**kw):return (old.ct.PortableStore if os.name!='nt' else a.im.Store)(root,_work_limits={'retained_bytes':1},**kw)
        kw=copy.copy(self.backend.base.ckw);kw['_store_factory']=limited;b=self.make_backend(_controller_kwargs=kw);r=b.dispatch('save',{'transaction_id':out['transaction_id']});self.assertEqual(r['status'],'IO_ERROR',r);self.assertEqual(r['code'],'RETAINED_WORK_LIMIT');self.assertIsNone(r['receipt']);self.assertEqual(self.execute('receipt',out)['status'],'OK');self.assertEqual(self.execute('save',out)['status'],'REPLAY')
    def test_18_context_isolation_epoch_mismatch_and_busy_close(self):
        one=self.prepare();two=self.prepare('url');m=p.Model();m.select_transaction(one['transaction_id']);m.begin('publish',{'transaction_id':one['transaction_id']},'Bank');self.assertFalse(m.select_transaction(two['transaction_id']));m.finish(self.execute('publish',one));m.begin('save',{'transaction_id':one['transaction_id']},'Bank');m.finish(self.execute('save',one));self.assertEqual(m.save['status'],'ACCEPTED');m.select_transaction(two['transaction_id']);self.assertIsNone(m.save);self.assertIsNone(m.publication);self.assertIsNone(m.last_receipt);self.assertIsNone(m.preparation);self.assertEqual(m.outcomes[one['transaction_id']]['save']['status'],'ACCEPTED');m.begin('save',{'transaction_id':two['transaction_id']},'Bank');m.finish({'status':'ACCEPTED','transaction_id':one['transaction_id']});self.assertIsNone(m.save);self.assertEqual(m.result['code'],'TRANSACTION_CONTEXT_MISMATCH');m.begin('receipt',{'transaction_id':two['transaction_id']},'Bank');m.generation+=1;m.finish({'status':'ERROR'});self.assertEqual(m.result['code'],'TRANSACTION_CONTEXT_MISMATCH');m.begin('save',{'transaction_id':two['transaction_id']},'Bank');m.close_request();self.assertFalse(m.closed);m.finish({'status':'UNKNOWN','transaction_id':two['transaction_id']});self.assertTrue(m.closed);self.assertEqual(m.save['status'],'UNKNOWN')
    def test_19_search_title_body_uri_rebuild_no_network(self):
        with patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
            for kind in ['note','url','file']:self.save(self.prepare(kind))
            self.assertEqual(self.backend.dispatch('rebuild',{})['status'],'BUILT')
            for field,query in [('title','Algorithm'),('body','theory'),('uri','example.invalid')]:
                r=self.backend.dispatch('search',{'query':query,'object_types':p.base.TYPES,'fields':[field],'revisions_mode':'current'});self.assertEqual(r['status'],'OK',r);self.assertGreater(r['data']['total_matches'],0)
    def test_20_configuration_profile_unsupported_and_cli_no_echo(self):
        roots={**self.roots,'authoring':self.roots['source']};out=a.Workspace(roots,_portable_fixture=os.name!='nt').prepare(self.fields());self.assertEqual(out['code'],'ROOT_OVERLAP');self.assertEqual(len(self.backend.base.roots),6)
        for limit in [{'policy_version':'future/2'},{'chunk_bytes':True},{'chunk_bytes':0}]:
            with self.assertRaises(a.Problem):self.workspace(_limits=limit)
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(authoring_ui.__file__)),'--alien','DO_NOT_ECHO'],capture_output=True,timeout=10);self.assertEqual(run.returncode,2);self.assertNotIn(b'DO_NOT_ECHO',run.stdout+run.stderr)
    def test_21_exact_64MiB_streamed_capture_hash_private_output(self):
        import hashlib
        block=b'owned boundary data\x00'*50000;remaining=64*1024*1024;digest=hashlib.sha256()
        with self.original.open('wb') as f:
            while remaining:
                chunk=block[:min(remaining,len(block))];f.write(chunk);digest.update(chunk);remaining-=len(chunk)
        out=self.prepare('file');storage=self.doc(out)['data']['storage'];self.assertEqual(storage['byte_length'],64*1024*1024);self.assertEqual(storage['sha256'],digest.hexdigest());copied=self.roots['source']/out['transaction_id']/'payload/original.bin'
        with a.io.File(copied) as f:
            if os.name=='nt':a.io.n.verify_private_acl(f.handle)
            else:self.assertEqual(copied.stat().st_mode&0o777,0o600)
        self.assertEqual(self.w.inspect(out['transaction_id'])['status'],'PREPARED');self.assertEqual(self.execute('publish',out)['status'],'PUBLISHED')
    def test_22_id_collision_never_replaces_existing_material(self):
        out=self.prepare();before=self.snapshot(out['transaction_id']);ids=[uuid.UUID(out['transaction_id']),uuid.UUID(out['ref']['object_id']),uuid.UUID(out['ref']['revision_id'])]
        with patch.object(a.uuid,'uuid4',side_effect=ids):collision=self.w.prepare(self.fields(body='Different content'))
        self.assertEqual(collision['code'],'INTENT_COLLISION');self.assertIsNone(collision['transaction_id']);self.assertEqual(self.snapshot(out['transaction_id']),before)
    def test_23_usage_never_stats_exclusively_held_empty_lock(self):
        real_scan=os.scandir
        class HeldLock:
            name='LOCK'
            def stat(self,*args,**kw):raise PermissionError(13,'Owned exclusive lock stat refusal')
            def is_symlink(self):raise AssertionError('Do not inspect held lock')
            def is_dir(self,*args,**kw):raise AssertionError('Do not inspect held lock')
        class Scan:
            def __init__(self,path):self.it=real_scan(path);self.path=Path(path)
            def __enter__(self):return (HeldLock() if self.path==self.roots_authoring and e.name=='LOCK' else e for e in self.it)
            def __exit__(self,*args):self.it.close()
        Scan.roots_authoring=self.roots['authoring']
        with patch.object(a.os,'scandir',side_effect=Scan):
            out=self.w.prepare(self.fields());self.assertEqual(out['status'],'PREPARED',out);self.assertEqual(self.w.listing()['status'],'OK')
        (self.roots['authoring']/'LOCK').write_bytes(b'not empty')
        self.assertEqual(self.w.prepare(self.fields())['status'],'REJECTED')
    def test_24_cached_zero_links_quota_uses_actual_private_file_handle(self):
        from types import SimpleNamespace
        one=self.prepare();real_scan=os.scandir
        class Entry:
            def __init__(self,e):self.e=e
            def __getattr__(self,key):return getattr(self.e,key)
            def stat(self,*args,**kw):
                s=self.e.stat(*args,**kw);return SimpleNamespace(st_nlink=0,st_size=s.st_size,st_file_attributes=getattr(s,'st_file_attributes',0))
        class Scan:
            def __init__(self,path):self.it=real_scan(path)
            def __enter__(self):return (Entry(e) for e in self.it)
            def __exit__(self,*args):self.it.close()
        with patch.object(a.os,'scandir',side_effect=Scan):
            self.assertEqual(self.w.listing()['status'],'OK');two=self.prepare('url');self.assertNotEqual(one['transaction_id'],two['transaction_id'])
            alias=self.h.f.temp/'owned-managed-hardlink';os.link(self.roots['source']/one['transaction_id']/'docs/object.json',alias)
            try:self.assertNotEqual(self.w.listing()['status'],'OK')
            finally:alias.unlink()

class NativeUI(Tests):
    def setUp(self):
        super().setUp();import tkinter as tk
        self.root=tk.Tk()
        try:self.window=authoring_ui.Window(self.root,self.backend);self.root.update();self.assertTrue(self.root.winfo_ismapped());self.assertEqual(str(self.window.txentry.cget('state')),'readonly')
        except BaseException:self.root.destroy();super().tearDown();raise
    def tearDown(self):
        if self.window.bridge.thread is not None:
            self.window.bridge.thread.join(65);self.assertFalse(self.window.bridge.thread.is_alive());self.window.bridge.poll()
        try:self.root.destroy()
        except Exception:pass
        super().tearDown()
    def pump(self,predicate=None,timeout=65):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            self.root.update()
            if predicate() if predicate else not self.window.model.busy:return
            time.sleep(.005)
        self.fail('Owned GUI bounded pump timeout')
    def button_event(self,b,wait=True):
        self.root.update();self.assertFalse(b.instate(['disabled']));b.event_generate('<Enter>');b.event_generate('<ButtonPress-1>',x=10,y=10);b.event_generate('<ButtonRelease-1>',x=10,y=10);self.root.update()
        if wait:self.pump()
    def click(self,key,wait=True):self.button_event(self.window.buttons[key],wait)
    def create(self,kind='note',**kw):
        self.click('new');w=self.window;w.kind.set(kind);w.kind_combo.event_generate('<<ComboboxSelected>>');self.root.update();fields=self.fields(kind,**kw);w.title.set(fields['title'])
        if kind=='file':
            from tkinter import filedialog
            with patch.object(filedialog,'askopenfilename',return_value=str(self.original)):w.choose_file()
            self.assertEqual(w.path.get(),str(self.original))
        elif kind=='url':w.uri.set(fields['uri'])
        else:w.body.insert('1.0',fields['body'])
        self.button_event(w.prepare_button);self.assertEqual(w.model.preparation['status'],'PREPARED',w.model.result);return copy.deepcopy(w.model.preparation)
    def pick_intent(self,tx):
        self.click('author_list');i=next(i for i,x in enumerate(self.window.model.intents) if x['transaction_id']==tx);self.window.intent_combo.current(i);self.window.intent_combo.event_generate('<<ComboboxSelected>>');self.root.update();self.pump();self.assertEqual(self.window.tx.get(),tx)
    def shot(self,label,form=False):
        target=self.window.form if form else self.root;target.update();png,info=window_capture.capture(target);folder=PROOF_ROOT/'NATIVE_SCREENSHOTS'/RUN_TOKEN;folder.mkdir(parents=True,exist_ok=True);name=self._testMethodName+'-'+label+'.png';(folder/name).write_bytes(png);CAPTURES.append({'test':self._testMethodName,'path':'NATIVE_SCREENSHOTS/'+RUN_TOKEN+'/'+name,'sha256':a.sha(png),**info})
    def ui_01_form_each_kind_to_actual_bank_detail_original_search(self):
        for kind in ['file','url','note']:
            out=self.create(kind);self.assertEqual(self.window.tx.get(),out['transaction_id']);self.assertEqual(str(self.window.txentry.cget('state')),'readonly');self.click('publish');self.assertEqual(self.window.model.publication['status'],'PUBLISHED');self.assertIsNone(self.window.model.save);self.click('save');self.pump(lambda:len(self.window.model.rows['Bank'])==['file','url','note'].index(kind)+1);self.assertEqual(self.window.model.save['status'],'ACCEPTED');self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],out['transaction_id']);self.shot(kind)
            i=next(i for i,x in enumerate(self.window.model.rows['Bank']) if x['ref']==out['ref']);tree=self.window.trees['Bank'];tree.selection_set(str(i));tree.event_generate('<<TreeviewSelect>>');self.root.update();self.click('detail');self.assertEqual(self.window.model.result['data']['document'],self.doc(out))
            if kind=='file':self.click('export');self.assertEqual(Path(self.window.model.result['data']['original']['path']).read_bytes(),self.raw)
        self.click('rebuild');self.window.search_text.set('theory');self.click('search');self.assertEqual(self.window.model.result['status'],'OK');self.assertGreater(len(self.window.model.rows['Search']),0);self.shot('search')
    def ui_02_A_B_A_panels_no_acceptance_leak_busy_selection(self):
        one=self.create();self.click('publish');self.click('save');self.click('receipt');two=self.create('url');self.assertIsNone(self.window.model.publication);self.assertIsNone(self.window.model.save);self.assertIsNone(self.window.model.last_receipt);self.assertNotIn('ACCEPTED',self.window.savestatus.get());self.pick_intent(one['transaction_id']);self.assertIsNone(self.window.model.save);self.assertNotIn('ACCEPTED',self.window.savestatus.get());self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],one['transaction_id']);self.pick_intent(two['transaction_id']);self.assertIsNone(self.window.model.last_receipt);self.assertIsNone(self.window.model.publication);self.assertNotIn(one['transaction_id'],self.window.savestatus.get());self.shot('second-isolated')
    def ui_03_chooser_cancel_limit_immutable_fields_no_allocation(self):
        from tkinter import filedialog
        self.click('new');w=self.window;w.kind.set('file');w.kind_combo.event_generate('<<ComboboxSelected>>');self.root.update()
        with patch.object(filedialog,'askopenfilename',return_value=''):w.choose_file()
        self.assertEqual(w.path.get(),'');self.assertEqual(self.w.listing()['items'],[]);w.kind.set('note');w.kind_combo.event_generate('<<ComboboxSelected>>');self.root.update();w.title.set('Too large');w.body.insert('1.0','🙂'*262145);self.button_event(w.prepare_button);self.assertIn('AUTHORING_INPUT_LIMIT',w.form_status.get());self.assertFalse(w.model.busy);self.assertEqual(self.w.listing()['items'],[]);self.shot('limit',form=True)
    def ui_04_cancel_capture_then_explicit_incomplete_and_sealed_recovery(self):
        cancel_entered=threading.Event();release=threading.Event()
        def hook(n,v):
            if n=='capture_chunk':cancel_entered.set();release.wait(3)
        self.window.bridge.backend=self.make_backend(_hook=hook,_limits={'chunk_bytes':4});self.click('new');w=self.window;w.kind.set('file');w.kind_combo.event_generate('<<ComboboxSelected>>');w.title.set('Cancelled');w.path.set(str(self.original));self.button_event(w.prepare_button,wait=False);self.assertTrue(cancel_entered.wait(2));self.assertFalse(w.cancel_button.instate(['disabled']));self.button_event(w.cancel_button,wait=False);release.set();self.pump();tx=w.model.transaction_id;self.assertEqual(w.model.preparation['status'],'INCOMPLETE');w.close_form();self.window.bridge.backend=self.backend;self.pick_intent(tx);self.assertEqual(w.model.preparation['code'],'INPUT_NOT_SEALED');self.click('author_finish');self.assertEqual(w.model.preparation['status'],'INCOMPLETE');self.shot('incomplete')
        def sealed(n,v):
            if n=='seal_published':raise OSError('Owned sealed interruption')
        out=self.workspace(_hook=sealed).prepare(self.fields());self.pick_intent(out['transaction_id']);self.assertEqual(w.model.preparation['status'],'SEALED');self.click('author_finish');self.assertEqual(w.model.preparation['status'],'PREPARED');self.click('publish');self.click('save');self.assertEqual(w.model.save['status'],'ACCEPTED');self.shot('sealed-recovered')
    def ui_05_actual_unknown_receipt_replay_and_retained_limit(self):
        out=self.create();self.click('publish')
        def lost(n,v):
            if n=='after_import':raise OSError('Owned postcommit loss')
        self.window.bridge.backend=self.make_backend(_controller_kwargs={'_hook':lost});self.click('save');self.assertEqual(self.window.model.save['status'],'UNKNOWN');self.assertIn('Исход неизвестен',self.window.details.get('1.0','end'));self.shot('unknown');self.window.bridge.backend=self.backend;self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],out['transaction_id']);self.click('save');self.assertEqual(self.window.model.save['status'],'REPLAY');self.assertEqual(self.h.h.h.count(),1)
        def limited(root,**kw):return a.im.Store(root,_work_limits={'retained_bytes':1},**kw)
        self.window.bridge.backend=self.make_backend(_controller_kwargs={'_store_factory':limited});self.click('save');self.assertEqual(self.window.model.save['status'],'IO_ERROR');self.assertEqual(self.window.model.save['code'],'RETAINED_WORK_LIMIT');self.assertIsNone(self.window.model.save['receipt']);self.shot('retained-limit');self.window.bridge.backend=self.backend;self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],out['transaction_id'])
    def ui_06_heartbeat_close_waits_final_outcome_reopen_without_original(self):
        out=self.create('file');self.original.unlink();old_window=self.window;self.root.destroy();self.assertIsNone(old_window.poll_id);import tkinter as tk
        self.root=tk.Tk();self.window=authoring_ui.Window(self.root,self.backend);self.pick_intent(out['transaction_id']);self.assertEqual(self.window.model.preparation['status'],'PREPARED');self.click('publish');entered=threading.Event();release=threading.Event();dispatch=self.backend.dispatch
        def delayed(action,args):entered.set();release.wait(3);return dispatch(action,args)
        self.backend.dispatch=delayed;self.click('save',wait=False);self.assertTrue(entered.wait(2));self.assertFalse(self.window.submit('author_list',{}));self.assertEqual(str(self.window.intent_combo.cget('state')),'disabled');ticks=[];self.root.after(10,lambda:ticks.append('alive'));self.pump(lambda:bool(ticks),timeout=2);self.window.close();self.assertTrue(self.window.model.closing);self.assertFalse(self.window.model.closed);self.shot('closing');release.set();self.pump(lambda:self.window.model.closed);self.assertEqual(self.window.model.save['status'],'ACCEPTED');self.assertEqual(self.h.h.h.count(),1)
    def ui_07_native_cli_default_seven_root_launch_refresh_close(self):
        code="import sys,json;sys.path.insert(0,sys.argv[1]);import authoring_ui as u;original=u.Window\nclass Probe(original):\n def __init__(self,root,backend):\n  super().__init__(root,backend);self.ticks=0;root.after(50,self.check)\n def check(self):\n  self.ticks+=1\n  if self.model.result is not None and not self.model.busy:\n   print(json.dumps({'mapped':bool(self.root.winfo_ismapped()),'status':self.model.result['status'],'roots':len(self.bridge.backend.workspace.roots)}),flush=True);self.close();return\n  if self.ticks>200:self.close();return\n  self.root.after(30,self.check)\nu.Window=Probe;sys.exit(u.main(sys.argv[2:]))"
        args=[sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent)]
        for role,path in self.roots.items():args.extend(['--'+role+'-root',str(path)])
        run=subprocess.run(args,capture_output=True,timeout=20);self.assertEqual(run.returncode,0,run.stdout+run.stderr);out=json.loads(run.stdout);self.assertTrue(out['mapped']);self.assertEqual(out['status'],'OK');self.assertEqual(out['roots'],7)

CAPTURES=[]
RUN_TOKEN=uuid.uuid4().hex
PROOF_ROOT=Path(__file__).parent/'implementation_20261007'
class Evidence(old.ct.Evidence):pass

def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    if os.name=='nt':suite.addTests(unittest.TestSuite(NativeUI(name) for name in dir(NativeUI) if name.startswith('ui_')))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(suite);sources=['authoring.py','authoring_io.py','authoring_presenter.py','authoring_ui.py','test_authoring.py','LIMITS.json'];report={'record_kind':'owned_creation_only_authoring_evidence','at':a.im.now(),'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'cases':result.cases,'source_sha256':{n:a.sha((Path(__file__).parent/n).read_bytes()) for n in sources},'native_window_captures':CAPTURES,'limitations':['Owned synthetic existing roots only; no real Bank/import/install or full R0/R1/MVP/release acceptance','Local IO only explicit POSIX fixture; actual Windows handles/default controller/mapped Tk required','Generated GUI events and owned client captures are not human/a11y acceptance','Original4 native reader symlink fixtures remain BLOCKED; no OS privilege changes','No providers/network/Watch/research or existing-object/Entity/Collection editor','OS process exit checkpoints, not hardware/power-loss proof']};PROOF_ROOT.mkdir(exist_ok=True);name=('NATIVE' if os.name=='nt' else 'LOCAL')+'_AUTHORING_'+RUN_TOKEN+'.json';raw=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode();(PROOF_ROOT/name).write_bytes(raw);print('FINAL',json.dumps({'success':result.wasSuccessful(),'tests_run':result.testsRun,'bad':result.bad,'captures':len(CAPTURES),'report':name,'sha256':a.sha(raw)}),flush=True);return not result.wasSuccessful()
if __name__=='__main__':sys.exit(main())
