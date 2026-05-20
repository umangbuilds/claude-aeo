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

Full guide with Windows, troubleshooting, and step-by-step instructions: **[INSTALL.md](INSTALL.md)**

### Quickest path — Claude desktop app, Code tab (no terminal)

1. Install the **Claude desktop app** from [claude.ai/download](https://claude.ai/download).
2. Open the app and click the **Code** tab in the sidebar.
3. In a fresh Code tab chat, type:
   ```
   install claude-aeo from github.com/umangbuilds/claude-aeo
   ```
4. Click **Allow once** on each permission prompt (typically 4–6). Claude Code clones the repo, installs the plugin, and runs `setup.sh` automatically.
5. Restart Claude Code, open a fresh Code tab, and run:
   ```
   /aeo-loop init
   ```

### CLI path (terminal)

```bash
$ claude plugin marketplace add umangbuilds/claude-aeo
```

Then inside a Claude Code session:

```
/plugin install claude-aeo@claude-aeo
/reload-plugins
/aeo-loop init
```

### After install — add API keys

Open `~/.config/aeo-loop/keys.toml` and paste at least 2 of: OpenAI, Anthropic, Perplexity, Gemini. See [INSTALL.md](INSTALL.md) for where to get each key.

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
