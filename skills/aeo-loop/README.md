# aeo-loop

> **New to AEO / SEO / GEO?** Read [`GETTING-STARTED.md`](GETTING-STARTED.md) instead — it assumes no marketing or coding background and walks through setup in plain English with a real example. This README is the technical reference; for the friendly walkthrough, start there.

Weekly AEO / SEO / GEO cadence for operators running across multiple properties. One command per property, every week, produces:

- A prioritized action-list of 5–10 items, ranked by predicted citation impact and effort.
- A multi-LLM citation-rate delta across OpenAI / Anthropic / Perplexity / Gemini.
- Browser-assisted execution for off-site actions — the skill pre-fills drafts on Reddit / Wikipedia / outreach forms; the operator reviews and submits.

`aeo-loop` does NOT replace your SEO/AEO skill collection. It sits on top of an existing `claude-seo` install (forked from open-source upstream) and adds the prioritization layer, longitudinal citation store, and browser-assist execution that the upstream skills don't provide.

The PRD is in [`aeo-loop-prd.md`](../../../aeo-loop-prd.md) at the working-directory root.

---

## Workflow philosophy — three principles the skill operates by

These are baked into the skill's behaviour. Anyone using `aeo-loop` inherits them by default — Claude reads them from `SKILL.md` on every activation and applies them to every decision the loop makes.

### 1. 3–4 options decisioning

Every choice the skill makes — which queries to retire, which platform to draft for, which competitor angle to compare, which outline variant to expand — follows the same pattern:

1. Generate 3 or 4 distinct options.
2. Score on fit + effort + reversibility.
3. Pick the **recommended** (or best on tie) and execute.
4. Mention the alternatives in passing in the output so you can audit the decision later.

You will rarely be asked "which option?" — only when the decision is **supercritical** (irreversible, expensive, affects another property's data) or **path-changing** (would alter the loop's structure for future weeks). For everything else, the skill picks and runs.

### 2. End-to-end autonomy

`/aeo-loop weekly <domain>` runs all 8 steps in one invocation without mid-flow confirmation prompts. The skill never pauses to ask "should I continue?" between Audit → Discover → Test → Analyze → Brief → Draft → Assist-prep → Track. You see one progress line per step and the final report.

The only stop conditions:
- A destructive command outside agreed scope (would modify upstream forked files, delete user data, push to a public repo without explicit ask).
- Genuinely irreducible ambiguity that the 3–4 options rule cannot resolve.

Submission of off-site actions stays operator-only — that is by design (see Principle 3).

### 3. Browser-assist Level A only — no auto-submission

The skill prepares drafts for Reddit threads, Wikipedia edits, X / LinkedIn posts, outreach emails. It pre-fills the form on the right platform when you run `/aeo-loop assist <action-id>`. **You click Submit.** The skill never POSTs anything.

Held firm even when paid scheduler APIs (Buffer, Hootsuite, Lemlist, Apollo) become available later. The cost of one Reddit / Wikipedia ban is higher than the time saved by automation. The line does not bend.

---

## Setup

### 1. Prerequisites

- Python 3.9 or newer (3.10+ recommended).
- `claude-seo` already installed under `.claude/skills/claude-seo/` (forked from upstream and copied in earlier — see project working directory).
- At least one LLM API key. Two or more for meaningful cross-LLM citation comparison.

### 2. Initialize

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py init
```

This creates:

- `~/.config/aeo-loop/keys.toml` — credential file (chmod 600). Empty by default.
- `~/.local/share/aeo-loop/store.db` — SQLite store, schema v1.

### 3. Add API keys

Edit `~/.config/aeo-loop/keys.toml`. Free tier needs only LLM keys; everything else is opt-in.

```toml
[llm]
openai     = "sk-..."
anthropic  = "sk-ant-..."
perplexity = "pplx-..."     # optional
gemini     = "..."           # optional

[seo_data]                   # ALL OPTIONAL — paid tiers only
dataforseo_login    = ""
dataforseo_password = ""
serpapi             = ""
firecrawl           = ""

[image_gen]
gemini_image = ""            # falls back to [llm].gemini if blank

[gsc]
oauth_client_json = ""       # path to Google OAuth client_secret*.json

[browser]
profile = "default"
```

### 4. Register a property

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py add-property example.com \
  --brand "Example" --one-liner "We do agentic payments" --category "fintech"
```

**India layer (optional, v0.1).** Add `--region india` if the brand's primary
buyers are in India. Currency defaults to `INR`. See
[`references/india-platforms.md`](references/india-platforms.md) for what this
unlocks — geo-pinned LLM prompts, INR-aware pricing prompts, Quora India /
JustDial / IndiaMART / MouthShut platform support, Indian publication
outreach targets, and a +15% score boost for India-region actions.

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py add-property moltpe.com \
  --brand "MoltPe" --one-liner "agentic payments" --category "fintech" \
  --region india
```

### 5. Bootstrap (queries, competitors, baseline)

The `bootstrap` subcommand is interactive in v0.1 — invoked from the slash command, Claude prompts for the inputs. Once Claude collects them, it runs:

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py add-query example.com "what are agentic payments" --query-type aeo
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py add-competitor example.com "Razorpay" --competitor-domain razorpay.com
```

### 6. Weekly run

```bash
/aeo-loop weekly example.com
```

Or directly:

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py weekly example.com
```

This runs the 8-step loop (audit, discover, test, analyze, brief, draft, assist-prep, track) and produces:

```
./aeo-loop-output/example.com/2026-W21/
  report.md
  citation_results.json
  candidates.json
  draft-001.md
  draft-002.md
  ...
```

The `report.md` is the operator-facing deliverable.

### 7. Set up routines (strongly recommended)

Run the loop on a schedule so you don't have to remember to invoke it. Five options ranked by easiest-first in [`references/scheduling-routines.md`](references/scheduling-routines.md):

- **Claude Code `/schedule`** (recommended for solo operators)
- **Claude Code `/loop`** (self-paced inside a session)
- **Local cron + headless `claude -p`** (macOS / Linux)
- **launchd** (macOS native, catches missed runs)
- **GitHub Actions** (cloud-scheduled, multi-property, team-friendly)

Recommended cadence:

| Cadence | Command | Notes |
|---|---|---|
| Weekly, Monday 9am | `/aeo-loop weekly <domain>` | Full 8-step loop. The main run. |
| Daily, weekday 8am (optional) | `/aeo-loop status <domain>` | Lightweight status check, surfaces unexpected drops. |

### 8. Execute off-site actions

When the operator is ready to submit a Reddit thread / Wikipedia edit / outreach email from the action list:

```bash
/aeo-loop assist <action-id>
```

Prints the URL to open and the clipboard content. **The skill never clicks Submit. The operator does.**

After submitting:

```bash
/aeo-loop mark-done <action-id> --cited-on=reddit
```

---

## Tiers

| Tier | What you get | Cost |
|---|---|---|
| **Free** (default) | Multi-LLM citation tracking, owned-property GSC ranks, forked SEO audit / GEO / schema skills, forked AEO discovery commands, browser-assist (Level A), longitudinal SQLite store, weekly action-list. | LLM API spend only (~$5–10/mo per property at v0.1 cadence). |
| **Enhanced** (opt-in) | + Competitor SERP tracking via SerpAPI or DataForSEO. + JS-rendered full-site crawl via Firecrawl. + Image generation via banana / Gemini. | Each provider has its own billing. |

The free tier runs end-to-end; enhanced features unlock automatically when their keys are present in `keys.toml`. The skill recommends enhanced providers in the action-list when a gap would close with one — never required.

---

## What `aeo-loop` will NOT do

These are hard non-goals (PRD Section 3):

- Auto-submit / auto-post / scheduled posting — even through paid scheduler APIs.
- Account creation, impersonation, automated outreach send.
- Pipeline / revenue attribution (lives in CRM).
- Multi-user / team collaboration (single-operator-per-laptop).
- Localization beyond English (v0.1).

The "no auto-submit" line is the value-line that keeps the skill out of bot territory and out of account-ban exposure on Reddit / Wikipedia / X.

---

## Layout

```
.claude/skills/aeo-loop/
├── SKILL.md                          # Claude's entry point + orchestration
├── README.md                         # this file
├── commands/
│   └── aeo-loop.md                   # /aeo-loop slash command
├── schemas/
│   └── store_v1.sql                  # SQLite schema (versioned)
├── scripts/
│   ├── aeo_loop.py                   # CLI entry point
│   ├── config.py                     # credential / capability detection
│   ├── store.py                      # SQLite wrapper
│   ├── citation_check.py             # multi-LLM polling + parse
│   ├── action_rank.py                # prioritization algorithm
│   └── browser_assist.py             # Level-A URL builder
├── tests/
│   ├── test_config.py
│   ├── test_store.py
│   ├── test_citation_check.py
│   ├── test_action_rank.py
│   ├── test_browser_assist.py
│   └── test_cli_smoke.py
└── references/
    ├── action-taxonomy.md
    ├── llm-citation-rubric.md
    └── drafting-prompts.md
```

---

## Testing

```bash
cd .claude/skills/aeo-loop
python3 -m unittest discover -s tests -t . -v
```

All tests stdlib-only — no pip installs required. 120+ tests cover the foundation, helpers, citation parsing, prompt-injection mitigations, key redaction, domain-boundary matching, model overrides, and CLI smoke flow.

---

## Status

v0.1 ships:

- Full free tier loop end-to-end
- CLI for all subcommands listed in `SKILL.md`
- 100+ stdlib tests
- Browser-assist for Reddit, Wikipedia (article + talk page), X, LinkedIn, Hacker News, email, generic forms

Deferred to v0.2 or later (per PRD Section 11):

- `THIRD_PARTY_LICENSES.md` attribution write-up (required before external distribution).
- Competitor SERP rank tracking via free means.
- OS keychain storage instead of plaintext `keys.toml`.
- Hindi / regional Indian language localization (English-only at v0.1; India-region geo-pinning is in v0.1).
- Cron / launchd scheduling wrapper (currently external — operator's own crontab).
- Pre-loaded Indian competitor sets per category (operator-supplied via `add-competitor`).
- Indian content-calendar triggers (Diwali, Holi, IPL, budget day, RBI policy day).

---

## License

MIT. See repo-root LICENSE (or in v0.1, see PRD Open Questions — attribution write-up pending feature settling).
