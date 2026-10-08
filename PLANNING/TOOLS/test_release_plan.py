"""Regression checks for version-plan integrity; no release acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('release_plan', ROOT / 'release_plan.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PLANNING = ROOT.parent
if (PLANNING / 'REQUIREMENTS_RELEASE_MAP.json').exists():
    PLAN_PATH = PLANNING / 'REQUIREMENTS_RELEASE_MAP.json'
    SOURCE_PATH = PLANNING.parent / 'DRAFT_NOTES' / 'REQUIREMENTS_MAP.json'
    ROADMAP_PATH = PLANNING / 'VERSION_ROADMAP.md'
else:
    PLAN_PATH = ROOT / 'release_map.json'
    SOURCE_PATH = ROOT / 'requirements.json'
    ROADMAP_PATH = ROOT / 'VERSION_ROADMAP.md'

def entry(plan, identifier):
    return next(e for e in plan['requirements'] if e['requirement_id'] == identifier)

class ReleasePlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(PLAN_PATH.read_text(encoding='utf-8'))
        source = json.loads(SOURCE_PATH.read_text(encoding='utf-8'))
        self.source = source['requirements']

    def test_current_plan_and_generated_document(self):
        MODULE.validate(self.plan, self.source)
        self.assertEqual(MODULE.render(self.plan), ROADMAP_PATH.read_text(encoding='utf-8'))

    def test_rejects_regressions(self):
        def late_mvp(p):
            s = entry(p, 'MVP-004')['slices'][0]
            m = next(m for m in p['milestones'] if m['id'] == 'R4')
            s.update(milestone='R4', system_version=m['system_version'], application_version=m['application_version'])

        cases = {
            'checkpoint_moved_to_R8': lambda p: p['mvp_checkpoint'].update(milestone='R8'),
            'MVP_system_version': lambda p: p['mvp_checkpoint'].update(system_version='9.9.9'),
            'stable_app_version': lambda p: p['stable_mvp_checkpoint'].update(application_version='9.9.9'),
            'duplicate_MVP_ids': lambda p: p['mvp_checkpoint']['required_ids'].append('MVP-001'),
            'unknown_sequence': lambda p: p['milestones'][1].update(sequencing_after='NO_SUCH_RELEASE'),
            'self_sequence': lambda p: p['milestones'][1].update(sequencing_after='R1'),
            'sequence_cycle': lambda p: p['milestones'][0].update(sequencing_after='R1'),
            'unknown_dependency': lambda p: p['milestones'][1].update(dependencies=['NO_SUCH_RELEASE']),
            'empty_system_scope': lambda p: entry(p, 'MVP-004')['slices'][0].update(system_scope='  '),
            'empty_app_scope': lambda p: entry(p, 'MVP-004')['slices'][0].update(application_scope=''),
            'unowned_system_scope': lambda p: entry(p, 'MVP-003')['slices'][0].update(system_scope='Unexpected system work'),
            'slice_version_drift': lambda p: entry(p, 'MVP-004')['slices'][0].update(application_version='9.9.9'),
            'MVP_delivery_after_checkpoint': late_mvp,
            'source_snapshot_drift': lambda p: entry(p, 'MVP-004').update(statement_snapshot='Changed obligation'),
            'source_count_drift': lambda p: p.update(source_requirement_count=p['source_requirement_count'] + 1),
            'unknown_decision_checkpoint': lambda p: entry(p, 'OPEN-018')['decision_checkpoints'][0].update(before='NO_SUCH_RELEASE'),
            'decision_first_deadline_drift': lambda p: entry(p, 'OPEN-018').update(decision_before_milestone='R6'),
            'empty_decision_scope': lambda p: entry(p, 'OPEN-018')['decision_checkpoints'][0].update(scope=''),
            'unordered_decision_checkpoints': lambda p: entry(p, 'OPEN-018')['decision_checkpoints'].reverse(),
            'early_relation_gate_postponed': lambda p: entry(p, 'OPEN-005').update(decision_before_milestone='R4', decision_checkpoints=entry(p, 'OPEN-005')['decision_checkpoints'][1:]),
            'temporal_expectation_gate_removed': lambda p: entry(p, 'OPEN-006').update(decision_before_milestone=None, decision_checkpoints=[]),
        }
        for label, change in cases.items():
            with self.subTest(regression=label):
                candidate = copy.deepcopy(self.plan)
                change(candidate)
                with self.assertRaises(ValueError):
                    MODULE.validate(candidate, self.source)

    def test_future_inventory_growth_has_no_fixed_115_limit(self):
        source = copy.deepcopy(self.source)
        added = copy.deepcopy(next(r for r in source if r['id'] == 'OPP-018'))
        added.update(id='OPP-TEST', statement='A future classified opportunity')
        source.append(added)
        candidate = copy.deepcopy(self.plan)
        planned = copy.deepcopy(entry(candidate, 'OPP-018'))
        planned.update(requirement_id=added['id'], statement_snapshot=added['statement'])
        candidate['requirements'].append(planned)
        candidate['source_requirement_count'] = len(source)
        counts = MODULE.validate(candidate, source)
        baseline_counts = MODULE.validate(self.plan, self.source)
        self.assertEqual(counts['opportunity_unassigned'], baseline_counts['opportunity_unassigned'] + 1)
        self.assertIn('**' + str(len(source)) + ' текущих ID**', MODULE.render(candidate))

if __name__ == '__main__':
    unittest.main(verbosity=2)
