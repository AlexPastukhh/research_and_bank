from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.work.observe_paid_work'
class ObservePaidWorkFeatureTests(ProjectCase):
    def test_creates_raw_observation_with_stable_source_provenance(self):
        r=self.feature(M,{'source_id':'s1','source_record_ref':'record:1','raw_text':'Build a dashboard','captured_fields':{'payout':100}},now='2026-10-01T01:00:00+00:00')
        self.assertEqual(r['stage'],'raw'); self.assertEqual(r['source_id'],'s1'); self.assertEqual(r['source_record_ref'],'record:1'); self.assertIn('raw_observation_id',r)
    def test_raw_observation_does_not_claim_normalized_classification_or_measurement(self):
        r=self.feature(M,{'source_id':'s1','source_record_ref':'record:1','raw_text':'Build a dashboard','captured_fields':{}},now='2026-10-01T01:00:00+00:00')
        self.assertNotIn('service_unit_id',r); self.assertNotIn('measurement_id',r)
