from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
M='research_system.features.monitoring.start_run'
class StartRunFeatureTests(ProjectCase):
    def test_starts_one_active_run_with_frozen_comparability_context(self):
        r=self.feature(M,{'run_id':'r1','method_id':'m','method_version':'1','scope_fingerprint':'scope','source_route_ids':['b','a']},now='2026-10-01T00:00:00+00:00')
        self.assertEqual(r['run_id'],'r1'); self.assertEqual(r['status'],'active'); self.assertEqual(r['source_route_ids'],['a','b']); self.assertEqual(r['research_date'],'2026-10-01')
    def test_second_active_run_is_rejected(self):
        self.feature(M,{'run_id':'r1','method_id':'m','method_version':'1','scope_fingerprint':'scope','source_route_ids':[]},now='2026-10-01T00:00:00+00:00')
        assert_error_code(self,'active_run_exists',lambda:self.feature(M,{'run_id':'r2','method_id':'m','method_version':'1','scope_fingerprint':'scope','source_route_ids':[]},now='2026-10-01T00:01:00+00:00'))
