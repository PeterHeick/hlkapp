"""Statistik-router — bookings, efficiency, providers, revenue."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

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
