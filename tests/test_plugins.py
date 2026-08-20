"""Unit tests for DeepRecon plugin system and extractors."""

from __future__ import annotations

from core.parser import PageData
from plugins import discover_plugins
from plugins.crypto_detector import CryptoDetector
from plugins.email_extractor import EmailExtractor
from plugins.fingerprinter import FingerprinterPlugin
from plugins.language_detector import LanguageDetector
from plugins.pgp_harvester import PGPHarvester


def test_discover_plugins():
    plugins = discover_plugins(["email_extractor", "crypto_detector", "fingerprinter"])
    assert len(plugins) >= 3
    names = [p.name for p in plugins]
    assert "email_extractor" in names
    assert "crypto_detector" in names
    assert "fingerprinter" in names


def test_crypto_detector():
    plugin = CryptoDetector()
    page = PageData(
        url="http://test.onion",
        text="Send 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or 0x742d35Cc6634C0532925a3b844Bc454e4438f44e or 44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGeiSTRMGKiRN2ePXCeGWB4BTdrGLdfSS5VJy5bPh",
    )
    res = plugin.extract(page)
    assert len(res["bitcoin"]) == 1
    assert len(res["ethereum"]) == 1
    assert len(res["monero"]) == 1


def test_email_extractor():
    plugin = EmailExtractor()
    page = PageData(
        url="http://test.onion",
        text="Contact support at admin@darkmarket.onion or test@example.com",
    )
    res = plugin.extract(page)
    assert "admin@darkmarket.onion" in res["emails"]
    assert "test@example.com" in res["emails"]


def test_fingerprinter_plugin():
    plugin = FingerprinterPlugin()
    page = PageData(
        url="http://test.onion",
        raw_html="<div data-reactroot=''>Hello from Next.js /_next/static with TailwindCSS class='p-4 bg-gray-900'></div>",
        headers={"Server": "nginx/1.18.0", "X-Powered-By": "Express"},
    )
    res = plugin.extract(page)
    tech = res["detected_technologies"]
    assert "React" in tech
    assert "Next.js" in tech
    assert "TailwindCSS" in tech
    assert "Nginx" in tech
    assert "Express/Node" in tech


def test_pgp_harvester():
    plugin = PGPHarvester()
    pgp_key = "-----BEGIN PGP PUBLIC KEY BLOCK-----\nmQENBF7...test\n-----END PGP PUBLIC KEY BLOCK-----"
    page = PageData(url="http://test.onion", text=f"My key:\n{pgp_key}")
    res = plugin.extract(page)
    assert len(res["pgp_blocks"]) == 1
