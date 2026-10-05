import json,sys,tempfile,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'TOOLS'))
from route_use_case import route
class UseCaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.reg=json.loads((ROOT/'CORE/USE_CASE_REGISTRY.json').read_text(encoding='utf-8')); cls.fx=json.loads((ROOT/'CORE/USE_CASE_ROUTING_FIXTURES.json').read_text(encoding='utf-8'))['fixtures']
 def test_routing_fixtures(self):
  for f in self.fx:
   with self.subTest(f=f['id']): self.assertEqual(route(self.reg,f['request'],f.get('state',{}))[0],f['expected_use_case_id'])
 def test_unique_ids_actions(self):
  ids=[u['id'] for u in self.reg['use_cases']]; ac=[u['action_class'] for u in self.reg['use_cases']]; self.assertEqual(len(ids),len(set(ids))); self.assertEqual(len(ac),len(set(ac)))
 def test_workflows_exist(self):
  for u in self.reg['use_cases']: self.assertTrue((ROOT/u['workflow']).exists())
 def test_no_routing_metadata_copies(self):
  for u in self.reg['use_cases']:
   t=(ROOT/u['workflow']).read_text(encoding='utf-8').lower()
   for x in ['## intent','## route here','## do not route','## normal next']: self.assertNotIn(x,t)
 def test_transitions_total_and_deterministic(self):
  valid={u['id'] for u in self.reg['use_cases']}
  for u in self.reg['use_cases']:
   self.assertEqual(set(u['outcomes']),{t['outcome'] for t in u['transitions']}); self.assertEqual(len(u['transitions']),len(u['outcomes']))
   for t in u['transitions']: self.assertTrue(t['to'] is None or t['to'] in valid)
 def test_boundary_rules(self): self.assertGreaterEqual(len(self.reg['boundary_rules']),14)
 def test_kinds(self): self.assertEqual(set(u['kind'] for u in self.reg['use_cases']),set(self.reg['use_case_kinds']))

 def test_complete_v3_contract_fields(self):
  required={'group','interaction_type','execution_owner','actor_intent','inputs','reads','writes','capabilities','outputs','freshness_requirements','comparability_requirements','acceptance','failure_modes','side_effects','idempotency','capability_requirements','ui_surfaces','api_queries','golden_paths'}
  for u in self.reg['use_cases']:
   self.assertTrue(required.issubset(u),u['id']); self.assertTrue(u['outputs'],u['id']); self.assertTrue(u['acceptance'],u['id'])
 def test_execution_owners(self):
  expected={
   'UC01':'application','UC02':'mixed','UC03':'research_agent','UC04':'research_agent','UC05':'research_agent',
   'UC06':'research_agent','UC07':'mixed','UC08':'mixed','UC09':'mixed','UC10':'research_agent',
   'UC11':'research_agent','UC12':'research_agent','UC13':'research_agent','UC14':'mixed','UC15':'mixed',
   'UC16':'mixed','UC17':'mixed','UC18':'internal','UC19':'development','UC20':'internal',
   'UC21':'application','UC22':'application','UC23':'application','UC24':'application','UC25':'application',
  }
  self.assertEqual(set(self.reg['execution_owners']),{'research_agent','application','mixed','internal','development'})
  self.assertEqual({u['id']:u['execution_owner'] for u in self.reg['use_cases']},expected)

 def test_workflow_is_procedure_only(self):
  for u in self.reg['use_cases']:
   s=(ROOT/u['workflow']).read_text().lower(); self.assertNotIn('## acceptance',s); self.assertNotIn('## allowed outcome',s)
 def test_generated_views_parity(self):
  for tool in ['generate_use_case_views.py','generate_system_map.py']:
   p=subprocess.run([sys.executable,str(ROOT/'TOOLS'/tool),'--check'],capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stdout+p.stderr)


 def test_phase2_query_use_cases(self):
  q=[u for u in self.reg['use_cases'] if u['interaction_type']=='query']
  self.assertEqual({u['id'] for u in q},{'UC21','UC22','UC23','UC24','UC25'})
  self.assertTrue(all(u['group']=='results' for u in q))
  self.assertTrue(all(not u['writes'] for u in q))
  self.assertEqual({u['outputs'][0]['type'] for u in q},{'CurrentStateSnapshot','ChangeSet','TrendSeries','InterpretationRecord','ResearchHealthSnapshot'})
 def test_command_query_boundaries(self):
  pairs=[
   ('what changed since yesterday',{'refresh_requested':True},'UC09'),
   ('what changed since yesterday',{'existing_change_result_available':True},'UC22'),
   ('measure payout for Programming',{},'UC08'),
   ('show trend for Programming payout',{},'UC23'),
   ('verify whether this claim is supported',{},'UC11'),
   ('explain the results already collected',{},'UC24'),
   ('audit the reusable system architecture',{},'UC19'),
   ('show how fresh the research data is',{},'UC25'),
  ]
  for text,state,expected in pairs:
   with self.subTest(text=text,state=state): self.assertEqual(route(self.reg,text,state)[0],expected)
 def test_no_screen_or_builder_use_cases(self):
  banned={'Direction Detail','Current State Screen','Daily Changes Screen','Trends Screen','Interpretations Screen','Coverage & Quality Screen'}
  self.assertFalse(any(u['name'] in banned for u in self.reg['use_cases']))
  self.assertFalse(any(u['name'].lower().startswith(('build ','render ','screen ')) for u in self.reg['use_cases']))

 def test_registry_version(self): self.assertEqual(self.reg['registry_version'],'3.2.0'); self.assertEqual(self.reg['contract_version'],'3.1.0')
 def test_no_match(self): self.assertEqual(route(self.reg,'zzqv completely unrelated phrase',{})[0],'UC19')
 def test_ambiguity(self): self.assertEqual(route(self.reg,'change architecture and update project cadence',{})[0],'UC19')
if __name__=='__main__': unittest.main()
