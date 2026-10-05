import json, tempfile
from pathlib import Path
from ARCHITECTURE_TESTS.support.integration import EmptyRootCase
from ARCHITECTURE_TESTS.support.future import tree_digest
M='research_system.features.migration.migrate_project'
class MigrateProjectFeatureTests(EmptyRootCase):
    def legacy_fixture(self,root:Path):
        (root/'RUNS').mkdir(parents=True); (root/'LEDGER').mkdir();
        (root/'STATE.json').write_text(json.dumps({'system_version':'1.11.0'}),encoding='utf-8'); (root/'RUN_STATE.json').write_text(json.dumps({'system_version':'1.11.0','active_daily_run_id':None}),encoding='utf-8')
        run={'run_id':'r1','started_at':'2026-10-01T00:00:00+00:00','completed_at':'2026-10-01T01:00:00+00:00','research_date':'2026-10-01','method_id':'m','method_version':'1','scope_fingerprint':'s','source_route_ids':['route'],'coverage_status':'complete'}
        (root/'RUNS/r1.json').write_text(json.dumps(run),encoding='utf-8'); obs={'observation_id':'o1','idempotency_key':'k1','run_id':'r1','entity_id':'e1','observation_class':'seen','source_id':'s1'}
        (root/'LEDGER/OBSERVATIONS.jsonl').write_text(json.dumps(obs)+'\n',encoding='utf-8'); (root/'LEDGER/DAILY_RUNS.jsonl').write_text(json.dumps(run)+'\n',encoding='utf-8'); (root/'LEDGER/DAILY_DIFFS.jsonl').write_text('',encoding='utf-8')
    def test_one_shot_migration_preserves_logical_ids_counts_and_semantic_values_and_writes_receipt(self):
        legacy=Path(tempfile.mkdtemp()); self.addCleanup(lambda: __import__('shutil').rmtree(legacy,ignore_errors=True)); self.legacy_fixture(legacy); before=tree_digest(legacy)
        r=self.feature(M,{'legacy_project_path':str(legacy),'target_system_version':'next'},now='2026-10-01T07:00:00+00:00')
        self.assertEqual(tree_digest(legacy),before,'migration must not mutate source baseline in place'); self.assertEqual(r['counts']['runs'],1); self.assertEqual(r['counts']['observations'],1); self.assertIn('r1',r['preserved_logical_ids']); self.assertIn('e1',r['preserved_logical_ids']); self.assertIn('migration_receipt_id',r); self.assertTrue(r['equivalence_audit']['ok'])
