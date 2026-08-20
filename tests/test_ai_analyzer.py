"""Unit tests for AI Analyzer and heuristic fallback."""

from __future__ import annotations

from core.ai_analyzer import AIAnalyzer


def test_ai_analyzer_heuristic_summary():
    analyzer = AIAnalyzer(provider="offline_heuristic")
    metadata = {
        "crypto": {
            "bitcoin": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],
            "ethereum": [],
            "monero": ["44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGeiSTRMGKiRN2ePXCeGWB4BTdrGLdfSS5VJy5bPh"]
        },
        "emails": ["operator@hidden.onion"],
        "pgp": ["BEGIN PGP"],
        "technologies": ["Nginx", "FastAPI"]
    }
    summary = analyzer.generate_investigation_summary(
        "http://darkmarket1234567.onion",
        "Dark web market escrow service with vendor directory and digital goods leak",
        metadata
    )
    assert "DeepRecon OSINT Threat Summary" in summary
    assert "http://darkmarket1234567.onion" in summary
    assert "Risk Classification: HIGH" in summary
    assert "operator@hidden.onion" in summary


def test_ai_analyzer_empty_content():
    analyzer = AIAnalyzer()
    summary = analyzer.generate_investigation_summary("http://test.onion", "", {})
    assert "No content" in summary
