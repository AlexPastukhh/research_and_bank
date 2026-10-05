import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class MonitoringRunAggregateTests(unittest.TestCase):
    def make_run(self):
        R=require_symbol("research_system.domain.monitoring", "DailyRun")
        return R.start(run_id="r1",started_at="2026-10-01T00:00:00Z",method_id="m",method_version="1",scope_fingerprint="s",source_route_ids=["b","a"])

    def test_run_freezes_comparability_identity_at_start(self):
        r=self.make_run(); assert_error_code(self,"run_context_immutable",lambda:r.change_scope("other")); assert_error_code(self,"run_context_immutable",lambda:r.change_method("m","2"))

    def test_observation_inherits_run_context(self):
        r=self.make_run(); o=r.record_observation(entity_id="e1",canonical_key="k",observation_class="seen",asserted_state="active",source_id="s1",semantic_payload={"x":1},observed_at="2026-10-01T00:01:00Z")
        self.assertEqual(o.run_id,"r1"); self.assertEqual(o.method_id,"m"); self.assertEqual(o.method_version,"1"); self.assertEqual(o.scope_fingerprint,"s"); self.assertEqual(list(o.source_route_ids),["a","b"])

    def test_exact_replay_is_idempotent(self):
        r=self.make_run(); kw=dict(entity_id="e1",canonical_key="k",observation_class="seen",asserted_state="active",source_id="s1",semantic_payload={"x":1},observed_at="2026-10-01T00:01:00Z")
        a=r.record_observation(**kw); b=r.record_observation(**kw)
        self.assertEqual(a.observation_id,b.observation_id); self.assertEqual(len(r.observations),1)

    def test_same_entity_from_different_source_is_distinct_evidence(self):
        r=self.make_run(); base=dict(entity_id="e1",canonical_key="k",observation_class="seen",asserted_state="active",semantic_payload={"x":1},observed_at="2026-10-01T00:01:00Z")
        a=r.record_observation(source_id="s1",**base); b=r.record_observation(source_id="s2",**base)
        self.assertNotEqual(a.observation_id,b.observation_id); self.assertEqual(len(r.observations),2)

    def test_query_absence_and_explicit_negative_remain_distinct(self):
        r=self.make_run(); a=r.record_observation(entity_id="e1",canonical_key="k",observation_class="query_absence",asserted_state="unknown",source_id="s1",semantic_payload={},observed_at="2026-10-01T00:01:00Z"); b=r.record_observation(entity_id="e2",canonical_key="k2",observation_class="explicit_negative",asserted_state="closed",source_id="s1",semantic_payload={},observed_at="2026-10-01T00:02:00Z")
        self.assertNotEqual(a.observation_class,b.observation_class)

    def test_finalize_sets_terminal_coverage_and_time(self):
        r=self.make_run(); r.finalize(coverage_status="complete",coverage_notes="",completed_at="2026-10-01T01:00:00Z")
        self.assertEqual(r.status,"completed"); self.assertEqual(r.coverage_status,"complete"); self.assertEqual(r.completed_at,"2026-10-01T01:00:00Z")

    def test_double_finalize_is_rejected(self):
        r=self.make_run(); r.finalize(coverage_status="complete",coverage_notes="",completed_at="2026-10-01T01:00:00Z")
        assert_error_code(self,"run_finalized",lambda:r.finalize(coverage_status="failed",coverage_notes="",completed_at="2026-10-01T02:00:00Z"))

    def test_observation_after_finalize_is_rejected(self):
        r=self.make_run(); r.finalize(coverage_status="complete",coverage_notes="",completed_at="2026-10-01T01:00:00Z")
        assert_error_code(self,"run_finalized",lambda:r.record_observation(entity_id="e1",canonical_key="k",observation_class="seen",asserted_state="active",source_id="s",semantic_payload={},observed_at="2026-10-01T02:00:00Z"))
