import unittest
from ARCHITECTURE_TESTS.support.future import require_symbol, assert_error_code

class TaskAggregateContractTests(unittest.TestCase):
    def make_task(self):
        Task=require_symbol("research_system.domain.tasks", "Task")
        return Task.create(task_id="t1",task_instance_key="i1",use_case_id="UC03",atomic_question="q",acceptance_test_ids=["a","b"],allowed_actions=["read","write"],forbidden_actions=["network"])

    def test_task_must_start_before_completion(self):
        t=self.make_task(); assert_error_code(self,"invalid_task_transition",lambda:t.complete())

    def test_task_cannot_be_done_while_acceptance_is_pending(self):
        t=self.make_task(); t.start(); t.set_acceptance("a","pass")
        assert_error_code(self,"acceptance_incomplete",lambda:t.complete())

    def test_failed_acceptance_blocks_done(self):
        t=self.make_task(); t.start(); t.set_acceptance("a","pass"); t.set_acceptance("b","fail")
        assert_error_code(self,"acceptance_failed",lambda:t.complete())

    def test_pass_or_not_applicable_acceptance_allows_done(self):
        t=self.make_task(); t.start(); t.set_acceptance("a","pass"); t.set_acceptance("b","not_applicable"); t.complete()
        self.assertEqual(t.status,"done")

    def test_completed_task_is_immutable(self):
        t=self.make_task(); t.start(); t.set_acceptance("a","pass"); t.set_acceptance("b","pass"); t.complete()
        assert_error_code(self,"task_finalized",lambda:t.set_acceptance("a","fail"))

    def test_forbidden_action_is_rejected_even_if_feature_attempts_it(self):
        t=self.make_task(); t.start(); assert_error_code(self,"action_forbidden",lambda:t.authorize_action("network"))
