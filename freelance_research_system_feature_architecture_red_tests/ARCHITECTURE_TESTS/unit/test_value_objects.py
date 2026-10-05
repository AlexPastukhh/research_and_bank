import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class ValueObjectContractTests(unittest.TestCase):
    def test_method_identity_requires_nonempty_id_and_version(self):
        """BASELINE: method id/version are mandatory provenance/comparability identity."""
        MethodIdentity=require_symbol("research_system.domain.value_objects", "MethodIdentity")
        assert_error_code(self,"invalid_method_identity",lambda: MethodIdentity("", "1"))
        assert_error_code(self,"invalid_method_identity",lambda: MethodIdentity("m", ""))

    def test_source_route_is_order_insensitive_and_deduplicated(self):
        """BASELINE: daily-run source-route set, not lexical ordering, participates in comparability."""
        SourceRoute=require_symbol("research_system.domain.value_objects", "SourceRoute")
        self.assertEqual(SourceRoute(["b","a","b"]), SourceRoute(["a","b"]))

    def test_complete_comparison_contexts_are_comparable_when_identity_matches(self):
        """BASELINE UC09: method/version/scope/source-routes + complete coverage define comparable runs."""
        C=require_symbol("research_system.domain.value_objects", "ComparisonContext")
        a=C(method_id="m",method_version="1",scope_fingerprint="s",source_route_ids=["a","b"],coverage_status="complete")
        b=C(method_id="m",method_version="1",scope_fingerprint="s",source_route_ids=["b","a"],coverage_status="complete")
        self.assertTrue(a.is_comparable_to(b))

    def test_method_version_change_breaks_comparability(self):
        C=require_symbol("research_system.domain.value_objects", "ComparisonContext")
        a=C("m","1","s",["a"],"complete"); b=C("m","2","s",["a"],"complete")
        self.assertFalse(a.is_comparable_to(b))

    def test_scope_change_breaks_comparability(self):
        C=require_symbol("research_system.domain.value_objects", "ComparisonContext")
        self.assertFalse(C("m","1","s1",["a"],"complete").is_comparable_to(C("m","1","s2",["a"],"complete")))

    def test_source_route_change_breaks_comparability(self):
        C=require_symbol("research_system.domain.value_objects", "ComparisonContext")
        self.assertFalse(C("m","1","s",["a"],"complete").is_comparable_to(C("m","1","s",["b"],"complete")))

    def test_partial_or_failed_coverage_breaks_comparability(self):
        C=require_symbol("research_system.domain.value_objects", "ComparisonContext")
        good=C("m","1","s",["a"],"complete")
        self.assertFalse(good.is_comparable_to(C("m","1","s",["a"],"partial")))
        self.assertFalse(good.is_comparable_to(C("m","1","s",["a"],"failed")))

    def test_time_window_rejects_reverse_range(self):
        """PROPOSAL: all parameterized query ranges share one validated value object."""
        W=require_symbol("research_system.domain.value_objects", "TimeWindow")
        assert_error_code(self,"invalid_time_window",lambda: W("2026-10-03","2026-10-01"))
