import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class MethodCatalogTests(unittest.TestCase):
    def test_same_method_version_cannot_be_overwritten_with_different_definition(self):
        C=require_symbol("research_system.domain.methods", "MethodCatalog"); c=C.empty(); c.add(method_id="m",method_version="1",purpose="p",status="active",capability_requirements=[],comparability_dimensions=["scope"])
        assert_error_code(self,"method_version_immutable",lambda:c.add(method_id="m",method_version="1",purpose="different",status="active",capability_requirements=[],comparability_dimensions=["scope"]))

    def test_new_method_version_preserves_old_version(self):
        C=require_symbol("research_system.domain.methods", "MethodCatalog"); c=C.empty(); c.add(method_id="m",method_version="1",purpose="p",status="active",capability_requirements=[],comparability_dimensions=[]); c.add(method_id="m",method_version="2",purpose="p2",status="active",capability_requirements=[],comparability_dimensions=[])
        self.assertIsNotNone(c.get("m","1")); self.assertIsNotNone(c.get("m","2"))

class ProjectPolicyTests(unittest.TestCase):
    def policy(self):
        P=require_symbol("research_system.domain.project_policy", "ProjectPolicy")
        return P.default()
    def test_ttl_must_be_positive(self):
        p=self.policy(); assert_error_code(self,"invalid_policy",lambda:p.change(default_source_ttl_days=0))
    def test_unknown_project_policy_key_is_rejected(self):
        p=self.policy(); assert_error_code(self,"unknown_policy_key",lambda:p.change(pretend_setting=True))
