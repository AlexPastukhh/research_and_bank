import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'src'/'research_system'
EXPECTED_AGGREGATE_MODULES={
    'domain/tasks.py','domain/session.py','domain/sources.py','domain/monitoring.py','domain/methods.py','domain/project_policy.py','domain/claims.py','domain/opportunities.py','domain/decisions.py','domain/value_objects.py'
}
EXPECTED_FEATURE_MODULES={
    'features/project/start.py','features/project/continue_baseline.py','features/tasks/execute.py',
    'features/sources/discover.py','features/sources/verify.py','features/sources/manage.py',
    'features/work/observe_paid_work.py','features/work/normalize.py','features/measurement/measure.py',
    'features/monitoring/start_run.py','features/monitoring/record_observation.py','features/monitoring/finish_run.py','features/monitoring/build_daily_diff.py',
    'features/novelty/rediscover.py','features/claims/triangulate.py','features/delivery/run_practical_test.py','features/acquisition/run_market_test.py',
    'features/decisions/update.py','features/methods/change_policy.py','features/checkpoint/create.py','features/repair/reconcile.py',
    'features/governance/audit_modify.py','features/migration/migrate_project.py',
    'features/queries/current_state.py','features/queries/changes.py','features/queries/trend.py','features/queries/interpretation.py','features/queries/research_health.py'
}

def imports(path:Path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    out=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): out += [a.name for a in n.names]
        elif isinstance(n,ast.ImportFrom) and n.module: out.append(n.module)
    return out

class ArchitectureBoundaryTests(unittest.TestCase):
    def test_expected_aggregate_and_value_object_modules_exist(self):
        self.assertTrue(PKG.exists(),'ARCHITECTURE RED: src/research_system does not exist yet')
        missing=sorted(x for x in EXPECTED_AGGREGATE_MODULES if not (PKG/x).exists())
        self.assertEqual(missing,[],f'missing aggregate/VO ownership modules: {missing}')

    def test_expected_end_to_end_feature_modules_exist(self):
        self.assertTrue(PKG.exists(),'ARCHITECTURE RED: src/research_system does not exist yet')
        missing=sorted(x for x in EXPECTED_FEATURE_MODULES if not (PKG/x).exists())
        self.assertEqual(missing,[],f'missing feature slices: {missing}')

    def test_domain_never_depends_on_features_infrastructure_or_docengine(self):
        self.assertTrue((PKG/'domain').exists(),'ARCHITECTURE RED: domain package missing')
        bad=[]
        for p in (PKG/'domain').rglob('*.py'):
            for imp in imports(p):
                if imp.startswith('research_system.features') or imp.startswith('research_system.infrastructure') or imp.startswith('docengine'):
                    bad.append((p.relative_to(PKG).as_posix(),imp))
        self.assertEqual(bad,[])

    def test_features_do_not_import_other_features(self):
        self.assertTrue((PKG/'features').exists(),'ARCHITECTURE RED: features package missing')
        bad=[]
        for p in (PKG/'features').rglob('*.py'):
            own='.'.join(p.relative_to(PKG).with_suffix('').parts[:-1])
            for imp in imports(p):
                if imp.startswith('research_system.features.'):
                    bad.append((p.relative_to(PKG).as_posix(),imp))
        self.assertEqual(bad,[],f'features must compose through domain/ports, not call feature modules: {bad}')

    def test_shared_is_technical_and_does_not_depend_on_domain_or_features(self):
        self.assertTrue((PKG/'shared').exists(),'ARCHITECTURE RED: shared package missing')
        bad=[]
        for p in (PKG/'shared').rglob('*.py'):
            for imp in imports(p):
                if imp.startswith('research_system.domain') or imp.startswith('research_system.features') or imp.startswith('research_system.infrastructure') or imp.startswith('docengine'):
                    bad.append((p.relative_to(PKG).as_posix(),imp))
        self.assertEqual(bad,[])

    def test_docengine_dependency_is_confined_to_infrastructure_adapter(self):
        self.assertTrue(PKG.exists(),'ARCHITECTURE RED: src/research_system does not exist yet')
        bad=[]
        for p in PKG.rglob('*.py'):
            if 'infrastructure/gendocen' in p.relative_to(PKG).as_posix(): continue
            if any(i.startswith('docengine') for i in imports(p)): bad.append(p.relative_to(PKG).as_posix())
        self.assertEqual(bad,[],f'gendocen must be an infrastructure adapter only: {bad}')
