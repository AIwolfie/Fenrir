"""Language detection plugin for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

from typing import Any

from core.parser import PageData
from plugins import BasePlugin

try:
    from langdetect import detect
except ImportError:  # pragma: no cover - optional dependency
    detect = None


class LanguageDetector(BasePlugin):
    """Detect the page language when langdetect is available."""

    name = "language_detector"

    def extract(self, page: PageData) -> dict[str, Any]:
        if detect is None:
            return {"language": page.language or None}
        text = page.text.strip()
        if not text:
            return {"language": None}
        try:
            return {"language": detect(text)}
        except Exception:
            return {"language": page.language or None}


PLUGIN_CLASS = LanguageDetector
