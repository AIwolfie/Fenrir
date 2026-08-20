"""Report generation for Fenrir OSINT Framework.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Iterable

try:
    from weasyprint import HTML
except (ImportError, OSError, Exception):  # pragma: no cover - optional dependency
    HTML = None


from config import ENABLE_PDF_EXPORT, REPORTS_PATH
from core.parser import PageData
from storage.db import FenrirDB
from utils.logger import get_logger


LOGGER = get_logger(__name__)
DISCLAIMER = (
    "Ethical use only: Fenrir is intended for authorized security research, "
    "threat intelligence, and defensive OSINT investigations."
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _as_dict(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError("Expected a mapping or dataclass instance")


def _render_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    thead = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


class ReportGenerator:
    """Generate HTML, JSON, and optional PDF reports from stored crawl data."""

    def __init__(self, db: DeepReconDB | None = None, reports_path: str | Path = REPORTS_PATH) -> None:
        self.db = db or DeepReconDB()
        self.reports_path = Path(reports_path)
        self.reports_path.mkdir(parents=True, exist_ok=True)

    def generate_session_report(self, session_id: int, title: str | None = None) -> dict[str, Path]:
        """Generate a session report from stored database records."""

        pages = self.db.list_pages(session_id)
        links = self.db.list_links()
        keyword_hits = self.db.list_keyword_hits(session_id)
        session = self.db.get_session(session_id)
        payload = self._build_payload(session=session, pages=pages, links=links, keyword_hits=keyword_hits)
        report_title = title or (session["name"] if session else f"Session {session_id}")
        return self._write_outputs(report_title, payload, session_id=session_id)

    def generate_legacy_report(self, data: list[dict[str, Any]], title: str = "DeepRecon Report") -> dict[str, Path]:
        """Generate a report from the legacy list-of-dicts format."""

        payload = self._build_legacy_payload(data)
        return self._write_outputs(title, payload)

    def _build_payload(
        self,
        *,
        session: dict[str, Any] | None,
        pages: list[dict[str, Any]],
        links: list[dict[str, Any]],
        keyword_hits: list[dict[str, Any]],
    ) -> dict[str, Any]:
        email_hits = sorted({email for page in pages for email in (page.get("meta", {}) or {}).get("emails", [])})
        crypto_hits = {
            "bitcoin": sorted({item for page in pages for item in (page.get("meta", {}) or {}).get("btc", [])}),
            "ethereum": sorted({item for page in pages for item in (page.get("meta", {}) or {}).get("eth", [])}),
            "monero": sorted({item for page in pages for item in (page.get("meta", {}) or {}).get("xmr", [])}),
        }
        return {
            "session": session,
            "pages": pages,
            "links": links,
            "keyword_hits": keyword_hits,
            "emails": email_hits,
            "crypto_hits": crypto_hits,
            "summary": {
                "pages_crawled": len(pages),
                "links_found": len(links),
                "keyword_hits": len(keyword_hits),
                "emails_found": len(email_hits),
                "btc_found": len(crypto_hits["bitcoin"]),
                "eth_found": len(crypto_hits["ethereum"]),
                "xmr_found": len(crypto_hits["monero"]),
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": DISCLAIMER,
        }

    def _build_legacy_payload(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        pages = []
        for item in data:
            pages.append(
                {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "meta": {
                        "emails": item.get("emails", []),
                        "btc": item.get("btc", []),
                        "pgp": item.get("pgp", []),
                    },
                }
            )
        return self._build_payload(session=None, pages=pages, links=[], keyword_hits=[])

    def _write_outputs(self, title: str, payload: dict[str, Any], session_id: int | None = None) -> dict[str, Path]:
        slug = title.lower().replace(" ", "_")[:50]
        timestamp = _timestamp()
        html_path = self.reports_path / f"{slug}_{timestamp}.html"
        json_path = self.reports_path / f"{slug}_{timestamp}.json"

        html_path.write_text(self._render_html(title, payload), encoding="utf-8")
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

        pdf_path: Path | None = None
        if ENABLE_PDF_EXPORT and HTML is not None:
            pdf_path = self.reports_path / f"{slug}_{timestamp}.pdf"
            HTML(string=html_path.read_text(encoding="utf-8"), base_url=str(self.reports_path)).write_pdf(pdf_path)

        if session_id is not None:
            self.db.add_report(
                {
                    "session_id": session_id,
                    "title": title,
                    "format": "html",
                    "path": str(html_path),
                    "summary": json.dumps(payload["summary"], ensure_ascii=True),
                }
            )

        LOGGER.info("Report written to %s", html_path)
        result = {"html": html_path, "json": json_path}
        if pdf_path is not None:
            result["pdf"] = pdf_path
        return result

    def _render_html(self, title: str, payload: dict[str, Any]) -> str:
        summary = payload["summary"]
        session_block = ""
        if payload.get("session"):
            session = payload["session"]
            session_block = f"<p class='session-meta'><strong>Session:</strong> {escape(str(session.get('name', '')))} &nbsp;|&nbsp; <strong>Target:</strong> {escape(str(session.get('seed_url', '')))}</p>"

        keyword_rows = [
            [hit.get("keyword"), hit.get("match_text"), hit.get("context", ""), hit.get("created_at", "")]
            for hit in payload.get("keyword_hits", [])
        ]
        link_rows = [
            [link.get("source_url"), link.get("target_url"), link.get("is_internal"), link.get("created_at", "")]
            for link in payload.get("links", [])
        ]
        
        email_items = "".join(f"<span class='tag email-tag'>{escape(email)}</span>" for email in payload.get("emails", [])) or "<p class='empty-state'>No email addresses detected.</p>"
        
        crypto_hits = payload.get("crypto_hits", {})
        btc_items = "".join(f"<span class='tag btc-tag'>BTC: {escape(addr)}</span>" for addr in crypto_hits.get("bitcoin", []))
        eth_items = "".join(f"<span class='tag eth-tag'>ETH: {escape(addr)}</span>" for addr in crypto_hits.get("ethereum", []))
        xmr_items = "".join(f"<span class='tag xmr-tag'>XMR: {escape(addr)}</span>" for addr in crypto_hits.get("monero", []))
        all_crypto = btc_items + eth_items + xmr_items or "<p class='empty-state'>No cryptocurrency addresses detected.</p>"

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fenrir OSINT Report - Threat Intelligence Dossier - {escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-base: #030712;
      --bg-surface: #0a101f;
      --bg-surface-elevated: #111a2e;
      --accent-cyan: #00f5d4;
      --accent-indigo: #6366f1;
      --accent-purple: #a855f7;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-highlight: rgba(0, 245, 212, 0.3);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-base);
      color: var(--text-main);
      padding: 0;
      line-height: 1.6;
    }}
    header {{
      background: linear-gradient(135deg, #050b18 0%, #0d1527 50%, #17102e 100%);
      border-bottom: 1px solid var(--border-subtle);
      padding: 48px 32px;
      position: relative;
      overflow: hidden;
    }}
    header::after {{
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo), var(--accent-purple));
    }}
    .header-content {{ max-width: 1280px; margin: 0 auto; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      background: rgba(0, 245, 212, 0.12);
      color: var(--accent-cyan);
      border: 1px solid rgba(0, 245, 212, 0.35);
      margin-bottom: 14px;
    }}
    h1 {{ font-size: 2.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em; margin-bottom: 8px; }}
    .timestamp {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--text-muted); }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 36px 24px; }}
    .card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      padding: 26px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
      transition: border-color 0.2s ease;
    }}
    .card:hover {{ border-color: rgba(255, 255, 255, 0.15); }}
    .card h2 {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 18px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .session-meta {{ color: var(--text-muted); margin-bottom: 16px; font-size: 0.95rem; }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 16px;
    }}
    .stat-box {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 18px;
      text-align: center;
    }}
    .stat-number {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 2rem;
      font-weight: 800;
      color: var(--accent-cyan);
      margin-top: 6px;
    }}
    .stat-label {{ font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em; }}
    .tag-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .tag {{
      display: inline-flex;
      align-items: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid transparent;
      user-select: all;
    }}
    .email-tag {{ background: rgba(56, 189, 248, 0.12); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }}
    .btc-tag {{ background: rgba(245, 158, 11, 0.12); color: #fbbf24; border-color: rgba(245, 158, 11, 0.3); }}
    .eth-tag {{ background: rgba(168, 85, 247, 0.12); color: #c084fc; border-color: rgba(168, 85, 247, 0.3); }}
    .xmr-tag {{ background: rgba(244, 63, 94, 0.12); color: #fb7185; border-color: rgba(244, 63, 94, 0.3); }}
    .table-responsive {{ overflow-x: auto; border-radius: 8px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
    th, td {{ border-bottom: 1px solid var(--border-subtle); padding: 14px 18px; text-align: left; vertical-align: top; }}
    th {{ background: #050812; color: var(--text-muted); font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
    tr:hover {{ background: rgba(255, 255, 255, 0.025); }}
    .disclaimer {{ background: rgba(245, 158, 11, 0.08); border-left: 4px solid var(--accent-amber); padding: 18px; font-size: 0.9rem; color: #fde68a; }}
    .empty-state {{ color: var(--text-dim); font-style: italic; font-size: 0.9rem; padding: 8px 0; }}
    footer {{
      text-align: center;
      padding: 32px;
      color: var(--text-dim);
      font-size: 0.85rem;
      border-top: 1px solid var(--border-subtle);
      margin-top: 40px;
    }}
    footer a {{ color: var(--accent-cyan); text-decoration: none; }}
  </style>
</head>
<body>
  <header>
    <div class="header-content">
      <span class="badge">🐺 Fenrir OSINT Intelligence Dossier • AIwolfie</span>
      <h1>{escape(title)}</h1>
      <p class="timestamp">Generated: {escape(payload.get('generated_at', ''))} • Classification: RESTRICTED DEFENSIVE INTEL</p>
    </div>
  </header>
  <main>
    <div class="card disclaimer">
      ⚠️ <strong>Legal & Ethical Authorization:</strong> {escape(payload.get('disclaimer', DISCLAIMER))}
    </div>

    <div class="card">
      <h2>📊 Mission Overview & Quantitative Metrics</h2>
      {session_block}
      <div class="summary-grid">
        <div class="stat-box"><div class="stat-label">Pages Scraped</div><div class="stat-number">{summary.get('pages_crawled', 0)}</div></div>
        <div class="stat-box"><div class="stat-label">Graph Links</div><div class="stat-number">{summary.get('links_found', 0)}</div></div>
        <div class="stat-box"><div class="stat-label">Threat Keywords</div><div class="stat-number">{summary.get('keyword_hits', 0)}</div></div>
        <div class="stat-box"><div class="stat-label">Emails Discovered</div><div class="stat-number">{summary.get('emails_found', 0)}</div></div>
        <div class="stat-box"><div class="stat-label">Crypto Wallets</div><div class="stat-number">{summary.get('btc_found', 0) + summary.get('eth_found', 0) + summary.get('xmr_found', 0)}</div></div>
      </div>
    </div>

    <div class="card">
      <h2>💰 Cryptocurrency Intelligence Artifacts</h2>
      <div class="tag-container">{all_crypto}</div>
    </div>

    <div class="card">
      <h2>📧 Extracted Communications & Emails</h2>
      <div class="tag-container">{email_items}</div>
    </div>

    <div class="card">
      <h2>🎯 Pattern Signatures & Keyword Hits</h2>
      <div class="table-responsive">
        {_render_table(['Keyword', 'Match', 'Context', 'Timestamp'], keyword_rows) if keyword_rows else '<p class="empty-state">No keyword hits recorded.</p>'}
      </div>
    </div>

    <div class="card">
      <h2>🔗 Discovered Traversal Link Graph</h2>
      <div class="table-responsive">
        {_render_table(['Source', 'Target', 'Internal', 'Timestamp'], link_rows) if link_rows else '<p class="empty-state">No links recorded.</p>'}
      </div>
    </div>
  </main>
  <footer>
    <p>Engineered by <strong><a href="https://github.com/AIwolfie/Fenrir" target="_blank">AIwolfie</a></strong> • Autonomous Dark Web OSINT & Threat Reconnaissance</p>
  </footer>
</body>
</html>"""


def save_report(data: list[dict[str, Any]]) -> dict[str, Path]:
    """Legacy helper preserved for backwards compatibility."""

    generator = ReportGenerator()
    return generator.generate_legacy_report(data)
