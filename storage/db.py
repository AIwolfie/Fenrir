"""SQLite storage layer for Fenrir OSINT.

Author: AIwolfie
Repository: https://github.com/AIwolfie/Fenrir

This module provides the persistence foundation for crawl sessions, pages,
links, keyword hits, reports, and full-text search.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from storage.models import KeywordHit, Link, Page, Report

_VALID_TABLES = frozenset({"sites", "sessions", "pages", "links", "keywords_found", "reports"})


class FenrirDB:
    """High-level SQLite wrapper used by the crawler, search, and reporter."""

    def __init__(self, db_path: str | Path = "storage/fenrir.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_info (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    version INTEGER NOT NULL
                );

                INSERT OR IGNORE INTO schema_info (id, version) VALUES (1, 1);

                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    root_url TEXT NOT NULL UNIQUE,
                    title TEXT,
                    status_code INTEGER,
                    tech_stack TEXT,
                    relevance_score REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    seed_url TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    notes TEXT,
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    finished_at TEXT
                );

                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER,
                    session_id INTEGER,
                    url TEXT NOT NULL UNIQUE,
                    final_url TEXT,
                    title TEXT,
                    content TEXT NOT NULL DEFAULT '',
                    raw_html TEXT,
                    status_code INTEGER,
                    content_type TEXT,
                    headers TEXT NOT NULL DEFAULT '{}',
                    meta TEXT NOT NULL DEFAULT '{}',
                    language TEXT,
                    relevance_score REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE SET NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER,
                    source_url TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    is_internal INTEGER NOT NULL DEFAULT 1,
                    anchor_text TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS keywords_found (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER,
                    keyword TEXT NOT NULL,
                    match_text TEXT NOT NULL,
                    context TEXT,
                    match_type TEXT NOT NULL DEFAULT 'keyword',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    title TEXT NOT NULL,
                    format TEXT NOT NULL DEFAULT 'html',
                    path TEXT NOT NULL,
                    summary TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                    url,
                    title,
                    content,
                    raw_html,
                    content='pages',
                    content_rowid='id'
                );

                CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages BEGIN
                    INSERT INTO pages_fts(rowid, url, title, content, raw_html)
                    VALUES (new.id, new.url, new.title, new.content, new.raw_html);
                END;

                CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages BEGIN
                    DELETE FROM pages_fts WHERE rowid = old.id;
                END;

                """
            )

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=True, sort_keys=True)
        return value

    @staticmethod
    def _deserialize_json(value: Any) -> dict[str, Any]:
        if not value:
            return {}
        if isinstance(value, dict):
            return value
        return json.loads(value)

    @staticmethod
    def _to_payload(record: Any) -> dict[str, Any]:
        if is_dataclass(record):
            return asdict(record)
        if isinstance(record, dict):
            return dict(record)
        raise TypeError("record must be a dataclass instance or dictionary")

    def init_db(self) -> None:
        """Initialize the database schema."""

        self._initialize()

    def create_session(self, name: str, seed_url: str | None = None, notes: str | None = None) -> int:
        """Insert a crawl session and return its identifier."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO sessions (name, seed_url, notes)
                VALUES (?, ?, ?)
                """,
                (name, seed_url, notes),
            )
            return int(cursor.lastrowid)

    def get_session(self, session_id: int) -> dict[str, Any] | None:
        """Fetch a session by identifier."""

        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return dict(row) if row else None

    def list_sessions(self) -> list[dict[str, Any]]:
        """Return all saved crawl sessions."""

        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM sessions ORDER BY started_at DESC").fetchall()
        return [dict(row) for row in rows]

    def delete_session(self, session_id: int) -> None:
        """Delete a session and its linked pages, links, and keyword hits."""

        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    def get_or_create_site(self, root_url: str, title: str | None = None) -> int:
        """Return an existing site id or create a new site record."""

        with self._connect() as connection:
            row = connection.execute("SELECT id FROM sites WHERE root_url = ?", (root_url,)).fetchone()
            if row:
                return int(row["id"])
            cursor = connection.execute(
                "INSERT INTO sites (root_url, title) VALUES (?, ?)",
                (root_url, title),
            )
            return int(cursor.lastrowid)

    def page_exists(self, url: str) -> bool:
        """Check whether a page URL already exists in storage."""

        with self._connect() as connection:
            row = connection.execute("SELECT 1 FROM pages WHERE url = ?", (url,)).fetchone()
        return row is not None

    def upsert_page(self, page: Page | dict[str, Any]) -> int:
        """Insert or update a page record and return its row id."""

        payload = self._to_payload(page)
        headers = self._serialize_value(payload.get("headers", {}))
        meta = self._serialize_value(payload.get("meta", {}))
        with self._connect() as connection:
            existing = connection.execute("SELECT id FROM pages WHERE url = ?", (payload["url"],)).fetchone()
            if existing:
                connection.execute("DELETE FROM pages WHERE id = ?", (existing["id"],))
                cursor = connection.execute(
                    """
                    INSERT INTO pages (
                        id, site_id, session_id, url, final_url, title, content, raw_html,
                        status_code, content_type, headers, meta, language, relevance_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        existing["id"],
                        payload.get("site_id"),
                        payload.get("session_id"),
                        payload["url"],
                        payload.get("final_url"),
                        payload.get("title"),
                        payload.get("content", ""),
                        payload.get("raw_html"),
                        payload.get("status_code"),
                        payload.get("content_type"),
                        headers,
                        meta,
                        payload.get("language"),
                        payload.get("relevance_score", 0.0),
                    ),
                )
                return int(cursor.lastrowid)

            cursor = connection.execute(
                """
                INSERT INTO pages (
                    site_id, session_id, url, final_url, title, content, raw_html,
                    status_code, content_type, headers, meta, language, relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("site_id"),
                    payload.get("session_id"),
                    payload["url"],
                    payload.get("final_url"),
                    payload.get("title"),
                    payload.get("content", ""),
                    payload.get("raw_html"),
                    payload.get("status_code"),
                    payload.get("content_type"),
                    headers,
                    meta,
                    payload.get("language"),
                    payload.get("relevance_score", 0.0),
                ),
            )
            return int(cursor.lastrowid)

    def add_links(self, page_id: int, source_url: str, links: Iterable[Link | dict[str, Any]]) -> int:
        """Store discovered links for a page and return the count inserted."""

        rows = 0
        with self._connect() as connection:
            for link in links:
                payload = self._to_payload(link)
                connection.execute(
                    """
                    INSERT INTO links (page_id, source_url, target_url, is_internal, anchor_text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        page_id,
                        source_url,
                        payload["target_url"],
                        int(bool(payload.get("is_internal", True))),
                        payload.get("anchor_text"),
                    ),
                )
                rows += 1
        return rows

    def add_keyword_hit(self, hit: KeywordHit | dict[str, Any]) -> int:
        """Store a keyword hit and return its identifier."""

        payload = self._to_payload(hit)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO keywords_found (page_id, keyword, match_text, context, match_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload.get("page_id"),
                    payload["keyword"],
                    payload["match_text"],
                    payload.get("context"),
                    payload.get("match_type", "keyword"),
                ),
            )
            return int(cursor.lastrowid)

    def add_report(self, report: Report | dict[str, Any]) -> int:
        """Store report metadata and return its identifier."""

        payload = self._to_payload(report)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reports (session_id, title, format, path, summary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload.get("session_id"),
                    payload["title"],
                    payload.get("format", "html"),
                    payload["path"],
                    payload.get("summary"),
                ),
            )
            return int(cursor.lastrowid)

    def list_pages(self, session_id: int | None = None) -> list[dict[str, Any]]:
        """Return stored pages, optionally filtered by session."""

        query = "SELECT * FROM pages"
        params: tuple[Any, ...] = ()
        if session_id is not None:
            query += " WHERE session_id = ?"
            params = (session_id,)
        query += " ORDER BY created_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_page_dict(row) for row in rows]

    def list_links(self, page_id: int | None = None) -> list[dict[str, Any]]:
        """Return stored links, optionally filtered by page."""

        query = "SELECT * FROM links"
        params: tuple[Any, ...] = ()
        if page_id is not None:
            query += " WHERE page_id = ?"
            params = (page_id,)
        query += " ORDER BY created_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def list_keyword_hits(self, session_id: int | None = None) -> list[dict[str, Any]]:
        """Return keyword hits, optionally filtered by session."""

        query = """
            SELECT keywords_found.*
            FROM keywords_found
            LEFT JOIN pages ON pages.id = keywords_found.page_id
        """
        params: tuple[Any, ...] = ()
        if session_id is not None:
            query += " WHERE pages.session_id = ?"
            params = (session_id,)
        query += " ORDER BY keywords_found.created_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def list_reports(self, session_id: int | None = None) -> list[dict[str, Any]]:
        """Return stored reports, optionally filtered by session."""

        query = "SELECT * FROM reports"
        params: tuple[Any, ...] = ()
        if session_id is not None:
            query += " WHERE session_id = ?"
            params = (session_id,)
        query += " ORDER BY created_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def search_pages(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """Search the FTS index and return matching pages."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT pages.*
                FROM pages_fts
                JOIN pages ON pages.id = pages_fts.rowid
                WHERE pages_fts MATCH ?
                ORDER BY bm25(pages_fts)
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        return [self._row_to_page_dict(row) for row in rows]

    def export_table(self, table_name: str, destination: str | Path, format: str = "json") -> Path:
        """Export a table to JSON or CSV."""

        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if table_name not in _VALID_TABLES:
            raise ValueError(f"Invalid table name: {table_name!r}")
        with self._connect() as connection:
            rows = connection.execute(f"SELECT * FROM {table_name}").fetchall()

        records = [dict(row) for row in rows]
        if format.lower() == "json":
            destination_path.write_text(json.dumps(records, indent=2, ensure_ascii=True), encoding="utf-8")
        elif format.lower() == "csv":
            with destination_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()) if records else [])
                if records:
                    writer.writeheader()
                    writer.writerows(records)
        else:
            raise ValueError("format must be 'json' or 'csv'")
        return destination_path

    def count_rows(self, table_name: str) -> int:
        """Return the number of rows in a table."""

        if table_name not in _VALID_TABLES:
            raise ValueError(f"Invalid table name: {table_name!r}")
        with self._connect() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"]) if row else 0

    @staticmethod
    def _row_to_page_dict(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["headers"] = DeepReconDB._deserialize_json(data.get("headers"))
        data["meta"] = DeepReconDB._deserialize_json(data.get("meta"))
        return data


# Backward compatibility alias
DeepReconDB = FenrirDB


def init_db(db_path: str | Path = "storage/fenrir.db") -> FenrirDB:
    """Create the database schema and return a DB wrapper."""

    return FenrirDB(db_path)


def save_result(url: str, emails: Sequence[str], btc: Sequence[str], pgp: Sequence[str]) -> int:
    """Compatibility helper for the legacy CLI.

    The old CLI only persisted a single result row. This now writes a page row
    into the new schema while preserving the original call signature.
    """

    db = FenrirDB()
    page = Page(
        url=url,
        title=None,
        content="",
        raw_html=None,
        meta={"emails": list(emails), "btc": list(btc), "pgp": list(pgp)},
    )
    return db.upsert_page(page)

