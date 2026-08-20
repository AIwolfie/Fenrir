"""Data models for DeepRecon storage.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Site:
    """Represents a crawled site."""

    id: int | None = None
    root_url: str = ""
    title: str | None = None
    status_code: int | None = None
    tech_stack: str | None = None
    relevance_score: float = 0.0
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class Page:
    """Represents a crawled page and its extracted metadata."""

    id: int | None = None
    site_id: int | None = None
    session_id: int | None = None
    url: str = ""
    final_url: str | None = None
    title: str | None = None
    content: str = ""
    raw_html: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    headers: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    language: str | None = None
    relevance_score: float = 0.0
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class Link:
    """Represents an edge between two pages."""

    id: int | None = None
    page_id: int | None = None
    source_url: str = ""
    target_url: str = ""
    is_internal: bool = True
    anchor_text: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class KeywordHit:
    """Represents a keyword or regex hit found in a page."""

    id: int | None = None
    page_id: int | None = None
    keyword: str = ""
    match_text: str = ""
    context: str | None = None
    match_type: str = "keyword"
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class Session:
    """Represents a crawl session."""

    id: int | None = None
    name: str = ""
    seed_url: str | None = None
    status: str = "active"
    notes: str | None = None
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None


@dataclass(slots=True)
class Report:
    """Represents a generated report artifact."""

    id: int | None = None
    session_id: int | None = None
    title: str = ""
    format: str = "html"
    path: str = ""
    summary: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
