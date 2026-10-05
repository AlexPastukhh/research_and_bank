from ARCHITECTURE_TESTS.support.integration import ProjectCase
M_DISC='research_system.features.sources.discover'; M='research_system.features.sources.verify'
class VerifySourceFeatureTests(ProjectCase):
    def source(self): return self.feature(M_DISC,{'canonical_name':'Market','discovery_route_ids':['search'],'discovered_via_source_ids':['seed']},now='2026-10-01T01:00:00+00:00')['source_id']
    def test_verification_is_dated_and_preserves_limitations(self):
        sid=self.source(); r=self.feature(M,{'source_id':sid,'mechanics':{'fee_percent':10},'eligibility':['adult'],'limitations':['country limited']},now='2026-10-02T01:00:00+00:00')
        self.assertEqual(r['source_id'],sid); self.assertEqual(r['verified_at'],'2026-10-02T01:00:00+00:00'); self.assertIn('country limited',r['limitations'])
    def test_verification_preserves_discovery_provenance(self):
        sid=self.source(); r=self.feature(M,{'source_id':sid,'mechanics':{},'eligibility':[],'limitations':[]},now='2026-10-02T01:00:00+00:00')
        self.assertIn('seed',r['source']['discovered_via_source_ids'])
