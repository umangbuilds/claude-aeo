# Action taxonomy

The full set of `action_type` values aeo-loop recognises, when to recommend each, and the default effort estimate in minutes (from `EFFORT_DEFAULTS_MIN` in `scripts/action_rank.py`).

When candidate actions are produced in Step 5 of the weekly loop, pick from this list. Custom types are allowed but fall back to 60 minutes default effort.

---

## On-site actions

These run on a property the operator owns. No browser-assist needed — the operator publishes via their own CMS.

| `action_type` | Default effort | When to use |
|---|---|---|
| `schema_add` | 15 min | Add or fix JSON-LD on existing pages. Article, Organization, BreadcrumbList, Product, LocalBusiness. **Avoid HowTo (deprecated Sept 2023). FAQPage only for gov / healthcare.** |
| `internal_link` | 10 min | Add a contextual link from a high-authority page to a target page. Cheap, often-overlooked SEO win. |
| `page_optimize` | 60 min | Rewrite the intro / headings of an existing page for AEO citability (134–167 word self-contained answer block in the first 60 words). |
| `blog_post` | 240 min | Net-new article (~1500 words) on an uncited query. Lead with the answer block. |
| `pillar_page` | 480 min | Comprehensive guide (~3000 words) on a category-level query. The flagship piece per topic cluster. |
| `image_gen` | 30 min | OG / hero / social preview image. Requires `banana` extension enabled. |

## Off-site actions

These require browser-assist (Level A). The skill pre-fills the form; the operator clicks Submit.

| `action_type` | Default effort | When to use |
|---|---|---|
| `reddit_thread` | 30 min | Answer a question in a relevant subreddit OR start a thread. **No promotional language. Lead with the question or observation, not the brand.** Declare affiliation in a flair / tag line. |
| `wikipedia_edit` | 60 min | Edit an existing Wikipedia page. **MUST be preceded by a `wikipedia_talk` action with COI disclosure if the page is about the operator's brand, employer, or client.** Use direct edit only when the topic is general (not the brand itself). |
| `wikipedia_talk` | 15 min | Propose changes via talk page. Preferred over direct edit when COI is involved. Standard practice: declare COI, propose edit, wait for community review. |
| `hacker_news_post` | 20 min | Submit a relevant story or link. HN has strict title rules — no editorialising. Most submissions never make front page; do not spam. |
| `outreach_email` | 20 min | One-line pitch for a backlink, guest post, podcast, interview. Keep to 3 lines max. |
| `social_post` | 15 min | X / Twitter post. One specific data point + one question. Not promotional. |
| `linkedin_post` | 15 min | LinkedIn share. Slightly longer than Twitter, same tone — observation + question. |
| `guest_post_pitch` | 45 min | Targeted outreach for a publication. Personalise per outlet. |
| `podcast_pitch` | 30 min | Outreach to a podcast host. Pitch what you'd actually talk about, not a generic founder-bio pitch. |

---

## Picking the right action for a gap

The candidate generation step (Step 5 of the weekly loop) maps gaps to action types. Rough heuristic:

| Gap signal | Best action type | Why |
|---|---|---|
| Uncited query, category-level | `pillar_page` | Long form, multiple H2s, deep schema → maximises chance of citation. |
| Uncited query, specific question | `blog_post` | Direct answer in first 60 words → maximises citability. |
| Competitor cited on our query, we're not | `blog_post` + `wikipedia_talk` | Match the canonical answer source. |
| Critical audit finding | `schema_add` or `page_optimize` | Address the blocker first. |
| GSC query at position 5–15 | `internal_link` + `page_optimize` | Push to top of page 1. |
| Category whitespace (no LLM cites anyone) | `reddit_thread` + `wikipedia_edit` | Seed the conversation. |
| Brand SERP weakness | `social_post` + `linkedin_post` | Increase brand mention volume. |

This is heuristic, not policy. Claude can pick differently with reasoning surfaced in the action description.

---

## Diversity cap

When ranking, prefer a mix of action types over piling on one. Default cap is 3 per type per week. This keeps the operator from receiving 10 blog post recommendations and 0 schema fixes.

---

## What we explicitly do NOT recommend

These never appear in `aeo-loop`'s action list:

- Buying links (PBNs, link farms, paid placements without `nofollow` / `sponsored`)
- Keyword stuffing
- Auto-generated low-quality content
- Cloaking / doorway pages
- HowTo schema on non-gov / non-healthcare sites
- FAQ schema on commercial sites (rich-result eligibility removed Aug 2023)
- Anything that requires automated posting / scheduled bots
