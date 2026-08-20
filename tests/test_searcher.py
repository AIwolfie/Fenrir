"""Unit tests for Searcher and intelligence scoring."""

from __future__ import annotations

from core.parser import PageData
from core.searcher import Searcher


def test_search_text_plain_and_regex():
    searcher = Searcher()
    text = "Found bitcoin wallet 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa in the database."
    
    hits = searcher.search_text(text, ["bitcoin", "wallet"])
    assert len(hits) == 2
    assert hits[0].keyword == "bitcoin"
    
    regex_hits = searcher.search_text(text, [r"1[a-km-zA-HJ-NP-Z1-9]{25,34}"], regex=True)
    assert len(regex_hits) == 1
    assert regex_hits[0].match_text == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"


def test_score_page():
    searcher = Searcher()
    page = PageData(
        url="http://test.onion",
        text="Dark market marketplace vendor portal login page",
        crypto_addresses={"bitcoin": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"], "ethereum": [], "monero": []},
        pgp_blocks=["-----BEGIN PGP PUBLIC KEY BLOCK-----"],
        flags=["login_page"],
    )
    score = searcher.score_page(page, keywords=["market", "vendor"])
    assert score.score > 40
    assert any("crypto" in r for r in score.reasons)
    assert "pgp_present" in score.reasons
