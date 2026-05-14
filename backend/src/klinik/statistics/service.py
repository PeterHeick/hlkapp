"""Statistik-beregning baseret på Gecko Booking-data."""
from __future__ import annotations

from klinik.gecko.models import Booking
from klinik.statistics.models import (
    BookingVolume,
    ProviderBreakdown,
    ProviderBreakdownResponse,
    ProviderTreatmentItem,
    ProvidersResponse,
    ProviderStats,
    TreatmentItem,
    TreatmentResponse,
    VolumeResponse,
)
from klinik.statistics.prices import load_prices


def aggregate_volume(bookings: list[Booking]) -> VolumeResponse:
    by_date: dict[str, list[Booking]] = {}
    for b in bookings:
        by_date.setdefault(b.bookedTime.date, []).append(b)
    items = [
        BookingVolume(
            date=date,
            count=len(bs),
            no_show_count=sum(1 for b in bs if b.noShow),
        )
        for date, bs in sorted(by_date.items())
    ]
    return VolumeResponse(
        bookings=items,
        total=len(bookings),
        no_show_total=sum(1 for b in bookings if b.noShow),
    )


def compute_by_treatment(bookings: list[Booking]) -> TreatmentResponse:
    prices = load_prices()
    by_service: dict[str, list[Booking]] = {}
    for b in bookings:
        name = (b.service.serviceName or "Ukendt") if b.service else "Ukendt"
        by_service.setdefault(name, []).append(b)
    items: list[TreatmentItem] = []
    for name, bs in by_service.items():
        unit = prices.get(name, 0.0)
        total = round(unit * len(bs), 2)
        no_shows = sum(1 for b in bs if b.noShow)
        rate = round(no_shows / len(bs) * 100, 1)
        items.append(TreatmentItem(
            service_name=name,
            booking_count=len(bs),
            no_show_count=no_shows,
            no_show_rate=rate,
            unit_price=unit,
            total_revenue=total,
        ))
    items.sort(key=lambda x: x.total_revenue, reverse=True)
    return TreatmentResponse(
        items=items,
        total_revenue=round(sum(i.total_revenue for i in items), 2),
    )


def compute_providers_breakdown(bookings: list[Booking]) -> ProviderBreakdownResponse:
    prices = load_prices()
    by_calendar: dict[int, list[Booking]] = {}
    for b in bookings:
        by_calendar.setdefault(b.calendar.calendarId, []).append(b)

    providers: list[ProviderBreakdown] = []
    for _cal_id, bs in by_calendar.items():
        name = bs[0].calendar.calendarName or str(bs[0].calendar.calendarId)
        by_svc: dict[str, list[Booking]] = {}
        for b in bs:
            svc = (b.service.serviceName or "Ukendt") if b.service else "Ukendt"
            by_svc.setdefault(svc, []).append(b)

        treatments: list[ProviderTreatmentItem] = []
        for svc, sbs in by_svc.items():
            rev = round(prices.get(svc, 0.0) * len(sbs), 2)
            treatments.append(ProviderTreatmentItem(service_name=svc, count=len(sbs), revenue=rev))

        total_rev = round(sum(t.revenue for t in treatments), 2)
        providers.append(ProviderBreakdown(
            calendar_name=name,
            total_revenue=total_rev,
            total_count=len(bs),
            treatments=sorted(treatments, key=lambda x: x.revenue, reverse=True),
        ))

    return ProviderBreakdownResponse(
        providers=sorted(providers, key=lambda x: x.total_revenue, reverse=True)
    )


def compute_providers(bookings: list[Booking]) -> ProvidersResponse:
    prices = load_prices()
    by_calendar: dict[int, list[Booking]] = {}
    for b in bookings:
        by_calendar.setdefault(b.calendar.calendarId, []).append(b)
    providers: list[ProviderStats] = []
    for _cal_id, bs in by_calendar.items():
        name = bs[0].calendar.calendarName or str(bs[0].calendar.calendarId)
        revenue = sum(
            prices.get(b.service.serviceName or "", 0.0) if b.service else 0.0
            for b in bs
        )
        no_shows = sum(1 for b in bs if b.noShow)
        rate = round(no_shows / len(bs) * 100, 1)
        providers.append(ProviderStats(
            calendar_name=name,
            booking_count=len(bs),
            no_show_count=no_shows,
            no_show_rate=rate,
            revenue=round(revenue, 2),
        ))
    return ProvidersResponse(providers=sorted(providers, key=lambda x: x.revenue, reverse=True))
