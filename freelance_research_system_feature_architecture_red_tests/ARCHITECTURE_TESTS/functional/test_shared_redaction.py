import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol

class RedactionHelperTests(unittest.TestCase):
    def redact(self,value): return require_symbol("research_system.shared.redaction","redact_secrets")(value)
    def test_nested_secret_keys_are_redacted(self): self.assertEqual(self.redact({"x":{"token":"abc"}}),{"x":{"token":"[REDACTED]"}})
    def test_secret_keys_are_case_insensitive(self): self.assertEqual(self.redact({"Authorization":"abc"}),{"Authorization":"[REDACTED]"})
    def test_lists_are_recursed(self): self.assertEqual(self.redact([{"api_key":"x"}]),[{"api_key":"[REDACTED]"}])
    def test_nonsecret_values_are_preserved(self): self.assertEqual(self.redact({"x":1,"name":"a"}),{"x":1,"name":"a"})
