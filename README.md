<div align="center">

# claude-aeo

### One command. Your brand in every AI answer.

Track whether ChatGPT, Claude, Perplexity, and Gemini cite you — and get a weekly shortlist of actions to make them start.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-7c3aed)](https://claude.ai/code)
[![Made for India](https://img.shields.io/badge/made%20for-India-ff9933)](https://github.com/umangbuilds/claude-aeo#built-for-india)

</div>

---

> **Not affiliated with or endorsed by Anthropic.**

---

## The problem

When someone asks ChatGPT *"best tools for X"* or *"how do I do Y"* — your brand either shows up or it doesn't. There is no ad slot. No bidding. No shortcut. Just whether AI models have enough evidence to cite you.

Most founders have no idea what their citation rate is. This skill measures it and closes the gap, one week at a time.

---

## What happens each week

```
/aeo-loop weekly yourdomain.com
```

In 5–15 minutes you get:

| | |
|---|---|
| **Citation rate** | % of your tracked queries where each AI names you — week over week |
| **Gap analysis** | What competitors are getting cited for that you aren't |
| **10 ranked actions** | Blog posts, Reddit threads, Wikipedia edits, outreach — ranked by impact vs. effort |
| **Ready drafts** | Every action comes with a draft. You review and click Submit. |

**The skill never auto-posts. You always click Submit yourself.** This is intentional.

---

## How it works

```
Week 1 (once)        Week 2               Week 3
────────────         ──────────────       ──────────────
bootstrap        →   /aeo-loop weekly  →  /aeo-loop weekly
set queries          → 10 actions          → did last week's
set competitors      → pick 3               actions move the
run baseline         → /assist              needle?
                     → you click Submit  → pick 3 more
                                         → /assist
                                         → you click Submit
```

Each action is pre-filled and opened in your browser. Nothing is posted without your eyes on it.

---

## Install

**Quickest path — Claude desktop app, Code tab (no terminal):**

Open the Code tab and type one sentence:
```
install claude-aeo from github.com/umangbuilds/claude-aeo
```
Click **Allow once** on each permission prompt (4–6). Claude Code clones the repo, installs the plugin, and runs setup automatically. Then:
```
/aeo-loop init
```

**CLI (terminal):**
```bash
$ claude plugin marketplace add umangbuilds/claude-aeo
```
Then inside Claude Code:
```
/plugin install claude-aeo@claude-aeo
/reload-plugins
/aeo-loop init
```

**Add API keys** — open `~/.config/aeo-loop/keys.toml`, paste at least 2 of: OpenAI, Anthropic, Perplexity, Gemini. Cost: ~₹40–160/week.

Full guide with Windows, WSL2, troubleshooting: **[INSTALL.md](INSTALL.md)**

New to this? Plain-English walkthrough: **[skills/aeo-loop/GETTING-STARTED.md](skills/aeo-loop/GETTING-STARTED.md)**

---

## Commands

| Command | What |
|---|---|
| `/aeo-loop init` | First-time setup — creates config + local store |
| `/aeo-loop add-property yourdomain.com --brand="..." --one-liner="..."` | Register your site |
| `/aeo-loop bootstrap yourdomain.com` | Walk through queries, competitors, baseline check |
| `/aeo-loop weekly yourdomain.com` | Weekly run — citation check + ranked action list |
| `/aeo-loop status yourdomain.com` | Latest citation rate + pending actions |
| `/aeo-loop assist <action-id>` | Open browser with draft pre-filled; you click Submit |
| `/aeo-loop mark-done <action-id>` | Record what shipped; tracks what moved the needle |

---

## Built for India

Add `--region india` to `add-property`:

```
/aeo-loop add-property yourdomain.com --brand="Your Brand" --one-liner="What you do" --region india
```

What this unlocks:
- LLM prompts geo-pinned to India
- Action pricing and estimates in INR
- Indian platform priority: Quora India, JustDial, IndiaMART, MouthShut
- Indian publication outreach list: YourStory, Inc42, ET Tech, The Ken, Entrackr

---

## Requirements

- **Claude Code 2.x+** — [claude.ai/download](https://claude.ai/download)
- **Python 3.10+** — [python.org](https://python.org)
- **2+ LLM API keys** — any 2 of: OpenAI, Anthropic, Perplexity, Gemini

---

## Repo structure

```
claude-aeo/
├── setup.sh                        — first-time install
├── .claude-plugin/plugin.json      — Claude Code plugin manifest
├── skills/
│   ├── aeo-loop/                   — weekly loop, citation tracking, browser-assist
│   │   ├── SKILL.md
│   │   ├── scripts/                — Python backend (store, citation_check, browser_assist)
│   │   ├── references/             — detailed step guides, India platforms
│   │   ├── assets/templates/       — report.md, draft-NNN.md
│   │   └── tests/                  — 168 tests, all green
│   └── aeo-orchestrator/           — natural-language routing
└── THIRD_PARTY_LICENSES.md         — attribution (required before external distribution)
```

---

## Built by

**[Umang](https://github.com/umangbuilds)** — part of the [DhurandharOS](https://github.com/umangbuilds/dhurandhar-os) stack for one-person operators.

DhurandharOS is an operating system for founders running products alone. claude-aeo is the AEO/SEO module — the piece that handles AI visibility so you don't have to think about it every week.

If you're building in India with a lean team and need your brand to show up when AI answers questions in your space, this is built for you.

---

## License

MIT. See [LICENSE](LICENSE).

Third-party attributions: [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) — must be completed before distributing outside the immediate team.

---

*This project is not affiliated with or endorsed by Anthropic.*
