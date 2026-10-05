import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class ExecutionSessionAggregateTests(unittest.TestCase):
    def session(self):
        S=require_symbol("research_system.domain.session", "ExecutionSession")
        return S.initialize(system_version="1.11.0")

    def test_only_one_task_can_be_active(self):
        s=self.session(); s.activate_task("UC03","t1")
        assert_error_code(self,"active_task_exists",lambda:s.activate_task("UC03","t2"))

    def test_finishing_wrong_task_cannot_clear_active_task(self):
        s=self.session(); s.activate_task("UC03","t1")
        assert_error_code(self,"active_task_mismatch",lambda:s.finish_task("t2"))
        self.assertEqual(s.active_task_id,"t1")

    def test_blocked_session_preserves_explicit_next_question(self):
        s=self.session(); s.block(next_question="Need source access")
        self.assertEqual(s.status,"blocked"); self.assertEqual(s.next_question,"Need source access")

    def test_checkpointed_session_retains_explicit_next_action(self):
        s=self.session(); s.set_next("UC09","t9",inputs=["scope:a"]); s.checkpoint()
        self.assertEqual(s.status,"checkpointed"); self.assertEqual(s.next_use_case_id,"UC09"); self.assertEqual(s.next_task_id,"t9")
