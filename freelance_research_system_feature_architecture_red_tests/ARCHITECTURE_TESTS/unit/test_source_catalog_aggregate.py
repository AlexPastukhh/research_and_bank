import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class SourceCatalogAggregateTests(unittest.TestCase):
    def catalog(self):
        C=require_symbol("research_system.domain.sources", "SourceCatalog")
        return C.empty()

    def test_discovery_candidate_is_deduplicated_by_canonical_identity(self):
        c=self.catalog(); a=c.discover(canonical_name="Example Market", discovered_via_source_ids=[], discovery_route_ids=["search"]); b=c.discover(canonical_name=" example market ", discovered_via_source_ids=[], discovery_route_ids=["search"])
        self.assertEqual(a.source_id,b.source_id); self.assertEqual(len(c.sources),1)

    def test_promotion_preserves_discovery_provenance(self):
        c=self.catalog(); s=c.discover(canonical_name="X",discovered_via_source_ids=["seed"],discovery_route_ids=["route1"]); c.promote(s.source_id,role="evidence",priority="P1")
        promoted=c.get(s.source_id); self.assertIn("seed",promoted.discovered_via_source_ids); self.assertIn("route1",promoted.discovery_route_ids)

    def test_general_priority_can_change_without_changing_role(self):
        c=self.catalog(); s=c.discover(canonical_name="X",discovered_via_source_ids=[],discovery_route_ids=[]); c.promote(s.source_id,role="discovery",priority="P3"); c.set_priority(s.source_id,"P1")
        self.assertEqual(c.get(s.source_id).source_role,"discovery")

    def test_review_history_is_append_only(self):
        c=self.catalog(); s=c.discover(canonical_name="X",discovered_via_source_ids=[],discovery_route_ids=[]); c.review(s.source_id,status="watch",note="first",at="2026-10-01T00:00:00Z"); c.review(s.source_id,status="active",note="second",at="2026-10-02T00:00:00Z")
        self.assertEqual([x.note for x in c.get(s.source_id).review_history],["first","second"])

    def test_retirement_does_not_delete_source_or_history(self):
        c=self.catalog(); s=c.discover(canonical_name="X",discovered_via_source_ids=[],discovery_route_ids=[]); c.promote(s.source_id,role="archive",priority="P4"); c.retire(s.source_id,at="2026-10-02T00:00:00Z")
        self.assertEqual(c.get(s.source_id).current_status,"retired"); self.assertEqual(len(c.sources),1)

    def test_task_specific_requirement_does_not_mutate_general_priority(self):
        c=self.catalog(); s=c.discover(canonical_name="X",discovered_via_source_ids=[],discovery_route_ids=[]); c.promote(s.source_id,role="both",priority="P2"); c.set_use_plan("plan1",s.source_id,role="evidence",requirement_level="required")
        self.assertEqual(c.get(s.source_id).current_priority,"P2")
