from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.delivery.run_practical_test'
class PracticalDeliveryFeatureTests(ProjectCase):
    def test_records_delivery_effort_dimensions_separately_from_market_demand(self):
        r=self.feature(M,{'service_unit_id':'svc1','brief_ref':'brief1','setup_minutes':10,'learning_minutes':5,'execution_minutes':60,'revision_minutes':15,'communication_minutes':10,'quality_gaps':['g1'],'tool_costs':2},now='2026-10-01T03:00:00+00:00')
        for k in ['setup_minutes','learning_minutes','execution_minutes','revision_minutes','communication_minutes','quality_gaps','tool_costs']: self.assertIn(k,r)
        self.assertNotIn('demand_score',r); self.assertNotIn('competition_score',r)
