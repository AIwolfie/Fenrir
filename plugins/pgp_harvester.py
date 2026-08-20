"""PGP key extraction plugin for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from typing import Any

from core.parser import PageData
from plugins import BasePlugin


PGP_PATTERN = re.compile(
    r"-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----",
    re.DOTALL,
)


class PGPHarvester(BasePlugin):
    """Extract PGP public key blocks from a page."""

    name = "pgp_harvester"

    def extract(self, page: PageData) -> dict[str, Any]:
        return {"pgp_blocks": [block.strip() for block in PGP_PATTERN.findall(page.raw_html or page.text or "")]}


PLUGIN_CLASS = PGPHarvester
