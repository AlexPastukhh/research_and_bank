from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
M='research_system.features.decisions.update'
class DecisionUpdateFeatureTests(ProjectCase):
    def test_unmeasured_dimension_cannot_be_used_to_decide(self):
        assert_error_code(self,'dimension_unmeasured',lambda:self.feature(M,{'subject_id':'svc1','dimension_updates':[{'dimension':'budget','assessment':'good','measurement_refs':[]}],'outcome':'keep'},now='2026-10-01T04:00:00+00:00'))
    def test_research_next_preserves_explicit_gaps_and_does_not_force_ranking(self):
        r=self.feature(M,{'subject_id':'svc1','dimension_updates':[],'outcome':'research_next','gaps':['budget']},now='2026-10-01T04:00:00+00:00')
        self.assertEqual(r['outcome'],'research_next'); self.assertEqual(r['gaps'],['budget']); self.assertNotIn('attractiveness_score',r)
