"""Fetch-orkestrator: foreground-fetch + baggrunds-backfill, global asyncio.Lock."""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3

logger = logging.getLogger(__name__)

_HISTORY_START = date(2021, 1, 1)
_UKENDT_CSV = Path("data") / "prislister" / "prisliste_UKENDT-DATO.csv"
_MIGRATION_WARNING = (
    "Prisliste migreret fra behandlinger.csv med ukendt dato. "
    "Omdøb filen til korrekt dato (prisliste_YYYY-MM-DD.csv) under data/prislister/."
)


def _migration_warning() -> str | None:
    return _MIGRATION_WARNING if _UKENDT_CSV.exists() else None

_lock: asyncio.Lock | None = None
_backfill_task: asyncio.Task[None] | None = None
_phase = "idle"
_last_error: str | None = None
_chunk_freshness: dict[str, datetime] = {}  # in-memory staleness for current/future chunks
_FRESH_SECONDS = 1800  # 30 min


def _get_lock() -> asyncio.Lock:
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock


def current_chunk_key() -> str:
    today = date.today()
    half = "H1" if today.month <= 6 else "H2"
    return f"{today.year}-{half}"


def chunk_range(chunk_key: str) -> tuple[str, str]:
    year_str, half = chunk_key.split("-")
    year = int(year_str)
    if half == "H1":
        return (f"{year}-01-01", f"{year}-06-30")
    return (f"{year}-07-01", f"{year}-12-31")


def all_chunks_up_to_today() -> list[str]:
    chunks: list[str] = []
    y, h = _HISTORY_START.year, 1
    current = current_chunk_key()
    while True:
        key = f"{y}-H{h}"
        chunks.append(key)
        if key == current:
            break
        h += 1
        if h > 2:
            h = 1
            y += 1
    return chunks


def historical_chunks() -> list[str]:
    all_c = all_chunks_up_to_today()
    return all_c[:-1]


def _chunk_key_for_date(d: date) -> str:
    half = "H1" if d.month <= 6 else "H2"
    return f"{d.year}-{half}"


def chunks_for_range(start: str, end: str) -> list[str]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    end_key = _chunk_key_for_date(end_date)
    result: list[str] = []
    y, h = _HISTORY_START.year, 1
    while True:
        key = f"{y}-H{h}"
        c_start, c_end = chunk_range(key)
        if date.fromisoformat(c_start) <= end_date and date.fromisoformat(c_end) >= start_date:
            result.append(key)
        if key == end_key:
            break
        h += 1
        if h > 2:
            h = 1
            y += 1
    return result


def _get_fetched_chunks(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT chunk_key FROM fetched_chunks").fetchall()
    return {r[0] for r in rows}


def _mark_chunk_fetched(conn: sqlite3.Connection, chunk_key: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO fetched_chunks (chunk_key, fetched_at) VALUES (?, ?)",
        (chunk_key, datetime.now().isoformat()),
    )
    conn.commit()


async def _fetch_and_store_chunk(chunk_key: str) -> bool:
    global _last_error
    from klinik.database import get_connection
    from klinik.gecko.client import fetch_bookings, upsert_bookings

    start, end = chunk_range(chunk_key)
    logger.info("Henter chunk %s (%s → %s)", chunk_key, start, end)
    try:
        bookings = await fetch_bookings(start, end)
        conn = get_connection()
        try:
            upsert_bookings(conn, bookings)
            chunk_end = date.fromisoformat(end)
            if chunk_end < date.today():
                _mark_chunk_fetched(conn, chunk_key)
            else:
                _chunk_freshness[chunk_key] = datetime.now()
        finally:
            conn.close()
        logger.info("Chunk %s: %d bookinger", chunk_key, len(bookings))
        _last_error = None
        return True
    except Exception as exc:
        _last_error = str(exc)
        logger.error("Chunk %s fejlede: %s", chunk_key, exc)
        return False


def _run_pricer_if_needed() -> None:
    from klinik.database import get_connection
    from klinik.gecko.pricer import apply_prices, should_reprice

    conn = get_connection()
    try:
        if should_reprice(conn):
            apply_prices(conn)
    finally:
        conn.close()


async def foreground_fetch(start: str, end: str) -> None:
    """Hent alle manglende chunks for perioden [start, end]. Prioriteret over backfill."""
    global _phase
    from klinik.database import get_connection

    needed = chunks_for_range(start, end)
    conn = get_connection()
    try:
        fetched = _get_fetched_chunks(conn)
    finally:
        conn.close()

    missing = [k for k in needed if k not in fetched or _chunk_is_stale(k)]
    if not missing:
        return

    lock = _get_lock()
    async with lock:
        prev_phase = _phase
        _phase = "foreground"
        try:
            # Re-read inside lock: snapshot taken before acquiring may be stale
            conn = get_connection()
            try:
                fetched_now = _get_fetched_chunks(conn)
            finally:
                conn.close()
            for chunk_key in missing:
                if chunk_key in fetched_now or not _chunk_is_stale(chunk_key):
                    continue
                await _fetch_and_store_chunk(chunk_key)
                fetched_now.add(chunk_key)
        finally:
            _phase = prev_phase if prev_phase != "foreground" else "idle"

    await asyncio.to_thread(_run_pricer_if_needed)


def _chunk_is_stale(key: str) -> bool:
    if key not in _chunk_freshness:
        return True
    return (datetime.now() - _chunk_freshness[key]).total_seconds() > _FRESH_SECONDS


async def _backfill_loop() -> None:
    global _phase
    from klinik.database import get_connection

    await asyncio.sleep(10)
    lock = _get_lock()
    while True:
        conn = get_connection()
        try:
            fetched = _get_fetched_chunks(conn)
        finally:
            conn.close()

        pending = [k for k in historical_chunks() if k not in fetched]
        if not pending:
            current = current_chunk_key()
            if _chunk_is_stale(current):
                async with lock:
                    _phase = "backfill"
                    await _fetch_and_store_chunk(current)
                await asyncio.to_thread(_run_pricer_if_needed)
            logger.info("Backfill komplet")
            _phase = "idle"
            break

        chunk_key = pending[0]
        async with lock:
            _phase = "backfill"
            await _fetch_and_store_chunk(chunk_key)

        await asyncio.to_thread(_run_pricer_if_needed)
        await asyncio.sleep(120)

    _phase = "idle"


async def start_backfill_loop() -> None:
    global _backfill_task
    if _backfill_task is not None and not _backfill_task.done():
        _backfill_task.cancel()
    _backfill_task = asyncio.create_task(_backfill_loop())


def get_sync_status() -> dict[str, object]:
    from klinik.database import get_connection

    conn = get_connection()
    try:
        hist = historical_chunks()
        fetched = _get_fetched_chunks(conn)
        row_priced = conn.execute(
            "SELECT value FROM sync_meta WHERE key = 'last_priced_at'"
        ).fetchone()
        row_oldest = conn.execute(
            "SELECT MIN(booked_date) FROM bookings"
        ).fetchone()
        row_count = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()
        pending_count = len([k for k in hist if k not in fetched])
    finally:
        conn.close()

    return {
        "phase": _phase,
        "chunks_done": len(fetched),
        "chunks_total": len(hist),
        "pending_chunks": pending_count,
        "oldest_booking_date": row_oldest[0] if row_oldest and row_oldest[0] else None,
        "booking_count": row_count[0] if row_count else 0,
        "last_priced_at": row_priced[0] if row_priced else None,
        "migration_warning": _migration_warning(),
        "error": _last_error,
    }
