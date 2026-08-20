"""HTML parsing and structured extraction for DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from bs4.exceptions import FeatureNotFound


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}")
BTC_PATTERN = re.compile(r"\b(?:bc1[ac-hj-np-z02-9]{11,71}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b")
ETH_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
XMR_PATTERN = re.compile(r"\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b|\b8[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b")
PGP_PATTERN = re.compile(
    r"-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----",
    re.DOTALL,
)


@dataclass(slots=True)
class FormField:
    """Structured description of a form field."""

    name: str | None = None
    field_type: str | None = None
    value: str | None = None
    placeholder: str | None = None


@dataclass(slots=True)
class PageData:
    """Structured representation of a crawled page."""

    url: str
    final_url: str | None = None
    title: str | None = None
    text: str = ""
    raw_html: str = ""
    links: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    crypto_addresses: dict[str, list[str]] = field(default_factory=dict)
    pgp_blocks: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, Any] = field(default_factory=dict)
    forms: list[dict[str, Any]] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    language: str | None = None
    content_type: str | None = None
    status_code: int | None = None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def _detect_technologies(soup: BeautifulSoup, headers: dict[str, Any]) -> list[str]:
    technologies: set[str] = set()
    server = str(headers.get("Server", "") or headers.get("server", "")).lower()
    powered_by = str(headers.get("X-Powered-By", "") or headers.get("x-powered-by", "")).lower()
    if "nginx" in server:
        technologies.add("nginx")
    if "apache" in server:
        technologies.add("apache")
    if "php" in powered_by:
        technologies.add("php")
    if soup.find(attrs={"id": re.compile("wordpress", re.I)}):
        technologies.add("wordpress")
    if soup.find("script", src=re.compile("react", re.I)):
        technologies.add("react")
    if soup.find("script", src=re.compile("vue", re.I)):
        technologies.add("vue")
    if soup.find("script", src=re.compile("angular", re.I)):
        technologies.add("angular")
    if any("bootstrap" in (tag.get("href", "") or "").lower() for tag in soup.find_all("link", href=True)):
        technologies.add("bootstrap")
    return sorted(technologies)


def _detect_flags(url: str, soup: BeautifulSoup, text: str) -> list[str]:
    flags: set[str] = set()
    lowered_url = url.lower()
    lowered_text = text.lower()
    for form in soup.find_all("form"):
        action = (form.get("action") or "").lower()
        if any(token in action for token in ("login", "signin", "sign-in", "auth")):
            flags.add("login_page")
    if any(token in lowered_url for token in ("login", "signin", "sign-in", "auth")):
        flags.add("login_page")
    if any(token in lowered_text for token in ("marketplace", "vendor", "escrow", "shopping cart")):
        flags.add("marketplace")
    if any(token in lowered_text for token in ("forum", "thread", "replies")):
        flags.add("forum")
    if soup.find("input", attrs={"type": re.compile("password", re.I)}):
        flags.add("login_form")
    return sorted(flags)


def parse_page(
    html: str,
    url: str,
    *,
    final_url: str | None = None,
    headers: dict[str, Any] | None = None,
    status_code: int | None = None,
    content_type: str | None = None,
) -> PageData:
    """Parse HTML content into a structured :class:`PageData` object."""

    headers = headers or {}
    try:
        soup = BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(" ", strip=True) if title_tag else None
    text = soup.get_text(" ", strip=True)

    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(url, anchor.get("href", ""))
        links.append(href)

    meta: dict[str, Any] = {}
    for tag in soup.find_all("meta"):
        name = tag.get("name") or tag.get("property") or tag.get("http-equiv")
        content = tag.get("content")
        if name and content:
            meta[str(name).lower()] = content

    forms: list[dict[str, Any]] = []
    for form in soup.find_all("form"):
        form_fields: list[FormField] = []
        for field in form.find_all(["input", "textarea", "select"]):
            form_fields.append(
                FormField(
                    name=field.get("name"),
                    field_type=field.get("type") or field.name,
                    value=field.get("value"),
                    placeholder=field.get("placeholder"),
                )
            )
        forms.append(
            {
                "action": urljoin(url, form.get("action", "")),
                "method": (form.get("method") or "GET").upper(),
                "fields": [asdict(field) for field in form_fields],
            }
        )

    emails = _unique(EMAIL_PATTERN.findall(html))
    phone_numbers = _unique(PHONE_PATTERN.findall(html))
    bitcoin = _unique(BTC_PATTERN.findall(html))
    ethereum = _unique(ETH_PATTERN.findall(html))
    monero = _unique(XMR_PATTERN.findall(html))
    pgp_blocks = [block.strip() for block in PGP_PATTERN.findall(html)]

    crypto_addresses = {
        "bitcoin": bitcoin,
        "ethereum": ethereum,
        "monero": monero,
    }

    technologies = _detect_technologies(soup, headers)
    flags = _detect_flags(url, soup, text)

    return PageData(
        url=url,
        final_url=final_url,
        title=title,
        text=text,
        raw_html=html,
        links=_unique([link for link in links if link]),
        emails=emails,
        crypto_addresses=crypto_addresses,
        pgp_blocks=pgp_blocks,
        phone_numbers=phone_numbers,
        meta=meta,
        headers=dict(headers),
        forms=forms,
        technologies=technologies,
        flags=flags,
        language=meta.get("lang") or meta.get("language"),
        content_type=content_type,
        status_code=status_code,
    )
