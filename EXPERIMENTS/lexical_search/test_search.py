"""Independent manual/oracle controls plus owned actual SQLite fault tests."""
from pathlib import Path
from contextlib import closing
import copy,hashlib,json,os,platform,shutil,socket,sqlite3,subprocess,sys,time,unittest,uuid
from unittest.mock import patch
import search as app
sys.path.insert(0,str(app.ROOT/'EXPERIMENTS/sqlite_importer'))
import test_importer as fixtures
sys.path.insert(0,str(app.ROOT/'PLANNING/TOOLS'))
import check_bank_queries as oracle

class Tests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');self.f.setUp();self.cache_root=self.f.temp/'cache';fixtures.private(self.cache_root);self.client=app.SearchAPI(self.f.root,self.cache_root);self.clients=[self.client];self.fixture=json.loads((app.ROOT/'PLANNING/CONTRACTS/BANK_QUERY_EXAMPLES.json').read_text(encoding='utf-8'));self.cache=self.cache_root/'search-cache.sqlite3'
    def tearDown(self):
        for c in self.clients:c.close()
        self.f.tearDown()
    def open(self,**kw):c=app.SearchAPI(self.f.root,self.cache_root,**kw);self.clients.append(c);return c
    def seed(self,maximum=4):
        heads={}
        for seq in range(1,maximum+1):
            b=fixtures.Bundle();b.m['transaction_id']=str(uuid.uuid4());b.m['operations']=[];b.files={}
            for item in self.fixture['revisions']:
                if item['commit_sequence']!=seq:continue
                d=item['document'];path='objects/'+d['object_id']+'.json';b.files[path]=app.im.encoded(d);b.m['operations'].append({'object_id':d['object_id'],'revision_id':d['revision_id'],'base_revision_id':heads.get(d['object_id']),'type':d['object_type'],'schema_ref':d['schema'],'document_path':path});heads[d['object_id']]=d['revision_id']
                if 'payload'in item:b.files[d['data']['storage']['file_path']]=oracle.payload(item)
            self.f.accepted(b)
    def query(self,**kw):q=copy.deepcopy(self.fixture['queries'][0]['request']);q.update(fields=['title','body','content','aliases'],query='alpha',request_id=str(uuid.uuid4()));q.update(kw);return q
    def result(self,q,client=None):
        r=(client or self.client).execute(app.im.encoded(q));self.assertIsNone(next(self.client.result_validator.iter_errors(r),None));return r
    def ok(self,q,client=None):r=self.result(q,client);self.assertEqual(r['status'],'OK',r);return r
    def error(self,q,code,client=None):r=self.result(q,client);self.assertEqual(r['status'],'ERROR',r);self.assertEqual(r['code'],code,r);self.assertNotIn('data',r);return r
    def build(self,client=None):r=(client or self.client).rebuild();self.assertEqual(r['status'],'BUILT',r);return r
    def corrupt_blob(self,table,column,rowid):
        with closing(sqlite3.connect(self.f.store.db,isolation_level=None)) as c:
            with c.blobopen(table,column,rowid,readonly=False) as b:b.write(b'!')
    def child(self,phase,root=None):
        return subprocess.run([sys.executable,str(Path(__file__)), '--child',str(self.f.root),str(root or self.cache_root),phase],capture_output=True,text=True,timeout=20)
    def large_postings(self):
        b=fixtures.Bundle.entity();op,d=b.doc('Entity');d['data']['aliases']=['word'+str(i).zfill(4)+'z'*1990 for i in range(1000)];b.files[op['document_path']]=app.im.encoded(d);return b
    def test_01_all_22_manual_refs_counts_and_independent_oracle(self):
        self.seed();before=self.f.store.db.read_bytes();self.build();schema,fixture,rows=oracle.check_all()
        for case in fixture['queries']:
            with self.subTest(control=case['id']):
                got=self.ok(case['request']);independent=oracle.search(case['request'],rows,schema);data=got['data'];self.assertEqual([h['ref'] for h in data['hits']],case['expected_refs']);self.assertEqual(data['total_matches'],case['expected_total']);self.assertEqual(sum(data['coverage'].values()),case['expected_corpus_count']);self.assertEqual(data['hits'],independent['hits']);self.assertEqual(data['coverage'],independent['coverage']);self.assertEqual(data['has_more'],independent['has_more'])
        self.assertEqual(before,self.f.store.db.read_bytes())
    def test_02_current_all_revisions_old_content(self):
        self.seed();self.build();q=self.query(query='inventory',fields=['content']);self.assertEqual(self.ok(q)['data']['hits'],[]);q['revisions_mode']='all_revisions';r=self.ok(q);self.assertEqual(r['data']['hits'][0]['ref']['revision_id'],'00000000-0000-4000-8000-000000000101')
    def test_03_and_cross_fields_alias_boundaries_duplicate_terms(self):
        self.seed();self.build();r=self.ok(self.query(query='alpha beta',fields=['aliases'],object_types=['Entity']));self.assertEqual(r['data']['total_matches'],1);self.assertEqual(self.ok(self.query(query='alphabeta',fields=['aliases']))['data']['total_matches'],0);a=self.ok(self.query(query='alpha'))['data']['hits'];b=self.ok(self.query(query='alpha alpha'))['data']['hits'];self.assertEqual(a,b)
    def test_04_unicode_normalization_literal_sql_tokens(self):
        self.seed();self.build()
        for value in ['Straße','STRASSE','cafe\u0301','café','Игры','alpha OR beta*']:
            q=self.query(query=value,revisions_mode='all_revisions');schema,_,rows=oracle.check_all();expected=oracle.search(q,rows,schema);self.assertEqual(self.ok(q)['data']['hits'],expected['hits'])
    def test_05_full_coverage_exclusions_not_integrity_or_truncation(self):
        self.seed();self.build();r=self.ok(self.query(query='notpresent',revisions_mode='all_revisions'));self.assertEqual(r['data']['coverage'],{'indexed':2,'locator_only':1,'unsupported_media':1,'invalid_utf8':1,'size_limit':1,'not_applicable':3});self.assertEqual(r['data']['hits'],[])
    def test_06_closed_requests_utf8_terms_numeric_limits(self):
        for changes in [{'extra':1},{'limit':True},{'limit':1.0},{'offset':-1},{'offset':10001},{'snapshot_sequence':False},{'object_types':['Source']},{'fields':['title','title']},{'revisions_mode':'event_time'}]:self.error(self.query(**changes),'INVALID_REQUEST')
        self.error(self.query(protocol='bad'),'UNSUPPORTED_PROTOCOL')
        for value,code in [('!!!','INVALID_REQUEST'),('я'*513,'LIMIT_EXCEEDED'),(' '.join('t'+str(n) for n in range(33)),'LIMIT_EXCEEDED')]:self.error(self.query(query=value),code)
        for raw in [b'{"a":1,"a":2}',b'{"x":NaN}',b'\xff',b'\xef\xbb\xbf{}',b'{"x":"\\ud800"}']:self.assertEqual(self.client.execute(raw)['code'],'INVALID_REQUEST')
        self.assertEqual(self.client.execute(b' '*16385)['code'],'LIMIT_EXCEEDED');self.assertEqual(self.client.execute(b'['*17+b'0'+b']'*17)['code'],'LIMIT_EXCEEDED')
    def test_07_missing_cache_unavailable_no_hidden_creation(self):
        self.seed();self.error(self.query(),'INDEX_UNAVAILABLE');self.assertFalse(self.cache.exists())
        with app.Cache(self.cache_root,self.f.root,self.client.limits) as c:c.initialize()
        self.error(self.query(),'INDEX_NOT_READY')
    def test_08_profile_and_unicode_mismatch_require_explicit_rebuild(self):
        self.seed();self.build()
        for field,value in [('unicode_version','other'),('profile_id','r1-wrong/1'),('normalization',99)]:
            with closing(sqlite3.connect(self.cache,isolation_level=None)) as c:c.execute('UPDATE generation SET '+field+'=?',(value,))
            self.error(self.query(),'INDEX_PROFILE_MISMATCH');self.build();self.ok(self.query())
    def test_09_stale_watermark_not_ready_old_snapshot_still_valid(self):
        self.seed(3);self.build();self.f.accepted(self.update_last());self.error(self.query(),'INDEX_NOT_READY');r=self.ok(self.query(snapshot_sequence=3));self.assertEqual(r['snapshot_sequence'],3);self.build();self.ok(self.query())
    def update_last(self):
        item=self.fixture['revisions'][-1];d=item['document'];b=fixtures.Bundle();b.m['transaction_id']=str(uuid.uuid4());path='objects/'+d['object_id']+'.json';b.m['operations']=[{'object_id':d['object_id'],'revision_id':d['revision_id'],'base_revision_id':'00000000-0000-4000-8000-000000000101','type':'Asset','schema_ref':d['schema'],'document_path':path}];b.files={path:app.im.encoded(d),d['data']['storage']['file_path']:oracle.payload(item)};return b
    def test_10_paging_snapshot_restart_and_old_pinned_hit_reopen(self):
        self.seed(3);self.build();q=self.query(limit=1);first=self.ok(q);self.assertTrue(first['data']['has_more']);pin=first['data']['hits'][0]['ref'];self.f.accepted(self.update_last());self.build();q.update(snapshot_sequence=3,offset=1);second=self.ok(q,self.open());self.assertEqual(second['snapshot_sequence'],3);self.assertNotEqual(first['data']['hits'],second['data']['hits'])
        request={'protocol':app.read.PROTOCOL,'request_id':str(uuid.uuid4()),'operation':'bank.get','object_type':pin['object_type'],'object_id':pin['object_id'],'selector':{'mode':'pinned','revision_id':pin['revision_id']}}
        with app.read.ReadAPI(self.f.root) as reader:r=reader.execute(app.im.encoded(request));self.assertEqual(r['status'],'OK');self.assertEqual(r['data']['ref'],pin)
    def test_11_postbuild_original_corruption_blocks_search_and_rebuild(self):
        self.seed();self.build();before=self.cache.read_bytes()
        with closing(sqlite3.connect(self.f.store.db)) as c:fid=c.execute("SELECT file_id FROM files WHERE path='raw/payload-101.bin'").fetchone()[0]
        self.corrupt_blob('files','file_blob',fid);self.error(self.query(),'INTEGRITY_ERROR');r=self.client.rebuild();self.assertEqual(r,{'status':'ERROR','code':'INTEGRITY_ERROR'});self.assertEqual(before,self.cache.read_bytes())
    def test_12_retained_document_or_receipt_corruption_no_cached_success(self):
        self.seed();self.build();self.corrupt_blob('accepted_receipts','receipt_blob',1);self.error(self.query(),'INTEGRITY_ERROR')
    def test_13_cache_postings_and_corpus_corruption_visible(self):
        self.seed();self.build()
        with closing(sqlite3.connect(self.cache,isolation_level=None)) as c:c.execute("UPDATE terms SET term='changed' WHERE rid='00000000-0000-4000-8000-000000000104' AND field_id=4 AND term='alpha'")
        self.error(self.query(),'INDEX_UNAVAILABLE');self.build()
        with closing(sqlite3.connect(self.cache,isolation_level=None)) as c:c.execute("UPDATE corpus SET document_sha256=? WHERE rid='00000000-0000-4000-8000-000000000104'",('0'*64,))
        self.error(self.query(),'INDEX_UNAVAILABLE')
    def test_14_cache_forged_own_checksum_still_compared_to_originals(self):
        self.seed();self.build()
        with closing(sqlite3.connect(self.cache,isolation_level=None)) as c:
            c.execute("UPDATE terms SET term='madeup' WHERE rid='00000000-0000-4000-8000-000000000104' AND field_id=4 AND term='alpha'");digest,n,p=self.client.cache_digest(c,app.read.Budget(self.client.limits));c.execute('UPDATE generation SET digest=?,revision_count=?,posting_count=?',(digest,n,p))
        self.error(self.query(query='madeup'),'INDEX_UNAVAILABLE')
    def test_15_cache_from_different_bank_not_served(self):
        self.seed();self.build();other=fixtures.Tests('test_01_supported_atomic_reopen_original_receipt');other.setUp()
        try:
            other.accepted();c=app.SearchAPI(other.root,self.cache_root)
            try:self.error(self.query(snapshot_sequence=1),'INDEX_UNAVAILABLE',c)
            finally:c.close()
        finally:other.tearDown()
    def test_16_unknown_cache_byte_identical_and_no_reinitialization(self):
        self.seed();self.cache.write_bytes(b'foreign-cache');before=self.cache.read_bytes();self.error(self.query(),'INDEX_UNAVAILABLE');self.assertEqual(self.client.rebuild()['code'],'INDEX_UNAVAILABLE');self.assertEqual(self.cache.read_bytes(),before)
    def test_17_known_headers_wrong_schema_rejected_untouched(self):
        self.seed();self.build()
        with closing(sqlite3.connect(self.cache,isolation_level=None)) as c:c.execute('CREATE TABLE unknown(x)')
        before=self.cache.read_bytes();self.error(self.query(),'INDEX_UNAVAILABLE');self.assertEqual(self.client.rebuild()['code'],'INDEX_UNAVAILABLE');self.assertEqual(self.cache.read_bytes(),before)
    def test_18_fault_before_publish_rolls_back_old_generation(self):
        self.seed(3);self.build();old=self.cache.read_bytes();self.f.accepted(self.update_last())
        def fail(name,value):
            if name=='before_publish':raise OSError('Owned publication I/O fault')
        self.assertEqual(self.open(_hook=fail).rebuild()['status'],'ERROR');self.assertEqual(old,self.cache.read_bytes());self.error(self.query(),'INDEX_NOT_READY');self.ok(self.query(snapshot_sequence=3));self.build();self.ok(self.query())
    def test_19_after_publish_fault_unknown_then_recover_query(self):
        self.seed()
        def fail(name,value):
            if name=='after_publish':raise OSError('Owned response lost after publication')
        result=self.open(_hook=fail).rebuild();self.assertEqual(result['status'],'UNKNOWN');self.ok(self.query())
    def test_20_owned_child_prepublication_first_reader_recovery(self):
        self.seed(3);self.build();self.f.accepted(self.update_last());self.f.accepted(self.large_postings());child=self.child('before_publish');self.assertEqual(child.returncode,71,child.stdout+child.stderr);self.assertTrue(Path(str(self.cache)+'-journal').exists());calls=[];original=app.Cache.connect
        def watched(cache,budget,write=False,recovery=True):calls.append(write);return original(cache,budget,write,recovery)
        with patch.object(app.Cache,'connect',watched):self.ok(self.query(snapshot_sequence=3))
        self.assertIn(True,calls);self.error(self.query(),'INDEX_NOT_READY')
    def test_21_owned_child_postpublication_new_generation_recovered(self):
        self.seed(3);self.build();self.f.accepted(self.update_last());child=self.child('after_publish');self.assertEqual(child.returncode,72,child.stdout+child.stderr);self.ok(self.query());self.assertEqual(self.ok(self.query())['snapshot_sequence'],4)
    def test_22_interrupted_initialization_not_a_complete_index(self):
        self.seed();child=self.child('init_before_commit');self.assertEqual(child.returncode,73,child.stdout+child.stderr);self.error(self.query(),'INDEX_UNAVAILABLE');before=self.cache.read_bytes();self.assertEqual(self.client.rebuild()['code'],'INDEX_UNAVAILABLE');self.assertEqual(before,self.cache.read_bytes())
    def test_23_real_sqlite_full_cache_page_limit_preserves_generation(self):
        self.seed(3);self.build();self.f.accepted(self.update_last());old=self.cache.read_bytes();configure=app.Cache.configure
        def limited(cache,c,write):
            configure(cache,c,write)
            if write:c.execute('PRAGMA max_page_count='+str(c.execute('PRAGMA page_count').fetchone()[0]))
        # Existing fixture may fit freelist pages; force a large own posting in new command.
        self.f.accepted(self.large_postings())
        with patch.object(app.Cache,'configure',limited):r=self.client.rebuild();self.assertEqual(r['status'],'ERROR',r)
        self.assertEqual(old,self.cache.read_bytes());self.ok(self.query(snapshot_sequence=3))
    def test_24_cache_busy_is_bounded_not_empty_success(self):
        self.seed();self.build();c=sqlite3.connect(self.cache,isolation_level=None);c.execute('BEGIN EXCLUSIVE');start=time.monotonic()
        try:self.error(self.query(),'BANK_BUSY');self.assertLess(time.monotonic()-start,3)
        finally:c.execute('ROLLBACK');c.close()
        self.ok(self.query())
    def test_25_bank_busy_is_bounded_not_empty_success(self):
        self.seed();self.build();c=sqlite3.connect(self.f.store.db,isolation_level=None);c.execute('BEGIN EXCLUSIVE')
        try:self.error(self.query(),'BANK_BUSY')
        finally:c.execute('ROLLBACK');c.close()
    def test_26_explicit_work_output_and_postings_limits_no_partial_success(self):
        self.seed();self.build()
        for limits in [{'stored_bytes_per_request':1},{'stored_metadata_bytes_per_request':1},{'response_bytes':100},{'elapsed_ms':0},{'sqlite_vm_steps':1000}]:self.error(self.query(),'LIMIT_EXCEEDED',self.open(_limits=limits))
        for limits in [{'corpus_revisions':1},{'postings':1}]:self.assertEqual(self.open(_limits=limits).rebuild()['code'],'LIMIT_EXCEEDED')
        self.ok(self.query())
    def test_27_private_cache_root_acl_overlap_and_real_hardlink_rejected(self):
        self.seed();self.build();c=app.SearchAPI(self.f.root,self.f.root)
        try:self.error(self.query(),'INDEX_UNAVAILABLE',c)
        finally:c.close()
        broad=self.f.temp/'broad';broad.mkdir(mode=0o777);os.chmod(broad,0o777)
        if os.name=='nt':changed=subprocess.run(['icacls',str(broad),'/grant','*S-1-1-0:(OI)(CI)R'],capture_output=True,timeout=10);self.assertEqual(changed.returncode,0,changed.stdout+changed.stderr)
        c=app.SearchAPI(self.f.root,broad)
        try:self.error(self.query(),'INDEX_UNAVAILABLE',c)
        finally:c.close()
        target=self.f.temp/'cache-alias';os.link(self.cache,target);self.error(self.query(),'INDEX_UNAVAILABLE');target.unlink();self.ok(self.query())
    def test_28_schema_config_and_readonly_query_authority(self):
        self.seed();self.build();bank=self.f.store.db.read_bytes()
        with app.Cache(self.cache_root,self.f.root,self.client.limits) as cache:
            c=cache.connect(app.read.Budget(self.client.limits),True)
            try:
                for pragma,value in [('synchronous',3),('foreign_keys',1),('trusted_schema',0)]:self.assertEqual(c.execute('PRAGMA '+pragma).fetchone()[0],value)
                self.assertTrue(c.getconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE));self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            finally:c.close()
            c=cache.connect(app.read.Budget(self.client.limits))
            try:
                for sql in ['DELETE FROM corpus','CREATE TABLE bad(x)','ATTACH DATABASE ":memory:" AS bad','PRAGMA writable_schema=ON']:
                    with self.assertRaises(sqlite3.DatabaseError):c.execute(sql)
            finally:c.close()
        self.ok(self.query());self.assertEqual(bank,self.f.store.db.read_bytes())
    def test_29_no_network_hidden_locator_fetch_or_field_expansion(self):
        self.seed();self.build()
        with patch.object(socket.socket,'connect',side_effect=AssertionError('No network')):
            r=self.ok(self.query(query='notsearchableexternal',fields=['title','aliases','body','content','uri','filename']));self.assertEqual(r['data']['total_matches'],0);self.ok(self.query(query='catalog',fields=['uri']))
    def test_30_exact_4m_content_boundary_and_above_not_truncated(self):
        b=self.f.large(4194304).edit('Asset',lambda d:d['data']['storage'].update(media_type='text/plain'));self.f.accepted(b);self.build();r=self.ok(self.query(object_types=['Asset']));self.assertEqual(r['data']['coverage']['indexed'],1)
        # Second command changes the same Asset to above extraction cap, preserving original.
        b=b.clone().revision('Asset');op,d=b.doc('Asset');raw=b'x'*4194305;d['data']['storage'].update(byte_length=len(raw),sha256=app.im.sha(raw));b.files[op['document_path']]=app.im.encoded(d);b.files[d['data']['storage']['file_path']]=raw;self.f.accepted(b);self.build();r=self.ok(self.query(object_types=['Asset']));self.assertEqual(r['data']['coverage']['size_limit'],1);self.assertEqual(r['data']['coverage']['indexed'],0)
    def test_31_empty_generation_and_missing_bank_no_initialization(self):
        self.build();r=self.ok(self.query());self.assertEqual(r['snapshot_sequence'],0);self.assertEqual(r['data']['total_matches'],0);self.assertEqual(sum(r['data']['coverage'].values()),0)
        other=self.f.temp/'absent';c=app.SearchAPI(other,self.cache_root)
        try:self.error(self.query(),'BANK_UNAVAILABLE',c);self.assertFalse(other.exists())
        finally:c.close()
    def test_32_cli_build_query_restart_and_errors(self):
        self.seed();base=[sys.executable,str(Path(app.__file__))];options=['--bank-root',str(self.f.root),'--cache-root',str(self.cache_root)];p=subprocess.run(base+['rebuild']+options,capture_output=True,timeout=20);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['status'],'BUILT')
        q=self.query();p=subprocess.run(base+['query']+options,input=app.im.encoded(q),capture_output=True,timeout=20);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['request_id'],q['request_id']);p=subprocess.run(base+['query']+options,input=b'{"bad":1}',capture_output=True,timeout=20);self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['code'],'UNSUPPORTED_PROTOCOL')
    def test_33_beyond_snapshot_error_never_empty(self):
        self.seed();self.build();self.error(self.query(snapshot_sequence=5),'SNAPSHOT_NOT_AVAILABLE');r=self.ok(self.query(snapshot_sequence=0));self.assertEqual(r['data']['total_matches'],0)
    def test_34_query_old_snapshot_and_build_hold_consistent_read_lock(self):
        self.seed(3);seen=[]
        def hook(name,value):
            if name=='snapshot_selected':seen.append(self.f.save(self.update_last()).state)
        c=self.open(_hook=hook);self.build(c);self.assertEqual(seen,['RETRYABLE_BUSY']);r=self.ok(self.query(),c);self.assertEqual(r['snapshot_sequence'],3);self.assertEqual(seen,['RETRYABLE_BUSY','RETRYABLE_BUSY']);self.f.accepted(self.update_last())

class Evidence(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[];self.bad=set()
    def addSuccess(self,t):super().addSuccess(t);self.cases.append({'id':t._testMethodName,'expected':'all integration assertions and manual controls pass','observed':'PASS'})
    def failed(self,t,e):self.bad.add(t._testMethodName);self.cases.append({'id':t._testMethodName,'observed':'FAIL','detail':self._exc_info_to_string(e,t)})
    def addFailure(self,t,e):super().addFailure(t,e);self.failed(t,e)
    def addError(self,t,e):super().addError(t,e);self.failed(t,e)
    def addSubTest(self,t,sub,e):super().addSubTest(t,sub,e);self.failed(t,e) if e else None
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child':
        def hook(name,value):
            if name==sys.argv[4]:os._exit({'before_publish':71,'after_publish':72,'init_before_commit':73}[name])
        with app.SearchAPI(sys.argv[2],sys.argv[3],_hook=hook) as client:client.rebuild()
        raise RuntimeError('Owned child did not reach required phase')
    result=unittest.TextTestRunner(verbosity=2,resultclass=Evidence).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));folder=Path(__file__).parent;at=app.im.now();report={'record_kind':'synthetic_R1_lexical_search_evidence','at':at,'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'unicode_data_version':app.unicodedata.unidata_version,'snapshot_adapter':'actual Windows secure reader handles' if os.name=='nt' else 'trusted portable fixture only','tests_run':result.testsRun,'success':result.wasSuccessful(),'skipped':len(result.skipped),'manual_control_queries':22,'cases':result.cases,'source_sha256':{p.name:app.im.sha(p.read_bytes()) for p in [folder/'search.py',folder/'test_search.py',folder/'cache_schema.sql',folder/'result.schema.json',folder/'LIMITS.json']},'limitations':['Synthetic private roots and complete generation within explicit work budget','Full-generation integrity audit each query; not a large-Bank throughput claim','Trusted code/operator/current owner/root parents','No real Bank/UI/privacy/hardware/release or whole-Unicode parity acceptance']}
    name='NATIVE_RESULTS.json' if os.name=='nt' else 'LOCAL_RESULTS.json';p=folder/name
    if p.exists():history=folder/'TEST_HISTORY';history.mkdir(exist_ok=True);shutil.copyfile(p,history/(name+'-'+uuid.uuid4().hex+'.json'))
    p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');p=folder/'ISSUES.json';issues=json.loads(p.read_text(encoding='utf-8'));known={i['id']:i for i in issues['issues']}
    for case in result.cases:
        iid='SEARCH-TEST-'+case['id'];i=known.get(iid)
        if case['observed']=='FAIL':
            if i is None:i={'id':iid,'title':'Integration assertion: '+case['id'],'history':[]};issues['issues'].append(i);known[iid]=i
            i['status']='open';i['history'].append({'at':at,'status':'open','evidence':name,'detail':case['detail']})
        elif i and i['status']=='open':i['status']='resolved';i['history'].append({'at':at,'status':'resolved','evidence':name,'note':'Rerun passed; prior failure retained.'})
    p.write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'tests_run':result.testsRun,'success':result.wasSuccessful(),'bad':sorted(result.bad),'manual_queries':22,'report':str(folder/name)}),flush=True);sys.exit(not result.wasSuccessful())
