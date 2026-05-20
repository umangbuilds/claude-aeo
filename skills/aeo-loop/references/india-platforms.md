# India platforms — reference

Indian-context platforms supported by the browser-assist layer + outreach
publication targets surfaced in action drafts. Listed here so a v0.1 operator
running an India-region property can see at a glance what's available and how
each platform's policies constrain the draft.

The skill never auto-submits. Every entry below is opened in the operator's
browser with the draft pre-filled or copied to the clipboard. The operator
reviews and clicks Submit.

---

## When to set `--region india`

Set on `add-property` when the brand's primary buyers are in India:

```bash
python3 .claude/skills/aeo-loop/scripts/aeo_loop.py add-property moltpe.com \
  --brand "MoltPe" --one-liner "agentic payments" --category fintech \
  --region india
```

The CLI defaults `--currency INR` when `--region india` is set and `--currency`
is omitted. Override with `--currency USD` (or any ISO 4217 code) if pricing
should be presented to customers in a different currency.

Effects of `--region india`:

1. **Citation prompts** are geo-pinned to India. Every (query, LLM) cell sends a
   prompt that ends with `I am based in India and asking for recommendations
   relevant to Indian users. Prefer providers operating in India where
   possible.` This shifts what the LLM names.
2. **INR is mentioned** on pricing-relevant queries (heuristic: query contains
   `price`, `pricing`, `cost`, `fee`, `subscription`, `plan`, `tier`, `cheap`,
   `affordable`, `budget`, `free`, `paid`). On non-pricing queries the currency
   modifier is silent.
3. **Indian-platform actions get a +15% score boost** in `action_rank`. An
   action targeting Quora India ties against a generic Reddit thread? The Quora
   India one wins. Magnitude is intentionally modest — boost re-ranks ties, not
   clear winners.

Query-level override is supported (`add-query ... --region india` on a property
that is otherwise global) for mixed portfolios.

---

## Supported Indian platforms (browser-assist)

| Action type            | Platform        | Notes |
|------------------------|-----------------|-------|
| `quora_india_answer`   | Quora India     | Body to clipboard. COI disclosure required in first line if brand/employer is the subject. BNBR (Be Nice, Be Respectful) policy treats hidden promotion as spam. |
| `justdial_listing`     | JustDial        | Verify business ownership first. Edit forms are JavaScript-rendered; manual paste. |
| `indiamart_listing`    | IndiaMART       | Seller-panel edits require seller login + 2FA. Sign in, then paste. |
| `mouthshut_review`     | MouthShut       | Reviewer must disclose affiliation. Hidden promotional reviews are removed and may flag the account. |
| `reddit_thread`        | Reddit (incl. r/india, r/IndianStartups, r/bangalore, r/mumbai, r/delhi, r/hyderabad, r/pune, r/chennai) | Existing reddit() helper. Pass the subreddit as `target_url` on the action. India subreddits available via `browser_assist.INDIAN_SUBREDDITS`. |

The existing `reddit()` helper works for Indian subreddits without any India-
specific code path — pass `r/india` / `r/IndianStartups` / metro subreddits as
the subreddit kwarg.

---

## Indian publication outreach (PR / earned media)

Editorial pitch targets surfaced in outreach-email draft actions. Use these
for guest-post pitches, story leads, or product-launch pitches when the
property is India-region.

| Publication       | Beat                    | Pitch endpoint              |
|-------------------|-------------------------|-----------------------------|
| YourStory         | startups                | editorial@yourstory.com     |
| Inc42             | startups                | editor@inc42.com            |
| ET Tech           | tech                    | editor@economictimes.com    |
| Moneycontrol      | fintech, markets        | editor@moneycontrol.com     |
| Livemint          | business                | feedback@livemint.com       |
| NDTV Profit       | business                | feedback@ndtv.com           |
| Forbes India      | business                | editorial@forbesindia.com   |
| VCCircle          | venture capital         | editor@vccircle.com         |

Pitches are drafted by the skill, opened via `mailto:` in the operator's mail
client. **The operator clicks Send.** The skill never sends mail.

Editorial pitch contacts drift as journalists move — verify the endpoint on
the publication's contact page before high-stakes outreach. The constants in
`scripts/browser_assist.py` (`INDIAN_PUBLICATIONS`) are the source of truth
and can be updated in place.

---

## INR-awareness checklist for owned pages

When a property is `--currency INR`, the operator's pricing pages should:

1. Display prices in `₹` (or `Rs.` if rendering control is limited) by default,
   with USD as a secondary option only.
2. Use the `Schema.org/Offer` `priceCurrency: "INR"` field (not `USD`) in
   structured-data markup. The forked `seo-schema` skill catches this.
3. State whether prices are inclusive of 18% GST. Indian buyers expect this
   line explicitly.
4. For SaaS subscriptions, name the billing cycle in INR — monthly amount, not
   USD-equivalent — so price-comparison queries to LLMs return your brand with
   a number that matches the page.

The action ranker will add INR-display findings to the `audit_findings` table
as `currency_consistency` category items when the page lacks them; these flow
into the weekly action list as `page_optimize` actions with `predicted_impact`
weighted on `addresses_critical_finding`.

---

## What's deferred (per PRD Section 11)

The following India layers are deliberately out of v0.1:

- **Hindi / regional language prompts** — v0.2/v0.3. English-only.
- **Indian SERP geo-targeting via free means** — paid-only via DataForSEO /
  SerpAPI at v0.1 (opt-in extension).
- **Pre-loaded competitor sets** per category (fintech, SaaS, e-comm) —
  operator-supplied via `add-competitor` at v0.1.
- **Indian content-calendar triggers** (Diwali, Holi, IPL, budget day, RBI
  policy day) — v0.2.
- **Indian regulatory body citation triggers** (RBI / SEBI / IRDAI press
  releases) — v0.2.

If any of these become urgent, promote them through the standard PRD update
flow.
