from ARCHITECTURE_TESTS.support.integration import ProjectCase
M_DISC='research_system.features.sources.discover'; M='research_system.features.novelty.rediscover'
class RediscoverNoveltyFeatureTests(ProjectCase):
    def test_only_candidates_not_represented_in_baseline_are_reported_as_novel(self):
        known=self.feature(M_DISC,{'canonical_name':'Known','discovery_route_ids':['seed'],'discovered_via_source_ids':[]},now='2026-10-01T01:00:00+00:00')['source_id']
        r=self.feature(M,{'candidates':[{'canonical_name':'Known'},{'canonical_name':'New'}]},now='2026-10-02T01:00:00+00:00')
        names={x['canonical_name'] for x in r['novelty_candidates']}; self.assertNotIn('Known',names); self.assertIn('New',names)
