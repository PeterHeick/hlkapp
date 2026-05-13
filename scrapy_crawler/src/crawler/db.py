"""SQLite buffer for crawl results — bruges af Scrapy pipeline."""
from __future__ import annotations

import hashlib
import sqlite3

from klinik.config import settings


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def get_connection() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(settings.db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS crawl_pages (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            url            TEXT UNIQUE NOT NULL,
            status_code    INTEGER,
            depth          INTEGER DEFAULT 0,
            parent_url     TEXT,
            title          TEXT,
            word_count     INTEGER DEFAULT 0,
            is_orphan      INTEGER DEFAULT 0,
            redirect_chain TEXT DEFAULT '[]',
            crawled_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS crawl_links (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT NOT NULL,
            target_url TEXT NOT NULL,
            UNIQUE(source_url, target_url)
        );
        CREATE INDEX IF NOT EXISTS idx_cp_url    ON crawl_pages(url);
        CREATE INDEX IF NOT EXISTS idx_cl_source ON crawl_links(source_url);
        CREATE INDEX IF NOT EXISTS idx_cl_target ON crawl_links(target_url);
    """)
    conn.commit()


def reset_db(conn: sqlite3.Connection) -> None:
    conn.executescript("DROP TABLE IF EXISTS crawl_pages; DROP TABLE IF EXISTS crawl_links;")
    conn.commit()
    init_db(conn)


def page_count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) FROM crawl_pages").fetchone()
    return int(row[0]) if row else 0
