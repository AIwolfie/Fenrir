"""Email extraction plugin for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from typing import Any

from core.parser import PageData
from plugins import BasePlugin


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class EmailExtractor(BasePlugin):
    """Extract email addresses from a parsed page."""

    name = "email_extractor"

    def extract(self, page: PageData) -> dict[str, Any]:
        return {"emails": sorted(set(EMAIL_PATTERN.findall(page.raw_html or page.text or "")))}


PLUGIN_CLASS = EmailExtractor
