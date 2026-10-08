"""Regression checks for inventory traceability; no product/release acceptance."""
import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('inventory',ROOT/'inventory.py')
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
class InventoryTests(unittest.TestCase):
 def setUp(self):self.data=list(MODULE.load(ROOT.parents[1]))
 def test_current_inventory_and_generated_crosswalk(self):
  result=MODULE.validate(*self.data)
  self.assertEqual(result['requirements'],len(self.data[0]['requirements']))
  self.assertEqual(result['backlog_items'],len(MODULE.source_bullets(self.data[4])))
 def test_rejects_invalid_metadata_and_references(self):
  mutations={
   'unknown_kind':lambda d:d[0]['requirements'][0].update(kind='everything'),
   'unknown_classification':lambda d:d[0]['requirements'][0].update(status='CURRENT_DECISION'),
   'unknown_axis':lambda d:d[0]['requirements'][0].update(axes=['AX-V99']),
   'duplicate_axis':lambda d:d[0]['requirements'][0].update(axes=['AX-V01','AX-V01']),
   'invented_author':lambda d:d[0]['requirements'][0]['origin'].update(basis='explicit_user'),
   'nonexistent_human_section':lambda d:d[0]['requirements'][0]['human_ref'].update(sections=['99']),
   'missing_history':lambda d:d[0]['requirements'][0].update(change_history=[]),
   'promoted_rewrite':lambda d:d[0]['requirements'][0]['normalization_review'].update(statement_rewrite_adopted=True),
   'duplicate_requirement':lambda d:d[0]['requirements'].append(copy.deepcopy(d[0]['requirements'][0])),
   'missing_backlog':lambda d:d[1]['items'].pop(),
   'duplicate_backlog_id':lambda d:d[1]['items'][1].update(backlog_id=d[1]['items'][0]['backlog_id']),
   'unknown_live_destination':lambda d:d[1]['items'][0].update(requirement_refs=['NEW-999']),
   'unknown_proposal_destination':lambda d:d[1]['items'][0].update(proposal_refs=['NEW-999']),
   'origin_excerpt_drift':lambda d:d[1]['items'][0]['source'].update(excerpt='different'),
   'proposal_live_ID_collision':lambda d:d[2]['entries'][0].update(proposal_id=d[0]['requirements'][0]['id']),
   'lost_NEGATIVE_example_decision':lambda d:next(x for x in d[1]['items'] if x['backlog_id']=='B026').update(disposition='pending_proposal'),
   'missing_proposal':lambda d:d[2]['entries'].pop(),
   'missing_dependency_proposal':lambda d:d[2]['dependency_review_rows'].pop(),
   'promoted_dependency':lambda d:d[2]['dependency_review_rows'][0].update(state='accepted'),
   'wrong_review_hash':lambda d:d[1]['review_source_snapshot'].update(text_sha256='0'*64),
   'wrong_source_hash':lambda d:d[1]['source_snapshot'].update(text_sha256='0'*64),
   'stale_GitHub_backend_active':lambda d:next(x for x in d[2]['entries'] if x['proposal_id']=='NEW-004').update(state='pending_not_adopted'),
   'crosswalk_drift':lambda d:d.__setitem__(3,d[3].replace('| INT-001 |','| WRONG |'))}
  for name,mutate in mutations.items():
   with self.subTest(name=name):
    d=copy.deepcopy(self.data);mutate(d)
    with self.assertRaises(ValueError):MODULE.validate(*d)
 def test_original_adopted_negative_example_scope_is_preserved(self):
  entry=next(x for x in self.data[0]['requirements'] if x['id']=='OPP-017')
  self.assertEqual(entry['status'],'TARGET_REQUIRED')
  self.assertEqual(entry['kind'],'product_capability')
  self.assertIn('outside MVP',entry['scope'])
  self.assertTrue(entry['change_history'])
if __name__=='__main__':unittest.main(verbosity=2)
