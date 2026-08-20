"""Async crawling engine for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import asyncio
import logging
import re
import urllib.robotparser
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

try:
    import aiohttp
except ImportError:  # pragma: no cover - optional dependency
    aiohttp = None

try:
    from aiohttp_socks import ProxyConnector
except ImportError:  # pragma: no cover - optional dependency
    ProxyConnector = None

from config import BYPASS_ROBOTS, CRAWL_DELAY, CRAWL_DEPTH, CRAWL_WORKERS, MAX_RETRIES, REQUEST_TIMEOUT, TOR_PROXY
from core.parser import PageData, parse_page
from storage.db import DeepReconDB
from storage.models import Link, Page
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter
from utils.tor_manager import get_session
from utils.validator import normalize_url


LOGGER = get_logger(__name__)
_BINARY_CONTENT_PREFIXES = ("image/", "audio/", "video/", "application/pdf", "application/zip")


def _site_root(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    scheme = parsed.scheme or "http"
    netloc = hostname
    if parsed.port:
        netloc = f"{hostname}:{parsed.port}"
    return urlunparse((scheme, netloc, "", "", "", ""))


def _is_internal(base_url: str, target_url: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(target_url)
    return (base.hostname or "").lower() == (target.hostname or "").lower()


def _should_skip_content(content_type: str | None) -> bool:
    if not content_type:
        return False
    lowered = content_type.lower()
    return any(lowered.startswith(prefix) for prefix in _BINARY_CONTENT_PREFIXES)


class AsyncCrawler:
    """Breadth-first async crawler with SQLite persistence."""

    def __init__(
        self,
        db: DeepReconDB | None = None,
        *,
        session_id: int | None = None,
        depth: int = CRAWL_DEPTH,
        workers: int = CRAWL_WORKERS,
        delay: float = CRAWL_DELAY,
        timeout: int = REQUEST_TIMEOUT,
        proxy_url: str = TOR_PROXY,
        bypass_robots: bool = BYPASS_ROBOTS,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self.db = db or DeepReconDB()
        self.session_id = session_id
        self.depth = max(0, depth)
        self.workers = max(1, workers)
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.proxy_url = proxy_url
        self.bypass_robots = bypass_robots
        self.max_retries = max(1, max_retries)
        self.rate_limiter = RateLimiter(self.delay)
        self._stop_requested = False
        self._worker_tasks: list[asyncio.Task] = []

    def stop(self) -> None:
        """Signal the crawler to abort active crawling workers immediately."""
        self._stop_requested = True
        for task in self._worker_tasks:
            if not task.done():
                task.cancel()

    async def crawl(self, seeds: list[str]) -> list[PageData]:
        """Crawl a list of seed URLs and persist discovered pages."""

        if aiohttp is None:
            raise RuntimeError("aiohttp is required for AsyncCrawler")

        # Only use SOCKS5 proxy for .onion targets; clearnet URLs use direct connection
        connector = None
        has_onion = any('.onion' in seed.lower() for seed in seeds)
        if has_onion and self.proxy_url and ProxyConnector is not None:
            proxy = self.proxy_url.replace("socks5h://", "socks5://")
            connector = ProxyConnector.from_url(proxy)
        elif has_onion and ProxyConnector is None:
            LOGGER.error("aiohttp_socks not installed; cannot crawl .onion URLs")
            return []

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        visited: set[str] = set()
        results: list[PageData] = []
        queue: asyncio.Queue[tuple[str, int, str]] = asyncio.Queue()

        for seed in seeds:
            normalized = normalize_url(seed)
            await queue.put((normalized, self.depth, _site_root(normalized)))

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            self._worker_tasks = [
                asyncio.create_task(self._worker(session, queue, visited, results))
                for _ in range(self.workers)
            ]
            try:
                await queue.join()
            except asyncio.CancelledError:
                pass
            for _ in self._worker_tasks:
                await queue.put(("", 0, ""))
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        return results

    async def _worker(
        self,
        session: aiohttp.ClientSession,
        queue: asyncio.Queue[tuple[str, int, str]],
        visited: set[str],
        results: list[PageData],
    ) -> None:
        while not self._stop_requested:
            try:
                url, depth, site_root = await queue.get()
            except asyncio.CancelledError:
                return
            try:
                if not url or self._stop_requested:
                    return
                if url in visited or depth < 0:
                    continue
                visited.add(url)

                page = await self._fetch_and_store(session, url, depth, site_root, queue, visited)
                if page is not None:
                    results.append(page)
            except asyncio.CancelledError:
                return
            finally:
                queue.task_done()

    async def _fetch_and_store(
        self,
        session: aiohttp.ClientSession,
        url: str,
        depth: int,
        site_root: str,
        queue: asyncio.Queue[tuple[str, int, str]],
        visited: set[str],
    ) -> PageData | None:
        if not self.bypass_robots and not self._allowed_by_robots(url):
            LOGGER.info("Skipping %s due to robots.txt", url)
            return None

        response = await self._fetch(session, url)
        if response is None:
            return None

        status_code, headers, body, final_url = response
        content_type = headers.get("content-type") or headers.get("Content-Type")
        if _should_skip_content(content_type):
            return None

        page = parse_page(
            body,
            url,
            final_url=final_url,
            headers=headers,
            status_code=status_code,
            content_type=content_type,
        )

        site_id = self.db.get_or_create_site(site_root, page.title)
        page_id = self.db.upsert_page(
            Page(
                session_id=self.session_id,
                site_id=site_id,
                url=page.url,
                final_url=page.final_url,
                title=page.title,
                content=page.text,
                raw_html=page.raw_html,
                status_code=page.status_code,
                content_type=page.content_type,
                headers=page.headers,
                meta=page.meta,
                language=page.language,
            )
        )

        links = []
        for link in page.links:
            links.append(
                Link(
                    page_id=page_id,
                    source_url=url,
                    target_url=link,
                    is_internal=_is_internal(url, link),
                )
            )
            normalized_link = normalize_url(link)
            if depth > 0 and normalized_link not in visited:
                await queue.put((normalized_link, depth - 1, site_root))

        if links:
            self.db.add_links(page_id, url, links)

        return page

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> tuple[int, dict[str, str], str, str] | None:
        for attempt in range(self.max_retries):
            try:
                await self.rate_limiter.wait()
                async with session.get(url, headers={"User-Agent": requests.utils.default_user_agent()}) as response:
                    body = await response.text(errors="ignore")
                    return response.status, dict(response.headers), body, str(response.url)
            except Exception as exc:  # pragma: no cover - network dependent
                if attempt + 1 >= self.max_retries:
                    LOGGER.warning("Failed to fetch %s: %s", url, exc)
                    return None
                await asyncio.sleep(min(2 ** attempt, 5))
        return None

    def _allowed_by_robots(self, url: str) -> bool:
        if ".onion" in url.lower():
            return True
        parsed = urlparse(url)
        robots_url = urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
        parser = urllib.robotparser.RobotFileParser()
        try:
            parser.set_url(robots_url)
            parser.read()
            return parser.can_fetch("DeepRecon", url)
        except Exception:
            return True



def crawl_recursive(url: str, depth: int = 1, visited: set[str] | None = None) -> list[str]:
    """Legacy synchronous crawler helper that returns discovered links."""

    visited = visited or set()
    if depth <= 0:
        return []

    normalized = normalize_url(url)
    if normalized in visited:
        return []
    visited.add(normalized)

    session = get_session()
    discovered: list[str] = []
    try:
        response = session.get(normalized, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        if _should_skip_content(response.headers.get("content-type")):
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            link = normalize_url(urljoin(normalized, anchor["href"]))
            discovered.append(link)
            if link.startswith("http"):
                discovered.extend(crawl_recursive(link, depth - 1, visited))
    except Exception as exc:  # pragma: no cover - network dependent
        LOGGER.warning("Error crawling %s: %s", normalized, exc)
    return discovered

