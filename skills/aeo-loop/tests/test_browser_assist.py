"""Tests for scripts/browser_assist.py — URL building per platform."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import browser_assist as ba  # noqa: E402


class RedditTests(unittest.TestCase):

    def test_strips_subreddit_prefix(self):
        r = ba.reddit("r/SEO", "title", "body")
        self.assertIn("/r/SEO/submit", r.open_url)

    def test_handles_bare_subreddit(self):
        r = ba.reddit("SEO", "title", "body")
        self.assertIn("/r/SEO/submit", r.open_url)

    def test_url_encodes_title_and_body(self):
        r = ba.reddit("SEO", "How to win AEO?", "body with spaces")
        parsed = parse_qs(urlparse(r.open_url).query)
        self.assertEqual(parsed["title"], ["How to win AEO?"])
        self.assertEqual(parsed["text"], ["body with spaces"])

    def test_clipboard_holds_body(self):
        r = ba.reddit("SEO", "t", "the body")
        self.assertEqual(r.clipboard, "the body")
        self.assertEqual(r.platform, "reddit")


class WikipediaTests(unittest.TestCase):

    def test_underscores_page_title(self):
        r = ba.wikipedia("My Brand", "draft text")
        self.assertIn("title=My_Brand", r.open_url)
        self.assertIn("action=edit", r.open_url)

    def test_includes_summary_when_provided(self):
        r = ba.wikipedia("X", "draft", summary="initial draft")
        parsed = parse_qs(urlparse(r.open_url).query)
        self.assertEqual(parsed["summary"], ["initial draft"])

    def test_coi_reminder_in_instructions(self):
        r = ba.wikipedia("X", "draft")
        self.assertIn("COI", r.instructions)

    def test_talk_page_uses_section_new(self):
        r = ba.wikipedia_talk("X", "discussion text")
        self.assertIn("Talk:X", r.open_url)
        self.assertIn("section=new", r.open_url)


class SocialTests(unittest.TestCase):

    def test_twitter_intent_url(self):
        r = ba.twitter("hello world")
        self.assertIn("twitter.com/intent/tweet", r.open_url)
        parsed = parse_qs(urlparse(r.open_url).query)
        self.assertEqual(parsed["text"], ["hello world"])

    def test_linkedin_with_url_uses_share_offsite(self):
        r = ba.linkedin("post body", url="https://example.com")
        self.assertIn("share-offsite", r.open_url)

    def test_linkedin_without_url_uses_feed_share(self):
        r = ba.linkedin("post body")
        self.assertIn("/feed/", r.open_url)

    def test_hacker_news_includes_title(self):
        r = ba.hacker_news("a story", url="https://example.com")
        parsed = parse_qs(urlparse(r.open_url).query)
        self.assertEqual(parsed["t"], ["a story"])
        self.assertEqual(parsed["u"], ["https://example.com"])


class EmailTests(unittest.TestCase):

    def test_mailto_format(self):
        r = ba.email("a@b.com", "subj", "body")
        self.assertTrue(r.open_url.startswith("mailto:a%40b.com?"))
        parsed = parse_qs(urlparse(r.open_url).query)
        self.assertEqual(parsed["subject"], ["subj"])
        self.assertEqual(parsed["body"], ["body"])


class GenericFormTests(unittest.TestCase):

    def test_passes_url_through(self):
        r = ba.generic_form("https://forms.example.com/contact", "the message")
        self.assertEqual(r.open_url, "https://forms.example.com/contact")
        self.assertEqual(r.clipboard, "the message")


class DispatchTests(unittest.TestCase):

    def test_unknown_platform_raises(self):
        with self.assertRaises(ValueError):
            ba.build("instagram", text="x")

    def test_build_dispatches_to_reddit(self):
        r = ba.build("reddit", subreddit="SEO", title="t", body="b")
        self.assertEqual(r.platform, "reddit")

    def test_build_dispatches_to_email(self):
        r = ba.build("email", to="a@b.com", subject="s", body="b")
        self.assertEqual(r.platform, "email")


class IndianPlatformTests(unittest.TestCase):
    """India layer — quora_india, justdial, indiamart, mouthshut + reference lists."""

    def test_quora_india_returns_payload_with_coi_reminder(self):
        r = ba.quora_india("https://in.quora.com/What-is-X", "my answer body")
        self.assertEqual(r.platform, "quora_india")
        self.assertEqual(r.open_url, "https://in.quora.com/What-is-X")
        self.assertEqual(r.clipboard, "my answer body")
        self.assertIn("COI", r.instructions)

    def test_justdial_returns_paste_instructions(self):
        r = ba.justdial("https://www.justdial.com/listing/abc", "update text")
        self.assertEqual(r.platform, "justdial")
        self.assertIn("JustDial", r.instructions)

    def test_indiamart_returns_seller_panel_hint(self):
        r = ba.indiamart("https://www.indiamart.com/seller/xyz", "catalog update")
        self.assertEqual(r.platform, "indiamart")
        self.assertIn("seller-panel", r.instructions)

    def test_mouthshut_returns_coi_warning(self):
        r = ba.mouthshut("https://www.mouthshut.com/product/abc", "review draft")
        self.assertEqual(r.platform, "mouthshut")
        self.assertIn("COI", r.instructions)

    def test_indian_platforms_listed_in_supported(self):
        for p in ("quora_india", "justdial", "indiamart", "mouthshut"):
            self.assertIn(p, ba.SUPPORTED_PLATFORMS)

    def test_build_dispatches_indian_platforms(self):
        r = ba.build("quora_india", question_url="https://in.quora.com/x", body="b")
        self.assertEqual(r.platform, "quora_india")
        r = ba.build("justdial", listing_url="https://www.justdial.com/x", body="b")
        self.assertEqual(r.platform, "justdial")

    def test_indian_publications_constant_shape(self):
        self.assertGreater(len(ba.INDIAN_PUBLICATIONS), 0)
        for pub in ba.INDIAN_PUBLICATIONS:
            self.assertIn("name", pub)
            self.assertIn("category", pub)
            self.assertIn("pitch_email", pub)
            self.assertIn("@", pub["pitch_email"])

    def test_indian_subreddits_present(self):
        self.assertIn("india", ba.INDIAN_SUBREDDITS)
        self.assertIn("IndianStartups", ba.INDIAN_SUBREDDITS)
        self.assertIn("bangalore", ba.INDIAN_SUBREDDITS)


class UrlSchemeSecurityTests(unittest.TestCase):

    def test_https_allowed(self):
        url = ba._validate_scheme("https://example.com/page")
        self.assertEqual(url, "https://example.com/page")

    def test_http_allowed(self):
        url = ba._validate_scheme("http://example.com/page")
        self.assertEqual(url, "http://example.com/page")

    def test_mailto_allowed(self):
        url = ba._validate_scheme("mailto:test@example.com")
        self.assertEqual(url, "mailto:test@example.com")

    def test_javascript_rejected(self):
        with self.assertRaises(ValueError):
            ba._validate_scheme("javascript:alert(1)")

    def test_data_uri_rejected(self):
        with self.assertRaises(ValueError):
            ba._validate_scheme("data:text/html,<script>alert(1)</script>")

    def test_generic_form_validates_scheme(self):
        with self.assertRaises(ValueError):
            ba.generic_form("javascript:void(0)", "body")

    def test_quora_india_validates_scheme(self):
        with self.assertRaises(ValueError):
            ba.quora_india("javascript:fetch('/')", "body")

    def test_justdial_validates_scheme(self):
        with self.assertRaises(ValueError):
            ba.justdial("data:text/html,evil", "body")

    def test_indiamart_validates_scheme(self):
        with self.assertRaises(ValueError):
            ba.indiamart("javascript:alert()", "body")

    def test_mouthshut_validates_scheme(self):
        with self.assertRaises(ValueError):
            ba.mouthshut("ftp://not-allowed.com/page", "body")


if __name__ == "__main__":
    unittest.main()
