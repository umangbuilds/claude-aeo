# Install claude-aeo

claude-aeo is a Claude Code skills package. Install it once; the weekly AEO loop runs with a single command every Monday.

> **Built for non-technical operators first.** The fastest path is the **Claude desktop app's Code tab** — Claude Code runs natively inside it, no terminal required. Power users can use the Claude Code CLI from their terminal. Both paths are below.

---

## Two install paths

**Path 1 — Claude desktop app, Code tab (no terminal):** recommended if you've never opened a terminal in your life. Install the Claude desktop app, open the Code tab, type one sentence. Claude Code does the rest with permission prompts.

**Path 2 — Claude Code CLI (terminal):** for operators comfortable on the command line. Run `$ claude` in your terminal, then run the commands below.

## How to read this guide

- **Lines starting with `$`** are terminal commands. Run them in Terminal.app (Mac), PowerShell (Windows), or your Linux shell. Skip these if you're on the desktop app path.
- **Lines starting with `/`** are Claude Code interactive commands — type them inside a Claude Code session, not in the terminal. They work in the CLI only, not in the desktop app's Code tab.

---

## Prerequisites

- **Claude Code 2.x or later.** Download from [claude.ai/download](https://claude.ai/download).
- **Python 3.10 or higher.** Check with `python3 --version`. Download from [python.org](https://python.org) if needed — pick 3.10 or higher.
- **At least 2 LLM API keys** (any 2 of: OpenAI, Anthropic, Perplexity, Gemini). The skill is free; the API calls cost ~₹40–160 / week depending on how many queries you track. See [skills/aeo-loop/GETTING-STARTED.md](skills/aeo-loop/GETTING-STARTED.md) for where to get keys.

---

## Quick install — desktop app, Code tab (recommended)

No terminal. No CLI. No slash commands.

1. Install the **Claude desktop app** from [claude.ai/download](https://claude.ai/download).
2. Open the app and click the **Code** tab in the sidebar.
3. In a fresh Code tab chat, type this single sentence:

   ```
   install claude-aeo from github.com/umangbuilds/claude-aeo
   ```

4. Click **Allow once** on each permission prompt that appears (typically 4–6 prompts). Claude Code will clone the repo, install the plugin, and run `setup.sh` for you.
5. Restart Claude Code (Cmd+Q on Mac and reopen, or close-and-reopen on Windows).
6. Open a fresh Code tab session and type:

   ```
   /aeo-loop init
   ```

   You should see something like:
   ```
   Initialized.
     Config: /Users/you/.config/aeo-loop/keys.toml
     Store:  /Users/you/.local/share/aeo-loop/store.db
     Active LLMs: none
   ```

Done with install. Now [add your API keys](#step-2--add-your-api-keys) below.

---

## Quick install — Claude Code CLI (terminal)

```bash
$ claude plugin marketplace add umangbuilds/claude-aeo
```

Then inside a Claude Code session:

```
/plugin install claude-aeo@claude-aeo
/plugin list
/reload-plugins
```

You should see `claude-aeo v0.1.0` listed as Enabled. Then run:

```
/aeo-loop init
```

---

## Manual install (if marketplace add fails)

```bash
# 1. Clone the repo
$ git clone https://github.com/umangbuilds/claude-aeo.git ~/.claude/plugins/claude-aeo

# 2. Add to Claude Code's plugin marketplace
$ claude plugin marketplace add ~/.claude/plugins/claude-aeo

# 3. Run setup (installs the forked SEO skill collection)
$ bash ~/.claude/plugins/claude-aeo/setup.sh
```

Then inside Claude Code:

```
/plugin install claude-aeo@claude-aeo
/plugin list
/reload-plugins
```

---

## Step 2 — Add your API keys

Open the config file the init step created:

```bash
open ~/.config/aeo-loop/keys.toml          # Mac
notepad %USERPROFILE%\.config\aeo-loop\keys.toml   # Windows
```

Paste your keys between the quotes:

```toml
[llm]
openai     = "sk-abc123..."
anthropic  = "sk-ant-xyz..."
perplexity = ""
gemini     = ""
```

You need **at least 2** keys. The skill still works with 2; 4 gives you the full cross-LLM citation matrix. Save and close.

Where to get keys:

| Service | Sign up | Get key |
|---|---|---|
| OpenAI | platform.openai.com/signup | platform.openai.com/api-keys |
| Anthropic | console.anthropic.com | Settings → API Keys |
| Perplexity | perplexity.ai/settings/api | Settings → API → Generate |
| Gemini | aistudio.google.com/apikey | Click "Create API key" |

---

## Step 3 — Register your website

```
/aeo-loop add-property yourdomain.com --brand="Your Brand" --one-liner="What you do in one sentence"
```

If your audience is primarily in India, add `--region india`:

```
/aeo-loop add-property yourdomain.com --brand="Your Brand" --one-liner="What you do" --region india
```

What `--region india` does: geo-pins LLM prompts to India, activates INR pricing awareness, prioritizes Indian platforms (Quora India, JustDial, IndiaMART, MouthShut) in the action list, and adds Indian publication outreach targets (YourStory, Inc42, ET Tech, etc.).

---

## Step 4 — First-time bootstrap

```
/aeo-loop bootstrap yourdomain.com
```

This walks you through adding your 5–10 tracked queries (the questions you want AI chatbots to name you for) and 3–5 competitors, then runs an initial baseline citation check.

---

## Step 5 — Your first weekly run

```
/aeo-loop weekly yourdomain.com
```

First run takes 5–15 minutes (the skill talks to 4 AI services). After that, results are at:

```
./aeo-loop-output/yourdomain.com/<YYYY-WW>/report.md
```

Open `report.md`. It has your citation rate, what changed, and 5–10 specific things to do this week, ranked by which would help most for least effort.

---

## What to expect each week

```
/aeo-loop weekly yourdomain.com      ← run once a week, ~10 min of attention

/aeo-loop assist <action-id>         ← when you're ready to execute an action
                                        opens browser with draft pre-filled;
                                        you review and click Submit

/aeo-loop mark-done <action-id>      ← after you've submitted; tracks what worked
```

The skill **never auto-posts**. You always click Submit yourself. This is intentional.

---

## Verifying everything works

Inside Claude Code:

```
/aeo-loop status yourdomain.com
```

You should see your latest citation rate and pending actions. If you see "property not found," re-run Step 3.

---

## Windows install

### Path A — Native Windows (PowerShell)

```powershell
# Install Claude Code
$ irm https://claude.ai/install.ps1 | iex

# Then proceed with Quick Install
$ claude plugin marketplace add umangbuilds/claude-aeo
```

**Windows gotchas:**
- Plugin path is `%USERPROFILE%\.claude\plugins\` (not `~/.claude/plugins/` like macOS/Linux).
- Keys file is at `%USERPROFILE%\.config\aeo-loop\keys.toml`.
- Store DB is at `%LOCALAPPDATA%\aeo-loop\store.db`.
- If `claude` command isn't found after install, restart PowerShell as administrator.

### Path B — WSL2 (recommended for developers)

```bash
$ curl -fsSL https://claude.ai/install.sh | sh
$ claude plugin marketplace add umangbuilds/claude-aeo
```

Standard Linux paths apply inside WSL2.

---

## Updating

```bash
$ cd ~/.claude/plugins/claude-aeo
$ git pull
```

Then inside Claude Code:

```
/plugin reload claude-aeo@claude-aeo
```

Your `keys.toml`, `store.db`, and weekly output folders are untouched on update.

---

## Uninstalling

Inside Claude Code:

```
/plugin uninstall claude-aeo@claude-aeo
/plugin marketplace remove claude-aeo
```

Then on disk:

```bash
$ rm -rf ~/.claude/plugins/claude-aeo
```

Your data (`~/.config/aeo-loop/keys.toml`, `~/.local/share/aeo-loop/store.db`, and `./aeo-loop-output/`) is **not touched**. Delete manually if you want a clean slate.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `"/plugin isn't available in this environment"` | You're in the desktop app Code tab. Use the natural-language install instead: type `install claude-aeo from github.com/umangbuilds/claude-aeo` in the chat. |
| `"no LLM providers configured"` | Keys not added to `keys.toml`. Re-do Step 2. |
| Weekly run takes a long time / looks frozen | Normal on first run. The skill is talking to 4 AI services. Wait up to 15 minutes. |
| One AI service returns errors | The skill continues with the others and marks the failing cells as `not_checked`. Free-tier rate limits and brief outages are common. |
| `"property not found"` | Run `/aeo-loop add-property yourdomain.com` first. |
| `/aeo-loop init` runs but keys.toml shows no keys | Open the file and paste your keys manually — see Step 2. |
| `python3: command not found` | Install Python 3.10+ from python.org. |

Full beginner guide with screenshots and plain-English explanations: [skills/aeo-loop/GETTING-STARTED.md](skills/aeo-loop/GETTING-STARTED.md).

---

*This project is not affiliated with or endorsed by Anthropic.*
