# Getting started — for people who don't come from marketing or coding

This guide assumes nothing. No marketing background, no SEO knowledge, no coding experience. If you can copy a command, paste it into your terminal, and read the output, you can use this skill.

If you already know what AEO, GEO, schema, GSC, and citation tracking are, skip this and read [README.md](README.md) instead — it's denser and quicker.

---

## What this skill actually does

Imagine Maya. She's 15. She runs a baking blog called `bakewithmaya.com`. She posts recipes every week. She wants more people to find her blog when they ask ChatGPT or Google "what's the easiest brownie recipe for beginners."

Here's the thing she discovered: **when she asks ChatGPT that question, ChatGPT names other baking blogs but not hers.** Same with Perplexity, same with Google's AI summary box. The AI tools that answer kids' homework, parents' cooking questions, and millions of other queries — they don't know Maya's blog exists.

This skill helps Maya (or you, or anyone with a website) do three things, every week:

1. **Check who AI chatbots are naming** when people ask questions Maya cares about.
2. **Get a list of 5–10 things to do this week** to slowly become one of the names they mention.
3. **Open the right page in her browser** with the post / message / edit pre-typed, so she just reviews and clicks Submit.

The skill does NOT post things for you. It prepares the post, opens the right page, and hands you the keyboard. You decide whether to send.

---

## Who this is for

You have a website (a blog, a small business site, a portfolio, a Discord community page, anything with a URL). You want more people to find it through search engines AND through AI chatbots. You can spend ~$5–10 per month on AI service fees, and you can run a few commands in your computer's terminal.

You do NOT need:

- A marketing background
- A coding background
- A team
- Money for an SEO agency
- An understanding of what AEO / GEO / SEO mean (we explain those at the bottom)

You DO need:

- A laptop (Mac, Windows, or Linux) that can run Python (most can, by default)
- Claude Code installed (free download from Anthropic — ask a tech-savvy friend if stuck)
- Sign-ups at a couple of AI companies, with a credit card on file
- About 30 minutes to set up the first time; 10 minutes a week after that

A note for parents / mentors: this is internal-use software, not a paid product. If a younger user is setting it up, the credit-card and account-creation steps need a grown-up's help. Everything else they can do themselves.

---

## What you'll spend money on

Honest upfront. You'll create accounts at AI companies (OpenAI, Anthropic, Perplexity, Google) and put a credit card on file. The skill makes small charges every time it runs:

- A typical weekly run costs about $0.50 to $2 in API fees.
- Across all 4 AI services, a month of weekly runs is usually $5 to $10 total per website.
- You can start with just one of the four AI services. The skill still works; you just see fewer perspectives.

You will NOT pay for:

- This skill itself (it's free).
- A subscription to a "SEO tool" (you don't need one).
- An agency.
- Hosting (the skill runs on your own laptop).

---

## Setup, step by step

Estimated time: 30 minutes the first time. After this, the weekly run is 10 minutes.

### Step 1 — Open your terminal

The terminal is the black/white text window on your computer where you type commands.

- **Mac:** press Command + Space, type "Terminal", press Enter.
- **Windows:** press the Windows key, type "PowerShell" or "Terminal", press Enter.
- **Linux:** you already know.

If you've never seen a terminal before, that's fine. You'll be typing exactly 5 to 8 short commands. Copy them from this guide, paste them in, press Enter.

### Step 2 — Make sure Python is installed

Type this and press Enter:

```bash
python3 --version
```

If you see something like `Python 3.9.6` or higher, you're set. If you see "command not found," download Python from `python.org`. Pick the version labeled "3.10" or higher.

### Step 3 — Tell the skill where you live (initialize it)

Run this command:

```bash
python3 ~/Documents/claudepe/dhurandhar_aeo+seo/.claude/skills/aeo-loop/scripts/aeo_loop.py init
```

(If your project lives in a different folder, adjust the path. The path is `<your-project-folder>/.claude/skills/aeo-loop/scripts/aeo_loop.py init`.)

The skill will tell you something like:

```
Initialized.
  Config: /Users/you/.config/aeo-loop/keys.toml  (edit this to add API keys)
  Store: /Users/you/.local/share/aeo-loop/store.db
  Tier: free
  Active LLMs: none
```

It created two files for you. The first one (the "Config") is where your AI service keys go. The second one (the "Store") is where the skill will save your weekly data so it can compare this week to last week.

### Step 4 — Get your AI service keys

You need at least TWO of the four. Start with whichever you already have an account at:

| Service | Where to sign up | Where to copy the API key from |
|---|---|---|
| **OpenAI** (ChatGPT's company) | `platform.openai.com/signup` | After login: `platform.openai.com/api-keys`, click "Create new secret key" |
| **Anthropic** (Claude's company) | `console.anthropic.com` | After login: Settings → API Keys → Create Key |
| **Perplexity** | `perplexity.ai/settings/api` | Settings → API → Generate |
| **Google Gemini** | `aistudio.google.com/apikey` | Click "Create API key" |

Each of these will:
- Ask you for an email
- Ask for a credit card (for billing — most have $5 free credit to start)
- Give you a long string of characters starting with `sk-` or similar. That's your key.

**Important:** treat the keys like passwords. Don't post them anywhere. Don't put them in a public file. If you ever accidentally share one, go back to the website and "revoke" or "delete" the key — they're easy to create new ones.

### Step 5 — Put your keys into the config file

Open the config file in any text editor (TextEdit on Mac, Notepad on Windows, or `nano` in the terminal):

```bash
open ~/.config/aeo-loop/keys.toml         # Mac
notepad %USERPROFILE%\.config\aeo-loop\keys.toml   # Windows
```

You'll see something like this:

```toml
[llm]
openai     = ""
anthropic  = ""
perplexity = ""
gemini     = ""
```

Paste your keys between the empty quotes. For example:

```toml
[llm]
openai     = "sk-abc123yourrealkeyhere"
anthropic  = "sk-ant-xyz789yourrealkey"
perplexity = ""
gemini     = ""
```

Two keys is the minimum the skill recommends. You can add more later.

Save the file and close it.

### Step 6 — Tell the skill about your website

```bash
python3 .../scripts/aeo_loop.py add-property bakewithmaya.com --brand "Bake With Maya" --one-liner "Easy baking recipes for beginners"
```

(Replace `bakewithmaya.com` with YOUR website, and the brand and one-liner with YOUR description.)

The `--brand` is what AI chatbots would write to refer to you. For a person it might be your name. For a business it's the business name. For a YouTube channel it's the channel name.

The `--one-liner` is one sentence describing what you do. Be specific. "Easy baking recipes for beginners" beats "a food blog."

**Are your readers mostly in India?** Add `--region india` at the end:

```bash
python3 .../scripts/aeo_loop.py add-property bakewithmaya.com --brand "Bake With Maya" --one-liner "Easy baking recipes for beginners" --region india
```

What that does: when the skill asks AI chatbots about your topic, it tells them you're asking from India. So instead of getting names of baking blogs popular in the US, you get the ones popular here. It also lets the skill suggest posting on Quora India, JustDial, MouthShut and writing to Indian magazines like YourStory and Inc42 — places that matter for Indian readers. If you sell anything, prices in your prompts are mentioned in ₹ (INR) instead of dollars. You can leave the flag off and add it later by running the same command with `--region india`.

### Step 7 — Tell the skill what questions you care about

These are the questions you imagine someone asking ChatGPT, where you'd love your website to come up.

For Maya:

```bash
python3 .../scripts/aeo_loop.py add-query bakewithmaya.com "easy brownie recipe for beginners"
python3 .../scripts/aeo_loop.py add-query bakewithmaya.com "first time baking what should I make"
python3 .../scripts/aeo_loop.py add-query bakewithmaya.com "moist chocolate cake without frosting"
```

Start with 5 to 10 questions. You can add more later. Phrase them the way a real person would type / speak — not the way an SEO expert would.

### Step 8 — Tell the skill who your competitors are

The skill compares — when AI mentions someone in your space and not you, that's a learning opportunity.

```bash
python3 .../scripts/aeo_loop.py add-competitor bakewithmaya.com "Sally's Baking Addiction"
python3 .../scripts/aeo_loop.py add-competitor bakewithmaya.com "King Arthur Baking" --competitor-domain kingarthurbaking.com
python3 .../scripts/aeo_loop.py add-competitor bakewithmaya.com "Joy of Baking"
```

You're done setting up. Anything else?

No. The setup is done. From now on it's a 10-minute weekly run.

---

## Your first weekly run

Once a week, run this from inside Claude Code:

```
/aeo-loop weekly bakewithmaya.com
```

The skill will do 8 things automatically, in one go, without asking you anything in between:

1. **Audit** your website for technical issues (broken links, missing titles, slow pages).
2. **Discover** new questions people are asking AI in your topic.
3. **Test** each of your questions against ChatGPT, Claude, Perplexity, Gemini — checks who's named and who isn't.
4. **Analyze** what changed from last week — better or worse.
5. **Brief** you on 5 to 10 things to do this week, ranked by which would help most for least effort.
6. **Draft** the content for each of those things — blog post drafts, social posts, replies you could post on Reddit, etc.
7. **Prep your browser** for the off-site stuff (Reddit posts, Wikipedia edits) so when you're ready, one command opens the right page with the text already typed in.
8. **Save** the results so next week's comparison knows where you were.

When the run finishes, the skill points you at a folder like this:

```
aeo-loop-output/bakewithmaya.com/2026-W21/
  report.md                 <- THE main file to read
  draft-001.md ... etc.     <- the actual posts / replies the skill wrote for you
```

Open `report.md`. It tells you:

- How many of your questions got you named this week, across each AI service
- How that compares to last week (better, worse, same)
- 5 to 10 specific things to do this week, ranked
- Where each draft lives so you can read it before posting

---

## Doing the things on the list

When you're ready to do one of the suggested actions (say, action #3 is "post this thread on r/Baking"):

```
/aeo-loop assist 3
```

The skill will:

- Print the exact link to open in your browser (Reddit's submit page for r/Baking, in this case).
- Put the draft text on your clipboard.
- Tell you the instructions.

You open the link, the form is pre-filled where possible, you paste the rest. **You read the post. You edit if needed. You click Submit.**

Once you've actually posted it:

```
/aeo-loop mark-done 3 --cited-on=reddit
```

This tells the skill "I did action #3, I posted on Reddit." Future runs will track whether your citation rate goes up because of it.

---

## What if I get stuck?

| Problem | What to do |
|---|---|
| "Command not found" when running python | Install Python from python.org — pick version 3.10 or higher. |
| The skill says "no LLM providers configured" | You didn't add any keys to `keys.toml`. Re-do Step 4 and 5. |
| The weekly run takes a long time / seems frozen | First runs can take 5–15 minutes because the skill is talking to 4 different AI services. Just wait. |
| One of the AI services returns errors | The skill keeps going with the other services and reports the failure. Free-tier limits and short downtimes are common. |
| I don't know what to put in `add-query` | Think of questions you'd type into ChatGPT if you didn't know the answer and wanted advice on your topic. 8 words or fewer per question is a good rule. |
| I don't know who my competitors are | Search for one of your queries on Google or ask ChatGPT "who are the most well-known sites that answer [your topic] questions." Pick the top 3–5. |

---

## A note on what NOT to do

This skill is designed to help you do real work — write better content, get genuine mentions, build real authority. It is NOT designed to:

- Auto-post stuff for you (you always click Submit yourself)
- Help you spam Reddit / Wikipedia / X — the skill refuses to draft anything that looks like spam, and the platforms will ban you if you try
- Trick AI services into citing you when your content isn't actually helpful

If you're tempted to write low-quality content just to get cited: don't. AI services are getting better at noticing patterns. Citation rate goes up for sites that are actually useful. The skill works because it helps you do less but more thoughtful work — not more sloppy work.

---

## Glossary — words you may have heard

Words that show up in the rest of the docs, in plain English:

- **AEO** (Answer Engine Optimization): making sure AI chatbots (ChatGPT, Claude, etc.) name you when they answer questions about your topic.
- **SEO** (Search Engine Optimization): making sure Google shows your website when people search.
- **GEO** (Generative Engine Optimization): same as AEO, different vendor's word.
- **LLM** (Large Language Model): the technical name for AI chatbots like ChatGPT, Claude, Gemini, Perplexity.
- **Citation**: when an AI or website names you / links to you / mentions your brand.
- **Citation rate**: out of the questions you care about, what percentage of them get you mentioned by AI chatbots. Higher is better.
- **Schema**: extra invisible info you add to your website that helps Google / AI services understand what each page is about. (The skill can generate this for you.)
- **API key**: a long password-like string that lets the skill talk to an AI service on your behalf.
- **Brand**: what AI chatbots would write to refer to you. Your name, business name, blog name.
- **Property**: another word for "your website."
- **Browser-assist**: the skill opens the right page in your browser with the text pre-filled. You click Submit. You're always the one who actually sends anything.
- **Weekly run**: the 8-step thing the skill does once per week. About 10 minutes of your attention.
- **Action-list**: the 5 to 10 things the skill recommends you do this week, ranked by which would help most for the time it takes.
- **Draft**: the actual content the skill wrote for you (blog post, Reddit thread, etc.). You read, edit, decide.

---

## Where to go next

- Want to set up the skill so it runs by itself every week? See [`references/scheduling-routines.md`](references/scheduling-routines.md) — picks a "let it run on Mondays at 9am" approach that matches your setup.
- Want to know the technical detail of how each step works? See the [README.md](README.md) — denser, written for builders.
- Want to know the philosophy behind why the skill works the way it does? Read the "Workflow philosophy" section near the top of [README.md](README.md).

---

You can do this. Most people who use SEO / AEO tools are operators or marketers, but the underlying work — write helpful things, get the right pages in front of the right people, measure what changes — is just attention and discipline. You don't need a marketing degree to bring those.
