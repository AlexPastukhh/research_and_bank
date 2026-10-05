import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class DecisionAggregateTests(unittest.TestCase):
    def decision(self):
        D=require_symbol("research_system.domain.decisions", "DecisionRecord")
        return D.create(decision_id="d1",subject_id="svc1")

    def test_dimension_can_be_used_only_with_measurement_evidence(self):
        d=self.decision(); assert_error_code(self,"dimension_unmeasured",lambda:d.evaluate_dimension("competition","favorable",measurement_refs=[]))

    def test_decision_can_be_research_next_with_explicit_gaps(self):
        d=self.decision(); d.set_outcome("research_next",gaps=["budget"]); self.assertEqual(d.outcome,"research_next"); self.assertEqual(d.gaps,["budget"])

    def test_master_attractiveness_score_is_not_supported(self):
        d=self.decision(); assert_error_code(self,"master_score_forbidden",lambda:d.set_master_score(0.9))
