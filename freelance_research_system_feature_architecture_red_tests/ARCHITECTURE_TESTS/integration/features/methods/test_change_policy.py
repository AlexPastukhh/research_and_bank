from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
M='research_system.features.methods.change_policy'
class ChangeMethodOrPolicyFeatureTests(ProjectCase):
    def test_method_change_creates_new_version_preserves_old_and_reports_impact(self):
        a=self.feature(M,{'kind':'method','method_id':'m','from_version':None,'to_version':'1','definition':{'purpose':'p','comparability_dimensions':['scope']}},now='2026-10-01T04:00:00+00:00')
        b=self.feature(M,{'kind':'method','method_id':'m','from_version':'1','to_version':'2','definition':{'purpose':'p2','comparability_dimensions':['scope']}},now='2026-10-02T04:00:00+00:00')
        self.assertEqual(b['previous_version'],'1'); self.assertEqual(b['new_version'],'2'); self.assertTrue(b['previous_version_preserved']); self.assertIn('impact',b)

    def test_configurable_project_policy_change_does_not_require_system_release(self):
        r=self.feature(M,{'kind':'project_policy','changes':{'default_source_ttl_days':15}},now='2026-10-01T04:00:00+00:00')
        self.assertFalse(r['system_release_required']); self.assertEqual(r['policy']['default_source_ttl_days'],15)

    def test_hard_invariant_change_is_rejected_from_project_policy_feature(self):
        assert_error_code(self,'system_governance_required',lambda:self.feature(M,{'kind':'project_policy','changes':{'canonical_schema_version':'999'}},now='2026-10-01T04:00:00+00:00'))
