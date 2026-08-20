from pathlib import Path

from core.parser import parse_page


def test_parse_page_extracts_emails_crypto_and_flags() -> None:
    fixture = Path(__file__).parent / "fixtures" / "mock_onion.html"
    page = parse_page(fixture.read_text(encoding="utf-8"), "http://example.onion")

    assert page.title == "Mock Market"
    assert page.links == ["http://example.onion/contact", "https://example.com/mirror"]
    assert "support@example.onion" in page.text
    assert page.emails == ["support@example.onion"]
    assert page.crypto_addresses["ethereum"] == ["0x1234567890abcdef1234567890abcdef12345678"]
    assert page.pgp_blocks
    assert "login_page" in page.flags
    assert "login_form" in page.flags
