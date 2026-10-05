from ARCHITECTURE_TESTS.support.integration import ProjectCase
M_DISC='research_system.features.sources.discover'; M='research_system.features.sources.manage'
class ManageSourcesFeatureTests(ProjectCase):
    def source(self): return self.feature(M_DISC,{'canonical_name':'Market','discovery_route_ids':['search'],'discovered_via_source_ids':[]},now='2026-10-01T01:00:00+00:00')['source_id']
    def test_role_general_priority_and_task_requirement_remain_independent(self):
        sid=self.source(); r=self.feature(M,{'source_id':sid,'role':'evidence','priority':'P2','status':'active','use_plan':{'use_plan_id':'p','role':'evidence','requirement_level':'required'}},now='2026-10-02T00:00:00+00:00')
        self.assertEqual(r['source_role'],'evidence'); self.assertEqual(r['current_priority'],'P2'); self.assertEqual(r['use_plan']['requirement_level'],'required')
    def test_retire_preserves_source_and_review_history(self):
        sid=self.source(); self.feature(M,{'source_id':sid,'status':'watch','review_note':'watch it'},now='2026-10-02T00:00:00+00:00'); r=self.feature(M,{'source_id':sid,'status':'retired','review_note':'retire'},now='2026-10-03T00:00:00+00:00')
        self.assertEqual(r['current_status'],'retired'); self.assertEqual([x['note'] for x in r['review_history']],['watch it','retire'])
