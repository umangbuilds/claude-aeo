"""Browser-assist URL builder for aeo-loop (Level A — assist only).

The skill never POSTs anything. Given a drafted action, this module returns
the URL that should be opened in the operator's default browser, plus the
draft body (which the caller copies to the clipboard or surfaces as text).

Supported platforms:
  - reddit         (submit page for a subreddit; title + body pre-filled via URL)
  - wikipedia      (edit page or talk-page edit URL — body to clipboard)
  - twitter / x    (compose intent URL; text pre-filled)
  - linkedin       (share intent; text pre-filled)
  - hacker_news    (submit URL with title pre-filled)
  - email          (mailto: URI with subject + body)
  - generic_form   (just open the URL; copy body to clipboard)

The clipboard step is the caller's responsibility (skill calls `pbcopy` on
macOS, `xclip` on Linux). This module returns the *intended* clipboard
content so the caller knows what to copy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote, urlencode

_ALLOWED_URL_SCHEMES = ("http://", "https://", "mailto:")


def _validate_scheme(url: str) -> str:
    """Reject URLs whose scheme is not http, https, or mailto.

    Prevents javascript: or data: payloads from reaching the browser-open path.
    """
    if not any(url.lower().startswith(s) for s in _ALLOWED_URL_SCHEMES):
        raise ValueError(
            f"URL scheme not allowed: {url!r}. Only http/https/mailto are permitted."
        )
    return url


@dataclass
class BrowserAssist:
    """One assist payload. The CLI surfaces this to the operator."""

    open_url: str
    clipboard: Optional[str]
    instructions: str
    platform: str




# Indian publications relevant to outreach drafts. Used by the action drafter
# and surfaced in the CLI status; the email() helper does the actual draft
# assembly when an action picks one of these. Pitch contacts are the typical
# editorial entry points published on the outlet's own contact pages — keep
# values generic (no individuals named) so drift is minimal as people move.
INDIAN_PUBLICATIONS = (
    {"name": "YourStory",      "category": "startup",   "pitch_email": "editorial@yourstory.com"},
    {"name": "Inc42",          "category": "startup",   "pitch_email": "editor@inc42.com"},
    {"name": "ET Tech",        "category": "tech",      "pitch_email": "editor@economictimes.com"},
    {"name": "Moneycontrol",   "category": "fintech",   "pitch_email": "editor@moneycontrol.com"},
    {"name": "Livemint",       "category": "business",  "pitch_email": "feedback@livemint.com"},
    {"name": "NDTV Profit",    "category": "business",  "pitch_email": "feedback@ndtv.com"},
    {"name": "Forbes India",   "category": "business",  "pitch_email": "editorial@forbesindia.com"},
    {"name": "VCCircle",       "category": "vc",        "pitch_email": "editor@vccircle.com"},
)


# Indian subreddits worth knowing about. The existing reddit() function works
# with any subreddit name; this list is for the CLI / action drafter to surface
# region-relevant defaults when a property has region='india'.
INDIAN_SUBREDDITS = (
    "india",
    "IndianStartups",
    "IndianStreetBets",
    "IndianTeenagers",
    "bangalore",
    "mumbai",
    "delhi",
    "hyderabad",
    "pune",
    "chennai",
)


def _coalesce_text(parts) -> str:
    return "\n\n".join(p for p in parts if p)


def reddit(subreddit: str, title: str, body: str = "") -> BrowserAssist:
    """Open the Reddit submit page for <subreddit>, pre-fill title and body.

    Reddit's submit URL accepts `title` and `text` query params for self-posts.
    """
    sub = subreddit.lstrip("r/").lstrip("/")
    params = {"title": title, "text": body, "selftext": "true"}
    url = f"https://www.reddit.com/r/{sub}/submit?{urlencode(params)}"
    return BrowserAssist(
        open_url=url,
        clipboard=body,
        instructions=(
            f"Reddit submit page for r/{sub} opening. Title and body are pre-filled "
            "from the URL — review and edit before clicking Post. If the form "
            "looks blank (Reddit sometimes strips long body params), paste from "
            "clipboard which holds the same body."
        ),
        platform="reddit",
    )


def wikipedia(page_title: str, body: str, summary: str = "") -> BrowserAssist:
    """Open Wikipedia edit page. Body goes to clipboard (URL param has length cap).

    Includes COI reminder in instructions. The operator must self-disclose COI.
    """
    page = page_title.replace(" ", "_")
    url = f"https://en.wikipedia.org/w/index.php?title={quote(page)}&action=edit"
    if summary:
        url += f"&summary={quote(summary)}"
    return BrowserAssist(
        open_url=url,
        clipboard=body,
        instructions=(
            f"Wikipedia edit page for '{page_title}' opening. Body is on your "
            "clipboard — paste into the editor.\n\n"
            "COI REMINDER: if this page is about your brand, employer, or a "
            "client, declare the conflict of interest on the talk page first. "
            "Editing your own brand page without disclosure violates Wikipedia's "
            "COI policy and can result in a block."
        ),
        platform="wikipedia",
    )


def wikipedia_talk(page_title: str, body: str) -> BrowserAssist:
    """Open the talk page edit URL (preferred path for COI disclosure)."""
    page = page_title.replace(" ", "_")
    url = f"https://en.wikipedia.org/w/index.php?title=Talk:{quote(page)}&action=edit&section=new"
    return BrowserAssist(
        open_url=url,
        clipboard=body,
        instructions=(
            f"Wikipedia talk page for '{page_title}' — add a new section. "
            "Body is on your clipboard. Use this for COI disclosure or proposing "
            "edits rather than direct article edits."
        ),
        platform="wikipedia_talk",
    )


def twitter(text: str) -> BrowserAssist:
    """X / Twitter web intent — pre-fills tweet composer."""
    url = f"https://twitter.com/intent/tweet?{urlencode({'text': text})}"
    return BrowserAssist(
        open_url=url,
        clipboard=text,
        instructions=(
            "X (Twitter) compose window opening with text pre-filled. Review "
            "char count — intent URL doesn't enforce the 280 limit until you "
            "click Post."
        ),
        platform="twitter",
    )


def linkedin(text: str, url: Optional[str] = None) -> BrowserAssist:
    """LinkedIn share intent. URL param shares a link; otherwise plain text post."""
    if url:
        params = {"url": url}
        open_url = f"https://www.linkedin.com/sharing/share-offsite/?{urlencode(params)}"
    else:
        open_url = "https://www.linkedin.com/feed/?shareActive=true"
    return BrowserAssist(
        open_url=open_url,
        clipboard=text,
        instructions=(
            "LinkedIn share dialog opening. The post text is on your clipboard "
            "— paste into the composer. LinkedIn does not accept pre-filled body "
            "text via URL params; clipboard is the only path."
        ),
        platform="linkedin",
    )


def hacker_news(title: str, url: str = "") -> BrowserAssist:
    """HN submit page. Title pre-fills via URL param; story URL also accepted."""
    params = {"t": title}
    if url:
        params["u"] = url
    open_url = f"https://news.ycombinator.com/submit?{urlencode(params)}"
    return BrowserAssist(
        open_url=open_url,
        clipboard=title,
        instructions=(
            "Hacker News submit page. Title is pre-filled. Review before submit; "
            "HN has strict guidelines about titles (no editorialising)."
        ),
        platform="hacker_news",
    )


def email(to: str, subject: str, body: str) -> BrowserAssist:
    """mailto: URI. Opens the operator's default mail client."""
    params = {"subject": subject, "body": body}
    open_url = f"mailto:{quote(to)}?{urlencode(params)}"
    return BrowserAssist(
        open_url=open_url,
        clipboard=body,
        instructions=(
            f"Mailto: opening to {to}. Subject and body pre-filled in your "
            "default mail client. If the body got truncated, paste from "
            "clipboard."
        ),
        platform="email",
    )


def quora_india(question_url: str, body: str) -> BrowserAssist:
    """Quora India answer composer. Body to clipboard; no URL pre-fill path.

    Quora does not accept pre-filled answer body via URL params. We open the
    question's in.quora.com URL and the operator pastes from clipboard.
    """
    return BrowserAssist(
        open_url=_validate_scheme(question_url),
        clipboard=body,
        instructions=(
            "Quora India question page opening. The answer draft is on your "
            "clipboard — paste into the Answer composer.\n\n"
            "COI REMINDER: if your brand or employer is the subject, disclose "
            "the affiliation in the first line of the answer. Quora's BNBR "
            "(Be Nice, Be Respectful) policy treats hidden promotion as spam."
        ),
        platform="quora_india",
    )


def justdial(listing_url: str, body: str) -> BrowserAssist:
    """JustDial business listing. Manual paste — JustDial form is JS-rendered."""
    return BrowserAssist(
        open_url=_validate_scheme(listing_url),
        clipboard=body,
        instructions=(
            f"JustDial listing page opening at {listing_url}. The update / "
            "review draft is on your clipboard. JustDial's edit forms are "
            "JavaScript-rendered — paste manually into the relevant field. "
            "Verify business ownership before submitting any edit."
        ),
        platform="justdial",
    )


def indiamart(listing_url: str, body: str) -> BrowserAssist:
    """IndiaMART product listing / catalog edit. Paste-driven."""
    return BrowserAssist(
        open_url=_validate_scheme(listing_url),
        clipboard=body,
        instructions=(
            f"IndiaMART page opening at {listing_url}. Draft is on your clipboard. "
            "IndiaMART seller-panel edits require seller login and 2FA — sign in "
            "first, then paste into the target field."
        ),
        platform="indiamart",
    )


def mouthshut(listing_url: str, body: str) -> BrowserAssist:
    """MouthShut.com review page. Body to clipboard."""
    return BrowserAssist(
        open_url=_validate_scheme(listing_url),
        clipboard=body,
        instructions=(
            f"MouthShut.com page opening at {listing_url}. Review draft is on "
            "your clipboard.\n\n"
            "COI REMINDER: MouthShut requires reviewers to disclose any "
            "affiliation with the business reviewed. Hidden promotional reviews "
            "are removed and may flag the account."
        ),
        platform="mouthshut",
    )


def generic_form(form_url: str, body: str) -> BrowserAssist:
    """Just open a URL; copy the draft to clipboard."""
    return BrowserAssist(
        open_url=_validate_scheme(form_url),
        clipboard=body,
        instructions=(
            f"Opening {form_url}. Draft is on your clipboard — paste into the "
            "appropriate field."
        ),
        platform="generic_form",
    )


_BUILDERS = {
    "reddit": reddit,
    "wikipedia": wikipedia,
    "wikipedia_talk": wikipedia_talk,
    "twitter": twitter,
    "linkedin": linkedin,
    "hacker_news": hacker_news,
    "email": email,
    "generic_form": generic_form,
    "quora_india": quora_india,
    "justdial": justdial,
    "indiamart": indiamart,
    "mouthshut": mouthshut,
}

# Single source of truth — derived from _BUILDERS so it never drifts.
SUPPORTED_PLATFORMS = tuple(_BUILDERS)


def build(action_type: str, **kwargs) -> BrowserAssist:
    """Dispatcher — pick the right builder by action type name.

    Raises ValueError if the type is not in SUPPORTED_PLATFORMS.
    """
    if action_type not in SUPPORTED_PLATFORMS:
        raise ValueError(
            f"unsupported platform {action_type!r}. "
            f"Supported: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    return _BUILDERS[action_type](**kwargs)
