import ast, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'src'/'research_system'
REGISTRY=ROOT/'CORE'/'USE_CASE_REGISTRY.json'

FEATURES_BY_UC={
 'UC01':['features/project/start.py'],
 'UC02':['features/project/continue_baseline.py'],
 'UC03':['features/tasks/execute.py'],
 'UC04':['features/sources/discover.py'],
 'UC05':['features/sources/verify.py'],
 'UC06':['features/work/observe_paid_work.py'],
 'UC07':['features/work/normalize.py'],
 'UC08':['features/measurement/measure.py'],
 'UC09':['features/monitoring/start_run.py','features/monitoring/record_observation.py','features/monitoring/finish_run.py','features/monitoring/build_daily_diff.py'],
 'UC10':['features/novelty/rediscover.py'],
 'UC11':['features/claims/triangulate.py'],
 'UC12':['features/delivery/run_practical_test.py'],
 'UC13':['features/acquisition/run_market_test.py'],
 'UC14':['features/decisions/update.py'],
 'UC15':['features/sources/manage.py'],
 'UC16':['features/methods/change_policy.py'],
 'UC17':['features/checkpoint/create.py'],
 'UC18':['features/repair/reconcile.py'],
 'UC19':['features/governance/audit_modify.py'],
 'UC20':['features/migration/migrate_project.py'],
 'UC21':['features/queries/current_state.py'],
 'UC22':['features/queries/changes.py'],
 'UC23':['features/queries/trend.py'],
 'UC24':['features/queries/interpretation.py'],
 'UC25':['features/queries/research_health.py'],
}

# Architectural ownership contract. A feature may use these shared aggregate/VO modules;
# importing a different aggregate is a signal that responsibility drifted and the red plan must be revisited explicitly.
ALLOWED_DOMAIN_BY_FEATURE={
 'features/project/start.py':{'research_system.domain.session','research_system.domain.project_policy','research_system.domain.value_objects'},
 'features/project/continue_baseline.py':{'research_system.domain.session','research_system.domain.value_objects'},
 'features/tasks/execute.py':{'research_system.domain.tasks','research_system.domain.session','research_system.domain.value_objects'},
 'features/sources/discover.py':{'research_system.domain.sources','research_system.domain.value_objects'},
 'features/sources/verify.py':{'research_system.domain.sources','research_system.domain.value_objects'},
 'features/sources/manage.py':{'research_system.domain.sources','research_system.domain.value_objects'},
 'features/work/observe_paid_work.py':{'research_system.domain.value_objects'},
 'features/work/normalize.py':{'research_system.domain.value_objects'},
 'features/measurement/measure.py':{'research_system.domain.opportunities','research_system.domain.value_objects'},
 'features/monitoring/start_run.py':{'research_system.domain.monitoring','research_system.domain.value_objects'},
 'features/monitoring/record_observation.py':{'research_system.domain.monitoring','research_system.domain.value_objects'},
 'features/monitoring/finish_run.py':{'research_system.domain.monitoring','research_system.domain.value_objects'},
 'features/monitoring/build_daily_diff.py':{'research_system.domain.monitoring','research_system.domain.value_objects'},
 'features/novelty/rediscover.py':{'research_system.domain.sources','research_system.domain.value_objects'},
 'features/claims/triangulate.py':{'research_system.domain.claims','research_system.domain.value_objects'},
 'features/delivery/run_practical_test.py':{'research_system.domain.opportunities','research_system.domain.value_objects'},
 'features/acquisition/run_market_test.py':{'research_system.domain.opportunities','research_system.domain.value_objects'},
 'features/decisions/update.py':{'research_system.domain.decisions','research_system.domain.value_objects'},
 'features/methods/change_policy.py':{'research_system.domain.methods','research_system.domain.project_policy','research_system.domain.value_objects'},
 'features/checkpoint/create.py':{'research_system.domain.session','research_system.domain.value_objects'},
 'features/repair/reconcile.py':{'research_system.domain.session','research_system.domain.monitoring','research_system.domain.sources','research_system.domain.methods','research_system.domain.claims','research_system.domain.opportunities','research_system.domain.decisions','research_system.domain.tasks','research_system.domain.project_policy','research_system.domain.value_objects'},
 'features/governance/audit_modify.py':{'research_system.domain.value_objects'},
 'features/migration/migrate_project.py':{'research_system.domain.session','research_system.domain.monitoring','research_system.domain.sources','research_system.domain.methods','research_system.domain.claims','research_system.domain.opportunities','research_system.domain.decisions','research_system.domain.tasks','research_system.domain.project_policy','research_system.domain.value_objects'},
 'features/queries/current_state.py':{'research_system.domain.value_objects'},
 'features/queries/changes.py':{'research_system.domain.value_objects'},
 'features/queries/trend.py':{'research_system.domain.value_objects'},
 'features/queries/interpretation.py':{'research_system.domain.value_objects'},
 'features/queries/research_health.py':{'research_system.domain.value_objects'},
}

def module_imports(path:Path):
    tree=ast.parse(path.read_text(encoding='utf-8')); out=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): out.update(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module: out.add(n.module)
    return out

class FeatureAggregateOwnershipTests(unittest.TestCase):
    def test_all_accepted_use_cases_are_assigned_to_end_to_end_feature_slices(self):
        registry=json.loads(REGISTRY.read_text(encoding='utf-8')); actual={x['id'] for x in registry['use_cases']}
        self.assertEqual(set(FEATURES_BY_UC),actual)

    def test_feature_slices_import_only_the_aggregates_they_are_allowed_to_coordinate(self):
        self.assertTrue(PKG.exists(),'ARCHITECTURE RED: implementation package not created yet')
        violations=[]
        for rel,allowed in ALLOWED_DOMAIN_BY_FEATURE.items():
            p=PKG/rel
            if not p.exists(): continue  # existence is enforced by test_module_boundaries
            for imp in module_imports(p):
                if imp.startswith('research_system.domain.') and imp not in allowed:
                    violations.append((rel,imp,sorted(allowed)))
        self.assertEqual(violations,[],f'aggregate ownership drift: {violations}')
