"""Contract counterexamples; no claims about the production index or endpoint."""
import copy, json, unittest, unicodedata
import check_bank_queries as q

class QueryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.schema, cls.fixture, cls.rows = q.check_all()
    def request(self): return copy.deepcopy(self.fixture['queries'][0]['request'])
    def fails(self, code, fn, *args):
        with self.assertRaises(q.QueryError) as caught: fn(*args)
        self.assertEqual(str(caught.exception), code)
    def test_manual_expected_refs_and_counts(self):
        q.check_all()
        r=self.request();r.update(query='analysis beta',fields=['title','body'])
        self.assertEqual([x['ref']['object_id'] for x in q.search(r,self.rows,self.schema)['hits']],
                         ['00000000-0000-4000-8000-000000000004'])
    def test_closed_requests_limits_modes(self):
        for updates in [{'extra':1},{'object_types':['Source']},{'fields':['title','title']},
                        {'fields':['provenance']},{'revisions_mode':'event_time'},{'limit':True},
                        {'offset':-1},{'snapshot_sequence':True},{'limit':101}]:
            r=self.request();r.update(updates);self.fails('INVALID_REQUEST',q.validate_request,r,self.schema)
        for query,code in [('!!!','INVALID_REQUEST'),('\ud800','INVALID_REQUEST'),('я'*513,'LIMIT_EXCEEDED'),
                           (' '.join('term'+str(i) for i in range(33)),'LIMIT_EXCEEDED')]:
            r=self.request();r['query']=query;self.fails(code,q.validate_request,r,self.schema)
        r=self.request();r['protocol']='local-bank-query/2';self.fails('UNSUPPORTED_PROTOCOL',q.validate_request,r,self.schema)
    def test_json_duplicates_and_nonfinite(self):
        for raw in [b'{"limit":1,"limit":2}',b'{"x":NaN}',b'\xff',b'\xef\xbb\xbf{}']:
            self.fails('INVALID_REQUEST',q.strict_json,raw)
    def test_pinned_get_never_falls_back_to_current(self):
        old=self.fixture['revisions'][0]['document'];new=self.fixture['revisions'][-1]['document']
        r=dict(protocol='local-bank-query/1',request_id=self.request()['request_id'],operation='bank.get',
               object_type='Asset',object_id=old['object_id'],selector=dict(mode='pinned',revision_id=old['revision_id']))
        self.assertEqual(q.get(r,self.rows,self.schema),old)
        r['selector']={'mode':'current'};self.assertEqual(q.get(r,self.rows,self.schema),new)
        r['selector']={'mode':'pinned','revision_id':'00000000-0000-4000-8000-000000000099'}
        self.fails('REVISION_NOT_FOUND',q.get,r,self.rows,self.schema)
        r['object_type']='Entity';self.fails('TYPE_MISMATCH',q.get,r,self.rows,self.schema)
        r.update(operation='collection.get',object_type='Collection',object_id='00000000-0000-4000-8000-000000000005',selector={'mode':'current'})
        collection=q.get(r,self.rows,self.schema)
        self.assertEqual(collection['data']['members'][0],q.ref(old))
        self.assertNotEqual(collection['data']['members'][0],q.ref(new))
    def test_pagination_keeps_prior_snapshot(self):
        r=self.request();r.update(query='alpha',fields=['content','body','title'],snapshot_sequence=3,limit=1)
        first=q.search(r,self.rows,self.schema);self.assertTrue(first['has_more'])
        r['offset']=1;second=q.search(r,self.rows,self.schema)
        self.assertNotEqual(first['hits'][0]['ref'],second['hits'][0]['ref'])
        self.assertEqual(first['snapshot_sequence'],second['snapshot_sequence'])
        self.assertEqual(first['total_matches'],second['total_matches'])
    def test_corrupt_retained_bytes_are_not_skipped(self):
        f=copy.deepcopy(self.fixture);f['revisions'][0]['payload']['text']+='tampered'
        self.fails('INTEGRITY_ERROR',q.build_corpus,f)
    def test_index_failure_not_empty_success(self):
        r=self.request();good=dict(available=True,complete_through_sequence=4,unicode_data_version=unicodedata.unidata_version,
                                  profile_id='r1-lexical/1',normalization_version=1)
        for changes,code in [({'available':False},'INDEX_UNAVAILABLE'),({'complete_through_sequence':3},'INDEX_NOT_READY'),
                             ({'unicode_data_version':'unknown'},'INDEX_PROFILE_MISMATCH'),
                             ({'profile_id':'other'},'INDEX_PROFILE_MISMATCH'),
                             ({'normalization_version':2},'INDEX_PROFILE_MISMATCH')]:
            cache=good.copy();cache.update(changes);self.fails(code,q.search,r,self.rows,self.schema,cache)
        r['snapshot_sequence']=5;self.fails('SNAPSHOT_NOT_AVAILABLE',q.search,r,self.rows,self.schema)
    def test_literal_and_exact_tokens(self):
        self.assertEqual(q.tokens('Straße STRASSE'),{'strasse'})
        self.assertEqual(q.tokens('cafe\u0301'),{'café'})
        self.assertNotEqual(q.tokens('cafe'),q.tokens('café'))
        self.assertEqual(q.tokens('alpha OR beta*'),{'alpha','or','beta'})
        self.assertEqual(q.tokens('游戏机制'),{'游戏机制'})

if __name__=='__main__': unittest.main()
