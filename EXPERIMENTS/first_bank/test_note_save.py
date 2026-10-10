"""Normal save, exact retry, CAS, and Windows creation descriptor regressions.

Uses owned temporary Banks and withdrawn windows only, never user records.
"""
from pathlib import Path
import copy,os,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'object_authoring/runtime'))
import test_objects,object_authoring as o,object_model,object_ui
p=o.first.p

class Tests(test_objects.Tests):
    def mismatched_default_owner(self):
        """Exercise real duplicate-token APIs, with only the source-owner query injected.

        Does not grant/elevate a token or claim to reproduce an elevated process.
        """
        n=o.io.n;real=n._token_sid
        def source_owner(token,kind):
            value=n.W.DWORD();count=n.W.DWORD()
            n.checked(n.token_info(token,8,n.C.byref(value),n.C.sizeof(value),n.C.byref(count)))
            return 'S-1-5-32-544' if kind==4 and value.value==1 else real(token,kind)
        return patch.object(n,'_token_sid',side_effect=source_owner)

    def thread_token(self):
        n=o.io.n;token=n.W.HANDLE()
        if not n.open_thread_token(n.thread(),8,True,n.C.byref(token)):
            self.assertEqual(n.C.get_last_error(),1008);return None
        try:return (n._token_sid(token,1),n._token_sid(token,4))
        finally:n.close_handle(token)

    def test_note08_sqlite_journal_owner_save_and_restore(self):
        if os.name!='nt':self.skipTest('Actual Windows token and SQLite journal APIs')
        n=o.io.n;before=self.thread_token();owners=[]
        def hook(name,value):
            if name=='before_commit':
                with n.Handle(Path(str(self.roots['bank']/'bank.sqlite')+'-journal'),_share=7) as h:
                    n.verify_private_acl(h);owners.append(n.security_sddl(h).split('D:',1)[0])
                self.assertEqual(self.thread_token(),(n.current_sid(),n.current_sid()))
        self.b.base.ckw['_store_factory']=lambda root,**kw:o.a.im.Store(root,_hook=hook,**kw)
        with self.mismatched_default_owner():
            out=self.b.dispatch('author_save',{'fields':{'kind':'note','title':'SQLite owner test','body':'Exact body','author_kind':'user'}})
            self.assertEqual(out['status'],'ACCEPTED',out);self.assertEqual(out['diagnostic_attempt']['availability'],'available')
            again=self.b.dispatch('continue_save',{'transaction_id':out['transaction_id'],'route':'author'});self.assertEqual(again['status'],'REPLAY',again)
            self.assertEqual(self.b.dispatch('rebuild',{})['status'],'BUILT')
        self.assertEqual(owners,['O:'+n.current_sid()]);self.assertEqual(self.thread_token(),before)
        self.assertEqual(self.detail(out['workflow']['preparation'])['data']['body'],'Exact body')

    def test_note09_sqlite_exception_restores_nested_token(self):
        if os.name!='nt':self.skipTest('Actual Windows token APIs')
        n=o.io.n;before=self.thread_token()
        with self.mismatched_default_owner():
            outer=n.SQLiteCreationOwner()
            try:
                active=self.thread_token();self.assertEqual(active,(n.current_sid(),n.current_sid()))
                with self.assertRaisesRegex(RuntimeError,'owned interruption'):
                    with o.a.im.Store(self.roots['bank']) as store:
                        c=store._connect(True)
                        try:c.execute('BEGIN IMMEDIATE');raise RuntimeError('owned interruption')
                        finally:c.close()
                self.assertEqual(self.thread_token(),active)
            finally:outer.close()
        self.assertEqual(self.thread_token(),before)

    def test_note10_existing_bad_journal_not_adopted(self):
        if os.name!='nt':self.skipTest('Actual Windows guarded SQLite')
        n=o.io.n;journal=Path(str(self.roots['bank']/'bank.sqlite')+'-journal')
        with n.Handle(journal,new=True) as h:h.write(b'owned sentinel');n.checked(n.flush_file(h.h))
        raw=journal.read_bytes();real=n.security_sddl
        def foreign(h):
            descriptor=real(h)
            return descriptor.replace('O:'+n.current_sid(),'O:BA',1) if h.path==journal else descriptor
        with self.mismatched_default_owner(),patch.object(n,'security_sddl',side_effect=foreign):
            with self.assertRaisesRegex(n.SafetyError,'UNTRUSTED_OWNER'):
                with o.a.im.Store(self.roots['bank']) as store:store._connect(True)
        self.assertEqual(journal.read_bytes(),raw);journal.unlink();self.assertIsNone(self.thread_token())

    def test_note01_one_save_exact_read_and_retry(self):
        fields={'kind':'note','title':'My ordinary note','body':'Exact user text\r\n🙂','author_kind':'user'}
        model=object_model.Model();self.assertTrue(model.begin('author_save',{'fields':fields},'Bank'))
        out=self.b.dispatch('author_save',{'fields':fields});self.assertEqual(out['status'],'ACCEPTED',out);self.assertTrue(model.finish(out))
        prepared=out['workflow']['preparation'];tx=out['transaction_id'];doc=self.detail(prepared)
        self.assertEqual(doc['title'],fields['title']);self.assertEqual(doc['data']['body'],fields['body']);self.assertEqual(doc['data']['author'],{'kind':'user','identity':None,'model':None})
        self.assertEqual(model.transaction_id,tx);self.assertEqual(model.receipt_args(tx)['expected_manifest_sha256'],prepared['manifest_sha256'])
        self.assertTrue(model.begin('continue_save',{'transaction_id':tx,'route':'author'},'Bank'))
        retry=self.b.dispatch('continue_save',{'transaction_id':tx,'route':'author'});self.assertEqual(retry['status'],'REPLAY',retry);self.assertEqual(retry['transaction_id'],tx);model.finish(retry)
        with o.a.im.Store(self.roots['bank']) as store:
            c=store._connect(False)
            try:self.assertEqual(c.execute('SELECT count(*) FROM commits').fetchone()[0],1)
            finally:c.close()
        flow=o.first.Flow('test',self.b.identity);flow.refresh_pending=False;flow.rebuild_pending=False;flow.apply('author_save',out);self.assertTrue(flow.refresh_pending);self.assertTrue(flow.rebuild_pending)

    def test_note02_structured_save_and_stale_edit(self):
        out=self.b.dispatch('object_save',{'fields':self.new()});self.assertEqual(out['status'],'ACCEPTED',out);base=out['workflow']['preparation']
        changed=self.b.dispatch('object_save',{'fields':{'title':'Changed title'},'base_ref':base['ref']});self.assertEqual(changed['status'],'ACCEPTED',changed)
        stale=self.b.dispatch('object_save',{'fields':{'title':'Other edit'},'base_ref':base['ref']});self.assertEqual(stale['code'],'STALE_BASE',stale)
        self.assertEqual(stale['workflow']['phase'],'save');self.assertEqual(stale['workflow']['preparation']['status'],'PREPARED');self.assertEqual(self.detail(base)['title'],'Problem algorithm theory')
        self.assertEqual(self.detail(changed['workflow']['preparation'])['title'],'Changed title')

    def test_note03_required_body_optional_identity_no_allocation(self):
        before=set(self.roots['authoring'].iterdir());out=self.b.dispatch('author_save',{'fields':{'kind':'note','title':'A title','body':'','author_kind':'user'}})
        self.assertEqual(out['status'],'REJECTED');self.assertEqual(out['code'],'EMPTY_INPUT');self.assertIsNone(out['transaction_id']);self.assertEqual(set(self.roots['authoring'].iterdir()),before)
        valid=self.b.workspace.fields({'kind':'note','title':'Title','body':'Text','author_kind':'user'});self.assertIsNone(valid['identity'])

    def test_note04_withdrawn_forms_human_choices_and_save_buttons(self):
        if os.name!='nt':self.skipTest('Actual Windows Tk layout')
        import tkinter as tk
        root=tk.Tk();root.withdraw();window=object_ui.Window(root,self.b);sent=[]
        window.submit=lambda action,args,tab=None:sent.append((action,copy.deepcopy(args))) or True
        try:
            root.update_idletasks();self.assertEqual(window.transaction_tools.winfo_manager(),'');self.assertEqual(window.author_tools.winfo_manager(),'');self.assertEqual(window.object_tools.winfo_manager(),'')
            window.new_form();window.form.withdraw();window.title.set('A title');window.author.set('user')
            window.prepare_button.invoke();self.assertEqual(window.form_status.get(),'Введи текст заметки.');self.assertEqual(sent,[])
            window.body.insert('1.0','Note text');self.assertEqual(window.prepare_button.cget('text'),'Сохранить');window.prepare_button.invoke()
            self.assertEqual(sent[-1][0],'author_save');self.assertEqual(sent[-1][1]['fields']['author_kind'],'user');self.assertEqual(tuple(window.kind_combo.cget('values')),('Заметка','Файл','Ссылка'))
            window.kind_combo.current(1);window.kind_combo.event_generate('<<ComboboxSelected>>');self.assertEqual(window.kind.get(),'file')
            window.close_form();window.open_object('Annotation');window.object_form.withdraw();window.object_vars['title'].set('Target note');window.object_body.insert('1.0','Another text')
            self.assertEqual(window.object_prepare_button.cget('text'),'Сохранить');window.object_prepare_button.invoke();self.assertEqual(sent[-1][0],'object_save')
            window.handle_extension_result('object_save',{'status':'INCOMPLETE','code':'INTERRUPTED','transaction_id':'00000000-0000-4000-8000-000000000001','workflow':{'route':'object','preparation':{'status':'INCOMPLETE','sealed_input_may_exist':True}}});window.object_prepare_button.invoke()
            self.assertEqual(sent[-1][0],'continue_save');self.assertNotIn('fields',sent[-1][1]);self.assertEqual(sent[-1][1]['route'],'object')
            window.technical.set(True);window.toggle_technical();self.assertEqual(window.transaction_tools.winfo_manager(),'pack');self.assertEqual(window.author_tools.winfo_manager(),'grid');self.assertEqual(window.object_tools.winfo_manager(),'pack')
            window.technical.set(False);window.toggle_technical();self.assertEqual(window.transaction_tools.winfo_manager(),'')
        finally:
            for name in ['poll_id','refresh_id']:
                token=getattr(window,name,None)
                if token is not None:root.after_cancel(token);setattr(window,name,None)
            root.destroy()

    def test_note05_windows_new_file_explicit_owner_existing_unchanged(self):
        if os.name!='nt':self.skipTest('Actual Windows security descriptors')
        n=o.io.n;original=n.create;calls=[];path=self.roots['source']/'owned-check.bin'
        def spy(*args):
            if args[3]:
                sa=n.C.cast(args[3],n.C.POINTER(n.SecurityAttributes)).contents;value=n.W.LPWSTR()
                n.checked(n.sd_string(sa.descriptor,1,1|4,n.C.byref(value),None))
                try:calls.append(value.value)
                finally:n.local_free(n.C.cast(value,n.C.c_void_p))
                self.assertFalse(sa.inherit)
            else:calls.append(None)
            return original(*args)
        with patch.object(n,'create',side_effect=spy):
            with o.io.File(path,new=True) as f:f.write(b'exact');f.flush()
            before=path.read_bytes()
            with o.io.File(path) as f:self.assertEqual(f.read(10),b'exact');f.check()
        self.assertEqual(calls[0].split('D:',1)[0],'O:'+n.current_sid());self.assertIsNone(calls[1]);self.assertEqual(path.read_bytes(),before)
        with n.Handle(path) as h:
            descriptor=n.security_sddl(h);self.assertEqual(descriptor.split('D:',1)[0],'O:'+n.current_sid());n.verify_private_acl(h)
            with patch.object(n,'security_sddl',return_value=descriptor.replace('O:'+n.current_sid(),'O:BA',1)):
                with self.assertRaisesRegex(n.SafetyError,'UNTRUSTED_OWNER'):n.verify_private_acl(h)

    def test_note06_composite_failure_keeps_transaction_and_fields(self):
        real=self.b.dispatch;calls=[]
        def dispatch(action,args):
            calls.append(action)
            if action=='save':return {'status':'UNKNOWN','code':'OPERATION_OUTCOME_UNCERTAIN','transaction_id':args['transaction_id']}
            return real(action,args)
        self.b.dispatch=dispatch;fields={'kind':'note','title':'Retry note','body':'Text remains','author_kind':'user'}
        model=object_model.Model();self.assertTrue(model.begin('author_save',{'fields':fields},'Bank'));unknown=self.b.dispatch('author_save',{'fields':fields});model.finish(unknown)
        tx=unknown['transaction_id'];self.assertEqual(unknown['status'],'UNKNOWN');self.assertEqual(model.transaction_id,tx);self.assertEqual(model.preparation['status'],'PREPARED');self.assertEqual(model.save['status'],'UNKNOWN')
        calls.clear();self.b.dispatch=real;recovered=self.b.dispatch('continue_save',{'transaction_id':tx,'route':'author'});self.assertEqual(recovered['status'],'ACCEPTED',recovered);self.assertEqual(recovered['transaction_id'],tx)
        self.assertEqual(self.detail(recovered['workflow']['preparation'])['data']['body'],'Text remains')

    def test_note07_native_search_cache_creation_and_readback(self):
        if os.name!='nt':self.skipTest('Actual Windows security descriptors')
        n=o.io.n;original=n.create;owners=[]
        def spy(*args):
            if args[4]==1 and str(args[0]).endswith('search-cache.sqlite3'):
                self.assertTrue(args[3]);sa=n.C.cast(args[3],n.C.POINTER(n.SecurityAttributes)).contents;value=n.W.LPWSTR()
                n.checked(n.sd_string(sa.descriptor,1,1,n.C.byref(value),None))
                try:owners.append(value.value)
                finally:n.local_free(n.C.cast(value,n.C.c_void_p))
            return original(*args)
        with patch.object(n,'create',side_effect=spy):
            result=self.b.dispatch('rebuild',{});self.assertEqual(result['status'],'BUILT',result)
        self.assertEqual(owners,['O:'+n.current_sid()])
        cache=self.roots['cache']/'search-cache.sqlite3'
        with n.Handle(cache) as h:n.verify_private_acl(h);self.assertGreater(h.size(),100)
