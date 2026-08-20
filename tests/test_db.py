from pathlib import Path

from core.parser import parse_page
from storage.db import DeepReconDB
from storage.models import Page


def test_db_insert_query_and_search(tmp_path: Path) -> None:
    db = DeepReconDB(tmp_path / "deeprecon.db")
    session_id = db.create_session("session_1", "http://example.onion")
    site_id = db.get_or_create_site("http://example.onion", "Example")

    page = parse_page(
        "<html><head><title>Alpha</title></head><body>alpha beta</body></html>",
        "http://example.onion",
    )
    page_id = db.upsert_page(
        Page(
            site_id=site_id,
            session_id=session_id,
            url=page.url,
            title=page.title,
            content=page.text,
            raw_html=page.raw_html,
            headers=page.headers,
            meta=page.meta,
            language=page.language,
        )
    )

    assert page_id == 1
    assert db.page_exists("http://example.onion")
    assert db.count_rows("pages") == 1
    results = db.search_pages("alpha")
    assert len(results) == 1
    assert results[0]["title"] == "Alpha"
