"""Gecko Booking API HTTP-klient — pagineret /booking fetch + SQLite upsert."""
from __future__ import annotations

import asyncio
import sqlite3

import httpx
from fastapi import HTTPException

from klinik.config import settings
from klinik.gecko.models import Booking

_FIELDS = "bookingId,bookedTime,calendar,service,noShow,bookedOnline,createdDate,createdTime"
_EXPAND_CAL = "calendarId,calendarName"
_EXPAND_SVC = "serviceId,serviceName"


async def fetch_bookings(start: str, end: str) -> list[Booking]:
    """Hent alle bookinger i perioden [start, end] (YYYY-MM-DD)."""
    token = settings.gecko_api_token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="Gecko API token ikke konfigureret")
    base = settings.gecko_base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    bookings: list[Booking] = []
    page = 0

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            if page > 0:
                await asyncio.sleep(0.3)
            try:
                resp = await client.get(
                    f"{base}/booking",
                    headers=headers,
                    params={
                        "period[start]": start,
                        "period[end]": end,
                        "page": page,
                        "rowsPerPage": 100,
                        "fields": _FIELDS,
                        "expand[calendar]": _EXPAND_CAL,
                        "expand[service]": _EXPAND_SVC,
                    },
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                body = exc.response.text[:500]
                raise HTTPException(
                    status_code=502,
                    detail=f"Gecko API fejl {exc.response.status_code}: {body}",
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Gecko API ikke tilgængeligt: {exc}",
                ) from exc

            data = resp.json()
            items: list[object] = data.get("list") or []
            if not items:
                break
            bookings.extend(Booking.model_validate(b) for b in items)
            paging = data.get("paging") or {}
            total = paging.get("totalRows") or paging.get("total") or 0
            if (total > 0 and len(bookings) >= total) or len(items) < 100:
                break
            page += 1

    return bookings


def upsert_bookings(conn: sqlite3.Connection, bookings: list[Booking]) -> None:
    """Gem bookinger i SQLite — bevarer eksisterende price-felt ved konflikt."""
    if not bookings:
        return
    rows = []
    for b in bookings:
        bt = b.bookedTime
        date_str = bt.date
        interval = bt.interval[0] if bt.interval else None
        time_from = interval.from_ if interval else None
        time_to = interval.to if interval else None
        duration = interval.duration_minutes() if interval else None
        rows.append((
            str(b.bookingId),
            date_str,
            time_from,
            time_to,
            duration,
            b.calendar.calendarId,
            b.calendar.calendarName,
            b.service.serviceId if b.service else None,
            b.service.serviceName if b.service else None,
            int(b.noShow),
            int(b.bookedOnline),
            b.createdDate,
            b.createdTime,
        ))
    with conn:
        conn.executemany(
            """
            INSERT INTO bookings (
                booking_id, booked_date, time_from, time_to, duration_minutes,
                calendar_id, calendar_name, service_id, service_name,
                no_show, booked_online, created_date, created_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(booking_id) DO UPDATE SET
                booked_date=excluded.booked_date,
                time_from=excluded.time_from,
                time_to=excluded.time_to,
                duration_minutes=excluded.duration_minutes,
                calendar_name=excluded.calendar_name,
                service_name=excluded.service_name,
                no_show=excluded.no_show,
                booked_online=excluded.booked_online
            """,
            rows,
        )
