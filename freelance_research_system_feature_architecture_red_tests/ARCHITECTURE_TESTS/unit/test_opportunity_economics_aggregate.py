import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class OpportunityEconomicsAggregateTests(unittest.TestCase):
    def econ(self):
        E=require_symbol("research_system.domain.opportunities", "OpportunityEconomics")
        return E.create(economics_id="econ1",service_unit_id="svc1")

    def test_preserves_cheap_and_expensive_payout_observations(self):
        e=self.econ(); e.record_payout(5,source="obs1"); e.record_payout(100,source="obs2")
        self.assertEqual([x.amount for x in e.payout_observations],[5,100])

    def test_effective_rate_not_available_without_required_inputs(self):
        e=self.econ(); e.record_payout(100,source="obs1")
        self.assertIsNone(e.effective_rate())

    def test_effective_rate_can_use_observed_effort(self):
        e=self.econ(); e.record_payout(100,source="obs1"); e.record_effort(execution_minutes=60,setup_minutes=0,revision_minutes=0,communication_minutes=0,acquisition_minutes=0,source="obs2",basis="observed"); e.record_costs(platform=0,tool=0,direct=0,source="obs3")
        self.assertEqual(e.effective_rate(),100)

    def test_practical_test_estimate_must_remain_marked_as_estimate(self):
        e=self.econ(); e.record_effort(execution_minutes=60,setup_minutes=10,revision_minutes=0,communication_minutes=0,acquisition_minutes=0,source="ptest1",basis="practical_test_estimate")
        self.assertEqual(e.effort_basis,"practical_test_estimate")

    def test_negative_effort_is_rejected(self):
        e=self.econ(); assert_error_code(self,"invalid_effort",lambda:e.record_effort(execution_minutes=-1,setup_minutes=0,revision_minutes=0,communication_minutes=0,acquisition_minutes=0,source="x",basis="observed"))
