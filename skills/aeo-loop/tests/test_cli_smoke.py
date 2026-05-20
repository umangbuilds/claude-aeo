"""Smoke tests for scripts/aeo_loop.py CLI.

End-to-end exercise of subcommands that don't require real LLM keys.
Citation-check is covered separately in test_citation_check.py via mocks.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import aeo_loop  # noqa: E402


class CLISmokeTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "store.db")
        self.config_path = str(Path(self.tmp.name) / "keys.toml")
        os.environ["AEO_LOOP_CONFIG"] = self.config_path

    def tearDown(self):
        os.environ.pop("AEO_LOOP_CONFIG", None)
        self.tmp.cleanup()

    def _run(self, *argv):
        """Run a CLI command, capturing stdout. Returns (rc, stdout_str)."""
        old_stdout = sys.stdout
        sys.stdout = buf = StringIO()
        try:
            rc = aeo_loop.main(["--db", self.db_path, "--json"] + list(argv))
        finally:
            sys.stdout = old_stdout
        return rc, buf.getvalue()

    def test_init_creates_config_and_store(self):
        rc, out = self._run("init")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["tier"], "free")
        self.assertTrue(Path(self.config_path).exists())
        self.assertTrue(Path(self.db_path).exists())

    def test_add_property_then_list(self):
        self._run("init")
        rc, _ = self._run("add-property", "example.com",
                          "--brand", "Example", "--one-liner", "we do x")
        self.assertEqual(rc, 0)
        rc, out = self._run("list-properties")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data[0]["domain"], "example.com")
        self.assertEqual(data[0]["brand_name"], "Example")

    def test_query_lifecycle(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, _ = self._run("add-query", "example.com", "what is example")
        self.assertEqual(rc, 0)
        rc, out = self._run("list-queries", "example.com")
        data = json.loads(out)
        self.assertEqual(data[0]["query_text"], "what is example")

    def test_competitor_added(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, _ = self._run("add-competitor", "example.com", "Rival Inc",
                          "--competitor-domain", "rival.com")
        self.assertEqual(rc, 0)

    def test_run_lifecycle(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, out = self._run("start-run", "example.com")
        run_id = json.loads(out)["run_id"]
        rc, _ = self._run("finish-run", "--run-id", str(run_id),
                          "--status", "completed")
        self.assertEqual(rc, 0)

    def test_record_actions_from_file(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, out = self._run("start-run", "example.com")
        run_id = json.loads(out)["run_id"]

        actions_payload = [
            {"action_type": "schema_add", "title": "Add Article schema to blog",
             "signals": {"addresses_critical_finding": True}},
            {"action_type": "blog_post", "title": "Pillar page on agentic payments",
             "signals": {"covers_uncited_query": True, "category_whitespace": True}},
        ]
        af = Path(self.tmp.name) / "actions.json"
        af.write_text(json.dumps(actions_payload))

        rc, out = self._run("record-actions", "example.com",
                            "--run-id", str(run_id),
                            "--actions-file", str(af),
                            "--top-n", "10")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(len(data["saved"]), 2)

        rc, out = self._run("list-actions", "example.com")
        actions = json.loads(out)
        self.assertEqual(len(actions), 2)

    def test_mark_done_then_status(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, out = self._run("start-run", "example.com")
        run_id = json.loads(out)["run_id"]

        payload = [{"action_type": "schema_add", "title": "t",
                    "signals": {"addresses_critical_finding": True}}]
        af = Path(self.tmp.name) / "a.json"
        af.write_text(json.dumps(payload))
        self._run("record-actions", "example.com", "--run-id", str(run_id),
                  "--actions-file", str(af))

        rc, out = self._run("list-actions", "example.com")
        action_id = json.loads(out)[0]["id"]
        rc, _ = self._run("mark-done", str(action_id), "--cited-on", "reddit")
        self.assertEqual(rc, 0)

        rc, out = self._run("list-actions", "example.com", "--status", "done")
        done_actions = json.loads(out)
        self.assertEqual(len(done_actions), 1)
        self.assertEqual(done_actions[0]["cited_on"], "reddit")

    def test_assist_for_reddit_action(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, out = self._run("start-run", "example.com")
        run_id = json.loads(out)["run_id"]

        payload = [{
            "action_type": "reddit_thread",
            "title": "Question about AEO best practices",
            "target_url": "AEO",
            "signals": {"covers_uncited_query": True},
        }]
        af = Path(self.tmp.name) / "a.json"
        af.write_text(json.dumps(payload))
        self._run("record-actions", "example.com", "--run-id", str(run_id),
                  "--actions-file", str(af))

        rc, out = self._run("list-actions", "example.com")
        aid = json.loads(out)[0]["id"]
        rc, out = self._run("assist", str(aid))
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["platform"], "reddit")
        self.assertIn("/r/AEO/submit", data["open_url"])

    def test_status_for_property_with_runs(self):
        self._run("init")
        self._run("add-property", "example.com")
        rc, out = self._run("start-run", "example.com")
        run_id = json.loads(out)["run_id"]
        self._run("finish-run", "--run-id", str(run_id), "--status", "completed")
        rc, out = self._run("status", "example.com")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["property"], "example.com")
        self.assertIsNotNone(data["latest_run"])

    def test_unknown_property_returns_3(self):
        self._run("init")
        rc, _ = self._run("status", "does-not-exist.com")
        self.assertEqual(rc, 3)

    def test_add_property_region_india_defaults_currency_INR(self):
        self._run("init")
        rc, out = self._run("add-property", "moltpe.com", "--region", "india")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["property"]["region"], "india")
        self.assertEqual(data["property"]["currency"], "INR")

    def test_add_property_explicit_currency_wins(self):
        self._run("init")
        rc, out = self._run(
            "add-property", "ex.com", "--region", "india", "--currency", "EUR",
        )
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["property"]["currency"], "EUR")

    def test_add_query_with_region_override_runs_clean(self):
        self._run("init")
        self._run("add-property", "ex.com")
        rc, _ = self._run(
            "add-query", "ex.com", "best upi gateways", "--region", "india",
        )
        self.assertEqual(rc, 0)

    def test_assist_for_quora_india_action(self):
        self._run("init")
        self._run("add-property", "ex.com", "--region", "india")
        rc, out = self._run("start-run", "ex.com")
        run_id = json.loads(out)["run_id"]
        payload = [{
            "action_type": "quora_india_answer",
            "title": "Answer about agentic payments",
            "target_url": "https://in.quora.com/What-are-agentic-payments",
            "signals": {"covers_uncited_query": True},
            "platform_region": "india",
        }]
        af = Path(self.tmp.name) / "a.json"
        af.write_text(json.dumps(payload))
        self._run("record-actions", "ex.com", "--run-id", str(run_id),
                  "--actions-file", str(af))
        rc, out = self._run("list-actions", "ex.com")
        aid = json.loads(out)[0]["id"]
        rc, out = self._run("assist", str(aid))
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["platform"], "quora_india")
        self.assertIn("in.quora.com", data["open_url"])


if __name__ == "__main__":
    unittest.main()
