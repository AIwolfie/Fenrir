"""Crypto address extraction plugin for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from typing import Any

from core.parser import PageData
from plugins import BasePlugin


BTC_PATTERN = re.compile(r"\b(?:bc1[ac-hj-np-z02-9]{11,71}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")
ETH_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
XMR_PATTERN = re.compile(r"\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b|\b8[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b")


class CryptoDetector(BasePlugin):
    """Extract BTC, ETH, and XMR addresses from a page."""

    name = "crypto_detector"

    def extract(self, page: PageData) -> dict[str, Any]:
        text = page.raw_html or page.text or ""
        return {
            "bitcoin": sorted(set(BTC_PATTERN.findall(text))),
            "ethereum": sorted(set(ETH_PATTERN.findall(text))),
            "monero": sorted(set(XMR_PATTERN.findall(text))),
        }


PLUGIN_CLASS = CryptoDetector
