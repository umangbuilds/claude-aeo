# LLM citation rubric

How `parse_response()` in `scripts/citation_check.py` decides `is_cited = 1 / 0 / NULL` for a (query, provider) cell, plus the edge cases Claude should hand-arbitrate when the parser is uncertain.

---

## The parser rule (deterministic)

A response is `is_cited = 1` if either of these is true:

1. The brand `domain` (case-insensitive substring) appears anywhere in the response, OR
2. The brand `name` (case-insensitive, **word-boundary match**) appears anywhere in the response.

Word boundary prevents `moltpe` matching inside `supermoltpex`. Domain is substring because URLs sometimes wrap punctuation oddly (`https://moltpe.com/`, `moltpe.com)`, etc.).

If neither matches, `is_cited = 0`.

If the response is empty or the provider errored out (3 retries exhausted), `is_cited = NULL` — not counted in the rate.

---

## Edge cases that need Claude's judgement

The parser is intentionally simple. For weekly review, Claude should sample 5–10 cells per run and re-arbitrate where the parser may have miscalled. Document the disagreement, then refine the rubric.

### Indirect mention via product / feature name only

> "Some startups in agentic payments offer wallet abstractions for AI agents."

If "wallet abstractions for AI agents" is the operator's signature product feature but the brand name is absent: parser says NOT cited. **Operator-level decision:** should this count? Default: NO. The LLM didn't actually name the brand. But add this to discovered_queries — there's a positioning opportunity to associate the brand with the feature.

### Citation in a list with hedging

> "Companies in this space include Razorpay, PhonePe, and possibly MoltPe."

Parser says CITED (word-boundary hit on "MoltPe"). Citation context preserves "possibly" — useful for the operator to see the hedging language and address it (likely a content gap on the brand's authority signals).

### URL-only citation

> "See https://moltpe.com/docs for the spec."

Parser says CITED (domain substring). Counts. URL-only citations are still surface area — the user will see the brand name in the rendered link.

### Brand name in negative framing

> "MoltPe was acquired in 2024 and is no longer accepting new merchants." (false)

Parser says CITED. The LLM hallucinated. Counts in the citation grid because the brand was named, but Claude should flag the hallucination during analysis — it's a content authority gap that should generate a `wikipedia_talk` or `blog_post` action to correct the record.

### Generic brand name that collides

If the operator's brand name is "Apple" (or any common word), the parser will false-positive heavily. **Workaround:** in property bootstrap, require a domain when brand name is generic. Parser then matches domain (substring) which is unambiguous.

### Cited only via a sub-brand or product line

> "Phantom Wallet, made by Solana, is popular."

If the operator has multiple products with separate brand names, each needs to be its own tracked entity (separate `properties` row or a future v0.2 sub-brands schema). v0.1: one brand per property row.

---

## Citation context — what we capture

For every cited cell, the parser extracts ~320 chars around the first brand mention. This goes into the `citation_context` column. Read it during analysis to:

- Distinguish positive citation from negative
- Spot hallucinations
- See competitor co-mentions
- Note positioning ("MoltPe is the leader in X" vs. "Companies like MoltPe also do X")

---

## Response excerpt — first 500 chars

`response_excerpt` is the first 500 chars of the model response. Use during analysis to see the framing — what the LLM thinks the question is about, before getting to specific brands. Often reveals query-intent mismatch (we tracked a query the LLM interprets totally differently than we expected).

---

## When to retire a query

If, after 6 consecutive weeks, a tracked query has 0 citations across all providers AND no competitors are cited either — the query is probably too niche, too future-tense, or worded in a way no one searches. Retire it via `aeo_loop.py retire-query` (TODO: v0.1 has store-level retire but no CLI flag yet) and replace with a higher-surface variant from `discovered_queries`.

---

## Reading the per-LLM grid

The grid breaks out by provider for a reason. The four LLMs have very different sourcing:

- **OpenAI (ChatGPT default)** — broad pretrain, slow on emerging topics, cites Wikipedia + authoritative news heavily.
- **Anthropic (Claude)** — similar to OpenAI but more conservative on uncertain claims, often refuses to name brands without high confidence.
- **Perplexity** — live web search; citation set is closest to "current SERP." Most volatile week-over-week.
- **Gemini** — Google's training + grounding; closest to AI Overview behaviour.

A citation in Perplexity is the cheapest win (live web). A citation in Anthropic or OpenAI is harder-earned (pretrain corpus). Gemini sits between.

If your citation rate moves only in Perplexity, you have a current-content problem, not a pretrain authority problem. If it moves in all four, your brand authority is genuinely improving.
