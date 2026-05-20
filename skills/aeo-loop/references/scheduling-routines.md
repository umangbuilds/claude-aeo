# Scheduling routines

`/aeo-loop weekly` is the value-add. Running it once is useful; running it on a regular cadence is the whole point. This page is the operator's setup reference for making weekly + daily runs happen on their own.

Five options, sorted by recommended-first.

---

## Option A — Claude Code `/schedule` (recommended)

**When:** You want true unattended scheduling, you have Claude Code installed, and you're fine with the run happening on Anthropic's remote infra.

This is the cleanest path. Claude Code's `/schedule` skill creates a remote scheduled agent that runs on Anthropic's infrastructure on a cron expression you supply.

```
/schedule create "Weekly AEO loop for moltpe.com" \
  --cron "0 9 * * MON" \
  --prompt "/aeo-loop weekly moltpe.com"

/schedule create "Daily AEO status check" \
  --cron "0 8 * * *" \
  --prompt "/aeo-loop status moltpe.com"
```

**Pros:** runs even when your laptop is off; no local cron setup; managed by Anthropic.
**Cons:** requires Claude Code account / billing on the schedule side; depends on Anthropic infra availability.

---

## Option B — Claude Code `/loop` (self-paced, inside a session)

**When:** You're already in a Claude Code session and want the loop to re-run itself periodically while you work in the same session.

```
/loop 7d /aeo-loop weekly moltpe.com
```

This re-runs the command every 7 days as long as the session stays open. Useful for active development but not for true unattended scheduling — closing the session stops the loop.

---

## Option C — Local cron + headless Claude Code (macOS / Linux)

**When:** You want everything local, you have `claude` CLI installed, and you want unattended runs without depending on a remote scheduler.

The full weekly loop requires Claude to orchestrate (the SKILL.md prose is the orchestration). Headless mode:

```cron
# crontab -e
# Weekly full loop, Monday 9am local
0 9 * * 1  cd /Users/you/Documents/your-project && claude -p "/aeo-loop weekly moltpe.com" >> ~/aeo-loop.log 2>&1

# Daily lightweight status, every weekday 8am
0 8 * * 1-5  cd /Users/you/Documents/your-project && claude -p "/aeo-loop status moltpe.com" >> ~/aeo-loop.log 2>&1
```

**Pros:** local, free, runs while your laptop is on.
**Cons:** requires Claude Code CLI and an active API key in env; runs consume API credits silently; if the laptop is asleep when the cron fires, the job is skipped (cron does not catch up missed runs).

---

## Option D — launchd (macOS native, more reliable than cron)

**When:** Same as Option C but you want the job to catch up if it was missed (laptop closed at the scheduled time).

Create `~/Library/LaunchAgents/com.aeo-loop.weekly.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.aeo-loop.weekly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-lc</string>
        <string>cd ~/Documents/your-project &amp;&amp; claude -p "/aeo-loop weekly moltpe.com" >> ~/aeo-loop.log 2>&amp;1</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key><integer>1</integer>
        <key>Hour</key><integer>9</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>RunAtLoad</key><false/>
</dict>
</plist>
```

Load it: `launchctl load ~/Library/LaunchAgents/com.aeo-loop.weekly.plist`.

**Pros:** native macOS scheduler, catches up missed runs, runs even when not logged in (if user agent allowed).
**Cons:** more setup syntax than cron.

---

## Option E — GitHub Actions (cloud-scheduled, headless)

**When:** You manage multiple properties as a team, you want runs to happen in cloud CI, and you're comfortable storing API keys as GitHub secrets.

Create `.github/workflows/aeo-loop-weekly.yml`:

```yaml
name: AEO loop weekly
on:
  schedule:
    - cron: '0 9 * * 1'   # Monday 9am UTC
  workflow_dispatch:

jobs:
  weekly:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Restore aeo-loop config
        run: |
          mkdir -p ~/.config/aeo-loop
          cat > ~/.config/aeo-loop/keys.toml <<EOF
          [llm]
          openai     = "${{ secrets.OPENAI_KEY }}"
          anthropic  = "${{ secrets.ANTHROPIC_KEY }}"
          perplexity = "${{ secrets.PERPLEXITY_KEY }}"
          gemini     = "${{ secrets.GEMINI_KEY }}"
          EOF
      - name: Run Claude Code headless
        run: |
          npx -y @anthropic-ai/claude-code -p "/aeo-loop weekly moltpe.com"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Commit weekly report
        run: |
          git config user.name "aeo-loop-bot"
          git config user.email "bot@example.com"
          git add aeo-loop-output/
          git commit -m "weekly AEO report" || echo "no changes"
          git push
```

**Pros:** cloud-scheduled, results commit to the repo, full team visibility.
**Cons:** runs cost GitHub Actions minutes; secrets management; the SQLite store doesn't follow (each run starts from scratch unless you also commit the DB — which is fine for read-only weekly reports but breaks longitudinal tracking). For longitudinal tracking on GHA, commit the SQLite DB at the end of each run.

---

## What about pure-Python cron (no Claude Code)?

If you want to run a *partial* loop without Claude orchestration — for example, just the citation tracking and status — you can call the Python CLI directly from cron:

```cron
# Daily citation check (no Claude needed — just collects data into SQLite)
0 8 * * 1-5  python3 /path/to/.claude/skills/aeo-loop/scripts/aeo_loop.py status moltpe.com >> ~/aeo-status.log 2>&1
```

This works for `status`, `citation-check` (if you wire your own run_id management), `list-actions`, `mark-done`. It does NOT cover the analyze/brief/draft steps — those require Claude reasoning over the data. So pure-Python cron is fine for collecting and surfacing, not for the full weekly loop.

---

## Recommended setup for a solo operator on macOS

1. **Option A (`/schedule`)** if you have it — easiest, most reliable, no infra. One command sets it up.
2. **Option D (launchd)** if you prefer local-only.

For a team or agency: **Option E (GitHub Actions)** — gives every property its own scheduled job, commit history is the audit log, and the team sees the weekly reports show up in the repo.

For first-time setup, just run the loop manually a few times to make sure it works end-to-end on your property, then schedule it. Do not schedule something that has not yet succeeded once on the bench.

---

## Failure mode: scheduled run silently breaks

A scheduled job that fails quietly is worse than no schedule at all. Build in a tripwire:

- Cron / launchd: tail `~/aeo-loop.log` weekly. Add an alert (`mail` command or `osascript -e 'display notification ...'`) if the log shows a non-zero exit.
- GitHub Actions: enable workflow failure notifications in repo settings → notifications.
- Claude Code `/schedule`: check `/schedule list` weekly to confirm last-run status.

Set a calendar reminder to check the schedule output weekly for the first month. If it has not silently broken by then, it probably will not.
