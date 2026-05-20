# Drafting prompts per action type

In Step 6 of the weekly loop, Claude generates the actual draft for each top-ranked action. These prompts keep voice consistent and the format aligned to what each platform rewards.

For every draft, load the property's brand identity first: `brand_name`, `one_liner`, `category`, and the competitor list. The draft should reference the brand authentically — not as a marketing line.

---

## `blog_post`

**Template:**

```
# {Title — usually a question or "X: a guide"}

## The short answer

{First 60-word block that fully answers the query. Self-contained. No setup.
Names {brand} once if natural. No clickbait.}

## Why this matters

{2-3 paragraphs of context. Lead with a specific data point or insight. Avoid
generic intros like "in today's fast-paced world."}

## {Specific aspect 1}
{Detail.}

## {Specific aspect 2}
{Detail.}

## How {brand} thinks about this
{One paragraph. Operator voice. Specific. Not promotional. Reads like a senior
operator at {brand} explaining their take, not a marketing landing page.}

## Common questions
{3-5 Q&A pairs. Each Q is a real user query. Each A is 30-50 words, citable.}

---
Author: {operator name}
Last updated: {today}
```

**Length:** 1200-1800 words.
**Schema:** Generate JSON-LD Article with author, datePublished, dateModified.

---

## `pillar_page`

Same template as blog_post but:
- Length 2500-3500 words
- 6-8 H2 sections covering the whole category, not one slice
- Each H2 internal-links to the category's blog_posts (build the cluster)
- Schema: Article + BreadcrumbList

---

## `page_optimize`

For an existing page that needs the AEO citability treatment:

```
Read the current page. Rewrite ONLY the intro section (above the first H2) to:

1. Open with a self-contained 60-word answer block.
2. State {brand}'s position on the topic in one specific sentence.
3. Preview what the page covers in 2-3 bullets.

Do not touch the rest of the page. Output ONLY the new intro block in a code
fence labeled "INTRO REPLACEMENT" plus an explanation of what changed.
```

---

## `schema_add`

Generate JSON-LD for a specific schema type. Always:
- Use schema.org context
- Validate against schema.org's docs
- Include only fields the page actually has data for (don't fabricate authors, dates, ratings)
- For Article: headline, description, author (Person), datePublished, dateModified, image
- For Organization: name, url, logo, sameAs (link to LinkedIn, Wikipedia, X profile)
- For LocalBusiness: name, address (PostalAddress), telephone, openingHours, geo (GeoCoordinates)
- **Skip HowTo (deprecated). Skip FAQPage for commercial sites.**

Output the JSON-LD in a code fence with the file path comment indicating where it goes on the page.

---

## `reddit_thread`

```
Subreddit: r/{target_sub}
Title: {Title — a question, not a brand mention}

Body:
{Open with a specific observation or question. NOT "I work at {brand} and
wanted to share..." NOT "Has anyone tried {brand}?" That gets deleted.}

{2-3 paragraphs of genuine context — what you've seen, why this is hard, what
the trade-offs are. Use specific numbers / examples.}

{Close with a real question to the community. Make it answerable in one
paragraph.}

---
*Disclosure: I work on {brand} ({domain}). Posting in my personal capacity.*
```

**Discipline:**
- Lead with the topic, not the brand
- Disclosure footer is mandatory — Reddit subs ban undisclosed self-promo
- One link max in the body, ideally none
- 200-400 words

---

## `wikipedia_talk`

```
Section header: COI disclosure and proposed edit on {Page Title}

Body:
Hello {{ping editors}},

I work for {brand} ({domain}). I would like to propose the following edit
to this article. I will not edit the article directly given the COI.

**Proposed change:** {one sentence summary}

**Current text** (cited from the article):
> {quote the exact current passage}

**Proposed text:**
> {your proposed version, NPOV, third-person, no marketing language}

**Sources:**
- {source 1: a reputable third-party publication, not your own website}
- {source 2}

Open to feedback. ~~~~
```

**Discipline:**
- COI declared first, before the request
- Direct quote of current text — proves you read the article
- NPOV: neutral point of view, no superlatives
- Sources are not your own site — they are third-party

---

## `wikipedia_edit`

Only for pages where the operator has no COI. Pages about the operator's brand REQUIRE a `wikipedia_talk` action first. The draft is the new text for a section, plus a one-line edit summary. Format:

```
ARTICLE: {page title}
SECTION: {section header to edit, or 'new section: <name>'}
EDIT SUMMARY: {short — what changed and why}

REPLACEMENT TEXT:
{new text, NPOV, with inline citations [1][2]}

CITATIONS:
[1] {url}
[2] {url}
```

---

## `outreach_email`

```
Subject: {7 words max, specific, not "Quick question" or "Following up"}

Hi {name},

{One sentence — what about their work caught your attention. Specific. Not
"loved your latest piece."}

{One sentence — what you'd like to propose. Direct.}

{One question — open-ended, easy to answer in 2 sentences.}

— {operator}, {brand}
```

**Discipline:**
- 3 lines body, max
- Subject line is specific, not generic
- One question, not three
- No attachments. No deck. No calendar link in cold outreach.

---

## `social_post` (X / Twitter)

```
{One specific data point. Not a generalization.}

{One question to invite engagement OR one contrarian take.}

{Optional: link to a longer piece — your own or someone else's that backs the point.}
```

**Discipline:**
- 240 chars max even though X allows more
- Not promotional — observation + question
- Don't tag the brand account in your own posts; that's spammy
- Threads are fine if the topic genuinely needs 4+ tweets, but each tweet must stand alone

---

## `linkedin_post`

Same shape as social_post but:
- 600-1000 chars
- Slightly more formal — LinkedIn rewards "professional but candid"
- Lead with a specific insight or counterintuitive take
- End with a question
- Use line breaks aggressively (LinkedIn's algorithm rewards readable formatting)

---

## `hacker_news_post`

Submit a link to your own pillar_page if it's genuinely informative. Title rules (HN-enforced):
- No editorialising ("Why X is the future")
- No "Show HN:" unless it's actually a Show HN
- No emojis, no all-caps
- Title matches the page's actual H1 or close to it

For a self-post (`text post`): keep to 150 words. Lead with the specific observation. End with a real question for the HN community.

---

## `guest_post_pitch`

Outreach to a publication editor. Same shape as `outreach_email` but include:
- 2-3 proposed headlines (let them pick)
- A line on why your perspective fits their audience specifically
- Link to one piece you've published (your blog, your LinkedIn)

NO full draft attached. Editors hate that.

---

## `podcast_pitch`

```
Subject: Guest idea — {topic in 5 words}

Hi {host},

{One sentence — a specific episode of theirs that connected to your work.
Show you've actually listened.}

{One sentence — your take on the topic, in your own voice.}

{One question — would they be open to discussing {specific angle}.}

— {operator}
```

NO bio paragraph. Hosts can google. The pitch is the topic, not the resume.
