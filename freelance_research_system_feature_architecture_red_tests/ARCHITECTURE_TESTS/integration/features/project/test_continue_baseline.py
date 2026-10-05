import json, tempfile
from pathlib import Path
from ARCHITECTURE_TESTS.support.integration import EmptyRootCase
from ARCHITECTURE_TESTS.support.future import tree_digest

M='research_system.features.project.continue_baseline'
class ContinueBaselineFeatureTests(EmptyRootCase):
    def test_reconstructs_baseline_without_mutating_supplied_baseline(self):
        """BASELINE UC02: reuse valid work rather than repeat it."""
        with tempfile.TemporaryDirectory() as td:
            baseline=Path(td); (baseline/'STATE.json').write_text(json.dumps({'system_version':'1.11.0','evidence':['e1']}),encoding='utf-8'); before=tree_digest(baseline)
            r=self.feature(M,{'project_id':'p1','baseline_path':str(baseline)},now='2026-10-01T00:00:00+00:00')
            self.assertEqual(tree_digest(baseline),before); self.assertIn('reconstructed_baseline',r); self.assertIn('delta_plan',r)

    def test_delta_plan_uses_explicit_reuse_refresh_continue_rediscover_categories(self):
        with tempfile.TemporaryDirectory() as td:
            baseline=Path(td); (baseline/'STATE.json').write_text(json.dumps({'system_version':'1.11.0'}),encoding='utf-8')
            r=self.feature(M,{'project_id':'p1','baseline_path':str(baseline)},now='2026-10-01T00:00:00+00:00')
            self.assertTrue(set(r['delta_plan']).issubset({'reuse','refresh','continue','rediscover'})); self.assertIn('next_action',r)
