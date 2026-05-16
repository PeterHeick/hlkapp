"""SQLite initialisering og connection-factory."""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

from klinik.config import settings

_BEHANDLINGER_CSV = Path("data") / "behandlinger.csv"
_PRISLISTER_DIR = Path("data") / "prislister"


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
                last_modified  TEXT,
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

            CREATE TABLE IF NOT EXISTS gecko_cache_meta (
                endpoint     TEXT PRIMARY KEY,
                last_fetched TEXT,
                etag         TEXT
            );

            CREATE TABLE IF NOT EXISTS bookings (
                booking_id       TEXT PRIMARY KEY,
                booked_date      TEXT NOT NULL,
                time_from        TEXT,
                time_to          TEXT,
                duration_minutes INTEGER,
                calendar_id      INTEGER,
                calendar_name    TEXT,
                service_id       INTEGER,
                service_name     TEXT,
                no_show          INTEGER DEFAULT 0,
                booked_online    INTEGER DEFAULT 0,
                created_date     TEXT,
                created_time     TEXT,
                price            REAL
            );
            CREATE INDEX IF NOT EXISTS idx_bookings_date     ON bookings(booked_date);
            CREATE INDEX IF NOT EXISTS idx_bookings_service  ON bookings(service_name);
            CREATE INDEX IF NOT EXISTS idx_bookings_calendar ON bookings(calendar_name);

            CREATE TABLE IF NOT EXISTS fetched_chunks (
                chunk_key  TEXT PRIMARY KEY,
                fetched_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sync_meta (
                key   TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS price_log (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                logged_at        TEXT NOT NULL,
                unknown_services TEXT
            );
        """)
        settings.exports_dir.mkdir(parents=True, exist_ok=True)
        conn.commit()
        try:
            conn.execute("ALTER TABLE crawl_pages ADD COLUMN last_modified TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        _migrate_behandlinger(conn)
    finally:
        conn.close()


def _migrate_behandlinger(conn: sqlite3.Connection) -> None:
    """Kopier behandlinger.csv → prislister/ ved første opstart af ny version."""
    _PRISLISTER_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(_PRISLISTER_DIR.glob("prisliste_*.csv"))
    if existing or not _BEHANDLINGER_CSV.exists():
        return
    dest = _PRISLISTER_DIR / "prisliste_UKENDT-DATO.csv"
    shutil.copy2(_BEHANDLINGER_CSV, dest)
