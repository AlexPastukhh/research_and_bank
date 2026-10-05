from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.sources.discover'
class DiscoverSourcesFeatureTests(ProjectCase):
    def test_discovery_returns_candidate_without_claiming_effectiveness(self):
        r=self.feature(M,{'canonical_name':'Example Market','discovery_route_ids':['search'],'discovered_via_source_ids':[]},now='2026-10-01T01:00:00+00:00')
        self.assertEqual(r['stage'],'inbox'); self.assertNotIn('effective',r); self.assertNotIn('verified_effectiveness',r)
    def test_repeat_discovery_is_deduplicated(self):
        a=self.feature(M,{'canonical_name':'Example Market','discovery_route_ids':['search'],'discovered_via_source_ids':[]},now='2026-10-01T01:00:00+00:00')
        b=self.feature(M,{'canonical_name':' example market ','discovery_route_ids':['search'],'discovered_via_source_ids':[]},now='2026-10-01T01:01:00+00:00')
        self.assertEqual(a['source_id'],b['source_id']); self.assertTrue(b['deduplicated'])
