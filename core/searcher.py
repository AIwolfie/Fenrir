"""Keyword search and scoring for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from core.parser import PageData


@dataclass(slots=True)
class KeywordMatch:
    """Represents a single keyword or regex hit."""

    keyword: str
    match_text: str
    context: str
    start: int
    end: int
    is_regex: bool = False


@dataclass(slots=True)
class SiteScore:
    """Simple scoring result for a page or site."""

    score: int
    reasons: list[str] = field(default_factory=list)


class Searcher:
    """Perform keyword/regex searches and lightweight intelligence scoring."""

    def __init__(self, context_window: int = 100) -> None:
        self.context_window = max(20, context_window)

    def search_text(
        self,
        text: str,
        terms: Iterable[str],
        *,
        regex: bool = False,
        case_sensitive: bool = False,
    ) -> list[KeywordMatch]:
        """Search text for keywords or regex patterns."""

        matches: list[KeywordMatch] = []
        haystack = text if case_sensitive else text.lower()
        for term in terms:
            if not term:
                continue
            if regex:
                pattern = re.compile(term, 0 if case_sensitive else re.IGNORECASE)
                for match in pattern.finditer(text):
                    matches.append(
                        KeywordMatch(
                            keyword=term,
                            match_text=match.group(0),
                            context=self._context(text, match.start(), match.end()),
                            start=match.start(),
                            end=match.end(),
                            is_regex=True,
                        )
                    )
            else:
                needle = term if case_sensitive else term.lower()
                start = 0
                while True:
                    index = haystack.find(needle, start)
                    if index == -1:
                        break
                    end = index + len(term)
                    matches.append(
                        KeywordMatch(
                            keyword=term,
                            match_text=text[index:end],
                            context=self._context(text, index, end),
                            start=index,
                            end=end,
                            is_regex=False,
                        )
                    )
                    start = end
        return matches

    def score_page(
        self,
        page: PageData,
        *,
        keywords: Iterable[str] | None = None,
        language_match: str | None = None,
    ) -> SiteScore:
        """Score a page on a 0-100 relevance scale."""

        reasons: list[str] = []
        score = 0
        text = page.text or ""
        words = max(len(text.split()), 1)

        if keywords:
            hits = self.search_text(text, keywords, regex=False)
            density = min((len(hits) * 12) + min(words // 100, 8), 35)
            score += density
            if hits:
                reasons.append(f"keyword_hits={len(hits)}")

        crypto_count = sum(len(values) for values in page.crypto_addresses.values())
        if crypto_count:
            boost = min(crypto_count * 12, 24)
            score += boost
            reasons.append(f"crypto={crypto_count}")

        if page.pgp_blocks:
            score += 20
            reasons.append("pgp_present")

        score += min(words // 80, 10)

        if language_match and page.language and page.language.lower().startswith(language_match.lower()):
            score += 10
            reasons.append(f"language={page.language}")

        if "login_page" in page.flags or "login_form" in page.flags:
            score += 5
            reasons.append("login_surface")

        return SiteScore(score=min(score, 100), reasons=reasons)

    def highlight(self, text: str, term: str) -> str:
        """Highlight matches for terminal output."""

        return re.sub(
            re.escape(term),
            f"[bold yellow]{term}[/bold yellow]",
            text,
            flags=re.IGNORECASE,
        )

    def _context(self, text: str, start: int, end: int) -> str:
        left = max(0, start - self.context_window)
        right = min(len(text), end + self.context_window)
        return text[left:right].strip()
