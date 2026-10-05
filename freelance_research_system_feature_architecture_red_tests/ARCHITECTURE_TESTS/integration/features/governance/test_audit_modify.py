from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
M='research_system.features.governance.audit_modify'
class GovernanceFeatureTests(ProjectCase):
    def test_hard_contract_change_requires_version_migration_tests_and_audit_evidence(self):
        assert_error_code(self,'governance_evidence_incomplete',lambda:self.feature(M,{'change_kind':'canonical_schema','changes':{'x':'y'},'new_system_version':None,'migration_plan':None,'regression_tests':[],'audit_evidence':[]},now='2026-10-01T06:00:00+00:00'))
    def test_audit_only_operation_does_not_mutate_research_truth(self):
        before=self.digest(); r=self.feature(M,{'change_kind':'audit_only','audit_axes':['AX10','AX13']},now='2026-10-01T06:00:00+00:00'); self.assertEqual(self.digest(),before); self.assertIn('audit_findings',r)
