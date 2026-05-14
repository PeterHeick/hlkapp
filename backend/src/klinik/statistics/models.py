"""Pydantic response-modeller til statistik-endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class BookingVolume(BaseModel):
    date: str
    count: int
    no_show_count: int


class VolumeResponse(BaseModel):
    bookings: list[BookingVolume]
    total: int
    no_show_total: int


class TreatmentItem(BaseModel):
    service_name: str
    booking_count: int
    no_show_count: int
    no_show_rate: float
    unit_price: float
    total_revenue: float


class TreatmentResponse(BaseModel):
    items: list[TreatmentItem]
    total_revenue: float


class ProviderStats(BaseModel):
    calendar_name: str
    booking_count: int
    no_show_count: int
    no_show_rate: float
    revenue: float


class ProvidersResponse(BaseModel):
    providers: list[ProviderStats]


class RevenueResponse(BaseModel):
    total_revenue: float
    by_service: dict[str, float]


class ProviderTreatmentItem(BaseModel):
    service_name: str
    count: int
    revenue: float


class ProviderBreakdown(BaseModel):
    calendar_name: str
    total_revenue: float
    total_count: int
    treatments: list[ProviderTreatmentItem]


class ProviderBreakdownResponse(BaseModel):
    providers: list[ProviderBreakdown]
