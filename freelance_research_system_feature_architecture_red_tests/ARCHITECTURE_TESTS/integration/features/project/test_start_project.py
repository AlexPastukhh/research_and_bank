from ARCHITECTURE_TESTS.support.integration import EmptyRootCase
from ARCHITECTURE_TESTS.support.future import assert_error_code

M='research_system.features.project.start'
class StartProjectFeatureTests(EmptyRootCase):
    def test_initializes_valid_project_with_explicit_version_and_idle_execution_state(self):
        """BASELINE UC01."""
        r=self.feature(M,{'project_id':'p1','research_day_timezone':'UTC'},now='2026-10-01T00:00:00+00:00')
        self.assertEqual(r['project_id'],'p1'); self.assertEqual(r['status'],'initialized'); self.assertIsNone(r['active_task_id']); self.assertIn('system_version',r)

    def test_existing_project_is_not_silently_overwritten(self):
        self.feature(M,{'project_id':'p1','research_day_timezone':'UTC'},now='2026-10-01T00:00:00+00:00')
        assert_error_code(self,'project_already_exists',lambda:self.feature(M,{'project_id':'p2','research_day_timezone':'UTC'},now='2026-10-01T00:00:01+00:00'))
