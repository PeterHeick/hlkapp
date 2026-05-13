"""Crawler DB-hjælpere til brug af både backend og analyse-pipeline."""
from __future__ import annotations

import sqlite3

from klinik.database import get_connection


def reset_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        "DROP TABLE IF EXISTS crawl_pages; DROP TABLE IF EXISTS crawl_links;"
    )
    conn.commit()
    from klinik.database import init_db
    init_db()


def page_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM crawl_pages").fetchone()
    conn.close()
    return int(row[0]) if row else 0
