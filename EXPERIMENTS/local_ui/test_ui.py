"""Headless tests + Windows-only real mapped Tk/event/window capture integration."""
from pathlib import Path
from contextlib import closing
import copy,errno,json,os,platform,shutil,socket,sqlite3,subprocess,sys,threading,time,unittest,uuid
from unittest.mock import patch
import presenter as app
import desktop,window_capture
sys.path.insert(0,str(app.commands.ROOT/'EXPERIMENTS/package_producer'))
import test_producer as pt
ct=pt.ct;fx=pt.fx
class Tests(unittest.TestCase):
    def setUp(self):
        self.h=pt.Tests('test_02_exact_bytes_manifest_ids_and_independent_hash_oracle');self.h.setUp();self.f=self.h.f;self.roots={'bank':self.f.root,'intake':self.f.intake,'stage':self.f.stage,'cache':self.h.h.cache,'output':self.h.h.outputs,'source':self.h.source};self.backend=self.make_backend()
    def tearDown(self):self.h.tearDown()
    def make_backend(self,**kw):
        if os.name!='nt':kw.setdefault('_controller_kwargs',{'_transport':ct.portable_read,'_store_factory':ct.PortableStore});kw.setdefault('_publisher_kwargs',{'_portable_fixture':True})
        return app.Backend(self.roots,**kw)
    def save(self,b=None):
        b,p,d=self.h.draft(b);tx=b.m['transaction_id'];r=self.backend.dispatch('publish',{'transaction_id':tx});self.assertEqual(r['status'],'PUBLISHED',r);r=self.backend.dispatch('save',{'transaction_id':tx});self.assertEqual(r['status'],'ACCEPTED',r);return b,r
    def q(self,**kw):return {'protocol':app.discovery.PROTOCOL,'object_types':app.TYPES,'snapshot_sequence':None,'after_object_id':None,'limit':10,**kw}
    def listing(self,**kw):return self.backend.dispatch('list',self.q(**kw))
    def ref(self,b=None,kind='Annotation'):return app.read.ref((b or self.f.bundle).doc(kind)[1])
    def test_01_empty_existing_bank_discovery_zero(self):
        r=self.listing();self.assertEqual(r['status'],'OK',r);self.assertEqual(r['snapshot_sequence'],0);self.assertEqual(r['items'],[]);self.assertFalse(r['has_more'])
    def test_02_list_matches_independent_docs_pins_sorted(self):
        b,r=self.save();out=self.listing();expected=sorted([{'ref':app.read.ref(json.loads(b.files[o['document_path']])),'title':json.loads(b.files[o['document_path']])['title']} for o in b.m['operations']],key=lambda d:d['ref']['object_id']);self.assertEqual([{k:i[k] for k in ['ref','title']} for i in out['items']],expected);self.assertEqual(out['snapshot_sequence'],1);self.assertEqual(self.h.h.count(),1)
    def test_03_asof_keyset_pages_stable_across_new_objects_and_update(self):
        b,r=self.save();first=self.listing(limit=2);self.assertTrue(first['has_more']);self.save(fx.Bundle('continuation'));self.save(fx.Bundle.entity());second=self.listing(limit=2,snapshot_sequence=first['snapshot_sequence'],after_object_id=first['next_after_object_id']);expected=sorted([self.ref(b,k) for k in app.TYPES],key=lambda d:d['object_id']);self.assertEqual([i['ref'] for i in first['items']+second['items']],expected);self.assertFalse(second['has_more']);self.assertEqual(self.listing()['snapshot_sequence'],3)
    def test_04_collection_filter_and_unavailable_snapshot(self):
        b,r=self.save();out=self.listing(object_types=['Collection']);self.assertEqual([i['ref'] for i in out['items']],[self.ref(b,'Collection')]);self.assertEqual(self.listing(snapshot_sequence=2)['code'],'SNAPSHOT_NOT_AVAILABLE')
    def test_05_candidate_response_metadata_limits_no_partial_success(self):
        self.save()
        for limits in [{'candidate_seeks':0},{'list_response_bytes':1},{'stored_metadata_bytes_per_request':1},{'elapsed_ms':-1}]:
            r=app.discovery.Discovery(self.f.root,_limits=limits).execute(self.q());self.assertEqual(r['status'],'ERROR',r);self.assertEqual(r['code'],'LIMIT_EXCEEDED');self.assertEqual(r['items'],[])
    def test_06_sqlite_progress_budget_exceeds_no_partial(self):
        self.save()
        for i in range(3):self.save(fx.Bundle.entity())
        original=app.read.ReadSession.__enter__
        def expensive(session):
            original(session)
            try:session.c.execute('WITH RECURSIVE n(x) AS (VALUES(0) UNION ALL SELECT x+1 FROM n WHERE x<1000000) SELECT sum(x) FROM n').fetchone();return session
            except BaseException:session.c.close();session.c=None;raise
        with patch.object(app.read.ReadSession,'__enter__',expensive):r=app.discovery.Discovery(self.f.root,_limits={'sqlite_vm_steps':0}).execute(self.q())
        self.assertEqual(r['status'],'ERROR',r);self.assertEqual(r['code'],'LIMIT_EXCEEDED');self.assertEqual(r['items'],[])
    def test_07_closed_request_invalid_bool_types_before_store_io(self):
        d=app.discovery.Discovery(self.f.root)
        with patch.object(app.im,'Store',side_effect=AssertionError('No store')):
            for change in [{'limit':True},{'snapshot_sequence':False},{'extra':'SQL'},{'protocol':'bad'},{'object_types':[]},{'object_types':['Collection','Collection']},{'after_object_id':'../escape'},{'limit':21}]:self.assertEqual(d.execute(self.q(**change))['code'],'INVALID_REQUEST')
    def test_08_missing_bank_not_created(self):
        absent=self.f.temp/'absent';out=app.discovery.Discovery(absent).execute(self.q());self.assertEqual(out['status'],'ERROR');self.assertFalse(absent.exists())
    def test_09_unknown_db_catalog_rejected(self):
        with closing(sqlite3.connect(self.f.store.db,isolation_level=None)) as c:c.execute('CREATE TABLE alien(x)')
        self.assertEqual(self.listing()['status'],'ERROR')
    def test_10_db_hardlink_refused(self):
        os.link(self.f.store.db,self.f.temp/'alias');self.assertEqual(self.listing()['status'],'ERROR')
    def test_11_real_bank_lock_visible_error(self):
        c=sqlite3.connect(self.f.store.db,isolation_level=None);c.execute('BEGIN EXCLUSIVE')
        try:self.assertEqual(self.listing()['code'],'BANK_BUSY')
        finally:c.close()
    def test_12_corrupt_document_rejected_no_partial_rows(self):
        self.save();name=self.f.bundle.doc('Annotation')[0]['document_path']
        with closing(sqlite3.connect(self.f.store.db,isolation_level=None)) as c:
            sql=c.execute("SELECT sql FROM sqlite_schema WHERE name='files_no_update'").fetchone()[0];c.execute('DROP TRIGGER files_no_update');raw=c.execute('SELECT file_blob FROM files WHERE path=?',(name,)).fetchone()[0];c.execute('UPDATE files SET file_blob=? WHERE path=?',(raw[:-1]+b' ',name));c.execute(sql)
        r=self.listing();self.assertEqual(r['status'],'ERROR',r);self.assertEqual(r['items'],[])
    def test_13_backend_absolute_disjoint_existing_roots_only(self):
        original=self.backend.roots['source']
        for p in [self.f.intake,Path('relative'),self.f.temp/'not-created']:
            self.backend.roots['source']=p;self.assertEqual(self.listing()['status'],'ERROR');self.assertFalse((self.f.temp/'not-created').exists())
        self.backend.roots['source']=original
    def test_14_publish_save_receipt_replay_separate_states(self):
        b,p,d=self.h.draft();tx=b.m['transaction_id'];pub=self.backend.dispatch('publish',{'transaction_id':tx});self.assertFalse(pub['Bank_accepted']);self.assertEqual(self.h.h.count(),0);self.assertEqual(self.backend.dispatch('inspect',{'transaction_id':tx})['status'],'PUBLISHED');saved=self.backend.dispatch('save',{'transaction_id':tx});self.assertEqual(saved['status'],'ACCEPTED');receipt=self.backend.dispatch('receipt',{'transaction_id':tx,'expected_manifest_sha256':pub['manifest_sha256']});self.assertEqual(receipt['data']['receipt'],saved['receipt']);self.assertEqual(self.backend.dispatch('save',{'transaction_id':tx})['status'],'REPLAY');self.assertEqual(self.h.h.count(),1)
    def test_15_unknown_save_after_import_actual_receipt_recovery(self):
        b,p,d=self.h.draft();tx=b.m['transaction_id'];self.backend.dispatch('publish',{'transaction_id':tx})
        def hook(n,v):
            if n=='after_import':raise OSError('PRIVATE_DO_NOT_ECHO')
        base=copy.copy(self.backend.ckw);base['_hook']=hook;backend=self.make_backend(_controller_kwargs=base);out=backend.dispatch('save',{'transaction_id':tx});self.assertEqual(out['status'],'UNKNOWN',out);self.assertNotIn('PRIVATE',json.dumps(out));self.assertEqual(self.backend.dispatch('receipt',{'transaction_id':tx})['status'],'OK');self.assertEqual(self.backend.dispatch('save',{'transaction_id':tx})['status'],'REPLAY')
    def test_16_pinned_original_export_persists_after_worker_adapter_close(self):
        b,r=self.save();out=self.backend.dispatch('export',{'ref':self.ref(b,'Asset')});self.assertEqual(out['status'],'OK',out);artifact=out['data']['original'];path=Path(artifact['path']);self.assertTrue(path.exists());self.assertEqual(app.im.sha(path.read_bytes()),artifact['sha256']);self.assertEqual(path.read_bytes(),b.files[b.doc('Asset')[1]['data']['storage']['file_path']]);self.assertIn('после закрытия',app.render(out))
    def test_17_search_explicit_rebuild_stale_and_fields_modes(self):
        self.save();args={'query':'synthetic','object_types':app.TYPES,'fields':['title','body','content'],'revisions_mode':'current'};self.assertEqual(self.backend.dispatch('search',args)['code'],'INDEX_UNAVAILABLE');self.assertEqual(self.backend.dispatch('rebuild',{})['status'],'BUILT');r=self.backend.dispatch('search',args);self.assertEqual(r['status'],'OK',r);self.assertGreater(r['data']['total_matches'],0);self.save(fx.Bundle('continuation'));self.assertEqual(self.backend.dispatch('search',args)['code'],'INDEX_NOT_READY');self.backend.dispatch('rebuild',{});self.assertEqual(self.backend.dispatch('search',{**args,'revisions_mode':'all_revisions'})['status'],'OK');self.assertEqual(self.backend.dispatch('search',{**args,'fields':[]})['status'],'ERROR')
    def test_18_selected_old_pin_opens_original_after_update(self):
        b,r=self.save();old=self.ref(b);self.save(fx.Bundle('continuation'));out=self.backend.dispatch('detail',{'ref':old});self.assertEqual(out['data']['ref'],old);self.assertEqual(out['data']['document'],b.doc('Annotation')[1]);self.assertEqual(self.backend.dispatch('history',{'ref':old})['data']['revisions'][1]['ref'],old)
    def test_19_collection_members_order_and_availability(self):
        b,r=self.save();out=self.backend.dispatch('detail',{'ref':self.ref(b,'Collection')});self.assertEqual(out['data']['document']['data']['members'],b.doc('Collection')[1]['data']['members']);self.assertTrue(all(x['availability']=='available' for x in out['data']['member_statuses']))
    def test_20_model_busy_capture_and_pinned_selection(self):
        m=app.Model();ref=self.ref();m.rows['Bank']=[{'ref':ref}];self.assertTrue(m.select('Bank',0));args={'ref':copy.deepcopy(ref)};self.assertTrue(m.begin('detail',args,'Bank'));args['ref']['revision_id']=str(uuid.uuid4());self.assertFalse(m.begin('save',{},'Bank'));self.assertFalse(m.select('Bank',0));self.assertEqual(m.active[1]['ref'],ref);m.finish({'status':'ERROR','code':'BANK_BUSY'});self.assertEqual(m.selected,ref)
    def test_21_model_close_waits_retains_unknown_final_outcome(self):
        m=app.Model();m.begin('save',{'transaction_id':self.h.tx},'Bank');m.close_request();self.assertFalse(m.closed);self.assertFalse(m.begin('save',{},'Bank'));self.assertFalse(m.finish({'status':'UNKNOWN','code':'COMMAND_OUTCOME_UNKNOWN'}));self.assertTrue(m.closed);self.assertEqual(m.save['status'],'UNKNOWN')
    def test_22_receipt_hash_only_for_matching_transaction(self):
        m=app.Model();m.publication={'transaction_id':self.h.tx,'manifest_sha256':'a'*64};self.assertEqual(m.receipt_args(self.h.tx)['expected_manifest_sha256'],'a'*64);self.assertIsNone(m.receipt_args(str(uuid.uuid4()))['expected_manifest_sha256'])
    def test_23_safe_plain_display_injection_and_bounded_preview(self):
        b=self.f.bundle.clone().edit('Annotation',lambda d:d['data'].update(body='<script>PRIVATE_MARK</script>'+('🙂'*40000)));d=b.doc('Annotation')[1];r={'status':'OK','code':'OK','data':{'document':d,'accepted_at':'today'}};text=app.display(r);self.assertIn('<script>PRIVATE_MARK</script>',text);self.assertIn('сокращён',text);self.assertLess(len(text.encode()),66000);self.assertNotIn('local-bank-query',text)
    def test_24_worker_serial_no_gui_thread_execution_close_model(self):
        release=threading.Event();entered=threading.Event();names=[]
        class Slow:
            def dispatch(self,*a):names.append(threading.current_thread().name);entered.set();release.wait(3);return {'status':'OK','code':'OK'}
        bridge=app.Bridge(Slow());self.assertTrue(bridge.submit('list',{}));self.assertTrue(entered.wait(2));self.assertFalse(bridge.submit('save',{}));self.assertIsNone(bridge.poll());release.set();bridge.thread.join(3);self.assertEqual(bridge.poll()['status'],'OK');self.assertEqual(names,['bank-ui-operation'])
    def test_25_invalid_cli_bounded_no_argument_echo(self):
        r=subprocess.run([sys.executable,'-X','utf8',str(Path(desktop.__file__)),'--sql','PRIVATE_PAYLOAD'],capture_output=True,timeout=10);self.assertEqual(r.returncode,2);self.assertNotIn(b'PRIVATE_PAYLOAD',r.stdout+r.stderr);self.assertEqual(json.loads(r.stdout)['code'],'UI_UNAVAILABLE')
    def test_26_closed_discovery_result_success_and_error(self):
        d=app.discovery.Discovery(self.f.root)
        for q in [self.q(),self.q(limit=True)]:self.assertIsNone(next(d.result_validator.iter_errors(d.execute(q)),None))
    def test_27_no_network_init_or_read_mutation(self):
        self.save();before=app.im.sha(self.f.store.db.read_bytes())
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No network')),patch.object(app.im.Store,'initialize',side_effect=AssertionError('No initialize')):self.assertEqual(self.listing()['status'],'OK');self.assertEqual(self.backend.dispatch('detail',{'ref':self.ref()})['status'],'OK')
        self.assertEqual(app.im.sha(self.f.store.db.read_bytes()),before)
    def test_28_discovery_uses_index_seeks_not_blob_history_scan(self):
        self.save()
        with app.im.Store(self.f.root) as store:
            with closing(store._connect(False)) as c:
                plans=[c.execute('EXPLAIN QUERY PLAN '+sql,params).fetchall() for sql,params in [('SELECT object_id FROM revisions WHERE object_id>? ORDER BY object_id LIMIT 1',('',)),('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 1',(self.ref()['object_id'],1))]]
                for plan in plans:self.assertTrue(any('SEARCH revisions USING' in row[3] and 'revisions_object_history' in row[3] for row in plan),plans)
    def test_29_poll_timer_lifetime_cancel_only_owned_root_destroy(self):
        class Root:
            def __init__(self):self.timers={};self.count=0
            def after(self,ms,callback):self.count+=1;token='timer-'+str(self.count);self.timers[token]=(ms,callback);return token
            def after_cancel(self,token):self.timers.pop(token)
        class EmptyBridge:
            def poll(self):return None
        w=desktop.Window.__new__(desktop.Window);w.root=Root();w.model=app.Model();w.bridge=EmptyBridge();w.poll_id=None;w.poll();self.assertEqual(len(w.root.timers),1);w.refresh_id=w.root.after(0,w.refresh_after)
        class Event:pass
        child=Event();child.widget=object();w.destroyed(child);self.assertEqual(len(w.root.timers),2);owned=Event();owned.widget=w.root;w.destroyed(owned);self.assertIsNone(w.poll_id);self.assertIsNone(w.refresh_id);self.assertEqual(w.root.timers,{})
class NativeUI(Tests):
    # Load only explicitly named GUI methods below, not inherited headless tests twice.
    def setUp(self):
        super().setUp();import tkinter as tk
        self.root=tk.Tk();self.window=desktop.Window(self.root,self.backend);self.root.update();self.assertTrue(self.root.winfo_ismapped());self.saved_captures=[]
    def tearDown(self):
        if self.window.bridge.thread is not None:
            self.window.bridge.thread.join(65)
            self.assertFalse(self.window.bridge.thread.is_alive(),'Bounded worker must finish')
            self.window.bridge.poll()
        try:self.root.destroy()
        except Exception:pass
        super().tearDown()
    def pump(self,predicate=None,timeout=65):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            self.root.update()
            if (predicate() if predicate else not self.window.model.busy):return
            time.sleep(0.005)
        self.fail('Native UI bounded pump timeout')
    def click(self,key,wait=True):
        self.root.update();b=self.window.buttons[key];self.assertFalse(b.instate(['disabled']));b.event_generate('<Enter>');b.event_generate('<ButtonPress-1>',x=10,y=10);b.event_generate('<ButtonRelease-1>',x=10,y=10);self.root.update();self.assertTrue(any(x.get('action')==key for x in self.window.events),key)
        if wait:self.pump()
    def pick(self,tab,kind=None):
        self.window.set_tab(tab);rows=self.window.model.rows[tab];i=next((i for i,x in enumerate(rows) if x['ref']['object_type']==kind),0) if kind else 0;tree=self.window.trees[tab];tree.selection_set(str(i));tree.event_generate('<<TreeviewSelect>>');self.root.update();self.assertEqual(self.window.model.selected,rows[i]['ref']);return copy.deepcopy(rows[i]['ref'])
    def shot(self,label):
        self.root.update();self.assertLessEqual(self.window.footer.winfo_rooty()-self.root.winfo_rooty()+self.window.footer.winfo_height(),self.root.winfo_height(),'Footer must stay inside owned client');png,info=window_capture.capture(self.root);self.assertGreater(info['unique_pixel_bytes'],10);folder=CAPTURE_ROOT/RUN_TOKEN;folder.mkdir(parents=True,exist_ok=True);name=self._testMethodName+'-'+label+'.png';(folder/name).write_bytes(png);CAPTURES.append({'test':self._testMethodName,'path':'NATIVE_SCREENSHOTS/'+RUN_TOKEN+'/'+name,'sha256':app.im.sha(png),**info});self.saved_captures.append(name)
    def ui_01_mapped_empty_window_mouse_refresh_and_screenshot(self):
        self.click('refresh');self.assertEqual(self.window.model.result['status'],'OK');self.assertEqual(self.window.model.rows['Bank'],[]);self.shot('empty')
    def ui_02_actual_publish_save_refresh_receipt_widgets(self):
        b,p,d=self.h.draft();self.window.tx.set(b.m['transaction_id']);self.click('publish');self.assertEqual(self.window.model.publication['status'],'PUBLISHED');self.assertEqual(self.h.h.count(),0);self.click('save');self.pump(lambda:len(self.window.model.rows['Bank'])==4);self.assertEqual(self.window.model.save['status'],'ACCEPTED');self.assertIn('ACCEPTED',self.window.savestatus.get());self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],b.m['transaction_id']);self.shot('saved')
    def ui_03_collections_selection_members_plain_view(self):
        self.save();self.window.set_tab('Collections');self.click('refresh');self.assertEqual(len(self.window.model.rows['Collections']),1);ref=self.pick('Collections');self.click('detail');self.assertEqual(self.window.model.result['data']['ref'],ref);self.assertIn('Доступность членов',self.window.details.get('1.0','end'));self.shot('collection')
    def ui_04_history_old_pin_update_and_reopen_window(self):
        b,r=self.save();self.click('refresh');old=self.pick('Bank','Annotation');self.save(fx.Bundle('continuation'));self.click('detail');self.assertEqual(self.window.model.result['data']['ref'],old);self.click('history');self.assertEqual(len(self.window.model.rows['History']),2);tree=self.window.trees['History'];tree.selection_set('1');tree.event_generate('<<TreeviewSelect>>');self.root.update();self.click('detail');self.assertEqual(self.window.model.result['data']['ref'],old);self.shot('old-pinned');old_window=self.window;bgerrors=[];self.root.tk.createcommand('bgerror',lambda *a:bgerrors.append(a));self.root.destroy();self.assertIsNone(old_window.poll_id);import tkinter as tk
        self.root=tk.Tk();self.window=desktop.Window(self.root,self.backend);self.click('refresh');new=self.pick('Bank','Annotation');self.assertNotEqual(new['revision_id'],old['revision_id']);self.click('detail');self.assertEqual(self.window.model.result['data']['ref'],new);self.assertEqual(bgerrors,[],'No queued deleted poll callback after destroy/reopen')
    def ui_05_search_missing_rebuild_fields_modes_and_hit_open(self):
        self.save();self.window.search_text.set('synthetic');self.click('search');self.assertEqual(self.window.model.result['code'],'INDEX_UNAVAILABLE');self.click('rebuild');self.assertEqual(self.window.model.result['status'],'BUILT');self.click('search');self.assertGreater(len(self.window.model.rows['Search']),0);selected=self.pick('Search');self.click('detail');self.assertEqual(self.window.model.result['data']['ref'],selected);self.window.search_mode.set('all_revisions');self.click('search');self.assertEqual(self.window.model.result['status'],'OK');self.shot('search')
    def ui_06_original_export_and_unknown_receipt_status(self):
        self.save();self.click('refresh');self.pick('Bank','Asset');self.click('export');self.assertEqual(self.window.model.result['data']['availability'],'bytes');path=Path(self.window.model.result['data']['original']['path']);self.assertTrue(path.exists());self.assertIn(str(path),self.window.details.get('1.0','end'));self.window.tx.set(str(uuid.uuid4()));self.click('receipt');self.assertEqual(self.window.model.result['code'],'RECEIPT_NOT_FOUND');self.assertIn('не доказывает',self.window.details.get('1.0','end'));self.shot('recovery')
    def ui_07_busy_heartbeat_close_waits_actual_final_outcome(self):
        entered=threading.Event();release=threading.Event();backend=self.window.bridge.backend;dispatch=backend.dispatch
        def delayed(action,args):entered.set();release.wait(3);return dispatch(action,args)
        backend.dispatch=delayed;self.click('refresh',wait=False);self.assertTrue(entered.wait(2));self.assertTrue(self.window.buttons['save'].instate(['disabled']));self.assertFalse(self.window.submit('save',{'transaction_id':self.h.tx}));ticks=[];self.root.after(10,lambda:ticks.append('alive'));self.pump(lambda:bool(ticks),timeout=2);self.window.close();self.assertTrue(self.window.model.closing);self.assertFalse(self.window.model.closed);self.shot('closing');release.set();self.pump(lambda:self.window.model.closed);self.assertEqual(self.window.model.result['status'],'OK');self.assertTrue(self.window.model.closed)
    def ui_08_actual_unknown_save_recover_receipt_repeat_without_new_id(self):
        b,p,d=self.h.draft();tx=b.m['transaction_id'];self.window.tx.set(tx);self.click('publish')
        def hook(n,v):
            if n=='after_import':raise OSError('Owned UI output fault')
        self.window.bridge.backend=self.make_backend(_controller_kwargs={'_hook':hook});self.click('save');self.assertEqual(self.window.model.save['status'],'UNKNOWN');self.assertIn('Исход неизвестен',self.window.details.get('1.0','end'));self.shot('unknown');self.window.bridge.backend=self.backend;self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],tx);self.click('save');self.pump(lambda:len(self.window.model.rows['Bank'])==4);self.assertEqual(self.window.model.save['status'],'REPLAY');self.assertEqual(self.h.h.count(),1);self.shot('recovered')
    def ui_10_actual_retained_limit_retry_preserves_accepted_state(self):
        b,_=self.save();tx=b.m['transaction_id'];self.window.tx.set(tx)
        def limited(root,**kw):return app.im.Store(root,_work_limits={'retained_bytes':1},**kw)
        self.window.bridge.backend=self.make_backend(_controller_kwargs={'_store_factory':limited})
        self.click('save');self.assertEqual(self.window.model.save['status'],'IO_ERROR');self.assertEqual(self.window.model.save['code'],'RETAINED_WORK_LIMIT');self.assertIsNone(self.window.model.save['receipt']);self.assertIn('не означает',self.window.details.get('1.0','end'));self.assertEqual(self.window.tx.get(),tx);self.shot('retained-limit')
        self.window.bridge.backend=self.backend;self.click('receipt');self.assertEqual(self.window.model.last_receipt['transaction_id'],tx);self.click('save');self.assertEqual(self.window.model.save['status'],'REPLAY');self.assertEqual(self.h.h.count(),1);self.shot('retained-retry')
    def ui_09_owned_process_default_cli_parser_launch_refresh_close(self):
        code="""import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import desktop
original=desktop.Window
class ProbeWindow(original):
 def __init__(self,root,backend):
  super().__init__(root,backend);self.ticks=0;root.after(80,self.check)
 def check(self):
  self.ticks+=1
  if self.model.result is not None and not self.model.busy:
   print(json.dumps({'mapped':bool(self.root.winfo_ismapped()),'status':self.model.result['status'],'page_items':len(self.model.rows['Bank'])}),flush=True);self.close();return
  if self.ticks>250:print('CLI_PROBE_TIMEOUT',flush=True);self.close();return
  self.root.after(30,self.check)
desktop.Window=ProbeWindow
sys.exit(desktop.main(sys.argv[2:]))
"""
        args=[sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent)]
        for role,path in self.roots.items():args += ['--'+role+'-root',str(path)]
        r=subprocess.run(args,capture_output=True,timeout=20);self.assertEqual(r.returncode,0,r.stderr+r.stdout);data=json.loads(r.stdout);self.assertTrue(data['mapped']);self.assertEqual(data['status'],'OK');self.assertEqual(data['page_items'],0)
CAPTURE_ROOT=Path(__file__).parent/'NATIVE_SCREENSHOTS'
RUN_TOKEN=uuid.uuid4().hex
CAPTURES=[]
class Evidence(ct.Evidence):
    def addSuccess(self,t):super().addSuccess(t)
if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    if os.name=='nt':suite.addTests(unittest.TestSuite(NativeUI(name) for name in dir(NativeUI) if name.startswith('ui_')))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(suite);folder=Path(__file__).parent;at=app.im.now();name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';sources=['discovery.py','presenter.py','desktop.py','window_capture.py','test_ui.py','discovery.schema.json','discovery_result.schema.json','LIMITS.json'];report={'record_kind':'synthetic_R1_local_ui_evidence','at':at,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'headless_groups':29,'native_ui_groups':9 if os.name=='nt' else 0,'ui_adapter':'actual mapped Windows Tk/native handles/default controller' if os.name=='nt' else 'headless presenter/backend/SQLite only; no local GUI evidence','cases':result.cases,'source_sha256':{n:app.im.sha((folder/n).read_bytes()) for n in sources},'native_window_captures':CAPTURES,'limitations':['Prepared-draft synthetic existing roots only; no real Bank/new-intent authoring/install/release acceptance','Local tests are headless; nine additional native mapped Tk/event/window screenshot groups required for UI completion','Generated Tk mouse/selection events are not physical human/a11y/keyboard/usability evidence','Plain bounded text/metadata and private persistent verified exports; no active preview/network/shell open','One bounded worker; close waits for started operation, no background polling/automatic quarantine cleanup','Discovery keyset/as-of and seek/VM/bytes/time caps; no unlimited large-Bank guarantee','Actual privacy/root configuration/backup/restore/hardware/full R0/R1 remain open']}
    out=folder/name
    if out.exists():history=folder/'TEST_HISTORY';history.mkdir(exist_ok=True);shutil.copyfile(out,history/(name+'-'+uuid.uuid4().hex+'.json'))
    out.write_text(json.dumps(report,indent=2)+'\n');issuespath=folder/'ISSUES.json';issues=json.loads(issuespath.read_text());known={x['id']:x for x in issues['issues']}
    for c in report['cases']:
        iid='UI-TEST-'+c['id'];i=known.get(iid)
        if c['observed']=='FAIL':
            if i is None:i={'id':iid,'finding':'Integration assertion '+c['id'],'history':[]};issues['issues'].append(i);known[iid]=i
            i['status']='open';i['history'].append({'at':at,'status':'open','evidence':name,'detail':c['detail']})
        elif i and i['status']=='open':i['status']='resolved_native' if os.name=='nt' else 'resolved_local';i['history'].append({'at':at,'status':i['status'],'evidence':name,'note':'Rerun passed, original failure retained.'})
    issuespath.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':result.bad,'captures':len(CAPTURES),'report':str(out)}),flush=True);sys.exit(not result.wasSuccessful())
