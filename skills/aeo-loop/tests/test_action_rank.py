"""Tests for scripts/action_rank.py — scoring reproducibility and ranking order."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import action_rank as ar  # noqa: E402


class ImpactComputationTests(unittest.TestCase):

    def test_all_signals_at_one_gives_impact_one(self):
        signals = {k: True for k in ar.SIGNAL_WEIGHTS}
        self.assertAlmostEqual(ar.compute_impact(signals), 1.0)

    def test_no_signals_gives_zero(self):
        self.assertEqual(ar.compute_impact({}), 0.0)

    def test_partial_signals_sum_correctly(self):
        signals = {
            "addresses_critical_finding": True,
            "covers_uncited_query": True,
        }
        expected = 0.30 + 0.25
        self.assertAlmostEqual(ar.compute_impact(signals), expected)

    def test_floats_coerced_correctly(self):
        signals = {"addresses_critical_finding": 0.5}
        self.assertAlmostEqual(ar.compute_impact(signals), 0.15)

    def test_out_of_range_clamped(self):
        signals = {"addresses_critical_finding": 5.0}
        self.assertAlmostEqual(ar.compute_impact(signals), 0.30)

    def test_unknown_signal_ignored(self):
        signals = {"completely_unknown_signal": True}
        self.assertEqual(ar.compute_impact(signals), 0.0)


class NormalizeActionTests(unittest.TestCase):

    def test_requires_action_type_and_title(self):
        with self.assertRaises(ValueError):
            ar.normalize_action({"action_type": "blog_post"})
        with self.assertRaises(ValueError):
            ar.normalize_action({"title": "t"})

    def test_uses_default_effort_for_action_type(self):
        a = ar.normalize_action({
            "action_type": "schema_add",
            "title": "Add Article schema",
        })
        self.assertEqual(a.effort_minutes, 15)

    def test_unknown_action_type_falls_back_to_60_min(self):
        a = ar.normalize_action({
            "action_type": "made_up_thing",
            "title": "t",
        })
        self.assertEqual(a.effort_minutes, 60)

    def test_explicit_effort_overrides_default(self):
        a = ar.normalize_action({
            "action_type": "blog_post",
            "title": "t",
            "effort_minutes": 90,
        })
        self.assertEqual(a.effort_minutes, 90)

    def test_effort_floored_at_min(self):
        a = ar.normalize_action({
            "action_type": "x",
            "title": "t",
            "effort_minutes": 1,
        })
        self.assertEqual(a.effort_minutes, ar.MIN_EFFORT)

    def test_score_is_impact_over_effort(self):
        a = ar.normalize_action({
            "action_type": "schema_add",
            "title": "t",
            "signals": {"addresses_critical_finding": True},
        })
        self.assertAlmostEqual(a.predicted_impact, 0.30, places=4)
        self.assertAlmostEqual(a.score, 0.30 / 15, places=6)


class RankActionsTests(unittest.TestCase):

    def _make(self, **kwargs):
        return {"action_type": kwargs.pop("action_type", "blog_post"),
                "title": kwargs.pop("title", "t"),
                **kwargs}

    def test_returns_top_n_sorted_desc(self):
        candidates = [
            self._make(title="low",
                       signals={"category_whitespace": True},
                       effort_minutes=240),
            self._make(title="high",
                       signals={"addresses_critical_finding": True,
                                "covers_uncited_query": True},
                       effort_minutes=15,
                       action_type="schema_add"),
            self._make(title="mid",
                       signals={"covers_uncited_query": True},
                       effort_minutes=60),
        ]
        result = ar.rank_actions(candidates, top_n=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "high")

    def test_top_n_caps_output(self):
        candidates = [self._make(title=f"a{i}") for i in range(20)]
        result = ar.rank_actions(candidates, top_n=5)
        self.assertEqual(len(result), 5)

    def test_diversity_cap_per_type(self):
        # Five blog_posts with same signals, all would rank equally
        candidates = [
            self._make(action_type="blog_post", title=f"b{i}",
                       signals={"covers_uncited_query": True})
            for i in range(5)
        ]
        # Add one schema_add with lower impact
        candidates.append(self._make(action_type="schema_add", title="schema",
                                     signals={"category_whitespace": True}))
        result = ar.rank_actions(candidates, top_n=10, diversity_cap_per_type=2)
        type_counts = {}
        for r in result:
            type_counts[r.action_type] = type_counts.get(r.action_type, 0) + 1
        self.assertLessEqual(type_counts["blog_post"], 2)

    def test_empty_input(self):
        self.assertEqual(ar.rank_actions([]), [])


class SummarizeTests(unittest.TestCase):

    def test_empty_actions_handled(self):
        self.assertIn("no actions", ar.summarize([]))

    def test_summary_contains_each_action(self):
        actions = ar.rank_actions([
            {"action_type": "blog_post", "title": "first action",
             "signals": {"covers_uncited_query": True}},
            {"action_type": "schema_add", "title": "second action",
             "signals": {"addresses_critical_finding": True}},
        ])
        out = ar.summarize(actions)
        self.assertIn("first action", out)
        self.assertIn("second action", out)


class RegionBoostTests(unittest.TestCase):
    """India layer — REGION_MATCH_BOOST applies when property + platform regions match."""

    def test_no_boost_when_property_global(self):
        actions = ar.rank_actions(
            [{"action_type": "blog_post", "title": "t",
              "signals": {"covers_uncited_query": True},
              "platform_region": "india"}],
            property_region="global",
        )
        self.assertFalse(actions[0].region_boost_applied)

    def test_no_boost_when_platform_global(self):
        actions = ar.rank_actions(
            [{"action_type": "blog_post", "title": "t",
              "signals": {"covers_uncited_query": True},
              "platform_region": "global"}],
            property_region="india",
        )
        self.assertFalse(actions[0].region_boost_applied)

    def test_boost_when_both_india(self):
        actions = ar.rank_actions(
            [{"action_type": "blog_post", "title": "t",
              "signals": {"covers_uncited_query": True},
              "platform_region": "india"}],
            property_region="india",
        )
        self.assertTrue(actions[0].region_boost_applied)

    def test_boost_changes_ordering(self):
        """India-region property + tied impact/effort: india platform wins."""
        candidates = [
            {"action_type": "blog_post", "title": "global one",
             "signals": {"covers_uncited_query": True},
             "platform_region": "global"},
            {"action_type": "blog_post", "title": "india one",
             "signals": {"covers_uncited_query": True},
             "platform_region": "india"},
        ]
        actions = ar.rank_actions(candidates, property_region="india")
        self.assertEqual(actions[0].title, "india one")
        self.assertTrue(actions[0].region_boost_applied)
        self.assertGreater(actions[0].score, actions[1].score)

    def test_boost_magnitude(self):
        boost = ar.rank_actions(
            [{"action_type": "blog_post", "title": "x",
              "signals": {"covers_uncited_query": True},
              "platform_region": "india", "effort_minutes": 60}],
            property_region="india",
        )[0]
        base = ar.rank_actions(
            [{"action_type": "blog_post", "title": "x",
              "signals": {"covers_uncited_query": True},
              "platform_region": "global", "effort_minutes": 60}],
            property_region="india",
        )[0]
        self.assertAlmostEqual(boost.score / base.score, ar.REGION_MATCH_BOOST, places=4)


if __name__ == "__main__":
    unittest.main()
