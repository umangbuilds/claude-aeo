# Third-party licenses

claude-aeo is built on top of two upstream open-source SEO skill collections, both MIT-licensed.
The four net-new modules (`citation_check.py`, `action_rank.py`, `browser_assist.py`, `store.py`)
are original work with no upstream equivalent.

---

## Upstream repositories

| Upstream | Author | License | What was taken |
|---|---|---|---|
| [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | Agrici Daniel | MIT | SEO skill patterns: site audit (`seo-audit`), GEO readiness (`seo-geo`), content briefs, keyword clustering (`seo-cluster`), schema JSON-LD generation (`seo-schema`), E-E-A-T scoring, local SEO, Google API integration helpers. Used as the `claude-seo` dependency installed by `setup.sh`. Not modified — treated as read-only upstream per AC-9. |
| [mangollc/claude-seo-skill](https://github.com/mangollc/claude-seo-skill) | MangoCo LLC | MIT | SEO assistant patterns: website audit structure, keyword research flows, content scoring, backlink strategy templates, AI search optimisation (`enhance-aeo`, `aeo-check`, `brand-serp`). Contributed skill-routing patterns used in `aeo-orchestrator`. Not modified — treated as read-only upstream per AC-9. |

---

## What claude-aeo adds (net-new, not derived from upstream)

| Module | Why it is net-new |
|---|---|
| `skills/aeo-loop/scripts/citation_check.py` | Upstream had citation checking only via DataForSEO's paid scraper. Direct-API free-tier calls to OpenAI, Anthropic, Perplexity, Gemini — no upstream equivalent. |
| `skills/aeo-loop/scripts/action_rank.py` | Weekly prioritised action list ranked by citation impact / effort. No upstream equivalent. |
| `skills/aeo-loop/scripts/browser_assist.py` | Browser-assist URL builder — pre-fill + open for off-site submission (Level A, no auto-post). No upstream equivalent. |
| `skills/aeo-loop/scripts/store.py` | Longitudinal SQLite store — week-over-week delta, run tracking, citation grid, action history. No upstream equivalent. |

---

## MIT license compliance

Both upstream repositories are MIT-licensed. MIT requires:
- LICENSE files are preserved in the upstream installs — satisfied (not modified).
- Attribution in any redistribution — satisfied by this file and the repo README.

No additional conditions (no copyleft, no attribution-in-binary clauses, no non-commercial restrictions).

---

## Upstream LICENSE texts

**AgriciDaniel/claude-seo** — MIT License, copyright Agrici Daniel.
Full text: https://github.com/AgriciDaniel/claude-seo/blob/main/LICENSE

**mangollc/claude-seo-skill** — MIT License, copyright MangoCo LLC.
Full text: https://github.com/mangollc/claude-seo-skill (LICENSE file; confirm at distribution time if moved).
