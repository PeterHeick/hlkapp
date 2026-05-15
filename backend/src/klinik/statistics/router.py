"""Statistik-router — bookings, efficiency, providers, revenue."""
from __future__ import annotations

import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from klinik.config import settings
from klinik.gecko.client import fetch_bookings
from klinik.statistics import service
from klinik.statistics.models import (
    ProviderBreakdownResponse,
    ProvidersResponse,
    RevenueResponse,
    TreatmentResponse,
    VolumeResponse,
)
from klinik.statistics.prices import load_prices

_CSV_HEADERS = {"Content-Disposition": "attachment"}
_BOM = "﻿"


def _csv_response(content: str, filename: str) -> Response:
    return Response(
        content=(_BOM + content).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

router = APIRouter(tags=["statistics"])


def _require_token() -> None:
    if not settings.gecko_api_token:
        raise HTTPException(status_code=400, detail="Gecko API token ikke konfigureret")


@router.get("/providers-by-treatment", response_model=ProviderBreakdownResponse)
async def get_providers_breakdown(start: str, end: str) -> ProviderBreakdownResponse:
    _require_token()
    return service.compute_providers_breakdown(await fetch_bookings(start, end))


@router.get("/bookings", response_model=VolumeResponse)
async def get_bookings(start: str, end: str) -> VolumeResponse:
    _require_token()
    return service.aggregate_volume(await fetch_bookings(start, end))


@router.get("/by-treatment", response_model=TreatmentResponse)
async def get_by_treatment(start: str, end: str) -> TreatmentResponse:
    _require_token()
    return service.compute_by_treatment(await fetch_bookings(start, end))


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers(start: str, end: str) -> ProvidersResponse:
    _require_token()
    return service.compute_providers(await fetch_bookings(start, end))


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(start: str, end: str) -> RevenueResponse:
    _require_token()
    bookings = await fetch_bookings(start, end)
    prices = load_prices()
    by_service: dict[str, float] = {}
    for b in bookings:
        if b.service and b.service.serviceName:
            name = b.service.serviceName
            by_service[name] = by_service.get(name, 0.0) + prices.get(name, 0.0)
    total = round(sum(by_service.values()), 2)
    return RevenueResponse(
        total_revenue=total,
        by_service={k: round(v, 2) for k, v in by_service.items()},
    )


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
    bookings = await fetch_bookings(start, end)
    prices = load_prices()
    by_service_count: dict[str, int] = {}
    by_service_revenue: dict[str, float] = {}
    for b in bookings:
        if b.service and b.service.serviceName:
            name = b.service.serviceName
            by_service_count[name] = by_service_count.get(name, 0) + 1
            by_service_revenue[name] = by_service_revenue.get(name, 0.0) + prices.get(name, 0.0)
    total = round(sum(by_service_revenue.values()), 2)
    buf = io.StringIO()
    buf.write("Behandling;Antal;Omsætning (kr)\n")
    for name, amount in sorted(by_service_revenue.items(), key=lambda x: -x[1]):
        buf.write(f"{name};{by_service_count.get(name, 0)};{int(round(amount))}\n")
    buf.write(f"Total;{sum(by_service_count.values())};{int(round(total))}\n")
    return _csv_response(buf.getvalue(), "omsætning.csv")


@router.get("/export/behandlinger")
async def export_behandlinger(start: str, end: str) -> Response:
    _require_token()
    result = service.compute_by_treatment(await fetch_bookings(start, end))
    buf = io.StringIO()
    buf.write("Behandling;Bookinger;Pris (kr);Omsætning (kr)\n")
    for item in result.items:
        pris = int(round(item.unit_price)) if item.unit_price > 0 else ""
        buf.write(f"{item.service_name};{item.booking_count};{pris};{int(round(item.total_revenue))}\n")
    return _csv_response(buf.getvalue(), "behandlinger.csv")


@router.get("/export/behandleroversigt")
async def export_behandleroversigt(start: str, end: str) -> Response:
    _require_token()
    result = service.compute_providers_breakdown(await fetch_bookings(start, end))
    buf = io.StringIO()
    buf.write("Behandler;Behandling;Antal;Omsætning (kr)\n")
    for p in result.providers:
        for t in p.treatments:
            buf.write(f"{p.calendar_name};{t.service_name};{t.count};{int(round(t.revenue))}\n")
    return _csv_response(buf.getvalue(), "behandleroversigt.csv")
