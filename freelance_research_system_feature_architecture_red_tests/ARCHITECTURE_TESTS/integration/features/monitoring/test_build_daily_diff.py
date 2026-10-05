from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.scenarios import completed_run
M='research_system.features.monitoring.build_daily_diff'
class BuildDailyDiffFeatureTests(ProjectCase):
    def test_gap_safe_reopen_is_reopened_not_new(self):
        completed_run(self.root,'r1','2026-10-01',observations=[{'entity_id':'e1','observation_class':'explicit_negative','asserted_state':'closed'}])
        completed_run(self.root,'r2','2026-10-02',observations=[])
        completed_run(self.root,'r3','2026-10-03',observations=[{'entity_id':'e1','observation_class':'seen','asserted_state':'active'}])
        r=self.feature(M,{'previous_run_id':'r2','current_run_id':'r3'},now='2026-10-03T02:00:00+00:00')
        self.assertIn('e1',r['reopened_ids']); self.assertNotIn('e1',r['new_entity_ids'])

    def test_query_absence_is_not_confirmed_closed(self):
        completed_run(self.root,'r1','2026-10-01',observations=[{'entity_id':'e1','observation_class':'seen'}])
        completed_run(self.root,'r2','2026-10-02',observations=[{'entity_id':'e1','observation_class':'query_absence','asserted_state':'unknown'}])
        r=self.feature(M,{'previous_run_id':'r1','current_run_id':'r2'},now='2026-10-02T02:00:00+00:00')
        self.assertNotIn('e1',r['confirmed_closed_ids'])

    def test_source_route_mismatch_returns_not_comparable_without_change_claims(self):
        completed_run(self.root,'r1','2026-10-01',routes=('a',),observations=[{'entity_id':'e1'}]); completed_run(self.root,'r2','2026-10-02',routes=('b',),observations=[{'entity_id':'e1'}])
        r=self.feature(M,{'previous_run_id':'r1','current_run_id':'r2'},now='2026-10-02T02:00:00+00:00')
        self.assertEqual(r['comparison_status'],'not_comparable'); self.assertEqual(r['new_entity_ids'],[]); self.assertEqual(r['changed_entity_ids'],[]); self.assertEqual(r['confirmed_closed_ids'],[]); self.assertEqual(r['reopened_ids'],[])

    def test_daily_diff_has_stable_identity_for_run_pair_and_is_persisted_as_domain_result(self):
        """PROPOSAL: preserve historical result identity while engine receipt owns provenance."""
        completed_run(self.root,'r1','2026-10-01'); completed_run(self.root,'r2','2026-10-02')
        a=self.feature(M,{'previous_run_id':'r1','current_run_id':'r2'},now='2026-10-02T02:00:00+00:00'); b=self.feature(M,{'previous_run_id':'r1','current_run_id':'r2'},now='2026-10-02T02:01:00+00:00')
        self.assertEqual(a['diff_id'],b['diff_id']); self.assertTrue(b['replay']); self.assertTrue(a['persisted_domain_result']); self.assertIn('engine_receipt_id',a)

    def test_future_run_does_not_make_fixed_historical_diff_stale(self):
        """PROPOSAL fixing pilot false-positive invalidation."""
        completed_run(self.root,'r1','2026-10-01'); completed_run(self.root,'r2','2026-10-02'); a=self.feature(M,{'previous_run_id':'r1','current_run_id':'r2'},now='2026-10-02T02:00:00+00:00')
        completed_run(self.root,'r3','2026-10-03')
        check=self.feature('research_system.features.queries.research_health',{'result_ref':a['result_ref']},now='2026-10-03T02:00:00+00:00')
        self.assertNotIn(a['result_ref'],check.get('stale_result_refs',[]))

    def test_backfilled_prior_run_does_invalidate_historical_diff_when_history_semantics_can_change(self):
        """PROPOSAL: dependency slice is historical prefix, not all future membership."""
        completed_run(self.root,'r1','2026-10-01'); completed_run(self.root,'r3','2026-10-03',observations=[{'entity_id':'e1'}]); a=self.feature(M,{'previous_run_id':'r1','current_run_id':'r3'},now='2026-10-03T02:00:00+00:00')
        completed_run(self.root,'r2','2026-10-02',observations=[{'entity_id':'e1','observation_class':'explicit_negative','asserted_state':'closed'}])
        check=self.feature('research_system.features.queries.research_health',{'result_ref':a['result_ref']},now='2026-10-03T03:00:00+00:00')
        self.assertIn(a['result_ref'],check.get('stale_result_refs',[]))
