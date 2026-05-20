"""Action ranking algorithm for aeo-loop.

The weekly loop generates candidate actions (Claude does the generation via
the 8-step loop, see codex/AGENTS-aeo-loop.md). This module assigns a deterministic score and returns the top N.

Score = predicted_impact / max(effort_minutes, MIN_EFFORT). Higher is better.

predicted_impact is a 0..1 weighted combination of signal flags:
  - addresses_critical_finding   (0.30)
  - covers_uncited_query         (0.25)
  - displacement_opportunity     (0.20)
  - ranking_improvement_potential(0.15)
  - category_whitespace          (0.10)

Signals are booleans or 0..1 floats; weights sum to 1.0 so impact is bounded.

Effort defaults are by action_type. The caller can override with explicit
effort_minutes in the action dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


MIN_EFFORT = 5  # floor so divide-by-effort doesn't explode

# Multiplicative score boost when the action's target region matches the
# property's region. Kept modest (1.15x) so the boost re-ranks ties and close
# competitors but does not displace a clearly higher-impact global action.
REGION_MATCH_BOOST = 1.15
REGION_DEFAULT = "global"

EFFORT_DEFAULTS_MIN: Dict[str, int] = {
    # On-site
    "schema_add": 15,
    "internal_link": 10,
    "page_optimize": 60,
    "blog_post": 240,
    "pillar_page": 480,
    "image_gen": 30,
    # Off-site
    "reddit_thread": 30,
    "wikipedia_edit": 60,
    "wikipedia_talk": 15,
    "hacker_news_post": 20,
    "outreach_email": 20,
    "social_post": 15,
    "guest_post_pitch": 45,
    "podcast_pitch": 30,
}

SIGNAL_WEIGHTS: Dict[str, float] = {
    "addresses_critical_finding": 0.30,
    "covers_uncited_query": 0.25,
    "displacement_opportunity": 0.20,
    "ranking_improvement_potential": 0.15,
    "category_whitespace": 0.10,
}

# Sanity check — weights must sum to 1.0 for impact to be bounded [0, 1].
assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 1e-9, "signal weights must sum to 1.0"


@dataclass
class ScoredAction:
    """One candidate action with computed impact / effort / score."""

    action_type: str
    title: str
    description: str = ""
    target_url: Optional[str] = None
    signals: Dict[str, float] = field(default_factory=dict)
    predicted_impact: float = 0.0
    effort_minutes: int = MIN_EFFORT
    score: float = 0.0
    extra: Dict[str, str] = field(default_factory=dict)
    platform_region: str = REGION_DEFAULT
    region_boost_applied: bool = False


def _coerce_signal(value) -> float:
    """Booleans / numeric → float 0..1. Anything else → 0."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    if v < 0:
        return 0.0
    if v > 1:
        return 1.0
    return v


def compute_impact(signals: Dict[str, float]) -> float:
    """Weighted sum of signal values per SIGNAL_WEIGHTS."""
    return sum(
        SIGNAL_WEIGHTS[name] * _coerce_signal(signals.get(name, 0))
        for name in SIGNAL_WEIGHTS
    )


def default_effort_for(action_type: str) -> int:
    return EFFORT_DEFAULTS_MIN.get(action_type, 60)


def normalize_action(raw: Dict, property_region: str = REGION_DEFAULT) -> ScoredAction:
    """Take a candidate action dict and produce a fully-scored ScoredAction.

    Required keys: action_type, title.
    Optional: description, target_url, signals (dict), effort_minutes (int),
              extra (dict), platform_region (str).

    If property_region matches the action's platform_region and both are
    non-global, score is multiplied by REGION_MATCH_BOOST so an Indian-platform
    action wins ties against a global one when the property is India-region.
    """
    if "action_type" not in raw or "title" not in raw:
        raise ValueError("normalize_action requires action_type and title")

    action_type = raw["action_type"]
    signals = raw.get("signals", {}) or {}
    impact = compute_impact(signals)
    effort = int(raw.get("effort_minutes") or default_effort_for(action_type))
    if effort < MIN_EFFORT:
        effort = MIN_EFFORT
    base_score = impact / effort

    platform_region = (raw.get("platform_region") or REGION_DEFAULT).lower()
    prop_region = (property_region or REGION_DEFAULT).lower()
    region_boost_applied = (
        platform_region == prop_region
        and platform_region != REGION_DEFAULT
    )
    final_score = base_score * (REGION_MATCH_BOOST if region_boost_applied else 1.0)

    return ScoredAction(
        action_type=action_type,
        title=raw["title"],
        description=raw.get("description", "") or "",
        target_url=raw.get("target_url"),
        signals={k: _coerce_signal(v) for k, v in signals.items()},
        predicted_impact=round(impact, 4),
        effort_minutes=effort,
        score=round(final_score, 6),
        extra=raw.get("extra", {}) or {},
        platform_region=platform_region,
        region_boost_applied=region_boost_applied,
    )


def rank_actions(
    candidates: List[Dict],
    top_n: int = 10,
    diversity_cap_per_type: Optional[int] = None,
    property_region: str = REGION_DEFAULT,
) -> List[ScoredAction]:
    """Score every candidate, sort descending, return top N.

    If diversity_cap_per_type is set, no more than that many actions of the
    same action_type appear in the output (prevents a flood of one kind).

    property_region applies REGION_MATCH_BOOST to candidates whose
    platform_region matches (and is non-global).
    """
    scored = [normalize_action(c, property_region=property_region) for c in candidates]
    scored.sort(key=lambda a: a.score, reverse=True)

    if diversity_cap_per_type is None:
        return scored[:top_n]

    out: List[ScoredAction] = []
    type_counts: Dict[str, int] = {}
    for action in scored:
        n = type_counts.get(action.action_type, 0)
        if n >= diversity_cap_per_type:
            continue
        out.append(action)
        type_counts[action.action_type] = n + 1
        if len(out) >= top_n:
            break
    return out


def summarize(actions: List[ScoredAction]) -> str:
    """Human-readable table for weekly reports."""
    if not actions:
        return "(no actions ranked)"
    lines = [
        "| Rank | Type | Title | Impact | Effort (min) | Score |",
        "|------|------|-------|--------|--------------|-------|",
    ]
    for i, a in enumerate(actions, 1):
        title = a.title if len(a.title) <= 50 else a.title[:47] + "..."
        lines.append(
            f"| {i} | {a.action_type} | {title} | "
            f"{a.predicted_impact:.2f} | {a.effort_minutes} | {a.score:.4f} |"
        )
    return "\n".join(lines)
