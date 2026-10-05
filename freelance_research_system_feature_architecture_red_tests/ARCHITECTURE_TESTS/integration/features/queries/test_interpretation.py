from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.queries.interpretation'
class InterpretationQueryTests(ProjectCase):
    def test_interpretation_is_read_only_and_links_existing_results_without_collecting_evidence(self):
        before=self.digest(); r=self.feature(M,{'scope':'all','period':['2026-10-01','2026-10-07'],'result_refs':['result:1'],'statement':'Existing results suggest X','confidence':'low','limitations':['limited evidence']},now='2026-10-08T08:00:00+00:00'); self.assertEqual(self.digest(),before)
        for k in ['interpretation_id','created_at','scope','period','statement','result_refs','confidence','limitations']: self.assertIn(k,r)
        self.assertFalse(r.get('evidence_collected',False))
