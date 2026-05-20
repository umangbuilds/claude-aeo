"""Multi-LLM citation testing for aeo-loop.

Given seed queries and a brand identity (name + domain + competitors), this
module sends each query to each configured LLM, parses responses for brand
mentions, and returns a citation grid.

Architecture:
  - LLMAdapter protocol with .query(prompt) -> str
  - One concrete adapter per provider (OpenAI / Anthropic / Perplexity / Gemini)
  - CitationChecker orchestrates the matrix with retry/backoff
  - parse_response() does brand/competitor detection on text

Stdlib only — urllib for HTTP, no requests dependency. Adapters use streaming-
unfriendly request/response; that is intentional for v0.1 simplicity.

Tests in tests/test_citation_check.py mock the adapters via the FakeAdapter
class for deterministic and offline runs.
"""

from __future__ import annotations

import json
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol


DEFAULT_QUERY_TEMPLATES = [
    "What are the best {seed}?",
    "Tell me about {seed}.",
    "Which companies / products are leaders in {seed}?",
    "I'm researching {seed}. Who should I look at?",
    "What is {seed} and who provides it?",
]


# Region modifiers — appended to a prompt to geo-pin the LLM's answer. The
# citation rubric does not need a region tag (brand/domain substring is the
# matcher) — what shifts under geo-pinning is the LLM's *selection* of which
# brands to mention.
REGION_MODIFIERS = {
    "global": "",
    "india": (
        " I am based in India and asking for recommendations relevant to "
        "Indian users. Prefer providers operating in India where possible."
    ),
}


# Currency modifier — appended when the seed query is pricing-relevant
# (heuristic: presence of any token in PRICING_TOKENS). Mentioning the
# operator's currency in the prompt nudges the LLM toward brands with
# transparent pricing in that currency.
CURRENCY_MODIFIERS = {
    "USD": "",
    "INR": " Where pricing is relevant, prices in INR are preferred.",
    "EUR": " Where pricing is relevant, prices in EUR are preferred.",
    "GBP": " Where pricing is relevant, prices in GBP are preferred.",
}

PRICING_TOKENS = (
    "price", "pricing", "cost", "fee", "subscription", "plan",
    "tier", "cheap", "affordable", "budget", "free", "paid",
)

_PRICING_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(t) for t in PRICING_TOKENS) + r")\b",
    re.IGNORECASE,
)


def _is_pricing_relevant(query_text: str) -> bool:
    """True if any pricing token appears as a word in the query (case-insensitive)."""
    return _PRICING_RE.search(query_text) is not None


def build_prompt(
    query_text: str,
    region: str = "global",
    currency: str = "USD",
) -> str:
    """Compose a geo + currency aware prompt from a base query.

    The base query is preserved verbatim; modifiers are appended. This keeps
    the citation rubric stable across runs while shifting the LLM's selection
    bias toward the operator's region and currency.

    For global / USD (the defaults), this is a pure pass-through.
    """
    region_mod = REGION_MODIFIERS.get(region or "global", "")
    currency_mod = CURRENCY_MODIFIERS.get(currency or "USD", "")
    apply_currency = bool(currency_mod) and _is_pricing_relevant(query_text)
    if not region_mod and not apply_currency:
        return query_text
    parts = [query_text]
    if region_mod:
        parts.append(region_mod.lstrip())
    if apply_currency:
        parts.append(currency_mod.lstrip())
    return " ".join(parts)


@dataclass
class CitationResult:
    """One (query, provider) cell of the citation grid."""

    query_text: str
    provider: str
    is_cited: Optional[int]   # 1 cited, 0 not cited, None not checked
    citation_context: Optional[str] = None
    response_excerpt: Optional[str] = None
    competitors_cited: List[str] = field(default_factory=list)
    error: Optional[str] = None
    attempts: int = 1


class LLMAdapter(Protocol):
    """Any object with a .query(prompt: str) -> str method."""

    name: str

    def query(self, prompt: str) -> str: ...


# ---------------------------------------------------------------------------
# Concrete adapters (urllib-based; live calls only — mocked in tests)
# ---------------------------------------------------------------------------


_KEY_QUERY_PARAM_RE = re.compile(r"([?&])key=[^&]*", re.IGNORECASE)


def _redact_key_from_url(text: str) -> str:
    """Strip ?key=... from a URL or error message string."""
    return _KEY_QUERY_PARAM_RE.sub(r"\1key=REDACTED", text)


class ProviderError(RuntimeError):
    """Raised by adapters when an HTTP call fails. Message has API keys redacted."""


def _http_post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    """POST JSON, return parsed JSON. Redacts ?key=... from any exception message."""
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        # Re-raise with redacted text so downstream logging / DB persistence
        # never sees the Gemini-style key-in-URL.
        msg = _redact_key_from_url(f"{type(e).__name__}: {e}")
        raise ProviderError(msg) from None


DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "perplexity": "sonar",
    "gemini": "gemini-2.0-flash",
}


class OpenAIAdapter:
    name = "openai"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS["openai"]

    def query(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = _http_post_json("https://api.openai.com/v1/chat/completions", headers, body)
        return resp["choices"][0]["message"]["content"]


class AnthropicAdapter:
    name = "anthropic"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS["anthropic"]

    def query(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        resp = _http_post_json("https://api.anthropic.com/v1/messages", headers, body)
        # response shape: {"content": [{"type":"text","text":"..."}], ...}
        parts = resp.get("content", [])
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text")


class PerplexityAdapter:
    name = "perplexity"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS["perplexity"]

    def query(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = _http_post_json("https://api.perplexity.ai/chat/completions", headers, body)
        return resp["choices"][0]["message"]["content"]


class GeminiAdapter:
    name = "gemini"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS["gemini"]

    def query(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        resp = _http_post_json(url, headers, body)
        candidates = resp.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)


def build_adapters_from_capabilities(caps, config: Dict[str, Dict[str, str]]) -> Dict[str, LLMAdapter]:
    """Given a Capabilities object and a parsed config, return active adapters.

    Reads [llm_models] section for per-provider model overrides. Falls back to
    DEFAULT_MODELS when override is empty or missing.
    """
    out: Dict[str, LLMAdapter] = {}
    llm_cfg = config.get("llm", {})
    models_cfg = config.get("llm_models", {})
    if caps.llm.get("openai"):
        out["openai"] = OpenAIAdapter(
            llm_cfg["openai"], model=models_cfg.get("openai") or None,
        )
    if caps.llm.get("anthropic"):
        out["anthropic"] = AnthropicAdapter(
            llm_cfg["anthropic"], model=models_cfg.get("anthropic") or None,
        )
    if caps.llm.get("perplexity"):
        out["perplexity"] = PerplexityAdapter(
            llm_cfg["perplexity"], model=models_cfg.get("perplexity") or None,
        )
    if caps.llm.get("gemini"):
        out["gemini"] = GeminiAdapter(
            llm_cfg["gemini"], model=models_cfg.get("gemini") or None,
        )
    return out


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


UNTRUSTED_OPEN = "<<<UNTRUSTED_LLM_OUTPUT>>>"
UNTRUSTED_CLOSE = "<<<END_UNTRUSTED>>>"


def _strip_control_chars(text: str) -> str:
    """Remove non-printable control characters except newline / tab.

    Mitigates ASI01 attack surface: a malicious LLM response containing
    terminal escape sequences, NULL bytes, or other control codes that
    could influence downstream rendering or Claude's reasoning over the
    stored excerpt.
    """
    if not text:
        return ""
    return "".join(
        c for c in text
        if c == "\n" or c == "\t"
        or (0x20 <= ord(c) < 0x7F)
        or ord(c) >= 0xA0   # keep printable Unicode (drops C1 controls 0x80-0x9F)
    )


def fence_untrusted(text: str) -> str:
    """Wrap LLM-response text in untrusted-data delimiters.

    Any downstream reader (Claude during analyze, the operator reading the
    report) must treat the content between the delimiters as evidence to
    reason ABOUT, never as instructions to follow. This is the ASI01
    defence per AGENTS.md "Prompt-injection defense" section.

    Breakout protection: if the text itself contains either delimiter
    literal, the delimiters inside the text are escaped before wrapping so
    an attacker cannot break out of the fence by including the close marker
    in their poisoned response.
    """
    safe = text.replace(UNTRUSTED_OPEN, UNTRUSTED_OPEN + "_ESCAPED")
    safe = safe.replace(UNTRUSTED_CLOSE, UNTRUSTED_CLOSE + "_ESCAPED")
    return f"{UNTRUSTED_OPEN}{safe}{UNTRUSTED_CLOSE}"


def _normalise(text: str) -> str:
    return text.lower()


_DOMAIN_LEFT_BOUNDARY = r"(?:^|[\s\(\[\"'`<>/:@])"
_DOMAIN_RIGHT_BOUNDARY = r"(?:$|[\s\)\]\"'`<>.,;:!?/])"


def _word_match(text_lower: str, token: str) -> bool:
    """Case-insensitive whole-word match for a single token in already-lower text.

    Used for brand-name and competitor matching where 'moltpe' inside
    'supermoltpex' must not count as a hit.
    """
    if not token:
        return False
    return re.search(r"\b" + re.escape(token.lower()) + r"\b", text_lower) is not None


def _brand_in_text(text_lower: str, brand_name: str, brand_domain: str) -> bool:
    """Match either brand name or domain with domain-aware boundaries.

    Domain match requires a non-domain character (or string start) immediately
    before the domain — prevents 'pay.com' false-positive matching inside
    'rapidpay.com'.
    """
    if brand_domain:
        dom = brand_domain.lower()
        pattern = _DOMAIN_LEFT_BOUNDARY + re.escape(dom) + _DOMAIN_RIGHT_BOUNDARY
        if re.search(pattern, text_lower):
            return True
        if text_lower.startswith(dom + "/") or text_lower == dom:
            return True
    return _word_match(text_lower, brand_name)


def _extract_context(text: str, brand_name: str, brand_domain: str, window: int = 160) -> Optional[str]:
    """Return the snippet around the first brand mention."""
    text_lower = text.lower()
    needle = None
    if brand_domain and brand_domain.lower() in text_lower:
        needle = brand_domain.lower()
    elif brand_name:
        m = re.search(r"\b" + re.escape(brand_name.lower()) + r"\b", text_lower)
        if m:
            needle = brand_name.lower()
    if not needle:
        return None
    idx = text_lower.find(needle)
    start = max(0, idx - window)
    end = min(len(text), idx + len(needle) + window)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def parse_response(
    text: str,
    brand_name: str,
    brand_domain: str = "",
    competitors: Optional[List[str]] = None,
) -> Dict:
    """Inspect a response and report citation status."""
    if not text:
        return {
            "is_cited": 0,
            "citation_context": None,
            "competitors_cited": [],
            "response_excerpt": "",
        }

    # Strip control chars at the boundary so they never enter the store.
    text = _strip_control_chars(text)
    text_lower = _normalise(text)
    cited = _brand_in_text(text_lower, brand_name, brand_domain)
    context = _extract_context(text, brand_name, brand_domain) if cited else None

    comp_hits: List[str] = [
        comp for comp in (competitors or [])
        if _word_match(text_lower, comp)
    ]

    return {
        "is_cited": 1 if cited else 0,
        "citation_context": context,
        "competitors_cited": comp_hits,
        "response_excerpt": text[:500],
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class BrandIdentity:
    name: str
    domain: str = ""
    competitors: List[str] = field(default_factory=list)
    region: str = "global"          # 'global' or 'india' at v0.1
    currency: str = "USD"           # ISO 4217; 'INR' for India-region brands


class CitationChecker:
    """Orchestrates query × provider matrix with retry/backoff."""

    def __init__(
        self,
        adapters: Dict[str, LLMAdapter],
        max_retries: int = 3,
        backoff_base: float = 1.5,
        prompt_template: str = "{query}",
    ):
        self.adapters = adapters
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.prompt_template = prompt_template

    def _sleep(self, seconds: float) -> None:  # pragma: no cover (mocked in tests)
        time.sleep(seconds)

    def check_one(
        self,
        query_text: str,
        provider: str,
        identity: BrandIdentity,
    ) -> CitationResult:
        adapter = self.adapters.get(provider)
        if adapter is None:
            return CitationResult(
                query_text=query_text, provider=provider,
                is_cited=None, error=f"no adapter configured for {provider}",
                attempts=0,
            )

        base = self.prompt_template.format(query=query_text)
        prompt = build_prompt(base, region=identity.region, currency=identity.currency)
        last_error: Optional[str] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = adapter.query(prompt)
                parsed = parse_response(
                    response, identity.name, identity.domain, identity.competitors
                )
                return CitationResult(
                    query_text=query_text,
                    provider=provider,
                    is_cited=parsed["is_cited"],
                    citation_context=parsed["citation_context"],
                    response_excerpt=parsed["response_excerpt"],
                    competitors_cited=parsed["competitors_cited"],
                    attempts=attempt,
                )
            except ProviderError as e:
                # Message is already redacted by _http_post_json.
                last_error = str(e)
                if attempt < self.max_retries:
                    delay = self.backoff_base ** attempt + random.uniform(0, 0.5)
                    self._sleep(delay)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                last_error = _redact_key_from_url(f"{type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    delay = self.backoff_base ** attempt + random.uniform(0, 0.5)
                    self._sleep(delay)
            except Exception as e:   # noqa: BLE001 — bubble unexpected errors after retries
                last_error = _redact_key_from_url(f"{type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    delay = self.backoff_base ** attempt + random.uniform(0, 0.5)
                    self._sleep(delay)

        return CitationResult(
            query_text=query_text,
            provider=provider,
            is_cited=None,
            error=last_error,
            attempts=self.max_retries,
        )

    def check_matrix(
        self,
        queries: List[str],
        identity: BrandIdentity,
        providers: Optional[List[str]] = None,
    ) -> List[CitationResult]:
        """Run every (query × provider) cell. Returns flat list."""
        chosen = providers or list(self.adapters.keys())
        out: List[CitationResult] = []
        for q in queries:
            for p in chosen:
                out.append(self.check_one(q, p, identity))
        return out


def grid_summary(results: List[CitationResult]) -> Dict:
    """Compute citation-rate summary stats from a flat list of results."""
    by_provider: Dict[str, Dict[str, int]] = {}
    for r in results:
        bucket = by_provider.setdefault(
            r.provider, {"cited": 0, "not_cited": 0, "not_checked": 0}
        )
        if r.is_cited == 1:
            bucket["cited"] += 1
        elif r.is_cited == 0:
            bucket["not_cited"] += 1
        else:
            bucket["not_checked"] += 1

    overall_checked = sum(b["cited"] + b["not_cited"] for b in by_provider.values())
    overall_cited = sum(b["cited"] for b in by_provider.values())
    overall_rate = (overall_cited / overall_checked) if overall_checked else 0.0

    return {
        "by_provider": by_provider,
        "overall_rate": overall_rate,
        "overall_checked": overall_checked,
        "overall_cited": overall_cited,
    }
