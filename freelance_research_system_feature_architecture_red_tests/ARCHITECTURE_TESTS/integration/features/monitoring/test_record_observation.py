from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
START='research_system.features.monitoring.start_run'; M='research_system.features.monitoring.record_observation'
class RecordObservationFeatureTests(ProjectCase):
    def setUp(self):
        super().setUp(); self.feature(START,{'run_id':'r1','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':['route']},now='2026-10-01T00:00:00+00:00')
    def req(self,**kw):
        x={'entity_id':'e1','canonical_key':'k','observation_class':'seen','asserted_state':'active','source_id':'s1','semantic_payload':{'x':1}}; x.update(kw); return x
    def test_observation_is_append_only_and_inherits_run_context(self):
        r=self.feature(M,self.req(),now='2026-10-01T00:01:00+00:00')
        self.assertEqual(r['run_id'],'r1'); self.assertEqual(r['method_id'],'m'); self.assertEqual(r['scope_fingerprint'],'s'); self.assertEqual(r['source_route_ids'],['route'])
    def test_exact_retry_is_idempotent(self):
        a=self.feature(M,self.req(),now='2026-10-01T00:01:00+00:00'); b=self.feature(M,self.req(),now='2026-10-01T00:01:00+00:00')
        self.assertEqual(a['observation_id'],b['observation_id']); self.assertTrue(b['replay'])
    def test_secret_values_are_redacted_before_persistence_or_result(self):
        r=self.feature(M,self.req(semantic_payload={'token':'abc','nested':{'password':'p'},'x':1}),now='2026-10-01T00:01:00+00:00')
        self.assertNotIn('abc',str(r)); self.assertNotIn("'p'",str(r)); self.assertIn('[REDACTED]',str(r))
    def test_record_without_active_run_is_rejected_after_finalize(self):
        self.feature('research_system.features.monitoring.finish_run',{'coverage_status':'complete','coverage_notes':''},now='2026-10-01T01:00:00+00:00')
        assert_error_code(self,'no_active_run',lambda:self.feature(M,self.req(),now='2026-10-01T01:01:00+00:00'))
