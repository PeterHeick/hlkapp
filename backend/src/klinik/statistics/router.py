"""Statistik-router — queries mod SQLite bookings-cache."""
from __future__ import annotations

import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from klinik.config import settings
from klinik.database import get_connection
from klinik.gecko.sync import foreground_fetch
from klinik.statistics import service
from klinik.statistics.models import (
    ProviderBreakdownResponse,
    ProvidersResponse,
    RevenueResponse,
    TreatmentResponse,
    VolumeResponse,
)
from klinik.statistics.prices import load_prices

router = APIRouter(tags=["statistics"])

_BOM = "﻿"


def _csv_response(content: str, filename: str) -> Response:
    return Response(
        content=(_BOM + content).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _require_token() -> None:
    if not settings.gecko_api_token:
        raise HTTPException(status_code=400, detail="Gecko API token ikke konfigureret")


def _validate_dates(start: str, end: str) -> None:
    from datetime import date  # noqa: PLC0415
    for val, name in ((start, "start"), (end, "end")):
        try:
            date.fromisoformat(val)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ugyldig dato '{val}' for '{name}'") from None


async def _ensure_chunks(start: str, end: str) -> None:
    """Hent manglende chunks i forgrunden hvis token er konfigureret."""
    _validate_dates(start, end)
    if settings.gecko_api_token:
        await foreground_fetch(start, end)


@router.get("/bookings", response_model=VolumeResponse)
async def get_bookings(start: str, end: str) -> VolumeResponse:
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        return service.aggregate_volume(conn, start, end)
    finally:
        conn.close()


@router.get("/by-treatment", response_model=TreatmentResponse)
async def get_by_treatment(start: str, end: str) -> TreatmentResponse:
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        return service.compute_by_treatment(conn, start, end)
    finally:
        conn.close()


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers(start: str, end: str) -> ProvidersResponse:
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        return service.compute_providers(conn, start, end)
    finally:
        conn.close()


@router.get("/providers-by-treatment", response_model=ProviderBreakdownResponse)
async def get_providers_breakdown(start: str, end: str) -> ProviderBreakdownResponse:
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        return service.compute_providers_breakdown(conn, start, end)
    finally:
        conn.close()


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(start: str, end: str) -> RevenueResponse:
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        by_service = service.compute_revenue_by_service(conn, start, end)
    finally:
        conn.close()
    total = round(sum(by_service.values()), 2)
    return RevenueResponse(total_revenue=total, by_service=by_service)


@router.get("/export/prisliste")
async def export_prisliste() -> Response:
    prices = load_prices()
    buf = io.StringIO()
    buf.write("Behandling;Pris\n")
    for name, price in prices.items():
        buf.write(f"{name};{int(round(price)) if price > 0 else ''}\n")
    return _csv_response(buf.getvalue(), "prisliste.csv")


@router.get("/export/omsaetning")
async def export_omsaetning(start: str, end: str) -> Response:
    _require_token()
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        by_service_rev = service.compute_revenue_by_service(conn, start, end)
        cnt_rows = conn.execute(
            """
            SELECT service_name, COUNT(*) FROM bookings
            WHERE booked_date >= ? AND booked_date <= ?
            GROUP BY service_name
            """,
            (start, end),
        ).fetchall()
    finally:
        conn.close()
    counts = {(r[0] or "Ukendt"): r[1] for r in cnt_rows}
    total = round(sum(by_service_rev.values()), 2)
    buf = io.StringIO()
    buf.write("Behandling;Antal;Omsætning (kr)\n")
    for name, amount in sorted(by_service_rev.items(), key=lambda x: -x[1]):
        buf.write(f"{name};{counts.get(name, 0)};{int(round(amount))}\n")
    buf.write(f"Total;{sum(counts.values())};{int(round(total))}\n")
    return _csv_response(buf.getvalue(), "omsætning.csv")


@router.get("/export/behandlinger")
async def export_behandlinger(start: str, end: str) -> Response:
    _require_token()
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        result = service.compute_by_treatment(conn, start, end)
    finally:
        conn.close()
    buf = io.StringIO()
    buf.write("Behandling;Bookinger;Pris (kr);Omsætning (kr)\n")
    for item in result.items:
        pris = int(round(item.unit_price)) if item.unit_price > 0 else ""
        buf.write(f"{item.service_name};{item.booking_count};{pris};{int(round(item.total_revenue))}\n")
    return _csv_response(buf.getvalue(), "behandlinger.csv")


@router.get("/export/behandleroversigt")
async def export_behandleroversigt(start: str, end: str) -> Response:
    _require_token()
    await _ensure_chunks(start, end)
    conn = get_connection()
    try:
        result = service.compute_providers_breakdown(conn, start, end)
    finally:
        conn.close()
    buf = io.StringIO()
    buf.write("Behandler;Behandling;Antal;Omsætning (kr)\n")
    for p in result.providers:
        for t in p.treatments:
            buf.write(f"{p.calendar_name};{t.service_name};{t.count};{int(round(t.revenue))}\n")
    return _csv_response(buf.getvalue(), "behandleroversigt.csv")
