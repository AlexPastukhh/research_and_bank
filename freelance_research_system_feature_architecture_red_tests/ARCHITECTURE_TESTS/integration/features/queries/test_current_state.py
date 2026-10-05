from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.queries.current_state'
class CurrentStateQueryTests(ProjectCase):
    def test_query_is_read_only_and_returns_freshness_coverage_method_and_exclusions(self):
        before=self.digest(); r=self.feature(M,{'scope':'all'},now='2026-10-01T08:00:00+00:00'); self.assertEqual(self.digest(),before)
        for k in ['snapshot_id','generated_at','scope','freshness_policy_version','coverage','results','excluded']: self.assertIn(k,r)
