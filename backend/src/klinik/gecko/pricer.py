"""Pris-assignment: daterede CSV-prislister → SQLite bookings.price."""
from __future__ import annotations

import csv
import json
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3

logger = logging.getLogger(__name__)

_PRISLISTER_DIR = Path("data") / "prislister"


def _parse_danish_number(s: str) -> float:
    cleaned = re.sub(r"[^\d,.]", "", s.strip())
    if not cleaned or not any(c.isdigit() for c in cleaned):
        return 0.0
    if "," in cleaned:
        return float(cleaned.replace(".", "").replace(",", "."))
    if "." in cleaned:
        parts = cleaned.split(".")
        if len(parts) == 2 and len(parts[1]) <= 2:
            return float(cleaned)
        return float(cleaned.replace(".", ""))
    return float(cleaned)


def load_prisliste_files() -> list[tuple[date, dict[str, float]]]:
    """Returner [(dato, {navn: pris})] sorteret efter dato."""
    result: list[tuple[date, dict[str, float]]] = []
    if not _PRISLISTER_DIR.exists():
        return result
    for path in sorted(_PRISLISTER_DIR.glob("prisliste_*.csv")):
        date_str = path.stem.removeprefix("prisliste_")
        try:
            parsed_date = (
                date(2000, 1, 1) if date_str == "UKENDT-DATO" else date.fromisoformat(date_str)
            )
        except ValueError:
            continue
        prices: dict[str, float] = {}
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                navn = (row.get("navn") or "").strip()
                pris_raw = (row.get("pris") or "0").strip()
                if navn:
                    prices[navn] = _parse_danish_number(pris_raw)
        result.append((parsed_date, prices))
    return sorted(result, key=lambda x: x[0])


def load_latest_prices() -> dict[str, float]:
    """Nyeste prisliste som {navn: pris}. Tom dict hvis ingen filer."""
    files = load_prisliste_files()
    return files[-1][1] if files else {}


def find_price(
    prisliste_files: list[tuple[date, dict[str, float]]],
    service_name: str,
    booking_date: date,
) -> float | None:
    """Pris for service på booking_date. Ingen prisliste for perioden → brug ældste."""
    if not prisliste_files:
        return None
    eligible = [(d, p) for d, p in prisliste_files if d <= booking_date]
    _, prices = eligible[-1] if eligible else prisliste_files[0]
    return prices.get(service_name)


def should_reprice(conn: sqlite3.Connection) -> bool:
    """True hvis nyeste prisliste-CSV er ændret siden last_priced_at."""
    if not _PRISLISTER_DIR.exists():
        return False
    csv_files = list(_PRISLISTER_DIR.glob("prisliste_*.csv"))
    if not csv_files:
        return False
    newest_mtime = max(f.stat().st_mtime for f in csv_files)
    row = conn.execute("SELECT value FROM sync_meta WHERE key = 'last_priced_at'").fetchone()
    if not row:
        return True
    try:
        return newest_mtime > datetime.fromisoformat(row[0]).timestamp()
    except (ValueError, TypeError):
        return True


def apply_prices(conn: sqlite3.Connection) -> None:
    """Prissæt alle bookinger ud fra daterede prislister. Log ukendte service-navne."""
    prisliste_files = load_prisliste_files()
    if not prisliste_files:
        logger.warning("Ingen prisliste-filer — kan ikke prissætte bookinger")
        _update_last_priced_at(conn)
        return

    rows = conn.execute(
        """
        SELECT booking_id, booked_date, service_name
        FROM bookings
        WHERE service_name IS NOT NULL
        """
    ).fetchall()

    if not rows:
        _update_last_priced_at(conn)
        return

    unknown: set[str] = set()
    updates: list[tuple[float | None, str]] = []
    for row in rows:
        booking_date = date.fromisoformat(row[1])
        service_name = row[2] or ""
        price = find_price(prisliste_files, service_name, booking_date)
        if price is None:
            unknown.add(service_name)
        updates.append((price, row[0]))

    with conn:
        conn.executemany("UPDATE bookings SET price = ? WHERE booking_id = ?", updates)

    if unknown:
        conn.execute(
            "INSERT INTO price_log (logged_at, unknown_services) VALUES (?, ?)",
            (datetime.now().isoformat(), json.dumps(sorted(unknown))),
        )
        conn.commit()
        logger.warning("Ukendte services (ingen pris): %s", ", ".join(sorted(unknown)))

    _update_last_priced_at(conn)
    logger.info("Prissatte %d bookinger, %d ukendte services", len(rows), len(unknown))


def _update_last_priced_at(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO sync_meta (key, value) VALUES ('last_priced_at', ?)",
        (datetime.now().isoformat(),),
    )
    conn.commit()


def prices_changed(new_prices: dict[str, int], latest_csv_path: Path) -> bool:
    """True hvis new_prices afviger fra latest_csv_path (normaliseret)."""
    if not latest_csv_path.exists():
        return True
    old: dict[str, float] = {}
    with latest_csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            navn = (row.get("navn") or "").strip()
            pris_raw = (row.get("pris") or "0").strip()
            if navn:
                old[navn] = _parse_danish_number(pris_raw)
    norm_old = {k: round(v) for k, v in old.items()}
    norm_new = {k: round(v) for k, v in new_prices.items()}
    return norm_old != norm_new
