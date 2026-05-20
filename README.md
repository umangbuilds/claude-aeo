<div align="center">

# aeo-loop (Codex CLI)

### One command. Your brand in every AI answer.

Track whether ChatGPT, Claude, Perplexity, and Gemini cite you —<br>and get a weekly shortlist of the specific actions that will make them start.

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Codex CLI](https://img.shields.io/badge/Codex%20CLI-skill-10a37f)](https://github.com/openai/codex)
[![Tests](https://img.shields.io/badge/tests-168%20passing-brightgreen)](skills/aeo-loop/tests/)
[![Made for India](https://img.shields.io/badge/made%20for-India-ff9933)](https://github.com/umangbuilds/claude-aeo#built-for-india)
[![DhurandharOS](https://img.shields.io/badge/DhurandharOS-module-1a1a2e)](https://github.com/umangbuilds/dhurandhar-os)

<br>

> **Not affiliated with or endorsed by OpenAI or Anthropic.**

</div>

---

## Why this matters right now

Search is changing faster than most founders realise.

When someone asks ChatGPT *"best accounting software for Indian freelancers"* or Perplexity *"which UPI app has the lowest MDR for kirana stores"* — they get a direct answer. Not ten blue links. A direct answer, with specific brands named.

That answer is being assembled from training data, forum threads, blog posts, documentation, and citations from trusted sources. **If your brand isn't in that evidence base, you don't get named.**

Traditional SEO optimises for Google's crawler. AEO (Answer Engine Optimisation) optimises for the evidence base that AI models draw on. They require different actions. This skill runs the AEO cadence for you, every week, automatically.

---

## The gap most founders don't know exists

Right now, across the queries that should mention your product, AI chatbots are either citing you, citing a competitor, or citing no one. Most founders have never checked.

This skill measures that gap — your **citation rate** — across four AI services, tracks it week over week, and generates the specific content (threads, articles, citations, outreach) that closes it.

---

## What you get each week

```bash
/aeo-loop weekly yourdomain.com
```

One command. 5–15 minutes. Then:

<br>

**Citation rate across all four AI services:**

```
Week 21 report — yourdomain.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Query                                ChatGPT  Claude  Perplexity  Gemini
─────────────────────────────────────────────────────────────────────────
"best tool for [your category]"         ✓        ✓        —           —
"how to [your use case]"                —        —        —           —
"[your category] for [your audience]"   —        ✓        —           ✓
"[competitor alternative] India"        —        —        —           —
─────────────────────────────────────────────────────────────────────────
Citation rate this week                50%      75%      0%         25%   →  38% avg
Last week                              42%      75%      0%         17%   →  34% avg
Change                                 +8pp      =       =          +8pp  →  +4pp
```

<br>

**A ranked action list — 10 specific things to do, ordered by impact vs. effort:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   Type              Title                             Effort   Impact
─────────────────────────────────────────────────────────────────────────
1   Quora answer      "Which [category] tools work      20 min   HIGH
                       best for [use case]?"
2   Blog post         "[Competitor] vs [Your Brand]:    2 hrs    HIGH
                       An honest comparison"
3   Reddit thread     r/[community] — share your        30 min   MED
                       case study
4   Wikipedia edit    Add [your brand] to the           15 min   MED
                       [category] page citations
5   Outreach          YourStory / Inc42 story pitch     45 min   MED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

<br>

**For every action — a ready-to-submit draft:**

```bash
/aeo-loop assist 1
```

Opens your browser with the draft pre-filled. You read it, edit if you want, click Submit. That's it.

**The skill never auto-posts. You always click Submit yourself.** This is a hard line, not a feature toggle.

---

## How the weekly cadence compounds

```
Week 1 (one-time setup)
  bootstrap → add 5–10 queries → add 3–5 competitors → run baseline
  takes ~20 minutes

Week 2 onwards — every Monday
  /aeo-loop weekly yourdomain.com
  → citation rate vs. last week
  → new action list
  → pick 3 actions that fit your week
  → /aeo-loop assist <id> for each
  → you click Submit
  → /aeo-loop mark-done <id>
  takes ~10 minutes of your attention

Months 2–3
  Actions from Week 2 start appearing in AI training pipelines
  Citation rate begins moving
  Skill surfaces which action types moved the needle for your domain
```

Most operators see measurable citation movement within 6–10 weeks of consistent weekly runs.

---

## Install

### Codex CLI (terminal)

```bash
git clone https://github.com/umangbuilds/claude-aeo
cd claude-aeo
bash codex/setup-codex.sh
```

The installer verifies Python 3.10+, stages the `/aeo-loop` slash command into `~/.codex/prompts/`, and scaffolds the config + SQLite store.

Then launch Codex inside the repo so `AGENTS.md` is auto-loaded:

```bash
codex
```

### Add API keys

Open `~/.config/aeo-loop/keys.toml` and fill in at least 2:

```toml
[llm]
openai     = "sk-..."
anthropic  = "sk-ant-..."
perplexity = ""
gemini     = ""
```

You need at least 2 to run the citation matrix. 4 gives you the full cross-LLM picture.
API call cost: ~₹40–160 per week depending on how many queries you track.

### Bootstrap your first property

Launch Codex from the repo:

```bash
codex
```

Then inside Codex, three slash commands:

```
/aeo-loop init
/aeo-loop add-property yourdomain.com --brand="Your Brand"
/aeo-loop bootstrap yourdomain.com
```

`bootstrap` is conversational — Codex looks at your site, proposes
queries and competitors, you edit / approve, and it runs the baseline
citation check.

Then once a week:

```
/aeo-loop weekly yourdomain.com
```

**Full guide:** [codex/INSTALL-CODEX.md](codex/INSTALL-CODEX.md)
**Operating contract** (what the agent reads): [AGENTS.md](AGENTS.md) + [codex/AGENTS-aeo-loop.md](codex/AGENTS-aeo-loop.md)

---

## Commands

| Command | What it does |
|---|---|
| `/aeo-loop init` | First-time setup — creates config + local SQLite store |
| `/aeo-loop add-property yourdomain.com --brand="..." --one-liner="..."` | Register your site |
| `/aeo-loop bootstrap yourdomain.com` | Guided setup: queries, competitors, baseline run |
| `/aeo-loop weekly yourdomain.com` | Weekly run — citation check + ranked action list |
| `/aeo-loop status yourdomain.com` | Current citation rate + pending actions at a glance |
| `/aeo-loop assist <action-id>` | Open browser with action draft pre-filled; you click Submit |
| `/aeo-loop mark-done <action-id>` | Record what shipped; builds your history of what worked |

---

## Built for India

```bash
python3 skills/aeo-loop/scripts/aeo_loop.py add-property yourdomain.com \
  --brand="Your Brand" --one-liner="What you do" --region india
```

`--region india` activates the full India layer:

| | Without `--region india` | With `--region india` |
|---|---|---|
| LLM prompts | Global context | Geo-pinned to India |
| Pricing | USD | INR |
| Platform priority | Generic | Quora India, JustDial, IndiaMART, MouthShut |
| Outreach list | Generic publications | YourStory, Inc42, ET Tech, The Ken, Entrackr |
| Citation boost | Standard | +15% weight for India-relevant citations |

If your users are in India, use this. The global defaults are not tuned for Indian search behaviour or Indian AI usage patterns.

---

## Without this vs. with this

| Manual approach | aeo-loop |
|---|---|
| Check each AI chatbot manually, one at a time | One command checks all four |
| No consistent tracking — you forget what it was last week | SQLite store, week-over-week delta |
| No idea what to do about a low citation rate | Ranked action list generated automatically |
| Write every piece of content from scratch | Draft ready for every action |
| No record of what moved the needle | `mark-done` builds your history |
| 3–5 hours/week if done properly | ~10 minutes of attention, skill handles the rest |

---

## Requirements

- **[Codex CLI](https://github.com/openai/codex)** — OpenAI's terminal agent
- **Python 3.10+** — [python.org](https://python.org)
- **2+ LLM API keys** — any combination of OpenAI, Anthropic, Perplexity, Gemini

---

## Repo structure

```
claude-aeo/
├── AGENTS.md                         — Codex auto-loads this for operating rules
├── README.md                         — this file
├── codex/
│   ├── AGENTS-aeo-loop.md            — subcommand surface + 8-step weekly recipe
│   ├── INSTALL-CODEX.md              — full install guide
│   ├── prompts/aeo-loop.md           — slash command (staged to ~/.codex/prompts/)
│   └── setup-codex.sh                — installer
├── skills/aeo-loop/                  — the weekly loop skill (agent-agnostic core)
│   ├── scripts/
│   │   ├── aeo_loop.py               — CLI entry point
│   │   ├── citation_check.py         — queries all 4 LLMs, stores results
│   │   ├── store.py                  — SQLite backend
│   │   ├── action_rank.py            — ranks actions by impact/effort
│   │   └── browser_assist.py         — opens browser with draft pre-filled
│   ├── references/                   — weekly step guides, India platform list
│   ├── assets/templates/             — report.md, draft-NNN.md
│   └── tests/                        — 168 tests, all green
└── THIRD_PARTY_LICENSES.md           — attribution
```

---

## FAQ

<details>
<summary><strong>How is this different from standard SEO tools?</strong></summary>

SEO tools (Ahrefs, SEMrush, etc.) optimise for Google's crawler — backlinks, keyword density, page speed. AI search engines don't work that way. They pull from training data and citation patterns, not real-time crawls. aeo-loop targets the evidence base that AI models draw on, which requires different content and different platforms.

</details>

<details>
<summary><strong>Will this guarantee my brand gets cited?</strong></summary>

No. Citation rate depends on your content quality, domain authority, and the competitive landscape in your category. What this skill does is measure your current rate, identify the specific gaps, and generate the content most likely to move the needle based on how citation patterns work across these models. Consistent weekly runs over 2–3 months is where operators see meaningful movement.

</details>

<details>
<summary><strong>What does it actually cost per week?</strong></summary>

API calls to 4 LLM services for 5–10 tracked queries: roughly ₹40–160/week depending on query count and which providers you use. The skill itself is free. Your API keys are your own — aeo-loop never touches billing or makes calls outside the weekly run.

</details>

<details>
<summary><strong>Can I use this for multiple websites?</strong></summary>

Yes. Each property is registered separately. Run `/aeo-loop weekly site1.com` and `/aeo-loop weekly site2.com` independently. Each gets its own citation history and action list.

</details>

<details>
<summary><strong>Does this work with Claude Code instead of Codex?</strong></summary>

This branch is Codex-only. The agent surface (`AGENTS.md`, `codex/`, the slash prompt) is built for OpenAI Codex CLI. The underlying Python core is agent-agnostic — porting back to a Claude plugin is straightforward, but not included here.

</details>

<details>
<summary><strong>Why does the skill never auto-post?</strong></summary>

Because AI-generated content posted without human review is how you burn trust with communities, get banned from platforms, and create citations that hurt more than help. Every piece of content this skill drafts is meant to be read, owned, and submitted by you. The browser-assist flow — pre-fill, you review, you click Submit — is the whole model. There is no auto-post mode and there will not be one.

</details>

---

## Built by

**[Umang](https://github.com/umangbuilds)** — part of the [DhurandharOS](https://github.com/umangbuilds/dhurandhar-os) stack.

DhurandharOS is an operating system built for founders running products with lean teams. It's a set of agent skills that handle the repeatable work — security review, spec writing, weekly loops — so the operator can stay focused on what only they can do.

aeo-loop is the AEO/SEO module. It handles the weekly cadence of AI visibility so you're not doing it manually, or worse, not doing it at all.

Built in India. Built for operators who don't have a marketing team. Built to compound.

---

## License

MIT. See [LICENSE](LICENSE).

Third-party attributions: [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) — must be completed before distributing outside the immediate team.

---

*This project is not affiliated with or endorsed by OpenAI or Anthropic.*
