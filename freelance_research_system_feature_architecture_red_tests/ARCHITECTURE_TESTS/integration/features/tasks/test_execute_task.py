from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code

M='research_system.features.tasks.execute'
class ExecuteTaskFeatureTests(ProjectCase):
    def test_executes_exact_selected_task_and_marks_done_only_after_passed_acceptance(self):
        req={'task_id':'t1','task_instance_key':'i1','use_case_id':'UC03','atomic_question':'q','acceptance_tests':['a'],'actions':['write'],'outputs':{'x':1}}
        r=self.feature(M,req,now='2026-10-01T01:00:00+00:00',acceptance_results={'a':'pass'})
        self.assertEqual(r['task_id'],'t1'); self.assertEqual(r['status'],'done'); self.assertEqual(r['outputs'],{'x':1})

    def test_failed_acceptance_keeps_task_non_done_and_does_not_advance_next_task(self):
        req={'task_id':'t1','task_instance_key':'i1','use_case_id':'UC03','atomic_question':'q','acceptance_tests':['a'],'actions':['write'],'outputs':{}}
        r=self.feature(M,req,now='2026-10-01T01:00:00+00:00',acceptance_results={'a':'fail'})
        self.assertNotEqual(r['status'],'done'); self.assertFalse(r.get('next_task_advanced',False))

    def test_forbidden_action_is_rejected(self):
        req={'task_id':'t1','task_instance_key':'i1','use_case_id':'UC03','atomic_question':'q','acceptance_tests':['a'],'actions':['network'],'forbidden_actions':['network'],'outputs':{}}
        assert_error_code(self,'action_forbidden',lambda:self.feature(M,req,now='2026-10-01T01:00:00+00:00',acceptance_results={'a':'pass'}))
