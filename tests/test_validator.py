from utils.validator import is_onion_url, normalize_url, sanitize_url


def test_is_onion_url_accepts_v3_length() -> None:
    assert is_onion_url("https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.onion")


def test_is_onion_url_rejects_non_onion() -> None:
    assert not is_onion_url("https://example.com")


def test_normalize_url_keeps_path() -> None:
    assert normalize_url("https://example.onion/path") == "https://example.onion/path"


def test_sanitize_url_strips_whitespace() -> None:
    assert sanitize_url("  https://example.onion/path  ") == "https://example.onion/path"
