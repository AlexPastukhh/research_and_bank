"""Counterexamples for silent observation, queued input and window shutdown."""
import copy,threading,time,unittest,uuid
from types import SimpleNamespace
from unittest.mock import patch
import app,integration as i

class Var:
    def __init__(self,value=''):self.value=value;self.writes=[]
    def get(self):return self.value
    def set(self,value):self.value=value;self.writes.append(value)

class Root:
    def __init__(self):self.destroyed=False;self.callbacks=[]
    def after(self,delay,callback):self.callbacks.append(callback);return len(self.callbacks)
    def destroy(self):self.destroyed=True

class Backend:
    context='quiet-owned';identity='owned-root'
    def __init__(self):self.release=threading.Event();self.entered=threading.Event();self.cancel=threading.Event();self.calls=[];self.active=0;self.maximum=0;self.objects=object()
    def dispatch(self,action,args):
        self.calls.append((action,copy.deepcopy(args)));self.active+=1;self.maximum=max(self.maximum,self.active)
        try:
            if action=='observe':
                self.entered.set()
                if not self.release.wait(5):raise RuntimeError('Owned observation did not finish')
                return {'status':'OK','code':'BANK_OBSERVED','context':self.context,'root_generation':self.identity,'token':[0,None],'identity':[1,2,'owned'],'cache_ready':True}
            if action=='save':return {'status':'ACCEPTED','code':'OWNED_ACCEPTED','transaction_id':args['transaction_id']}
            return {'status':'OK','code':'OWNED_RESULT'}
        finally:self.active-=1

class Tests(unittest.TestCase):
    def setUp(self):
        self.backend=Backend();self.w=app.Window.__new__(app.Window);w=self.w
        w.model=i.p.Model();w.bridge=i.p.base.Bridge(self.backend);w.root=Root();w.flow=i.Flow(self.backend.context,self.backend.identity)
        w.flow.token=[0,None];w.flow.identity=[1,2,'owned'];w.flow.index_ready=True;w.flow.refresh_pending=False;w.flow.rebuild_pending=False
        w.observing=False;w.waiting_action=False;w.background=False;w.observe_at=time.monotonic()+3600;w.poll_id=None;w.events=[]
        w.status=Var('Пользовательский результат');w.sync_status=Var('Bank подключён; поиск готов');w.pubstatus=Var();w.savestatus=Var();w.tx=Var()
        w.form_status=None;w.state_changes=[];w.shown=[];w.paints=0;w.set_busy=lambda value:w.state_changes.append(value)
        w.tab=lambda:'Bank';w.show_result=lambda result:w.shown.append(copy.deepcopy(result));w.paint_rows=lambda:setattr(w,'paints',w.paints+1)
        w.model.result={'status':'OK','code':'PINNED_DETAIL'};w.model.status=w.status.get();w.model.selected={'object_type':'Entity','object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4())}
        self.before=copy.deepcopy((w.model.result,w.model.selected,w.model.status,w.model.generation))
    def tearDown(self):
        self.backend.release.set()
        if self.w.bridge.thread:self.w.bridge.thread.join(6)
    def observe(self):
        self.assertTrue(self.w.submit('observe',{}));self.assertTrue(self.backend.entered.wait(2))
    def finish(self,predicate):
        self.backend.release.set();deadline=time.monotonic()+6
        while not predicate() and time.monotonic()<deadline:self.w.poll();time.sleep(.005)
        self.assertTrue(predicate())
    def test_01_repeated_idle_observation_does_not_toggle_controls_or_replace_user_context(self):
        w=self.w
        for _ in range(3):
            self.observe();self.assertFalse(w.model.busy);self.finish(lambda:not w.observing)
        self.assertEqual(w.state_changes,[]);self.assertEqual(w.status.writes,[]);self.assertEqual(w.sync_status.writes,[])
        self.assertEqual(w.shown,[]);self.assertEqual(w.paints,0);self.assertEqual((w.model.result,w.model.selected,w.model.status,w.model.generation),self.before)
        self.assertEqual(self.backend.maximum,1)
    def test_02_click_during_observation_runs_once_with_captured_arguments_after_poll(self):
        w=self.w;self.observe();args={'ref':copy.deepcopy(w.model.selected)};expected=copy.deepcopy(args)
        self.assertTrue(w.submit('detail',args));args['ref']['revision_id']='changed-outside-request'
        self.assertFalse(w.submit('detail',args));self.assertEqual([x[0] for x in self.backend.calls],['observe'])
        self.finish(lambda:not w.model.busy and not w.observing)
        self.assertEqual(self.backend.calls,[('observe',{}),('detail',expected)]);self.assertEqual(w.state_changes,[True,False]);self.assertEqual(self.backend.maximum,1)
        self.assertEqual(w.shown[-1]['code'],'OWNED_RESULT')
    def test_03_close_waits_for_idle_observation_without_starting_another_operation(self):
        w=self.w;self.observe();w.close();self.assertFalse(w.root.destroyed);self.assertTrue(w.model.closing)
        self.assertFalse(w.submit('detail',{}));self.finish(lambda:w.root.destroyed)
        self.assertEqual([x[0] for x in self.backend.calls],['observe']);self.assertTrue(w.model.closed)
    def test_04_close_after_queued_save_waits_for_its_exact_transaction_result(self):
        w=self.w;tx=str(uuid.uuid4());self.assertTrue(w.model.select_transaction(tx));self.observe()
        self.assertTrue(w.submit('save',{'transaction_id':tx}));w.close();self.assertFalse(w.root.destroyed)
        self.finish(lambda:w.root.destroyed)
        self.assertEqual(self.backend.calls[-1],('save',{'transaction_id':tx}));self.assertEqual(w.model.save['status'],'ACCEPTED');self.assertEqual(w.model.transaction_id,tx)
    def test_05_search_click_during_observation_is_retained_without_overlapping_worker(self):
        w=self.w;w.set_tab=lambda name:None;w.search_type=Var('Все типы');w.search_text=Var('pinned-word');w.search_mode=Var('current');w.field_vars={'body':Var(True)}
        self.observe();w.search();self.assertEqual(w.flow.search_pending['query'],'pinned-word');self.assertEqual(len(self.backend.calls),1)
        self.backend.release.set()
        deadline=time.monotonic()+6
        # Search scheduling is real; the backend's test result remains pending until polled.
        while len(self.backend.calls)<2 and time.monotonic()<deadline:w.poll();time.sleep(.005)
        self.assertEqual(self.backend.calls[1][0],'search');self.assertEqual(self.backend.maximum,1)
    def test_06_new_object_form_can_open_during_poll_and_stale_context_is_ignored(self):
        w=self.w;self.observe();self.assertFalse(w.model.busy)
        import sys
        sys.path.insert(0,str(i.runtime.ROOT/'EXPERIMENTS/object_authoring/runtime'))
        import object_ui
        w.object_form=None;w.form=None;w.object_vars={};w.object_lists={};w.object_controls=[]
        sentinel=RuntimeError('Entered form construction while observer active')
        with patch.object(object_ui.m,'Values',side_effect=sentinel):
            with self.assertRaisesRegex(RuntimeError,'Entered form construction'):object_ui.Window.open_object(w,'Entity')
        before=copy.deepcopy(w.flow.token)
        w.flow.apply('observe',{'status':'OK','context':'other','root_generation':'other','token':[99,None]})
        self.assertEqual(w.flow.token,before)

class NativeLayout(unittest.TestCase):
    def test_withdrawn_tk_controls_are_inside_reserved_area_before_expanding_panes(self):
        import sys,tkinter as tk
        sys.path.insert(0,str(i.runtime.ROOT/'EXPERIMENTS/object_authoring/runtime'))
        import object_ui
        root=tk.Tk();root.withdraw()
        try:
            w=object_ui.Window(root,Backend());root.update_idletasks()
            outer=w.tools_area.master;packed=outer.pack_slaves();paned=next(x for x in packed if x.winfo_class()=='TPanedwindow')
            self.assertLess(packed.index(w.tools_area),packed.index(paned))
            for key in ['attempts','safeguard','new_entity','new_collection','target_note','edit_object','object_list','object_next','object_finish']:
                control=w.buttons[key];self.assertEqual(control.master.master,w.tools_area)
            bar=w.buttons['new_entity'].master;self.assertLessEqual(bar.winfo_reqwidth(),root.minsize()[0]-32)
            self.assertEqual(w.buttons['edit_object'].grid_info()['row'],1);self.assertFalse(root.winfo_ismapped())
        finally:root.destroy()
