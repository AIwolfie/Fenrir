"""URL validation and sanitization helpers for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse

ONION_HOST_LENGTHS = {16, 56}


def is_onion_url(url: str) -> bool:
    """Return True when the URL points to a valid onion host."""

    parsed = urlparse(url.strip())
    hostname = parsed.hostname or ""
    if parsed.scheme not in {"http", "https"}:
        return False
    if not hostname.endswith(".onion"):
        return False
    onion_label = hostname[:-6]
    return len(onion_label) in ONION_HOST_LENGTHS and onion_label.isalnum()


def normalize_url(url: str) -> str:
    """Normalize a URL for crawling."""

    parsed = urlparse(url.strip())
    scheme = parsed.scheme or "http"
    hostname = parsed.hostname or ""
    netloc = hostname
    if parsed.port:
        netloc = f"{hostname}:{parsed.port}"
    path = parsed.path or "/"
    return urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))


def sanitize_url(url: str) -> str:
    """Return a trimmed, normalized URL string."""

    return normalize_url(url.strip())
