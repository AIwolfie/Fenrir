"""Unit tests for report generation."""

from __future__ import annotations

from pathlib import Path
from core.reporter import ReportGenerator
from storage.db import DeepReconDB


def test_generate_session_report(tmp_path: Path):
    db = DeepReconDB(tmp_path / "test_recon.db")
    session_id = db.create_session("Operation_Phoenix", seed_url="http://example.onion")
    site_id = db.get_or_create_site("http://example.onion", "Example Site")
    
    page_id = db.upsert_page({
        "site_id": site_id,
        "session_id": session_id,
        "url": "http://example.onion",
        "title": "Hidden Vault",
        "content": "Secret onion content with BTC and emails",
        "meta": {"emails": ["contact@vault.onion"], "btc": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"]}
    })
    
    db.add_keyword_hit({
        "page_id": page_id,
        "keyword": "secret",
        "match_text": "Secret",
        "context": "...Secret onion content..."
    })

    reporter = ReportGenerator(db=db, reports_path=tmp_path / "reports")
    outputs = reporter.generate_session_report(session_id)
    
    assert "html" in outputs
    assert "json" in outputs
    assert outputs["html"].exists()
    assert outputs["json"].exists()
    
    html_content = outputs["html"].read_text(encoding="utf-8")
    assert "Fenrir OSINT Report" in html_content
    assert "Operation_Phoenix" in html_content
    assert "contact@vault.onion" in html_content
    assert "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" in html_content
