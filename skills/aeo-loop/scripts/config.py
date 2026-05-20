"""Credential and capability config for aeo-loop.

Reads ~/.config/aeo-loop/keys.toml (or AEO_LOOP_CONFIG path) and reports
which providers are configured. Writes a template on first install.

Schema (keys.toml):

    [llm]
    openai = "sk-..."
    anthropic = "sk-ant-..."
    perplexity = "pplx-..."
    gemini = "..."

    [seo_data]
    dataforseo_login = ""
    dataforseo_password = ""
    serpapi = ""
    firecrawl = ""

    [image_gen]
    gemini_image = ""

    [gsc]
    oauth_client_json = ""

    [browser]
    profile = "default"
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


DEFAULT_CONFIG_DIR = Path.home() / ".config" / "aeo-loop"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "keys.toml"

LLM_PROVIDERS = ("openai", "anthropic", "perplexity", "gemini")
SEO_DATA_PROVIDERS = ("dataforseo", "serpapi", "firecrawl")
IMAGE_GEN_PROVIDERS = ("gemini_image",)


TEMPLATE = """# aeo-loop credential file
# chmod 600 this file. Never commit it. Never share it.
# Empty values disable the provider; aeo-loop degrades gracefully.

[llm]
openai     = ""
anthropic  = ""
perplexity = ""
gemini     = ""

[llm_models]
# Optional per-provider model overrides. Leave empty to use the documented
# defaults baked into scripts/citation_check.py DEFAULT_MODELS. When a model
# is deprecated by the provider, override here without touching code.
openai     = ""
anthropic  = ""
perplexity = ""
gemini     = ""

[seo_data]
# Optional paid SEO data providers. Free-tier runs without these.
dataforseo_login    = ""
dataforseo_password = ""
serpapi             = ""
firecrawl           = ""

[image_gen]
# Optional. Re-uses [llm].gemini if both are present and only one is set.
gemini_image = ""

[gsc]
# Path to Google OAuth client_secret*.json for Search Console.
oauth_client_json = ""

[browser]
# Chrome profile name for browser-assist (Level A).
profile = "default"
"""


def _parse_simple_toml(text: str) -> Dict[str, Dict[str, str]]:
    """Minimal TOML reader for the aeo-loop schema (sections + string keys).

    Handles: comments (#), section headers ([section]), key = "value" pairs.
    Does not handle: nested tables, arrays, multi-line strings, numeric / bool
    coercion. Sufficient for keys.toml.
    """
    result: Dict[str, Dict[str, str]] = {}
    current = result.setdefault("__root__", {})
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = result.setdefault(section, {})
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        current[key] = value
    result.pop("__root__", None)
    return result


@dataclass
class Capabilities:
    """Which providers are configured with non-empty keys."""

    llm: Dict[str, bool] = field(default_factory=dict)
    seo_data: Dict[str, bool] = field(default_factory=dict)
    image_gen: Dict[str, bool] = field(default_factory=dict)
    gsc_connected: bool = False
    browser_profile: str = "default"

    @property
    def active_llms(self) -> tuple:
        return tuple(p for p, on in self.llm.items() if on)

    @property
    def tier(self) -> str:
        """Free vs Enhanced classification based on which keys are present."""
        any_paid = any(self.seo_data.values()) or any(self.image_gen.values())
        return "enhanced" if any_paid else "free"

    def degradation_notes(self) -> list:
        """Human-readable list of features unavailable due to missing keys."""
        notes = []
        if len(self.active_llms) < 2:
            notes.append(
                "fewer than 2 LLM providers configured — cross-LLM citation comparison "
                "will be partial. Add a second key to keys.toml for richer signal."
            )
        if not self.seo_data.get("dataforseo") and not self.seo_data.get("serpapi"):
            notes.append(
                "no SERP data provider configured — competitor SERP tracking is "
                "deferred. Free-tier covers owned-property ranks via GSC."
            )
        if not self.seo_data.get("firecrawl"):
            notes.append(
                "no Firecrawl key — full-site JS-rendered crawl is unavailable. "
                "WebFetch fallback handles static pages."
            )
        if not self.image_gen.get("gemini_image"):
            notes.append(
                "no image-gen key — OG / hero image actions will be flagged but "
                "not auto-drafted."
            )
        if not self.gsc_connected:
            notes.append(
                "Google Search Console not connected — owned-property SEO rank "
                "tracking unavailable until OAuth is completed."
            )
        return notes


def _config_path() -> Path:
    override = os.environ.get("AEO_LOOP_CONFIG")
    if override:
        return Path(override).expanduser()
    return DEFAULT_CONFIG_PATH


class InsecureConfigError(RuntimeError):
    """Raised when keys.toml ends up world-readable / group-readable."""


def write_template(path: Path = None, allow_insecure: bool = False) -> Path:
    """Create the config directory and write a template file if missing.

    Returns the path written. If the file already exists, leaves it alone
    and returns the existing path.

    On non-Windows systems, the file is chmod 0o600 and verified — if the
    final mode still has any group/world bits set, raises InsecureConfigError
    so credentials are not silently left readable. Pass allow_insecure=True
    to skip the verification (rare — for tests or unusual filesystems).
    """
    target = path or _config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(TEMPLATE)
        if os.name != "nt":
            try:
                os.chmod(target, 0o600)
            except OSError:
                pass
            if not allow_insecure:
                try:
                    mode = os.stat(target).st_mode & 0o777
                    if mode & 0o077:
                        raise InsecureConfigError(
                            f"{target} has insecure permissions ({oct(mode)}). "
                            "Expected 0o600. Move keys.toml off this filesystem, "
                            "or pass allow_insecure=True (not recommended)."
                        )
                except FileNotFoundError:
                    pass
    return target


def load_config(path: Path = None) -> Dict[str, Dict[str, str]]:
    """Load and parse keys.toml. Returns {} if missing (caller decides handling)."""
    target = path or _config_path()
    if not target.exists():
        return {}
    return _parse_simple_toml(target.read_text())


def detect_capabilities(config: Dict[str, Dict[str, str]] = None) -> Capabilities:
    """Inspect a config dict and report which providers are active."""
    if config is None:
        config = load_config()

    llm_section = config.get("llm", {})
    seo_section = config.get("seo_data", {})
    img_section = config.get("image_gen", {})
    gsc_section = config.get("gsc", {})
    browser_section = config.get("browser", {})

    llm = {p: bool(llm_section.get(p, "").strip()) for p in LLM_PROVIDERS}

    # DataForSEO needs BOTH login and password to be active.
    seo_data = {
        "dataforseo": bool(seo_section.get("dataforseo_login", "").strip())
        and bool(seo_section.get("dataforseo_password", "").strip()),
        "serpapi": bool(seo_section.get("serpapi", "").strip()),
        "firecrawl": bool(seo_section.get("firecrawl", "").strip()),
    }

    image_gen = {
        "gemini_image": bool(img_section.get("gemini_image", "").strip())
        or bool(llm_section.get("gemini", "").strip()),
    }

    gsc_path = gsc_section.get("oauth_client_json", "").strip()
    gsc_connected = bool(gsc_path) and Path(gsc_path).expanduser().exists()

    profile = browser_section.get("profile", "default").strip() or "default"

    return Capabilities(
        llm=llm,
        seo_data=seo_data,
        image_gen=image_gen,
        gsc_connected=gsc_connected,
        browser_profile=profile,
    )


def get_provider_key(provider: str, config: Dict[str, Dict[str, str]] = None) -> str:
    """Return the API key for a given provider, or '' if not configured.

    Provider names match Capabilities fields: llm.openai, seo_data.serpapi, etc.
    """
    if config is None:
        config = load_config()
    section, _, name = provider.partition(".")
    return (config.get(section, {}).get(name, "") or "").strip()


if __name__ == "__main__":
    # Quick diagnostic when run directly.
    path = write_template()
    caps = detect_capabilities()
    print(f"Config: {path}")
    print(f"Tier: {caps.tier}")
    print(f"Active LLMs: {', '.join(caps.active_llms) or 'none'}")
    print(f"GSC connected: {caps.gsc_connected}")
    print(f"Browser profile: {caps.browser_profile}")
    notes = caps.degradation_notes()
    if notes:
        print("\nDegradation notes:")
        for n in notes:
            print(f"  - {n}")
