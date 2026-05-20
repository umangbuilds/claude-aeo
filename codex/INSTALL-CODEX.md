# Installing claude-aeo on Codex CLI

This is the Codex-compatible variant of `claude-aeo`. Use it if you run
the OpenAI Codex CLI instead of Claude Code. The two variants share the
same Python core (`skills/aeo-loop/scripts/`), the same config file
(`~/.config/aeo-loop/keys.toml`), the same SQLite store, and the same
output directory layout. Only the agent-facing surface differs.

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

## Register your property

```bash
python3 skills/aeo-loop/scripts/aeo_loop.py add-property yourdomain.com \
  --brand="Your Brand" --region=global
```

Add `--region india` if your audience is primarily Indian — that enables
geo-pinned LLM prompts, INR-aware pricing, Indian platforms in
browser-assist, and a +15% region-match boost.

## Bootstrap

```bash
python3 skills/aeo-loop/scripts/aeo_loop.py bootstrap yourdomain.com
```

Interactively prompts for queries, competitors, and brand framing, then
runs a baseline citation check.

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

## Differences from the Claude variant

| Concern | Claude Code | Codex CLI |
|---|---|---|
| Plugin manifest | `.claude-plugin/plugin.json` | none |
| Entry doc | `skills/aeo-loop/SKILL.md` | `codex/AGENTS-aeo-loop.md` (+ repo-root `AGENTS.md`) |
| Slash command | `skills/aeo-loop/commands/aeo-loop.md` | `~/.codex/prompts/aeo-loop.md` |
| Sub-skill calls | `Skill(seo-audit)`, `Skill(seo-geo)`, etc. | Inline reasoning + `WebFetch` / `curl` |
| Config file | `~/.config/aeo-loop/keys.toml` | same |
| SQLite store | `~/.local/share/aeo-loop/aeo-loop.db` | same |
| Output | `./aeo-loop-output/...` | same |

The Codex variant gives up the upstream `claude-seo` skill collection
(audit, geo, content briefs, schema) and replaces them with inline
reasoning + `WebFetch`. This matches the "free tier" path that
`SKILL.md` already specifies — feature parity for the four net-new
modules (`citation_check.py`, `action_rank.py`, `browser_assist.py`,
`store.py`) which are agent-agnostic and unchanged.

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
