from ARCHITECTURE_TESTS.support.integration import ProjectCase
M_OBS='research_system.features.work.observe_paid_work'; M='research_system.features.work.normalize'
class NormalizeWorkFeatureTests(ProjectCase):
    def raw(self,text,ref): return self.feature(M_OBS,{'source_id':'s1','source_record_ref':ref,'raw_text':text,'captured_fields':{}},now='2026-10-01T01:00:00+00:00')['raw_observation_id']
    def test_normalization_classifies_service_unit_and_facets_without_mutating_raw(self):
        rid=self.raw('Build a dashboard','record:1'); r=self.feature(M,{'raw_observation_ids':[rid],'classification':{rid:{'service_unit_id':'dashboard','facets':['analytics']}}},now='2026-10-01T02:00:00+00:00')
        self.assertEqual(r['items'][0]['service_unit_id'],'dashboard'); self.assertIn('analytics',r['items'][0]['facets']); self.assertEqual(r['items'][0]['raw_observation_id'],rid)
    def test_duplicate_raw_observations_can_collapse_to_one_normalized_unit_with_provenance(self):
        a=self.raw('Build a dashboard','record:1'); b=self.raw('Build a dashboard','record:2'); r=self.feature(M,{'raw_observation_ids':[a,b],'deduplication_groups':[[a,b]],'classification':{a:{'service_unit_id':'dashboard','facets':[]},b:{'service_unit_id':'dashboard','facets':[]}}},now='2026-10-01T02:00:00+00:00')
        self.assertEqual(len(r['items']),1); self.assertEqual(set(r['items'][0]['raw_observation_ids']),{a,b})
