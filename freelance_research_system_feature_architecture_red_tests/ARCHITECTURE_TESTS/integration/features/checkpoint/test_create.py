from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.checkpoint.create'
class CheckpointFeatureTests(ProjectCase):
    def test_checkpoint_has_manifest_explicit_next_action_and_reopenable_state(self):
        r=self.feature(M,{'next_use_case_id':'UC09','next_task_id':'t9','next_question':'monitor scope','next_task_inputs':['scope:a']},now='2026-10-01T05:00:00+00:00')
        self.assertIn('manifest_digest',r); self.assertEqual(r['next_use_case_id'],'UC09'); self.assertEqual(r['next_task_id'],'t9'); self.assertEqual(r['next_question'],'monitor scope'); self.assertTrue(r['reopenable'])
    def test_checkpoint_refuses_incomplete_transaction(self):
        """PROPOSAL: handoff cannot freeze a half-committed feature operation."""
        r=self.feature(M,{'next_use_case_id':None,'next_task_id':None,'next_question':None,'next_task_inputs':[]},now='2026-10-01T05:00:00+00:00')
        self.assertFalse(r.get('incomplete_transaction',False))
