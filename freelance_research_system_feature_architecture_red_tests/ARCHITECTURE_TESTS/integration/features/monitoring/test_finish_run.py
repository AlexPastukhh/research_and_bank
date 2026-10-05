from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
START='research_system.features.monitoring.start_run'; M='research_system.features.monitoring.finish_run'
class FinishRunFeatureTests(ProjectCase):
    def setUp(self):
        super().setUp(); self.feature(START,{'run_id':'r1','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':[]},now='2026-10-01T00:00:00+00:00')
    def test_finalize_records_coverage_and_releases_active_run_slot_atomically(self):
        r=self.feature(M,{'coverage_status':'complete','coverage_notes':'ok'},now='2026-10-01T01:00:00+00:00')
        self.assertEqual(r['status'],'completed'); self.assertEqual(r['coverage_status'],'complete')
        nxt=self.feature(START,{'run_id':'r2','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':[]},now='2026-10-02T00:00:00+00:00')
        self.assertEqual(nxt['run_id'],'r2')
    def test_double_finalize_is_rejected_without_corrupting_active_slot(self):
        self.feature(M,{'coverage_status':'complete','coverage_notes':''},now='2026-10-01T01:00:00+00:00')
        assert_error_code(self,'no_active_run',lambda:self.feature(M,{'coverage_status':'failed','coverage_notes':''},now='2026-10-01T02:00:00+00:00'))
