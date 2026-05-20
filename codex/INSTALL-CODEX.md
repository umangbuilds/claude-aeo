# Installing aeo-loop on Codex CLI

A weekly AEO/SEO/GEO cadence skill for the OpenAI Codex CLI. Tracks
whether ChatGPT, Claude, Perplexity, and Gemini cite your brand, and
produces a ranked weekly action-list to close the gap.

## Prerequisites

- **Codex CLI** — https://github.com/openai/codex (the slash prompt
  will still install if Codex isn't on PATH yet; you just can't invoke
  it until Codex is installed)
- **Python 3.10+** on PATH
- At least 2 LLM API keys (any 2 of OpenAI / Anthropic / Perplexity /
  Gemini). Free tier needs no other keys.

## One-shot install

```bash
git clone https://github.com/umangbuilds/claude-aeo
cd claude-aeo
bash codex/setup-codex.sh
```

The installer:

1. Checks for `codex` and `python3`.
2. Copies `codex/prompts/aeo-loop.md` to `~/.codex/prompts/aeo-loop.md`
   so `/aeo-loop` is available inside Codex sessions.
3. Reminds you to export `AEO_LOOP_REPO` so the prompt can find this
   checkout from any working directory.
4. Verifies the repo-root `AGENTS.md` is present (Codex auto-loads it
   when invoked from this directory).
5. Runs `aeo_loop.py init` to scaffold `~/.config/aeo-loop/keys.toml`
   and the SQLite store at `~/.local/share/aeo-loop/aeo-loop.db`.

## Add API keys

```bash
$EDITOR ~/.config/aeo-loop/keys.toml
```

Fill in at least 2 of: `openai`, `anthropic`, `perplexity`, `gemini`.

## Register your property and bootstrap

Launch Codex from the repo so `AGENTS.md` is auto-loaded:

```bash
codex
```

Then inside Codex, three slash commands:

```
/aeo-loop init
/aeo-loop add-property yourdomain.com --brand="Your Brand" --region=global
/aeo-loop bootstrap yourdomain.com
```

Add `--region india` to `add-property` if your audience is primarily
Indian — that enables geo-pinned LLM prompts, INR-aware pricing, Indian
platforms in browser-assist, and a +15% region-match boost.

`bootstrap` is conversational. Codex looks at your homepage, proposes
queries and competitors, you edit / approve, and it runs the baseline
citation check.

> **Note:** `bootstrap` and `weekly` are slash commands driven by the
> agent reading `codex/AGENTS-aeo-loop.md`. They are not Python
> subcommands. The Python CLI (`aeo_loop.py`) exposes only the
> deterministic primitives: `init`, `add-property`, `add-query`,
> `add-competitor`, `start-run`, `citation-check`, `record-actions`,
> `finish-run`, `assist`, `mark-done`, `status`, and the `list-*`
> commands.

## Run the weekly loop from Codex

Open Codex CLI in this repository directory (so `AGENTS.md` is loaded)
and type:

```
/aeo-loop weekly yourdomain.com
```

Codex reads `codex/AGENTS-aeo-loop.md` for the operating contract and
executes the autonomous 8-step loop. Output lands in
`./aeo-loop-output/<domain>/<YYYY-WW>/`. The main deliverable is
`report.md`.

## Running without the slash command

Every subcommand works directly from any shell:

```bash
python3 skills/aeo-loop/scripts/aeo_loop.py status yourdomain.com
python3 skills/aeo-loop/scripts/aeo_loop.py assist <action-id>
python3 skills/aeo-loop/scripts/aeo_loop.py mark-done <action-id> --cited-on=reddit
```

The slash command exists for the autonomous orchestration only — the
parts that need an LLM (audit, discover, analyze, brief, draft).

## How the loop works under Codex

- **Audit / Discover** — Codex uses `curl` + `WebFetch` to pull
  headers, robots, sitemap, top pages, Google PAA, Reddit / Quora
  results — then reasons inline about technical / content / schema /
  GEO readiness and groups discovered queries.
- **Test / Brief / Assist / Track** — driven by the four agent-agnostic
  Python modules (`citation_check.py`, `action_rank.py`,
  `browser_assist.py`, `store.py`). Same code paths regardless of
  which agent drives.
- **Analyze / Draft** — pure Codex reasoning, with
  `skills/aeo-loop/references/drafting-prompts.md` as the drafting
  contract and the `<<<UNTRUSTED_LLM_OUTPUT>>>` fences enforcing the
  prompt-injection defense from `AGENTS.md`.

| Concern | Path |
|---|---|
| Entry doc (auto-loaded) | `AGENTS.md` (repo root) |
| Operating contract | `codex/AGENTS-aeo-loop.md` |
| Slash command | `~/.codex/prompts/aeo-loop.md` (staged by installer) |
| Config file | `~/.config/aeo-loop/keys.toml` |
| SQLite store | `~/.local/share/aeo-loop/store.db` |
| Output | `./aeo-loop-output/<domain>/<YYYY-WW>/` |

## Troubleshooting

- **`/aeo-loop` not found in Codex.** Re-run `bash codex/setup-codex.sh`
  and confirm `~/.codex/prompts/aeo-loop.md` exists. Restart Codex.
- **Codex can't find the repo.** Either run Codex from the repo root,
  or `export AEO_LOOP_REPO=/path/to/claude-aeo` in your shell rc.
- **`citation-check` exits with code 2.** Missing keys.toml — re-run
  `python3 skills/aeo-loop/scripts/aeo_loop.py init` and edit
  `~/.config/aeo-loop/keys.toml`.
- **`citation-check` exits with code 1.** No queries tracked yet — run
  `bootstrap` first.
