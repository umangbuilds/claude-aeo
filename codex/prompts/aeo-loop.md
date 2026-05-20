---
description: Weekly AEO/SEO cadence — citation tracking, ranked action-list, browser-assisted execution (Codex variant)
argument-hint: "[init | add-property | bootstrap | weekly | status | assist | mark-done | ...] [args...]"
---

# /aeo-loop (Codex)

Entry point for the `aeo-loop` skill running under Codex CLI.

**Operating contract:** read `codex/AGENTS-aeo-loop.md` in the current
repository root (or the repository at `$AEO_LOOP_REPO` if set). That
file specifies the subcommand surface, the 8-step weekly recipe, the
output layout, and failure modes. The repo-root `AGENTS.md` covers the
high-level rules (autonomy, prompt-injection defense, decisioning rule,
capability detection).

**Python CLI** lives at `skills/aeo-loop/scripts/aeo_loop.py`. Forward
arguments directly:

```bash
python3 skills/aeo-loop/scripts/aeo_loop.py $ARGUMENTS
```

For the autonomous weekly run, do NOT just shell out — execute the
8-step loop as described in `codex/AGENTS-aeo-loop.md` §"The 8-step
weekly loop (Codex execution recipe)", which interleaves Codex
reasoning steps (audit, discover, analyze, brief, draft) with the
Python CLI calls (start-run, citation-check, record-actions, finish-run).

**Common entry points:**

- First time: `/aeo-loop init`
- Register a property: `/aeo-loop add-property <domain> --brand="..."`
- Onboard: `/aeo-loop bootstrap <domain>`
- Weekly autonomous run: `/aeo-loop weekly <domain>`
- See where you stand: `/aeo-loop status <domain>`
- Browser-assist an action: `/aeo-loop assist <action-id>`
- Mark an action done: `/aeo-loop mark-done <action-id> --cited-on=reddit`

The weekly run is autonomous by contract — never ask the operator
"should I continue?" between steps. Log step failures in the report
and keep going.
