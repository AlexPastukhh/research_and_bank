import json,sys,tempfile,subprocess,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RuntimeTests(unittest.TestCase):
 def runp(self,*args,ok=True):
  p=subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True)
  if ok and p.returncode!=0: self.fail(p.stdout+'\n'+p.stderr)
  return p
 def init(self,td): self.runp(ROOT/'TOOLS/init_project.py',td,'testproj')
 def test_path_confinement(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); idx=json.loads((Path(td)/'PROJECT_INDEX.json').read_text()); idx['artifacts']['state']='../outside.json'; (Path(td)/'PROJECT_INDEX.json').write_text(json.dumps(idx)); self.assertNotEqual(self.runp(ROOT/'TOOLS/validate_project.py',td,ok=False).returncode,0)
 def test_observation_idempotency_and_source_provenance(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r1','--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','route1','--now','2026-10-01T00:00:00+00:00')
   a=[ROOT/'TOOLS/record_observation.py',td,'--entity-id','e1','--canonical-key','k','--class','seen','--state','active','--source-id','s1','--payload-json','{"x":1}','--now','2026-10-01T00:01:00+00:00']; self.runp(*a); self.runp(*a); b=a.copy(); b[b.index('s1')]='s2'; self.runp(*b)
   lines=(Path(td)/'LEDGER/OBSERVATIONS.jsonl').read_text().strip().splitlines(); self.assertEqual(len(lines),2)
 def test_not_seen_not_closed_and_gap_safe_new(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td)
   def run(rid,date,see):
    self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id',rid,'--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','route1','--now',f'{date}T00:00:00+00:00')
    if see:self.runp(ROOT/'TOOLS/record_observation.py',td,'--entity-id','e1','--canonical-key','k','--class','seen','--state','active','--source-id','s1','--payload-json','{"x":1}','--now',f'{date}T00:01:00+00:00')
    self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now',f'{date}T01:00:00+00:00')
   run('r1','2026-10-01',True); run('r2','2026-10-02',False); run('r3','2026-10-03',True)
   p=self.runp(ROOT/'TOOLS/build_daily_diff.py',td,'--current-run','r3','--previous-run','r2'); d=json.loads(p.stdout); self.assertNotIn('e1',d['new_entity_ids'])
 def test_source_route_blocks_comparability(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td)
   for rid,route,date in [('r1','a','2026-10-01'),('r2','b','2026-10-02')]:
    self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id',rid,'--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route',route,'--now',date+'T00:00:00+00:00'); self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now',date+'T01:00:00+00:00')
   d=json.loads(self.runp(ROOT/'TOOLS/build_daily_diff.py',td,'--current-run','r2','--previous-run','r1').stdout); self.assertEqual(d['comparison_status'],'not_comparable')
 def test_double_finalize_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r1','--method-id','m','--method-version','1','--scope-fingerprint','s','--now','2026-10-01T00:00:00+00:00'); self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now','2026-10-01T01:00:00+00:00'); p=self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','failed',ok=False); self.assertNotEqual(p.returncode,0)
 def test_secret_redaction(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r1','--method-id','m','--method-version','1','--scope-fingerprint','s','--now','2026-10-01T00:00:00+00:00'); self.runp(ROOT/'TOOLS/record_observation.py',td,'--entity-id','e1','--canonical-key','k','--class','seen','--source-id','s1','--payload-json','{"token":"abc","x":1}'); text=(Path(td)/'LEDGER/OBSERVATIONS.jsonl').read_text(); self.assertNotIn('abc',text); self.assertIn('[REDACTED]',text)

 def test_reopen_after_gap(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td)
   # r1 explicit negative, r2 no observation, r3 active -> reopened, never new.
   self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r1','--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','a','--now','2026-10-01T00:00:00+00:00')
   self.runp(ROOT/'TOOLS/record_observation.py',td,'--entity-id','e1','--canonical-key','k','--class','explicit_negative','--state','closed','--source-id','s1','--payload-json','{}','--now','2026-10-01T00:01:00+00:00')
   self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now','2026-10-01T01:00:00+00:00')
   self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r2','--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','a','--now','2026-10-02T00:00:00+00:00'); self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now','2026-10-02T01:00:00+00:00')
   self.runp(ROOT/'TOOLS/start_daily_run.py',td,'--run-id','r3','--method-id','m','--method-version','1','--scope-fingerprint','s','--source-route','a','--now','2026-10-03T00:00:00+00:00')
   self.runp(ROOT/'TOOLS/record_observation.py',td,'--entity-id','e1','--canonical-key','k','--class','seen','--state','active','--source-id','s1','--payload-json','{}','--now','2026-10-03T00:01:00+00:00'); self.runp(ROOT/'TOOLS/finish_daily_run.py',td,'--coverage','complete','--now','2026-10-03T01:00:00+00:00')
   d=json.loads(self.runp(ROOT/'TOOLS/build_daily_diff.py',td,'--current-run','r3','--previous-run','r2').stdout); self.assertIn('e1',d['reopened_ids']); self.assertNotIn('e1',d['new_entity_ids'])
 def test_task_done_requires_acceptance(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); tdir=Path(td)/'TASKS'; task={'task_id':'x','task_instance_key':'k','use_case_id':'UC03','request_ref':'r','route_reason':'r','use_case_registry_version':'2.0.0','router_kind':'system','atomic_question':'q','status':'done','acceptance_tests':[{'id':'a','status':'fail'}]}; (tdir/'x.json').write_text(json.dumps(task)); p=self.runp(ROOT/'TOOLS/validate_project.py',td,ok=False); self.assertNotEqual(p.returncode,0)
 def test_invalid_run_state_enum_fails(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); rp=Path(td)/'RUN_STATE.json'; r=json.loads(rp.read_text()); r['status']='banana'; rp.write_text(json.dumps(r)); p=self.runp(ROOT/'TOOLS/validate_project.py',td,ok=False); self.assertNotEqual(p.returncode,0)
 def test_manifest_integrity_detects_missing_file(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); self.runp(ROOT/'TOOLS/checkpoint_project.py',td,'--now','2026-10-01T02:00:00+00:00'); target=Path(td)/'PROJECT_BRIEF.md'; target.unlink(); p=self.runp(ROOT/'TOOLS/validate_project.py',td,ok=False); self.assertNotEqual(p.returncode,0)
 def test_bootstrap_cycle_points_to_actual_workbook(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'src'; self.init(src); cyc=Path(td)/'cycle'; self.runp(ROOT/'TOOLS/bootstrap_cycle.py','-o',cyc,src); idx=json.loads((cyc/'PROJECT/PROJECT_INDEX.json').read_text()); self.assertEqual(idx['artifacts']['workbook'],'research.xlsx'); self.assertTrue((cyc/'PROJECT/research.xlsx').exists())
 def test_migration_110_to_111(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td)
   for name in ['STATE.json','RUN_STATE.json']:
    p=Path(td)/name; x=json.loads(p.read_text()); x['system_version']='1.10.0'; p.write_text(json.dumps(x))
   self.runp(ROOT/'TOOLS/migrate_project.py',td,'--apply'); s=json.loads((Path(td)/'STATE.json').read_text()); r=json.loads((Path(td)/'RUN_STATE.json').read_text()); self.assertEqual(s['system_version'],'1.11.0'); self.assertEqual(r['system_version'],'1.11.0')


 def test_dependency_propagation(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); g={'schema_version':'1.0','edges':[{'from_node_id':'A','to_node_id':'B'},{'from_node_id':'B','to_node_id':'C'}]}; (Path(td)/'DEPENDENCY_GRAPH.json').write_text(json.dumps(g)); d=json.loads(self.runp(ROOT/'TOOLS/propagate_changes.py',td,'A').stdout); self.assertEqual(d['affected'],['B','C'])
 def test_unknown_project_config_key_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   self.init(td); cp=Path(td)/'PROJECT_CONFIG.json'; c=json.loads(cp.read_text()); c['pretend_setting']=True; cp.write_text(json.dumps(c)); p=self.runp(ROOT/'TOOLS/validate_project.py',td,ok=False); self.assertNotEqual(p.returncode,0)

if __name__=='__main__': unittest.main()
