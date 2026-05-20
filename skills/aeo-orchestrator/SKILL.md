---
name: aeo-orchestrator
description: "Natural-language routing layer for AEO/SEO/GEO work. Activates when the operator expresses intent in plain English — not when they use a /aeo-loop slash command (those go directly to aeo-loop). Maps intent to the right downstream skill: aeo-loop (weekly cadence, citation tracking), seo-audit, seo-page, seo-technical, seo-content, seo-schema, seo-geo, seo-local, enhance-aeo, aeo-check, brand-serp, content-decay, score-page, and others in the forked SEO ecosystem. Trigger phrases: 'audit my site', 'check citations', 'what is my AEO doing', 'what should I work on', 'are we cited on ChatGPT', 'technical SEO issues', 'find new questions', 'write a brief for', 'what is my citation rate', 'SEO health', 'AI Overview ranking', 'brand SERP', 'content decay'. Does not replace individual skills — routes to them."
user-invokable: false
license: MIT
metadata:
  version: "0.1.0"
  category: seo
---

# aeo-orchestrator — Routing layer for the AEO/SEO ecosystem

When the operator types a natural-language request related to AEO / SEO / GEO / LLM EO, this skill is the dispatcher. It does NOT do the work itself; it picks the right downstream skill and invokes it via the Skill tool (or routes to a slash command).

Reuses the same value-line as aeo-loop: **end-to-end autonomous**. Once intent is parsed and a route is chosen, the orchestrator does NOT pause to ask the operator "should I run X?" — it runs it. The operator only sees the final output. The only exception: when intent is genuinely ambiguous, apply the 3-4 options pattern and surface the routes.

---

## The 3-4 options decisioning rule (mirrored from aeo-loop)

Every time this orchestrator faces a routing choice — or any sub-decision while running a chained route — apply this rule:

1. Generate **3 or 4 distinct interpretations / route options.**
2. Score each on: (a) fit to the user's intent, (b) how much output it produces, (c) cost (LLM tokens, API calls).
3. Pick the best (or **recommended** when close) and execute.
4. Ask the operator only when the decision is:
   - **Supercritical** — irreversible, expensive, or affects another property's data.
   - **Path-changing** — would alter the loop's structure for future weeks.

Otherwise: pick and run. Mention the alternatives in passing in the output so the operator can audit later.

---

## Routing table

Intent on the left → skill / command to invoke on the right. Match on intent **substance**, not exact wording. When in doubt, apply the 3-4 options rule.

### Weekly / cadence operations

| If operator intent is... | Route to | Why |
|---|---|---|
| "weekly run", "let's do this week's AEO", "what should I work on this week", "Monday AEO check" | `/aeo-loop weekly <domain>` | The whole point of the weekly skill. |
| "what's my status", "where am I", "citation rate this week", "how am I doing on AEO" | `/aeo-loop status <domain>` | Lightweight, no LLM polling. |
| "show me the action list", "what are the actions" | `/aeo-loop list-actions <domain>` | Direct list query. |
| "I shipped X, mark it done" | `/aeo-loop mark-done <action-id> --cited-on=<platform>` | Action lifecycle update. |
| "open the browser for action N", "let me submit action N", "help me post action N" | `/aeo-loop assist <action-id>` | Browser-assist (Level A only). |
| "set up a routine", "schedule the weekly", "cron the AEO check" | Load `aeo-loop/references/scheduling-routines.md` and walk operator through chosen option | Routing to docs + setup, not a skill. |

### Single-property audit / page-level work

| Intent | Route to | Why |
|---|---|---|
| "audit my site", "full SEO audit", "site-wide audit" | `Skill(seo-audit, <domain>)` | Parallel sub-agent full audit. |
| "audit this page", "analyze this URL", "deep dive on <url>" | `Skill(seo-page, <url>)` | Single-page deep analysis. |
| "technical SEO check", "indexability", "crawlability", "Core Web Vitals" | `Skill(seo-technical, <url>)` | 9-category technical audit. |
| "content quality", "E-E-A-T", "thin content", "readability" | `Skill(seo-content, <url>)` | Content quality analysis. |
| "schema check", "JSON-LD", "structured data", "add schema for <type>" | `Skill(seo-schema, <url>)` | Detection / validation / generation. |
| "sitemap audit", "generate sitemap", "XML sitemap issues" | `Skill(seo-sitemap, <url>)` | Sitemap analysis. |
| "score this page", "is this page good", "what's the on-page SEO score" | `/score-page <url> <keyword>` (forked command) | 0–100 page scoring. |

### AEO / LLM citation / GEO

| Intent | Route to | Why |
|---|---|---|
| "are we cited on ChatGPT / Perplexity / Gemini / Claude", "AI search visibility", "LLM citations for <brand>" | `Skill(seo-geo, <url>)` for the forked GEO rubric **OR** `/aeo-check <brand> <queries>` (forked command) for direct LLM check **OR** `/aeo-loop status <domain>` for longitudinal data | 3-option case — pick by recency needed. If operator wants the trend, route to aeo-loop. If one-shot snapshot, route to aeo-check. If full rubric audit, route to seo-geo. Explain choice. |
| "AI Overviews", "SGE", "GEO readiness", "ChatGPT search rankings" | `Skill(seo-geo, <url>)` | Forked GEO rubric. |
| "what questions are people asking AI", "AEO discovery", "PAA mining", "find LLM questions" | `/enhance-aeo <domain> <topics>` (forked command) | Deep AI question discovery. |

### Brand / SERP / competitive

| Intent | Route to | Why |
|---|---|---|
| "brand SERP", "what shows up when someone googles my brand" | `/brand-serp <brand>` (forked command) | Brand SERP optimization. |
| "competitor analysis", "what are competitors doing", "competitor pages" | `Skill(seo-competitor-pages, <url>)` | Competitor comparison page generation. |
| "backlink profile", "who links to us", "referring domains" | `Skill(seo-backlinks, <domain>)` | Backlink analysis (free + premium). |

### Content briefing / generation

| Intent | Route to | Why |
|---|---|---|
| "write a brief for <topic>", "content brief", "outline for <query>" | `Skill(seo-content-brief, <topic-or-url>)` | Detailed brief generation. |
| "write a blog post about X", "I need a pillar page" | Draft inline using `aeo-loop/references/drafting-prompts.md` template, save to `./aeo-loop-output/<domain>/<iso-week>/draft-NNN.md` | The aeo-loop drafting templates already cover this. |
| "topic clusters", "content map", "what should I cluster" | `Skill(seo-cluster, <seed-keyword>)` | Semantic clustering. |
| "OG image", "hero image", "social preview image" | `Skill(seo-image-gen, ...)` (banana extension, if installed) | Image gen via Gemini. |
| "image optimization", "alt text", "image SEO" | `Skill(seo-images, <url>)` | On-page image SEO. |

### Local / maps / e-commerce / international

| Intent | Route to | Why |
|---|---|---|
| "local SEO", "Google Business Profile", "GBP", "citations" (local sense), "NAP" | `Skill(seo-local, <url>)` | Local SEO suite. |
| "maps", "geo-grid", "map pack ranking", "competitor radius" | `Skill(seo-maps, <args>)` | Maps intelligence. |
| "e-commerce SEO", "product schema", "marketplace" | `Skill(seo-ecommerce, <url>)` | E-commerce-specific. |
| "hreflang", "multi-language site", "international SEO" | `Skill(seo-hreflang, <url>)` | i18n SEO. |
| "programmatic SEO", "scale pages", "templated pages" | `Skill(seo-programmatic, ...)` | Programmatic SEO. |

### Decay / refresh / drift

| Intent | Route to | Why |
|---|---|---|
| "content decay", "what content is stale", "what needs refreshing" | `/content-decay <client>` (forked command) | Decay detection with priority ranking. |
| "SEO drift", "compare to baseline", "what changed", "regression check" | `Skill(seo-drift, <url>)` | Baseline + compare. |
| "search experience", "page-type mismatch", "user stories" | `Skill(seo-sxo, <url>)` | SXO analysis. |

### Google API data

| Intent | Route to | Why |
|---|---|---|
| "GSC data", "Search Console queries", "PageSpeed Insights", "CrUX", "GA4 organic traffic" | `Skill(seo-google, <command> <url>)` | Google APIs suite. |

### Strategic / planning

| Intent | Route to | Why |
|---|---|---|
| "SEO plan", "strategy for <business-type>", "where do I start" | `Skill(seo-plan, <business-type>)` | Strategic planning by industry. |
| "new client onboarding" | `/new-client <client>` (forked command) if available, else fall back to bootstrap a property via `/aeo-loop add-property` + `/aeo-loop bootstrap` | Client onboarding flow. |
| "monthly report", "deliverable for client" | `Skill(seo-google, report)` for the forked PDF / Excel report style, plus `/aeo-loop status` for citation summary | Multi-skill compose. |

### Setup / config / meta

| Intent | Route to | Why |
|---|---|---|
| "how do I install", "first time setup", "what API keys do I need" | Read `aeo-loop/README.md` and `aeo-loop/references/scheduling-routines.md` | Documentation. |
| "what skills are available", "what can I do", "what commands are there" | List this routing table | Self-referential. |

---

## Routing examples (voice samples)

### Clear intent — route and run, do not ask

> Operator: "audit moltpe.com"
>
> Orchestrator (internal): Single-property full audit. Route to `Skill(seo-audit, moltpe.com)`. Run.

### Ambiguous intent — apply 3-4 options rule

> Operator: "what's my AEO doing"
>
> Orchestrator: Three honest reads. (1) Citation rate this week → `/aeo-loop status`. (2) Full GEO rubric audit on the homepage → `Skill(seo-geo, moltpe.com)`. (3) Direct LLM visibility check across the 4 engines → `/aeo-check moltpe agentic-payments`. **Recommended: 1** because it gives you week-over-week trend. Want 2 or 3 instead? Otherwise running 1 now. (If no response within a few seconds in interactive mode, run the recommended.)

### Compound intent — chain multiple routes

> Operator: "audit moltpe.com and tell me which actions to take this week"
>
> Orchestrator (internal): That's "audit + brief". Two routes in sequence: `Skill(seo-audit, moltpe.com)` for the audit + `/aeo-loop weekly moltpe.com` for the brief and action list. Run the audit first; pipe its findings into the weekly run. Or just route to `/aeo-loop weekly moltpe.com` which already audits as Step 1 of the loop. Pick the second (subsumes the first). Run.

### Intent that needs setup first

> Operator: "what's my citation rate"
>
> Orchestrator: Check `/aeo-loop status moltpe.com` first. If the response says no LLM keys configured (exit 2), route the operator to setup: print the relevant lines from `aeo-loop/README.md` step 3, then re-attempt.

### Off-route intent — decline cleanly

> Operator: "set up a cron job to auto-post to Reddit every day"
>
> Orchestrator: Decline. This crosses the bot line in aeo-loop's Non-goal #2. Quote that line, offer the legitimate alternative: `/aeo-loop weekly` produces drafts; `/aeo-loop assist <action-id>` opens the browser for manual posting. Do not route to anything that auto-posts.

---

## When this skill activates

Trigger on natural-language intent matching any pattern in the routing table. Do not require slash-command invocation — auto-activate when the operator is clearly in AEO/SEO territory.

Specific trigger phrases that map directly to routes (sample, not exhaustive):

- "audit", "score", "analyze", "check", "test" (the action verbs of SEO/AEO work)
- "citation", "cited", "AI Overview", "ChatGPT", "Perplexity", "Gemini", "LLM"
- "rank", "position", "SERP", "Google", "GSC", "Search Console"
- "schema", "JSON-LD", "structured data"
- "competitor", "vs", "compared to"
- "content", "blog", "post", "brief", "outline", "pillar"
- "backlink", "referring domain", "link profile"
- "local", "GBP", "Google Business", "maps"
- "weekly", "monthly", "cadence", "routine", "schedule"
- Property names / domains that have been registered (route to that property's commands)

Does NOT activate on:

- Pure code questions ("how do I write a Python function") — outside scope
- Build/launch/product strategy questions — those go to DhurandharOS workflow if loaded
- General questions ("what is SEO") — these are background, not actionable routes

---

## What this skill does NOT do

- **Does not duplicate aeo-loop's weekly chain.** The 8-step loop lives in `aeo-loop/SKILL.md`. The orchestrator just dispatches to `/aeo-loop weekly`.
- **Does not modify upstream forked skills.** AC-9 from `aeo-loop-prd.md` Section 5 still applies. Strictly additive.
- **Does not run any LLM HTTP calls itself.** Multi-LLM polling lives in `aeo-loop/scripts/citation_check.py`. The orchestrator only routes.
- **Does not generate content.** Routes to the right content-producing skill (aeo-loop draft step, seo-content-brief, seo-content).
- **Does not pause the loop mid-run for confirmation.** End-to-end autonomy held — once routed, the downstream skill executes its own loop without orchestrator interruption.
- **Does not route to bot-territory actions.** Anything that auto-submits / auto-posts / auto-sends gets declined per aeo-loop Non-goal #2.

---

## Failure modes

| Failure | Handling |
|---|---|
| Intent genuinely ambiguous | Apply 3-4 options rule. Pick recommended, mention alternatives, run. |
| Required skill not installed (forked skill missing) | Surface the missing skill name + install path. Do not silently fall back to a worse alternative without saying so. |
| Property not registered with aeo-loop | Route to `/aeo-loop add-property <domain>` first, then re-attempt the original intent. |
| LLM keys missing | Route to the relevant section of `aeo-loop/README.md` for setup. |
| Two skills are equally good fits | Pick the one with lower cost (free over paid; cached over fresh). Mention the alternative. |
| Operator asks for something that crosses a non-goal | Decline cleanly, quote the non-goal, offer the legitimate alternative. |

---

## How this skill is itself "additive"

`aeo-orchestrator` does not modify any other skill. It only reads other skills (their descriptions and routing tables) and invokes them. All routing decisions are documented inline in this file so the operator can read and adjust.

Updating the routing table is the maintenance loop: every time a new skill is added to the project, add a row to the routing table here. Every time the routing surprises the operator in a bad way, refine the row.

---

## Relationship to aeo-loop

| Skill | Owns |
|---|---|
| **aeo-orchestrator** (this file) | Natural-language → skill routing across the whole ecosystem. |
| **aeo-loop** | The 8-step weekly chain. Once routed to, runs end-to-end autonomously. |
| **forked claude-seo skills and commands** | The individual capabilities (audit, schema, geo, scoring, decay, etc.). |

Three layers, separate concerns:

```
operator types natural language
   ↓
aeo-orchestrator (routes)
   ↓
aeo-loop OR a forked skill (executes)
   ↓
report / draft / browser-assist / data persisted
```

---

## License

MIT. Original to this project. Strictly additive over the forked claude-seo ecosystem (AC-9 from `aeo-loop-prd.md`, with the single documented exception in `claude-seo/FORK-MODIFICATIONS.md`).
