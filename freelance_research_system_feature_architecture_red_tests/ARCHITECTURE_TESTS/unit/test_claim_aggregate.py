import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class ClaimAggregateTests(unittest.TestCase):
    def claim(self):
        C=require_symbol("research_system.domain.claims", "Claim")
        return C.create(claim_id="c1",claim_text="X is true",subject="X",predicate="is true",scope="s",population="p",geography="g",language="en",timeframe="2026")

    def test_supporting_and_counterevidence_are_both_preserved(self):
        c=self.claim(); c.add_evidence(evidence_id="a",stance="supporting",independence="independent",limitations=[]); c.add_evidence(evidence_id="b",stance="contradicting",independence="independent",limitations=["small sample"])
        self.assertEqual({x.evidence_id for x in c.evidence},{"a","b"})

    def test_reassessment_must_not_delete_counterevidence(self):
        c=self.claim(); c.add_evidence(evidence_id="b",stance="contradicting",independence="independent",limitations=[]); c.assess(status="partially_confirmed",confidence="medium",at="2026-10-01T00:00:00Z")
        self.assertEqual(c.evidence[0].evidence_id,"b")

    def test_duplicate_evidence_identity_is_idempotent_not_duplicated(self):
        c=self.claim(); c.add_evidence(evidence_id="a",stance="supporting",independence="independent",limitations=[]); c.add_evidence(evidence_id="a",stance="supporting",independence="independent",limitations=[])
        self.assertEqual(len(c.evidence),1)

    def test_conflicting_duplicate_evidence_is_rejected(self):
        c=self.claim(); c.add_evidence(evidence_id="a",stance="supporting",independence="independent",limitations=[])
        assert_error_code(self,"evidence_identity_conflict",lambda:c.add_evidence(evidence_id="a",stance="contradicting",independence="independent",limitations=[]))
