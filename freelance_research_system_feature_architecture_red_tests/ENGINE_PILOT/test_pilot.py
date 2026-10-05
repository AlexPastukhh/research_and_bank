import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
TOOL = HERE / "research_engine.py"


class EnginePilotTests(unittest.TestCase):
    def runp(self, *args, ok=(0,)):
        proc = subprocess.run([sys.executable, str(TOOL), *map(str, args)], text=True, capture_output=True)
        if proc.returncode not in ok:
            self.fail(proc.stdout + "\n" + proc.stderr)
        return proc

    def test_gap_safe_reopen_and_membership_invalidation(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "project"
            self.runp("init", p)
            self.runp("start", p, "--run-id", "r1", "--method-id", "m", "--method-version", "1", "--scope-fingerprint", "s", "--source-route", "a", "--now", "2026-10-01T00:00:00+00:00")
            self.runp("observe", p, "--entity-id", "e1", "--canonical-key", "k", "--class", "explicit_negative", "--state", "closed", "--source-id", "s1", "--payload-json", "{}", "--now", "2026-10-01T00:01:00+00:00")
            self.runp("finish", p, "--coverage", "complete", "--now", "2026-10-01T01:00:00+00:00")

            self.runp("start", p, "--run-id", "r2", "--method-id", "m", "--method-version", "1", "--scope-fingerprint", "s", "--source-route", "a", "--now", "2026-10-02T00:00:00+00:00")
            self.runp("finish", p, "--coverage", "complete", "--now", "2026-10-02T01:00:00+00:00")

            self.runp("start", p, "--run-id", "r3", "--method-id", "m", "--method-version", "1", "--scope-fingerprint", "s", "--source-route", "a", "--now", "2026-10-03T00:00:00+00:00")
            self.runp("observe", p, "--entity-id", "e1", "--canonical-key", "k", "--class", "seen", "--state", "active", "--source-id", "s1", "--payload-json", "{}", "--now", "2026-10-03T00:01:00+00:00")
            self.runp("finish", p, "--coverage", "complete", "--now", "2026-10-03T01:00:00+00:00")
            self.runp("diff", p, "--current-run", "r3", "--previous-run", "r2")

            md = (p / "docs/research/daily_diff.md").read_text(encoding="utf-8")
            self.assertIn("- e1", md)
            receipt = next((p / "docs/_dependency/receipts").glob("receipt-*.json"))
            evidence = json.loads(receipt.read_text(encoding="utf-8"))
            refs = {item["source"] for item in evidence["dependencies"]}
            self.assertIn("resource://research/run_index#/run_ids", refs)
            self.assertIn("resource://runs/r1", refs)
            self.assertIn("resource://runs/r2", refs)
            self.assertIn("resource://runs/r3", refs)

            self.runp("start", p, "--run-id", "r4", "--method-id", "m", "--method-version", "1", "--scope-fingerprint", "s", "--source-route", "a", "--now", "2026-10-04T00:00:00+00:00")
            check = self.runp("check", p, ok=(0,)).stdout
            payload = json.loads(check.strip().splitlines()[-1])
            result = payload["data"]["results"][0]
            self.assertEqual(result["status"], "build_required")
            self.assertIn("dependency_changed", result["diff"]["reason_codes"])


if __name__ == "__main__":
    unittest.main()
