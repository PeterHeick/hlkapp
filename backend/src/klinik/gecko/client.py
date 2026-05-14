"""Gecko Booking API HTTP-klient — pagineret /booking fetch."""
from __future__ import annotations

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
    base = settings.gecko_base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    bookings: list[Booking] = []
    page = 0  # Gecko bruger 0-baseret paginering

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
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
