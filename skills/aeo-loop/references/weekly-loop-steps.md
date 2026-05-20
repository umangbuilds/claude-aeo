# Weekly loop — step-by-step recipes

Detailed bash recipes for each of the 8 steps in `/aeo-loop weekly <domain>`.
Read this file when executing a weekly run. `AGENTS.md` (repo root) and `codex/AGENTS-aeo-loop.md` cover the "what"; this file covers the "how" at the command level.

---

## Pre-flight

```bash
python3 scripts/aeo_loop.py --json init
python3 scripts/aeo_loop.py --json status <domain>
# Verify property is registered. Abort with setup message if not.

RUN_ID=$(python3 scripts/aeo_loop.py --json start-run <domain> --run-type weekly | jq -r .run_id)
```

---

## Step 1 — Audit (inline reasoning over fetched pages)

Fetch and reason inline — no audit sub-skill exists in the Codex variant:

```bash
# Technical: headers, robots, sitemap
curl -sI "https://<domain>" > /tmp/aeo-headers.txt
curl -s  "https://<domain>/robots.txt" > /tmp/aeo-robots.txt
curl -s  "https://<domain>/sitemap.xml" > /tmp/aeo-sitemap.xml

# Content + schema: fetch homepage + 3-5 top pages via WebFetch or curl,
# grep for <script type="application/ld+json"> blocks, validate inline.
```

Reason inline against `references/llm-citation-rubric.md` for citation
readiness signals. GEO readiness checks: AI-readable headings, FAQ
schema, robots allows GPTBot / PerplexityBot / ClaudeBot / Google-Extended.

Persist findings:

```bash
sqlite3 ~/.local/share/aeo-loop/store.db <<SQL
INSERT INTO audit_findings (run_id, property_id, category, severity, finding_text, page_url)
VALUES ($RUN_ID, $PROPERTY_ID, 'technical', 'high', 'Missing meta description on /about', 'https://...');
SQL
```

---

## Step 2 — Discover (WebFetch PAA / Reddit / Quora; inline keyword surface)

Pull candidate queries inline:

```bash
# Google PAA — WebFetch the SERP for each seed query, extract "People also ask".
# Reddit  — WebFetch https://www.reddit.com/search/?q=<query>&sort=top
# Quora   — WebFetch https://www.quora.com/search?q=<query>
```

Keyword surface mining is inline reasoning — group discovered queries
into clusters by intent (informational / commercial / navigational) and
score by competitor-citation gap from the citation matrix.

Persist discovered queries:

```bash
python3 scripts/aeo_loop.py add-query <domain> "<discovered query>" --query-type aeo
# OR for low-confidence finds:
sqlite3 ~/.local/share/aeo-loop/store.db <<SQL
INSERT OR IGNORE INTO discovered_queries (run_id, property_id, query_text, source)
VALUES ($RUN_ID, $PROPERTY_ID, '<text>', 'paa');
SQL
```

---

## Step 3 — Test (citation rate, the load-bearing measurement)

```bash
python3 scripts/aeo_loop.py --json citation-check <domain> --run-id $RUN_ID > citation_results.json
python3 scripts/aeo_loop.py --json status <domain>   # historical grid
```

---

## Step 4 — Analyze (Claude reasons over the data)

Read `citation_results.json`, last week's grid (via `citation_grid_for_week`), GSC rankings (if connected), and audit findings. Identify:

- **Citation gaps:** queries where 0/N LLMs cite us — high opportunity if competitors are cited.
- **Citation regressions:** queries cited last week but not this week.
- **Ranking gaps:** GSC queries ranking 5–15.
- **Critical audit findings:** anything blocking indexing.
- **Discovered queries with high surface count:** promote to tracked.

Output a structured analysis dict in memory for Step 5.

---

## Step 5 — Brief (generate candidate actions)

Generate 15–25 candidates, score, and persist top 5–10:

```bash
cat > /tmp/candidates.json <<EOF
[
  {"action_type": "blog_post",
   "title": "What are agentic payments? A practical guide",
   "description": "Long-form answer for query 'what are agentic payments'",
   "target_url": "https://<domain>/blog/agentic-payments-guide",
   "signals": {"covers_uncited_query": true, "category_whitespace": true},
   "effort_minutes": 240,
   "extra": {"draft_path": "./aeo-loop-output/<domain>/<iso-week>/draft-001.md"}},
  ...
]
EOF

python3 scripts/aeo_loop.py --json record-actions <domain> \
  --run-id $RUN_ID \
  --actions-file /tmp/candidates.json \
  --top-n 10 \
  --diversity-cap 3
```

Action type taxonomy and effort defaults: `references/action-taxonomy.md`.
Signals scoring: `scripts/action_rank.py`.

---

## Step 6 — Draft (Claude writes the actual content)

For each top action, save to `./aeo-loop-output/<domain>/<YYYY-WW>/draft-NNN.md`.
Template: `assets/templates/draft-NNN.md`.
Drafting prompts per action type: `references/drafting-prompts.md`.

Update the action row with `draft_path`:

```bash
sqlite3 ~/.local/share/aeo-loop/store.db <<SQL
UPDATE actions SET draft_path = './aeo-loop-output/<domain>/<iso-week>/draft-001.md'
WHERE id = <action_id>;
SQL
```

---

## Step 7 — Assist (operator-triggered, not part of `weekly`)

The weekly run does NOT open browsers. Operator triggers when ready:

```bash
/aeo-loop assist <action-id>
```

Skill prints: URL to open, clipboard content, instructions.
**Never auto-submit. Operator clicks Submit themselves.**

---

## Step 8 — Track (finish run + write report)

```bash
python3 scripts/aeo_loop.py finish-run --run-id $RUN_ID --status completed
```

Write report at `./aeo-loop-output/<domain>/<YYYY-WW>/report.md`.
Template: `assets/templates/report.md`.
