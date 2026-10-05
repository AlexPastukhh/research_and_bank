from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.queries.research_health'
class ResearchHealthQueryTests(ProjectCase):
    def test_health_query_is_read_only_and_reports_diagnostics_without_repairing(self):
        before=self.digest(); r=self.feature(M,{'scope':'all'},now='2026-10-08T08:00:00+00:00'); self.assertEqual(self.digest(),before)
        for k in ['generated_at','freshness','coverage','comparability','quality_flags','system_audit']: self.assertIn(k,r)
        self.assertFalse(r.get('repair_performed',False)); self.assertFalse(r.get('refresh_performed',False))
