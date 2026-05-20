# claude-aeo

Weekly AEO/SEO/GEO cadence skill for Claude Code.

**This project is not affiliated with or endorsed by Anthropic.**

---

## What it does

One command per week per website:

```
/aeo-loop weekly yourdomain.com
```

Produces:
- Citation rate across ChatGPT, Claude, Perplexity, Gemini — week over week
- 5–10 prioritized actions (blog posts, Reddit threads, Wikipedia edits, outreach)
- Drafted content for each action, ready to review and submit
- Browser-assist: opens the right page with draft pre-filled; you click Submit

The skill never auto-posts. You review every draft and click Submit yourself.

---

## Install

```bash
bash setup.sh
```

The setup script will:
1. Check for Claude Code CLI and Python 3.10+
2. Explain why `claude-seo` (the forked SEO skill collection) is needed, and ask your permission before installing it
3. Install `claude-seo` via `claude plugin install` if you confirm
4. Verify the aeo-loop CLI is working
5. Print next steps

After setup, add your LLM API keys to `~/.config/aeo-loop/keys.toml` (created automatically during setup). You need at least 2 of: OpenAI, Anthropic, Perplexity, Gemini.

**New to this? Start here:** `skills/aeo-loop/GETTING-STARTED.md` — plain English guide, no SEO or coding background needed.

---

## Quick reference

| Command | What |
|---|---|
| `/aeo-loop init` | Initialize config + store |
| `/aeo-loop add-property yourdomain.com --brand="..." --one-liner="..."` | Register a property |
| `/aeo-loop bootstrap yourdomain.com` | First-time: set queries, competitors, baseline |
| `/aeo-loop weekly yourdomain.com` | Weekly loop — full 8 steps |
| `/aeo-loop status yourdomain.com` | Citation rate + pending actions |
| `/aeo-loop assist <action-id>` | Open browser with draft pre-filled |
| `/aeo-loop mark-done <action-id>` | Record that you submitted an action |

India-region support: add `--region india` to `add-property` to enable geo-pinned LLM prompts, INR pricing awareness, and Indian platform prioritization (Quora India, JustDial, IndiaMART, MouthShut, YourStory outreach).

---

## Structure

```
claude-aeo/
├── setup.sh                  — first-time install
├── .claude-plugin/plugin.json
├── skills/
│   ├── aeo-loop/             — weekly loop + citation tracking + browser-assist
│   └── aeo-orchestrator/     — natural-language routing across the SEO ecosystem
└── THIRD_PARTY_LICENSES.md   — must be completed before external distribution
```

---

## License

MIT. See [LICENSE](LICENSE).

Third-party attributions: see [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md). This file must be completed before distributing outside the immediate team.
