"""Tests for scripts/store.py — schema apply, idempotent inserts, citation grid."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import store as store_mod  # noqa: E402


def fresh_store() -> store_mod.Store:
    """Return a Store backed by a fresh temp DB with schema applied."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    s = store_mod.Store(tmp.name)
    s.apply_schema()
    return s


class SchemaTests(unittest.TestCase):

    def test_apply_schema_records_version(self):
        s = fresh_store()
        try:
            # v2 migration adds region / currency / platform_region columns.
            self.assertEqual(s.current_schema_version(), 2)
        finally:
            s.close()

    def test_apply_schema_is_idempotent(self):
        s = fresh_store()
        try:
            s.apply_schema()
            s.apply_schema()
            self.assertEqual(s.current_schema_version(), 2)
        finally:
            s.close()


class PropertyTests(unittest.TestCase):

    def test_add_property_returns_id(self):
        s = fresh_store()
        try:
            pid = s.add_property("example.com", brand_name="Example", one_liner="we do x")
            self.assertGreater(pid, 0)
            row = s.get_property_by_domain("example.com")
            self.assertEqual(row["brand_name"], "Example")
        finally:
            s.close()

    def test_add_property_is_idempotent_on_domain(self):
        s = fresh_store()
        try:
            pid1 = s.add_property("example.com", brand_name="First")
            pid2 = s.add_property("example.com", brand_name="Second")
            self.assertEqual(pid1, pid2)
            row = s.get_property_by_domain("example.com")
            self.assertEqual(row["brand_name"], "Second")
        finally:
            s.close()

    def test_list_properties_sorted(self):
        s = fresh_store()
        try:
            s.add_property("b.com")
            s.add_property("a.com")
            rows = s.list_properties()
            self.assertEqual([r["domain"] for r in rows], ["a.com", "b.com"])
        finally:
            s.close()


class QueryAndCompetitorTests(unittest.TestCase):

    def test_query_type_validation(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            with self.assertRaises(ValueError):
                s.add_query(pid, "q", query_type="invalid")
        finally:
            s.close()

    def test_add_query_idempotent(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            qid1 = s.add_query(pid, "what is x", "aeo")
            qid2 = s.add_query(pid, "what is x", "aeo")
            self.assertEqual(qid1, qid2)
        finally:
            s.close()

    def test_retired_queries_excluded_by_default(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            q1 = s.add_query(pid, "q1")
            q2 = s.add_query(pid, "q2")
            s.retire_query(q2)
            active = s.list_queries(pid)
            all_ = s.list_queries(pid, include_retired=True)
            self.assertEqual(len(active), 1)
            self.assertEqual(len(all_), 2)
        finally:
            s.close()

    def test_competitor_idempotent_on_name(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            c1 = s.add_competitor(pid, "ACME")
            c2 = s.add_competitor(pid, "ACME", domain="acme.com")
            self.assertEqual(c1, c2)
        finally:
            s.close()


class RunTests(unittest.TestCase):

    def test_start_run_validates_type(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            with self.assertRaises(ValueError):
                s.start_run(pid, "invalid")
        finally:
            s.close()

    def test_start_and_finish_run(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            s.finish_run(rid, "completed")
            latest = s.latest_run(pid, "weekly")
            self.assertEqual(latest["id"], rid)
            self.assertEqual(latest["status"], "completed")
        finally:
            s.close()


class CitationGridTests(unittest.TestCase):

    def setUp(self):
        self.s = fresh_store()
        self.pid = self.s.add_property("ex.com")
        self.q1 = self.s.add_query(self.pid, "q1")
        self.q2 = self.s.add_query(self.pid, "q2")

    def tearDown(self):
        self.s.close()

    def test_latest_grid_returns_most_recent(self):
        run1 = self.s.start_run(self.pid, "weekly", iso_week="2026-W01")
        self.s.record_citation(run1, self.pid, self.q1, "openai", is_cited=0)

        run2 = self.s.start_run(self.pid, "weekly", iso_week="2026-W02")
        self.s.record_citation(run2, self.pid, self.q1, "openai", is_cited=1)

        grid = self.s.latest_grid = self.s.latest_citation_grid(self.pid)
        self.assertEqual(grid[(self.q1, "openai")]["is_cited"], 1)

    def test_citation_rate_excludes_not_checked(self):
        run1 = self.s.start_run(self.pid, "weekly", iso_week="2026-W01")
        self.s.record_citation(run1, self.pid, self.q1, "openai", is_cited=1)
        self.s.record_citation(run1, self.pid, self.q2, "openai", is_cited=0)
        self.s.record_citation(run1, self.pid, self.q1, "anthropic", is_cited=None)

        rate = self.s.citation_rate(self.pid)
        self.assertAlmostEqual(rate, 0.5)

    def test_week_grid_isolated_by_iso_week(self):
        run1 = self.s.start_run(self.pid, "weekly", iso_week="2026-W01")
        self.s.record_citation(run1, self.pid, self.q1, "openai", is_cited=1)

        run2 = self.s.start_run(self.pid, "weekly", iso_week="2026-W02")
        self.s.record_citation(run2, self.pid, self.q1, "openai", is_cited=0)

        w1 = self.s.citation_grid_for_week(self.pid, "2026-W01")
        w2 = self.s.citation_grid_for_week(self.pid, "2026-W02")
        self.assertEqual(w1[(self.q1, "openai")]["is_cited"], 1)
        self.assertEqual(w2[(self.q1, "openai")]["is_cited"], 0)


class ActionTests(unittest.TestCase):

    def test_action_score_computed_from_impact_and_effort(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            aid = s.add_action(
                rid, pid, action_type="blog_post", title="t",
                predicted_impact=0.8, effort_minutes=120,
            )
            actions = s.list_actions(pid)
            self.assertEqual(actions[0]["id"], aid)
            self.assertAlmostEqual(actions[0]["score"], 0.8 / 120)
        finally:
            s.close()

    def test_actions_ordered_by_score_desc(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            s.add_action(rid, pid, action_type="x", title="low",
                         predicted_impact=0.2, effort_minutes=60)
            s.add_action(rid, pid, action_type="x", title="high",
                         predicted_impact=0.9, effort_minutes=30)
            actions = s.list_actions(pid)
            self.assertEqual(actions[0]["title"], "high")

        finally:
            s.close()

    def test_update_action_status(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            aid = s.add_action(rid, pid, action_type="x", title="t")
            s.update_action_status(aid, "done", cited_on="reddit")
            row = s.list_actions(pid, status="done")[0]
            self.assertEqual(row["cited_on"], "reddit")
        finally:
            s.close()

    def test_invalid_status_rejected(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            aid = s.add_action(rid, pid, action_type="x", title="t")
            with self.assertRaises(ValueError):
                s.update_action_status(aid, "invalid")
        finally:
            s.close()


class DiscoveredQueryTests(unittest.TestCase):

    def test_discovered_query_increments_surface_count(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            id1 = s.add_discovered_query(rid, pid, "what is foo", "paa")
            id2 = s.add_discovered_query(rid, pid, "what is foo", "paa")
            self.assertEqual(id1, id2)
            row = s.conn.execute(
                "SELECT surface_count FROM discovered_queries WHERE id = ?", (id1,)
            ).fetchone()
            self.assertEqual(row["surface_count"], 2)
        finally:
            s.close()


class IsoWeekTests(unittest.TestCase):

    def test_iso_week_format(self):
        import datetime as dt
        w = store_mod.iso_week_now(dt.datetime(2026, 5, 20, tzinfo=dt.timezone.utc))
        self.assertEqual(w, "2026-W21")


class RegionCurrencyTests(unittest.TestCase):
    """Schema v2 — region and currency on properties, region on queries,
    platform_region on actions."""

    def test_property_defaults_to_global_USD(self):
        s = fresh_store()
        try:
            s.add_property("plain.com")
            row = s.get_property_by_domain("plain.com")
            self.assertEqual(row["region"], "global")
            self.assertEqual(row["currency"], "USD")
        finally:
            s.close()

    def test_add_property_india_INR(self):
        s = fresh_store()
        try:
            s.add_property("moltpe.com", region="india", currency="INR")
            row = s.get_property_by_domain("moltpe.com")
            self.assertEqual(row["region"], "india")
            self.assertEqual(row["currency"], "INR")
        finally:
            s.close()

    def test_property_region_update_via_upsert(self):
        """Second add_property call with new region updates the row."""
        s = fresh_store()
        try:
            s.add_property("ex.com")
            s.add_property("ex.com", region="india", currency="INR")
            row = s.get_property_by_domain("ex.com")
            self.assertEqual(row["region"], "india")
            self.assertEqual(row["currency"], "INR")
        finally:
            s.close()

    def test_query_region_nullable_defaults_none(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            qid = s.add_query(pid, "what are agentic payments")
            row = s.conn.execute(
                "SELECT region FROM queries WHERE id = ?", (qid,)
            ).fetchone()
            self.assertIsNone(row["region"])
        finally:
            s.close()

    def test_query_region_override(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            qid = s.add_query(pid, "best upi payments for shops", region="india")
            row = s.conn.execute(
                "SELECT region FROM queries WHERE id = ?", (qid,)
            ).fetchone()
            self.assertEqual(row["region"], "india")
        finally:
            s.close()

    def test_action_platform_region_defaults_global(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com")
            rid = s.start_run(pid, "weekly")
            aid = s.add_action(
                run_id=rid, property_id=pid,
                action_type="reddit_thread", title="t",
            )
            row = s.conn.execute(
                "SELECT platform_region FROM actions WHERE id = ?", (aid,)
            ).fetchone()
            self.assertEqual(row["platform_region"], "global")
        finally:
            s.close()

    def test_action_platform_region_india(self):
        s = fresh_store()
        try:
            pid = s.add_property("ex.com", region="india", currency="INR")
            rid = s.start_run(pid, "weekly")
            aid = s.add_action(
                run_id=rid, property_id=pid,
                action_type="quora_india_answer", title="t",
                platform_region="india",
            )
            row = s.conn.execute(
                "SELECT platform_region FROM actions WHERE id = ?", (aid,)
            ).fetchone()
            self.assertEqual(row["platform_region"], "india")
        finally:
            s.close()


class EnsureColumnSecurityTests(unittest.TestCase):

    def test_allowlisted_table_accepted(self):
        s = fresh_store()
        try:
            # 'properties' is in the allowlist — should not raise
            s._ensure_column("properties", "region", "TEXT")
        finally:
            s.close()

    def test_non_allowlisted_table_raises(self):
        s = fresh_store()
        try:
            with self.assertRaises(ValueError) as ctx:
                s._ensure_column("schema_version", "evil", "TEXT")
            self.assertIn("not in allowlist", str(ctx.exception))
        finally:
            s.close()

    def test_sql_injection_table_name_rejected(self):
        s = fresh_store()
        try:
            with self.assertRaises(ValueError):
                s._ensure_column("properties; DROP TABLE properties; --", "x", "TEXT")
        finally:
            s.close()


if __name__ == "__main__":
    unittest.main()
