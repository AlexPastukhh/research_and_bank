from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.repair.reconcile'
class RepairFeatureTests(ProjectCase):
    def test_repair_reports_and_reconciles_completed_run_left_marked_active_without_inventing_observations(self):
        """PROPOSAL derived from reproduced crash window."""
        seed=self.feature('research_system.features.monitoring.start_run',{'run_id':'r1','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':[]},now='2026-10-01T00:00:00+00:00')
        # test-only fault hook must create the exact durable split state that recovery owns
        fault=self.feature('research_system.features.monitoring.finish_run',{'coverage_status':'complete','coverage_notes':''},now='2026-10-01T01:00:00+00:00',fault_at='after_run_persist_before_session_commit')
        r=self.feature(M,{'mode':'conservative'},now='2026-10-01T02:00:00+00:00')
        self.assertIn('active_run_reconciled',r['repairs']); self.assertEqual(r.get('invented_observation_count',0),0)
        nxt=self.feature('research_system.features.monitoring.start_run',{'run_id':'r2','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':[]},now='2026-10-02T00:00:00+00:00')
        self.assertEqual(nxt['run_id'],'r2')
