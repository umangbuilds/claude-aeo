"""Tests for scripts/config.py — capability detection across key permutations."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make the scripts/ dir importable without packaging.
SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import config  # noqa: E402


class ParseSimpleTomlTests(unittest.TestCase):

    def test_handles_sections_and_quoted_strings(self):
        text = """
        # comment
        [llm]
        openai = "sk-test"
        anthropic = ''

        [seo_data]
        serpapi = "real-key"  # trailing comment
        """
        parsed = config._parse_simple_toml(text)
        self.assertEqual(parsed["llm"]["openai"], "sk-test")
        self.assertEqual(parsed["llm"]["anthropic"], "")
        self.assertEqual(parsed["seo_data"]["serpapi"], "real-key")

    def test_blank_file_returns_empty(self):
        self.assertEqual(config._parse_simple_toml(""), {})

    def test_ignores_malformed_lines(self):
        text = "no equals sign here\n[s]\nfoo = bar"
        parsed = config._parse_simple_toml(text)
        self.assertEqual(parsed["s"]["foo"], "bar")


class WriteTemplateTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "keys.toml"

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_template_when_missing(self):
        result = config.write_template(self.path)
        self.assertTrue(result.exists())
        self.assertIn("[llm]", result.read_text())
        self.assertIn("[seo_data]", result.read_text())

    def test_does_not_overwrite_existing(self):
        self.path.write_text('[llm]\nopenai = "preserved"\n')
        config.write_template(self.path)
        self.assertIn("preserved", self.path.read_text())


class CapabilityDetectionTests(unittest.TestCase):

    def _caps(self, llm=None, seo_data=None, image_gen=None, gsc=None):
        cfg = {}
        if llm is not None:
            cfg["llm"] = llm
        if seo_data is not None:
            cfg["seo_data"] = seo_data
        if image_gen is not None:
            cfg["image_gen"] = image_gen
        if gsc is not None:
            cfg["gsc"] = gsc
        return config.detect_capabilities(cfg)

    def test_no_keys_is_free_tier_with_no_active_llms(self):
        caps = self._caps()
        self.assertEqual(caps.tier, "free")
        self.assertEqual(caps.active_llms, ())

    def test_single_llm_key_active(self):
        caps = self._caps(llm={"openai": "sk-1"})
        self.assertIn("openai", caps.active_llms)
        self.assertEqual(len(caps.active_llms), 1)

    def test_all_four_llms_active(self):
        caps = self._caps(llm={p: f"key-{p}" for p in config.LLM_PROVIDERS})
        self.assertEqual(set(caps.active_llms), set(config.LLM_PROVIDERS))

    def test_paid_seo_provider_flips_tier_to_enhanced(self):
        caps = self._caps(seo_data={"serpapi": "real-key"})
        self.assertEqual(caps.tier, "enhanced")

    def test_dataforseo_requires_both_login_and_password(self):
        only_login = self._caps(seo_data={"dataforseo_login": "x"})
        self.assertFalse(only_login.seo_data["dataforseo"])

        both = self._caps(seo_data={"dataforseo_login": "x", "dataforseo_password": "y"})
        self.assertTrue(both.seo_data["dataforseo"])

    def test_image_gen_falls_back_to_llm_gemini(self):
        caps = self._caps(llm={"gemini": "g-key"})
        self.assertTrue(caps.image_gen["gemini_image"])

    def test_empty_string_keys_are_not_active(self):
        caps = self._caps(llm={"openai": "", "anthropic": "   "})
        self.assertEqual(caps.active_llms, ())

    def test_degradation_notes_when_one_llm_only(self):
        caps = self._caps(llm={"openai": "sk-1"})
        notes = caps.degradation_notes()
        self.assertTrue(any("fewer than 2 LLM providers" in n for n in notes))

    def test_degradation_notes_when_no_serp_provider(self):
        caps = self._caps(llm={"openai": "a", "anthropic": "b"})
        notes = caps.degradation_notes()
        self.assertTrue(any("competitor SERP" in n for n in notes))

    def test_no_degradation_notes_when_fully_configured(self):
        # Need a gsc file that exists, so write a temp one.
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp.write(b"{}")
        tmp.close()
        try:
            caps = self._caps(
                llm={p: f"k-{p}" for p in config.LLM_PROVIDERS},
                seo_data={
                    "dataforseo_login": "l",
                    "dataforseo_password": "p",
                    "serpapi": "s",
                    "firecrawl": "f",
                },
                image_gen={"gemini_image": "i"},
                gsc={"oauth_client_json": tmp.name},
            )
            self.assertEqual(caps.degradation_notes(), [])
        finally:
            os.unlink(tmp.name)


class GetProviderKeyTests(unittest.TestCase):

    def test_returns_key_for_nested_provider(self):
        cfg = {"llm": {"openai": "sk-test"}}
        self.assertEqual(config.get_provider_key("llm.openai", cfg), "sk-test")

    def test_returns_empty_for_missing(self):
        self.assertEqual(config.get_provider_key("llm.openai", {}), "")


class EnvOverrideTests(unittest.TestCase):

    def test_env_var_overrides_default_path(self):
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(b'[llm]\nopenai = "from-env"\n')
            fname = f.name
        try:
            os.environ["AEO_LOOP_CONFIG"] = fname
            try:
                cfg = config.load_config()
                self.assertEqual(cfg["llm"]["openai"], "from-env")
            finally:
                del os.environ["AEO_LOOP_CONFIG"]
        finally:
            os.unlink(fname)


if __name__ == "__main__":
    unittest.main()
