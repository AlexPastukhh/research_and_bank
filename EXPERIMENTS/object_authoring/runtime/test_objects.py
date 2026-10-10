"""Independent retained bytes/CAS/SQL oracles with owned roots and actual process leases."""
from pathlib import Path
import copy, hashlib, json, os, subprocess, sys, unittest, uuid
import object_authoring as o
sys.path.insert(0, str(o.ROOT / 'EXPERIMENTS/first_bank'))
import test_first_bank as fb

class Tests(fb.Tests):
    # Reuse fixtures, not all inherited test cases in the object suite.
    def setUp(self):
        super().setUp(); self.all_roots = {**self.roots, 'object_authoring': self.temp / 'object_authoring'}
        fb.creation.old.fx.private(self.all_roots['object_authoring'])
        self.kw = {} if os.name == 'nt' else {'_portable_fixture': True,
          '_controller_kwargs': {'_transport': fb.creation.old.ct.portable_read, '_store_factory': fb.creation.old.ct.PortableStore},
          '_publisher_kwargs': {'_portable_fixture': True}}
        self.b = o.Backend(self.all_roots, context='object-test', **self.kw); self.ow = self.b.objects

    def new(self, typ='Entity', **changes):
        data = self.ow.defaults(typ)
        if typ == 'Annotation': data['body'] = 'A targeted explanation'
        return {'object_type': typ, 'title': 'Problem algorithm theory', 'data': data, **changes}

    def obj(self, fields=None, **kw):
        out = self.ow.prepare(fields or self.new(), **kw); self.assertEqual(out['status'], 'PREPARED', out); return out

    def commit(self, out):
        tx = {'transaction_id': out['transaction_id']}
        pub = self.b.dispatch('publish', tx); self.assertIn(pub['status'], ['PUBLISHED', 'ALREADY_PUBLISHED'], pub)
        saved = self.b.dispatch('save', tx); self.assertIn(saved['status'], ['ACCEPTED', 'REPLAY'], saved); return saved

    def detail(self, out):
        r = self.b.dispatch('detail', {'ref': out['ref']}); self.assertEqual(r['status'], 'OK', r); return r['data']['document']

    def test_obj01_all_objects_pins_order_stable_history_sql(self):
        entity = self.obj(); self.commit(entity)
        edit = self.obj({'title': 'Algorithm improved'}, base_ref=entity['ref']); self.commit(edit)
        self.assertEqual(edit['ref']['object_id'], entity['ref']['object_id']); self.assertNotEqual(edit['ref']['revision_id'], entity['ref']['revision_id'])
        note = self.obj(self.new('Annotation', data={**self.ow.defaults('Annotation'), 'body': 'Explain theory', 'targets': [entity['ref']]})); self.commit(note)
        collection = self.obj(self.new('Collection', data={'members': [edit['ref'], note['ref'], entity['ref']]})); self.commit(collection)
        self.assertEqual(self.detail(collection)['data']['members'], [edit['ref'], note['ref'], entity['ref']])
        self.assertEqual(self.detail(entity)['title'], 'Problem algorithm theory')
        store_factory = o.a.im.Store if os.name == 'nt' else fb.creation.old.ct.PortableStore
        with store_factory(self.roots['bank']) as store:
            c = store._connect(False)
            try:
                self.assertEqual(c.execute('SELECT count(*) FROM revisions WHERE object_id=?', (entity['ref']['object_id'],)).fetchone()[0], 2)
                self.assertEqual(c.execute('SELECT base_revision_id FROM revisions WHERE revision_id=?', (edit['ref']['revision_id'],)).fetchone()[0], entity['ref']['revision_id'])
            finally: c.close()

    def test_obj02_old_new_shared_lock_no_nested_lease(self):
        self.b.config()
        with self.w.session():
            refused = self.ow.prepare(self.new()); self.assertEqual(refused['code'], 'AUTHORING_BUSY', refused); self.assertIsNone(refused['transaction_id'])
        with self.ow.session():
            refused = self.w.prepare(self.f.fields()); self.assertEqual(refused['code'], 'AUTHORING_BUSY', refused)
        note = self.prepare(); self.save(note)
        out = self.obj(); self.commit(out); self.assertEqual(self.commit(out)['status'], 'REPLAY')

    def test_obj03_retained_original_and_replacement_exact(self):
        path = self.temp / 'source.txt'; raw = b'\xef\xbb\xbfexact retained\r\n'; path.write_bytes(raw)
        old = self.prepare(path); self.save(old); path.unlink()
        out = self.obj({'title': 'Only metadata changed'}, base_ref=old['ref']); self.commit(out)
        self.assertEqual(self.detail(out)['data']['storage']['media_type'], 'text/plain')
        self.assertEqual(Path(self.b.dispatch('export', {'ref': out['ref']})['data']['original']['path']).read_bytes(), raw)
        replacement = self.temp / 'replacement.txt'; new = 'Новый оригинал\r\n'.encode(); replacement.write_bytes(new)
        edited = self.obj({'title': 'Replacement'}, base_ref=out['ref'], replacement={'path': str(replacement), 'input_mode': 'utf8_text'})
        replacement.unlink(); self.assertEqual(self.ow.inspect(edited['transaction_id'])['status'], 'PREPARED'); self.commit(edited)
        for obj, expected in [(old, raw), (out, raw), (edited, new)]:
            exported = self.b.dispatch('export', {'ref': obj['ref']}); self.assertEqual(exported['status'], 'OK', exported)
            self.assertEqual(Path(exported['data']['original']['path']).read_bytes(), expected)
        self.assertEqual(self.detail(edited)['provenance']['origin_kind'], 'unknown')

    def test_obj04_stale_base_exact_retry_and_explicit_new_edit(self):
        base = self.obj(); self.commit(base)
        a = self.obj({'title': 'Competing A'}, base_ref=base['ref']); b = self.obj({'title': 'Competing B'}, base_ref=base['ref'])
        self.commit(a); tx = b['transaction_id']; before = (self.roots['source'] / tx / 'DRAFT.json').read_bytes()
        self.assertEqual(self.b.dispatch('publish', {'transaction_id': tx})['status'], 'PUBLISHED')
        for _ in range(2): self.assertEqual(self.b.dispatch('save', {'transaction_id': tx})['code'], 'STALE_BASE')
        self.assertEqual((self.roots['source'] / tx / 'DRAFT.json').read_bytes(), before)
        fresh = self.obj({'title': 'Explicit next edit'}, base_ref=a['ref']); self.commit(fresh)
        self.assertNotEqual(fresh['transaction_id'], tx); self.assertEqual(fresh['base_ref'], a['ref'])

    def test_obj05_sealed_recovery_without_bank_or_original_and_tamper(self):
        def hook(name, value):
            if name == 'seal_published': raise OSError('checkpoint')
        w = o.Workspace(self.all_roots, self.b, _portable_fixture=os.name != 'nt', _hook=hook)
        failed = w.prepare(self.new()); tx = failed['transaction_id']; self.assertEqual(self.ow.inspect(tx)['status'], 'SEALED')
        self.assertEqual(self.ow.inspect(tx, finish=True)['status'], 'PREPARED')
        intent = self.all_roots['object_authoring'] / tx / 'INTENT.json'; raw = intent.read_bytes(); d = json.loads(raw); d['template']['title'] = 'tampered'; intent.write_bytes(o.encoded(d))
        self.assertEqual(self.ow.inspect(tx)['code'], 'INTENT_INTEGRITY'); intent.write_bytes(raw)
        out = self.ow.inspect(tx); self.commit(out)
        intent.write_bytes(b'broken')
        receipt = self.b.dispatch('receipt', {'transaction_id': tx, 'expected_manifest_sha256': out['manifest_sha256']})
        self.assertEqual(receipt['status'], 'OK', receipt); self.assertEqual(self.b.dispatch('save', {'transaction_id': tx})['status'], 'REPLAY')

    def test_obj06_closed_fields_limits_and_reference_failure(self):
        for bad in [self.new(data={**self.ow.defaults('Entity'), 'properties': {}}), self.new(object_id=str(uuid.uuid4())),
                    self.new(data={**self.ow.defaults('Entity'), 'aliases': ['x']*129})]:
            out = self.ow.prepare(bad); self.assertIsNone(out['transaction_id'], out)
        refs = {'object_type': 'Asset', 'object_id': str(uuid.uuid4()), 'revision_id': str(uuid.uuid4())}
        out = self.ow.prepare(self.new(data={**self.ow.defaults('Entity'), 'asset_refs': [refs]})); self.assertIsNone(out['transaction_id'], out); self.assertTrue(out['code'].startswith('BASE_'), out)

    def test_obj07_normal_64m_and_one_over_before_allocation(self):
        path = self.temp / 'large.bin'
        with path.open('wb') as f: f.truncate(64*1024*1024)
        old = self.prepare(path, input_mode='binary'); self.save(old)
        out = self.obj({'title': 'Retained 64MiB'}, base_ref=old['ref']); self.commit(out)
        self.assertEqual(self.detail(out)['data']['storage']['byte_length'], 64*1024*1024)
        with path.open('wb') as f: f.truncate(64*1024*1024+1)
        out = self.ow.prepare({'title': 'Too large'}, base_ref=old['ref'], replacement={'path': str(path), 'input_mode': 'binary'})
        self.assertEqual(out['code'], 'AUTHORING_INPUT_LIMIT'); self.assertIsNone(out['transaction_id'])

    def test_obj08_actual_two_process_lease_exit_release(self):
        code = "import sys,time;sys.path.insert(0,sys.argv[1]);import object_authoring as o;lease=o.io.WorkspaceLock(o.Path(sys.argv[2]));lease.__enter__();print('LOCKED',flush=True);time.sleep(30)"
        child = subprocess.Popen([sys.executable, '-c', code, str(Path(__file__).parent), str(self.roots['authoring'] / 'LOCK')], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), 'LOCKED')
            refused = self.ow.prepare(self.new()); self.assertEqual(refused['code'], 'AUTHORING_BUSY', refused)
            legacy = self.w.prepare(self.f.fields()); self.assertEqual(legacy['code'], 'AUTHORING_BUSY', legacy)
        finally:
            child.kill(); child.communicate(timeout=10)
        self.commit(self.obj()); legacy = self.prepare(); self.save(legacy)

    def test_obj09_overlay_config_reopen_rollback_preserves_original(self):
        import configuration as cfg
        base = self.temp / 'configured'; cfg.r.setup(base, portable=os.name != 'nt')
        original = (base / 'config.json').read_bytes(); before = cfg.r.load(base, portable=os.name != 'nt')
        enabled = cfg.setup(base, portable=os.name != 'nt')
        self.assertEqual(len(enabled['roots']), 8); self.assertEqual((base / 'config.json').read_bytes(), original)
        self.assertEqual(cfg.load(base, portable=os.name != 'nt')['config_id'], enabled['config_id'])
        self.assertEqual(cfg.r.load(base, portable=os.name != 'nt'), before)
        cfg.rollback(base, portable=os.name != 'nt'); self.assertEqual((base / 'config.json').read_bytes(), original)
        self.assertFalse((base / cfg.NAME).exists()); self.assertTrue((base / 'object_authoring').is_dir())

    def child(self, action, args, phase):
        code = """import sys,json,os
sys.path.insert(0,sys.argv[1]);import object_authoring as o;import test_objects as t
kw={} if os.name=='nt' else {'_portable_fixture':True,'_controller_kwargs':{'_transport':t.fb.creation.old.ct.portable_read,'_store_factory':t.fb.creation.old.ct.PortableStore},'_publisher_kwargs':{'_portable_fixture':True}}
phase=sys.argv[5]
def hook(n,v):
 if n==phase:os._exit(77)
if sys.argv[3]=='object_prepare':kw['_hook']=hook
elif sys.argv[3]=='publish':kw.setdefault('_publisher_kwargs',{})['_hook']=hook
else:kw.setdefault('_controller_kwargs',{})['_hook']=hook
b=o.Backend(json.loads(sys.argv[2]),**kw);b.dispatch(sys.argv[3],json.loads(sys.argv[4]))
"""
        return subprocess.run([sys.executable,'-X','utf8','-c',code,str(Path(__file__).parent),json.dumps({k:str(v) for k,v in self.all_roots.items()}),action,json.dumps(args),phase],capture_output=True,timeout=35)

    def test_obj10_actual_exits_intent_base_capture_draft_and_seal(self):
        path=self.temp/'exit.txt';path.write_bytes(b'exact exit bytes\r\n');old=self.prepare(path);self.save(old)
        phases=['allocated','intent_published_pending','intent_published','base_published_pending','base_published','source_created','capture_chunk','original_flushed','document_flushed','draft_flushed','seal_published_pending','seal_published','draft_published']
        for phase in phases:
            before=set(self.all_roots['object_authoring'].iterdir())
            child=self.child('object_prepare',{'fields':{'title':'Crash '+phase},'base_ref':old['ref']},phase)
            self.assertEqual(child.returncode,77,(phase,child.stdout,child.stderr))
            created=set(self.all_roots['object_authoring'].iterdir())-before;self.assertEqual(len(created),1)
            tx=next(iter(created)).name;result=self.ow.inspect(tx)
            expected='PREPARED' if phase=='draft_published' else 'SEALED' if phase=='seal_published' else 'INCOMPLETE'
            self.assertEqual(result['status'],expected,(phase,result))
            if expected=='SEALED':self.assertEqual(self.ow.inspect(tx,finish=True)['status'],'PREPARED')

    def test_obj11_publication_exit_and_postcommit_unknown_same_id_receipt(self):
        out=self.obj();tx=out['transaction_id']
        child=self.child('publish',{'transaction_id':tx},'after_move');self.assertEqual(child.returncode,77,(child.stdout,child.stderr))
        self.assertIn(self.b.dispatch('resume',{'transaction_id':tx})['status'],['PUBLISHED','ALREADY_PUBLISHED'])
        child=self.child('save',{'transaction_id':tx},'after_import');self.assertEqual(child.returncode,77,(child.stdout,child.stderr))
        receipt=self.b.dispatch('receipt',{'transaction_id':tx,'expected_manifest_sha256':out['manifest_sha256']})
        self.assertEqual(receipt['status'],'OK',receipt);self.assertEqual(self.b.dispatch('save',{'transaction_id':tx})['status'],'REPLAY')
        self.assertEqual(self.f.h.h.h.count(),1)

    def test_obj12_ui_values_worker_context_pins_and_close(self):
        import object_model as model
        entity=self.obj();self.commit(entity);base,_=self.ow.read_base(entity['ref'])
        form=model.Values(self.ow,'Entity',base);form.title='Changed through structured form';form.data['aliases']=['algorithm','theory']
        state=model.Model();state.select_transaction(entity['transaction_id']);state.selected=copy.deepcopy(entity['ref'])
        state.begin('object_prepare',form.args(),'Bank');bridge=o.first.p.base.Bridge(self.b);self.assertTrue(bridge.submit('object_prepare',form.args()))
        while (result:=bridge.poll()) is None: __import__('time').sleep(.005)
        state.finish(result);self.assertEqual(state.transaction_id,result['transaction_id']);self.assertEqual(state.preparation['base_ref'],entity['ref'])
        # A→B→A selects immutable contexts; a changed generation rejects the active outcome.
        old=entity['transaction_id'];new=result['transaction_id']
        state.select_transaction(old);state.select_transaction(new);state.select_transaction(old)
        state.begin('object_load',{'transaction_id':old},'Bank');state.generation+=1;state.finish(self.ow.inspect(old))
        self.assertEqual(state.result['code'],'TRANSACTION_CONTEXT_MISMATCH')
        values=model.Values(self.ow,'Collection');values.add_ref('members',entity['ref']);values.add_ref('members',result['ref']);values.move('members',1,-1)
        self.assertEqual(values.data['members'],[result['ref'],entity['ref']])
        state.select_transaction(new);state.begin('save',{'transaction_id':new},'Bank');state.close_request();state.finish({'status':'UNKNOWN','transaction_id':new,'code':'OPERATION_OUTCOME_UNCERTAIN'})
        self.assertTrue(state.closed);self.assertFalse(state.begin('object_prepare',form.args(),'Bank'))

    def test_obj13_utf8_cancel_boundaries_and_explicit_binary_media(self):
        path=self.temp/'replace.dat';path.write_bytes(b'ok\xff');old=self.prepare(path,input_mode='binary');self.save(old)
        bad=self.ow.prepare({'title':'Invalid text'},base_ref=old['ref'],replacement={'path':str(path),'input_mode':'utf8_text'})
        self.assertEqual(bad['code'],'INVALID_UTF8');self.assertEqual(self.ow.inspect(bad['transaction_id'])['status'],'INCOMPLETE')
        out=self.obj({'title':'Explicit binary'},base_ref=old['ref'],replacement={'path':str(path),'input_mode':'binary'});self.commit(out)
        self.assertEqual(self.detail(out)['data']['storage']['media_type'],'application/octet-stream')
        self.assertEqual(self.ow.prepare(self.new(),cancel=lambda:True)['status'],'CANCELLED')
        out=self.obj(self.new(data={**self.ow.defaults('Entity'),'aliases':['alias'+str(i) for i in range(128)]}));self.commit(out)
        too_many=self.ow.prepare(self.new(data={**self.ow.defaults('Entity'),'aliases':['alias'+str(i) for i in range(129)]}))
        self.assertEqual(too_many['code'],'OBJECT_LIST_LIMIT');self.assertIsNone(too_many['transaction_id'])
        path.write_bytes(b'final\xe2\x82')
        bad=self.ow.prepare({'title':'Final partial codepoint'},base_ref=old['ref'],replacement={'path':str(path),'input_mode':'utf8_text'})
        self.assertEqual(bad['code'],'INVALID_UTF8')

    def test_obj14_128_pins_normal_case_and_129_refusal(self):
        fixture=fb.creation.old.fx.Bundle.entity();op,doc=fixture.doc('Entity');fixture.m['operations']=[];fixture.files={};refs=[]
        for i in range(128):
            value=copy.deepcopy(doc);value.update(object_id=str(uuid.uuid4()),revision_id=str(uuid.uuid4()),title='Owned reference '+str(i))
            path='docs/entity-'+str(i)+'.json';fixture.files[path]=o.encoded(value)
            fixture.m['operations'].append({**op,'object_id':value['object_id'],'revision_id':value['revision_id'],'document_path':path})
            refs.append({k:value[k] for k in ['object_type','object_id','revision_id']})
        self.f.h.save(fixture)
        out=self.obj(self.new('Collection',data={'members':refs}));self.commit(out)
        self.assertEqual(self.detail(out)['data']['members'],refs)
        one_more={**refs[0],'revision_id':str(uuid.uuid4())}
        bad=self.ow.prepare(self.new('Collection',data={'members':refs+[one_more]}));self.assertEqual(bad['code'],'OBJECT_LIST_LIMIT');self.assertIsNone(bad['transaction_id'])

    def test_obj15_real_form_callback_preserves_pinned_base(self):
        import object_model as model,object_ui
        from types import SimpleNamespace
        entity=self.obj();self.commit(entity);base,_=self.ow.read_base(entity['ref'])
        form=model.Values(self.ow,'Entity',base)
        class Var:
            def __init__(self,value):self.value=value
            def get(self):return self.value
            def set(self,value):self.value=value
        sent=[];window=object_ui.Window.__new__(object_ui.Window)
        window.model=SimpleNamespace(busy=False,closing=False,selected={'object_type':'Entity','object_id':str(uuid.uuid4()),'revision_id':str(uuid.uuid4())})
        window.object_values=form;window.object_vars={k:Var(v) for k,v in {'title':'Form callback edit','entity_kind':'algorithm','origin':'unknown','source_locator':''}.items()}
        window.object_status=Var('');window.submit=lambda action,args:sent.append((action,args))
        window.prepare_object();self.assertEqual(sent[0][0],'object_prepare');self.assertEqual(sent[0][1]['base_ref'],entity['ref'])
        out=self.obj(sent[0][1]['fields'],base_ref=sent[0][1]['base_ref']);self.commit(out);self.assertEqual(self.detail(out)['data']['entity_kind'],'algorithm')

    def test_obj16_search_evolution_all_four_edits_and_locator_replacement(self):
        entity=self.obj(self.new(data={**self.ow.defaults('Entity'),'entity_kind':'problem','aliases':['evolutionterm']}));self.commit(entity)
        for kind in ['algorithm','theory']:
            d=self.detail(entity)['data'];d['entity_kind']=kind
            entity=self.obj({'title':kind+' evolutionterm','data':d},base_ref=entity['ref']);self.commit(entity)
        note=self.obj(self.new('Annotation',data={**self.ow.defaults('Annotation'),'body':'evolutionterm explanation','targets':[entity['ref']]}));self.commit(note)
        note2=self.obj({'title':'Edited note evolutionterm'},base_ref=note['ref']);self.commit(note2)
        coll=self.obj(self.new('Collection',data={'members':[note['ref'],entity['ref'],note2['ref']]}));self.commit(coll)
        coll2=self.obj({'title':'Edited collection evolutionterm'},base_ref=coll['ref']);self.commit(coll2)
        locator=self.w.prepare(self.f.fields('url'));self.save(locator)
        d=self.f.doc(locator)['data'];d['storage']['uri']='https://example.invalid/new'
        locator2=self.obj({'title':'Edited Asset evolutionterm','data':d},base_ref=locator['ref']);self.commit(locator2)
        self.assertEqual(self.detail(locator2)['provenance']['source_locator'],'https://example.invalid/new')
        self.assertEqual(self.b.dispatch('rebuild',{})['status'],'BUILT')
        found=self.b.dispatch('search',{'object_types':sorted(o.TYPES),'fields':['title','body','aliases'],'query':'evolutionterm','revisions_mode':'all_revisions'})
        self.assertEqual(found['status'],'OK',found)
        ids={row['ref']['revision_id'] for row in found['data']['hits']}
        self.assertTrue({entity['ref']['revision_id'],note['ref']['revision_id'],note2['ref']['revision_id'],coll2['ref']['revision_id'],locator2['ref']['revision_id']}<=ids)

    def test_obj17_v1_v2_compatibility_quota_and_context_isolation(self):
        path=self.temp/'old-profile.txt';path.write_bytes(b'old v1 bytes\xff\r\n')
        legacy=o.a.Workspace(self.roots,_portable_fixture=os.name!='nt',_limits={'policy_version':'r1-authoring/1'})
        old=legacy.prepare({'kind':'file','title':'Frozen v1','path':str(path)});self.assertEqual(old['status'],'PREPARED',old)
        self.save(old);path.unlink();edited=self.obj({'title':'Edit old binary'},base_ref=old['ref']);self.commit(edited)
        self.assertEqual(self.detail(edited)['data']['storage']['media_type'],'application/octet-stream')
        old_intent=json.loads((self.roots['authoring']/old['transaction_id']/'INTENT.json').read_bytes())
        self.assertEqual(old_intent['profile']['policy_version'],'r1-authoring/1')
        before={p.relative_to(self.temp).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in ['source','object_authoring'] for p in self.all_roots[root].rglob('*') if p.is_file()}
        for limits in [{'intents':1},{'workspace_bytes_including_managed_source':0},{'work_bytes':0},{'capture_elapsed_ms':0},{'workspace_scan_entries':0}]:
            w=o.Workspace(self.all_roots,self.b,_portable_fixture=os.name!='nt',_limits=limits);refused=w.prepare(self.new())
            self.assertIsNone(refused['transaction_id'],refused)
        after={p.relative_to(self.temp).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in ['source','object_authoring'] for p in self.all_roots[root].rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        flow=o.first.Flow('A',self.b.identity);out=self.b.dispatch('observe',{});out['context']='B'
        flow.apply('observe',out);self.assertIsNone(flow.token)

    def test_obj18_unchanged_form_does_not_prepare_any_of_five_inputs(self):
        import object_model as model,object_ui
        from types import SimpleNamespace
        class Var:
            def __init__(self,value):self.value='' if value is None else value
            def get(self):return self.value
            def set(self,value):self.value=value
        objects=[self.obj(self.new(typ)) for typ in ['Entity','Annotation','Collection']]
        for out in objects:self.commit(out)
        file=self.temp/'no-op.txt';file.write_bytes(b'exact unchanged\r\n')
        locator=self.w.prepare({'kind':'url','title':'Owned URL','uri':'https://example.invalid/no-op'})
        self.assertEqual(locator['status'],'PREPARED',locator)
        for out in [self.prepare(file),locator]:self.save(out);objects.append(out)
        def snapshot():
            return {p.relative_to(self.temp).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in ['source','object_authoring','bank'] for p in self.roots.get(root,self.all_roots[root]).rglob('*') if p.is_file()}
        for out in objects:
            with self.subTest(ref=out['ref']):
                base,_=self.ow.read_base(out['ref']);typ=base['document']['object_type'];form=model.Values(self.ow,typ,base)
                v=base['document']['data'];pv=base['document']['provenance']
                fields={'title':form.title,'origin':pv['origin_kind'],'source_locator':pv['source_locator']}
                if typ=='Entity':fields['entity_kind']=v['entity_kind']
                if typ=='Annotation':fields.update(annotation_kind=v['kind'],format=v['content_format'],author=v['author']['kind'],identity=v['author']['identity'],model=v['author']['model'])
                if typ=='Asset':
                    if v['storage']['mode']=='locator':fields.update(uri=v['storage']['uri'],label=v['storage']['label'])
                    else:fields.update(replacement_path='',replacement_mode='binary')
                sent=[];window=object_ui.Window.__new__(object_ui.Window)
                window.model=SimpleNamespace(busy=False,closing=False,selected=None,transaction_id='keep-this-preparation')
                window.object_values=form;window.object_vars={k:Var(x) for k,x in fields.items()};window.object_status=Var('')
                window.object_body=SimpleNamespace(get=lambda *args:v['body']) if typ=='Annotation' else None
                window.submit=lambda action,args:sent.append((action,args))
                before=snapshot();captured=copy.deepcopy(form.base)
                window.prepare_object();self.assertEqual(sent,[]);self.assertEqual(window.object_status.get(),'Изменений нет')
                window.object_vars['title'].set('Changed title');window.prepare_object();self.assertEqual(len(sent),1)
                self.assertEqual(sent[0][1]['base_ref'],out['ref'])
                window.object_vars['title'].set(form.base['document']['title']);window.prepare_object()
                self.assertEqual(len(sent),1);self.assertEqual(window.object_status.get(),'Изменений нет')
                self.assertEqual(snapshot(),before);self.assertEqual(form.base,captured);self.assertEqual(window.model.transaction_id,'keep-this-preparation')

    def test_obj19_change_detection_preserves_explicit_intent_and_order(self):
        import object_model as model
        a=self.obj();self.commit(a);b=self.obj();self.commit(b)
        collection=self.obj(self.new('Collection',data={'members':[a['ref'],b['ref']]}));self.commit(collection)
        base,_=self.ow.read_base(collection['ref']);v=model.Values(self.ow,'Collection',base)
        self.assertFalse(v.has_changes());v.move('members',0,1);self.assertTrue(v.has_changes());v.move('members',0,1);self.assertFalse(v.has_changes())
        v.provenance['source_locator']='https://example.invalid/source';self.assertTrue(v.has_changes())
        v.provenance['source_locator']=base['document']['provenance']['source_locator'];self.assertFalse(v.has_changes())
        v.provenance['producer']={'name':'ignored technical producer'};self.assertFalse(v.has_changes())
        v.replacement={'path':'explicitly selected file','input_mode':'binary'};self.assertTrue(v.has_changes())
        self.assertTrue(model.Values(self.ow,'Collection').has_changes())
        self.assertTrue(model.Values(self.ow,'Annotation',target=a['ref']).has_changes())
        note=self.obj(self.new('Annotation'));self.commit(note);base,_=self.ow.read_base(note['ref']);v=model.Values(self.ow,'Annotation',base)
        v.data['body']+=' ';self.assertTrue(v.has_changes());v.data['body']=base['document']['data']['body'];self.assertFalse(v.has_changes())
        v.add_ref('targets',a['ref']);self.assertTrue(v.has_changes())

    def test_obj20_human_search_history_and_exact_technical_context(self):
        import object_model as model
        p=o.first.p.base
        old=self.obj(self.new(title='Original presentationterm'));self.commit(old)
        new=self.obj({'title':'Changed presentationterm'},base_ref=old['ref']);self.commit(new)
        self.assertEqual(self.b.dispatch('rebuild',{})['status'],'BUILT')
        args={'query':'presentationterm','object_types':['Entity'],'fields':['title'],'revisions_mode':'current'}
        hits=self.b.dispatch('search',args);self.assertEqual(hits['status'],'OK',hits)
        self.assertEqual([(x['ref'],x['title']) for x in hits['data']['hits']],[(new['ref'],'Changed presentationterm')])
        history=self.b.dispatch('history',{'ref':new['ref']});self.assertEqual(history['status'],'OK',history)
        self.assertEqual([(x['ref'],x['title']) for x in history['data']['revisions']],[(new['ref'],'Changed presentationterm'),(old['ref'],'Original presentationterm')])
        m=model.Model();m.begin('history',{'ref':new['ref']},'History');m.finish(history);m.select('History',1)
        pinned=copy.deepcopy(m.selected);details=self.b.dispatch('detail',{'ref':pinned})
        normal=p.display(details,labels=m.labels);technical=p.display(details,technical=True)
        self.assertIn('Original presentationterm',normal);self.assertNotIn('Revision:',normal)
        for key in ['object_id','revision_id']:
            self.assertNotIn(old['ref'][key],normal);self.assertIn(old['ref'][key],technical)
        self.assertEqual(m.selected,pinned);self.assertEqual(details['data']['ref'],old['ref'])
        for row in history['data']['revisions']:
            text=' '.join(p.row_values(row));self.assertIn(row['title'],text);self.assertNotIn(row['ref']['revision_id'],text)
        intents=p.intent_labels([{'title':'Duplicate','transaction_id':'a'},{'title':'Duplicate','transaction_id':'b'}]);self.assertNotEqual(*intents)
        self.assertEqual(p.chosen_types('Сущность'),['Entity'])
        note=self.obj(self.new('Annotation',data={**self.ow.defaults('Annotation'),'body':'Plain AI text','author':{'kind':'ai','identity':'Assistant name','model':'Example model'}}));self.commit(note)
        text=p.display(self.b.dispatch('detail',{'ref':note['ref']}))
        self.assertIn('Assistant name',text);self.assertIn('Example model',text);self.assertIn('plain_text',text)

    @unittest.skipUnless(os.name=='nt','Owned withdrawn Tk verification runs on Windows')
    def test_obj21_withdrawn_tk_details_and_noop_controls(self):
        import tkinter as tk,object_ui
        out=self.obj();self.commit(out);base,_=self.ow.read_base(out['ref'])
        root=tk.Tk();root.withdraw();window=None
        try:
            window=object_ui.Window(root,self.b)
            window.model.remember({'ref':out['ref'],'title':base['document']['title']})
            window.model.selected=copy.deepcopy(out['ref'])
            window.model.rows['Bank']=[{'ref':out['ref'],'title':base['document']['title'],'accepted_at':base['accepted_at']}]
            window.paint_rows();window.show_result(self.b.dispatch('detail',{'ref':out['ref']}))
            self.assertEqual(window.txline.winfo_manager(),'');self.assertEqual(window.tabs.tab(list(window.tab_names)[2],'state'),'hidden')
            self.assertNotIn(out['ref']['revision_id'],window.details.get('1.0','end'))
            window.technical.set(True);window.toggle_technical();self.assertEqual(window.txline.winfo_manager(),'pack')
            self.assertIn(out['ref']['revision_id'],window.details.get('1.0','end'))
            window.technical.set(False);window.toggle_technical();self.assertEqual(window.txline.winfo_manager(),'')
            window.set_tab('History');self.assertEqual(window.tab(),'History');window.set_tab('Bank')
            window.open_object('Entity',base=base);window.object_form.withdraw()
            sent=[];window.submit=lambda action,args,tab=None:sent.append((action,args));window.prepare_object()
            self.assertEqual(sent,[]);self.assertEqual(window.object_status.get(),'Изменений нет')
            self.assertEqual(window.model.selected,out['ref']);self.assertFalse(window.model.busy)
            window.technical.set(True);window.toggle_technical();self.assertEqual(window.form_technical.winfo_manager(),'pack')
            window.technical.set(False);window.toggle_technical();self.assertEqual(window.form_technical.winfo_manager(),'')
        finally:
            if window and window.object_form:window.object_form.destroy()
            root.destroy()

if __name__ == '__main__':
    suite = unittest.TestSuite(Tests(n) for n in unittest.defaultTestLoader.getTestCaseNames(Tests) if n.startswith('test_obj'))
    sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
