---
description: Weekly AEO/SEO cadence per property — citation tracking, ranked action-list, browser-assisted execution
argument-hint: "[init | add-property | bootstrap | weekly | status | assist | mark-done | ...] [args...]"
---

# /aeo-loop

Entry point for the `aeo-loop` skill. Routes `$ARGUMENTS` directly to the skill's logic per `SKILL.md`.

Calls `scripts/aeo_loop.py` for data operations and orchestrates the 8-step weekly loop:

1. Audit → 2. Discover → 3. Test (citation rate) → 4. Analyze → 5. Brief → 6. Draft → 7. Assist → 8. Track

See `SKILL.md` for the full subcommand reference and orchestration logic.

**Common entry points:**

- First time: `/aeo-loop init`
- Register a property: `/aeo-loop add-property <domain>`
- Onboard a property: `/aeo-loop bootstrap <domain>`
- Weekly run: `/aeo-loop weekly <domain>`
- See where you stand: `/aeo-loop status <domain>`
- Execute an off-site action: `/aeo-loop assist <action-id>`
- Mark an action done: `/aeo-loop mark-done <action-id> --cited-on=reddit`

The `weekly` subcommand runs the entire loop end-to-end without further prompts. The operator only needs to act on the produced drafts and the `assist` step.
