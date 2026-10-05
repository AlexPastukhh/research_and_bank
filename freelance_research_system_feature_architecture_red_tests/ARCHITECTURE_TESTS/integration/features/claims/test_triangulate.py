from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.claims.triangulate'
class TriangulateClaimFeatureTests(ProjectCase):
    def test_assessment_preserves_support_counterevidence_independence_and_limitations(self):
        r=self.feature(M,{'claim':{'claim_id':'c1','claim_text':'X','subject':'s','predicate':'p','scope':'scope','population':'pop','geography':'g','language':'en','timeframe':'2026'},'evidence':[{'evidence_id':'e1','stance':'supporting','independence':'independent','limitations':[]},{'evidence_id':'e2','stance':'contradicting','independence':'dependent','limitations':['old']}],'assessment':{'status':'disputed','confidence':'medium'}},now='2026-10-01T03:00:00+00:00')
        self.assertEqual({x['evidence_id'] for x in r['evidence']},{'e1','e2'}); self.assertEqual(r['status'],'disputed'); self.assertIn('old',str(r))
