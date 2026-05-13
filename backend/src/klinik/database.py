"""SQLite initialisering og connection-factory."""
from __future__ import annotations

import sqlite3

from klinik.config import settings


def get_connection() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(settings.db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS crawl_pages (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                url          TEXT UNIQUE NOT NULL,
                title        TEXT,
                status_code  INTEGER,
                depth        INTEGER DEFAULT 0,
                parent_url   TEXT,
                word_count   INTEGER DEFAULT 0,
                is_orphan    INTEGER DEFAULT 0,
                redirect_chain TEXT DEFAULT '[]',
                crawled_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            -- Gecko-cache metadata (Fase 3)
            CREATE TABLE IF NOT EXISTS gecko_cache_meta (
                endpoint     TEXT PRIMARY KEY,
                last_fetched TEXT,
                etag         TEXT
            );
        """)
        settings.exports_dir.mkdir(parents=True, exist_ok=True)
        conn.commit()
    finally:
        conn.close()
