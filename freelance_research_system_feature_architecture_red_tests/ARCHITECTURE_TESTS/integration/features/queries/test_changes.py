from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.scenarios import completed_run
M='research_system.features.queries.changes'
class ChangesQueryTests(ProjectCase):
    def test_parameterized_changes_query_is_read_only_and_does_not_start_monitoring_run(self):
        completed_run(self.root,'r1','2026-10-01',observations=[{'entity_id':'e1'}]); completed_run(self.root,'r2','2026-10-02',observations=[{'entity_id':'e1','semantic_payload':{'x':2}}]); before=self.digest(); r=self.feature(M,{'from_run_id':'r1','to_run_id':'r2','scope':'all'},now='2026-10-02T08:00:00+00:00'); self.assertEqual(self.digest(),before)
        for k in ['change_set_id','from_date','to_date','scope','comparison_status','events','coverage']: self.assertIn(k,r)
        self.assertFalse(r.get('monitoring_run_created',False))
