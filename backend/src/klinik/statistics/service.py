"""Statistik-beregning direkte fra SQLite bookings-tabel."""
from __future__ import annotations

import sqlite3

from klinik.statistics.models import (
    BookingVolume,
    ProviderBreakdown,
    ProviderBreakdownResponse,
    ProvidersResponse,
    ProviderStats,
    ProviderTreatmentItem,
    TreatmentItem,
    TreatmentResponse,
    VolumeResponse,
)


def aggregate_volume(conn: sqlite3.Connection, start: str, end: str) -> VolumeResponse:
    rows = conn.execute(
        """
        SELECT booked_date,
               COUNT(*) AS cnt,
               SUM(no_show) AS no_shows
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY booked_date
        ORDER BY booked_date
        """,
        (start, end),
    ).fetchall()
    items = [
        BookingVolume(date=r[0], count=r[1], no_show_count=r[2] or 0)
        for r in rows
    ]
    total = sum(i.count for i in items)
    no_show_total = sum(i.no_show_count for i in items)
    return VolumeResponse(bookings=items, total=total, no_show_total=no_show_total)


def compute_by_treatment(conn: sqlite3.Connection, start: str, end: str) -> TreatmentResponse:
    rows = conn.execute(
        """
        SELECT service_name,
               COUNT(*) AS cnt,
               SUM(no_show) AS no_shows,
               COALESCE(SUM(price), 0) AS total_rev,
               COALESCE(AVG(price), 0) AS avg_price
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY service_name
        """,
        (start, end),
    ).fetchall()
    items: list[TreatmentItem] = []
    for r in rows:
        name = r[0] or "Ukendt"
        cnt = r[1]
        no_shows = r[2] or 0
        total_rev = round(float(r[3]), 2)
        avg_price = round(float(r[4]), 2)
        rate = round(no_shows / cnt * 100, 1) if cnt else 0.0
        items.append(TreatmentItem(
            service_name=name,
            booking_count=cnt,
            no_show_count=no_shows,
            no_show_rate=rate,
            unit_price=avg_price,
            total_revenue=total_rev,
        ))
    items.sort(key=lambda x: x.total_revenue, reverse=True)
    return TreatmentResponse(
        items=items,
        total_revenue=round(sum(i.total_revenue for i in items), 2),
    )


def compute_providers(conn: sqlite3.Connection, start: str, end: str) -> ProvidersResponse:
    rows = conn.execute(
        """
        SELECT calendar_name,
               COUNT(*) AS cnt,
               SUM(no_show) AS no_shows,
               COALESCE(SUM(price), 0) AS revenue
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY calendar_name
        """,
        (start, end),
    ).fetchall()
    providers: list[ProviderStats] = []
    for r in rows:
        name = r[0] or "Ukendt"
        cnt = r[1]
        no_shows = r[2] or 0
        rev = round(float(r[3]), 2)
        rate = round(no_shows / cnt * 100, 1) if cnt else 0.0
        providers.append(ProviderStats(
            calendar_name=name,
            booking_count=cnt,
            no_show_count=no_shows,
            no_show_rate=rate,
            revenue=rev,
        ))
    return ProvidersResponse(providers=sorted(providers, key=lambda x: x.revenue, reverse=True))


def compute_providers_breakdown(
    conn: sqlite3.Connection, start: str, end: str
) -> ProviderBreakdownResponse:
    rows = conn.execute(
        """
        SELECT calendar_name,
               service_name,
               COUNT(*) AS cnt,
               COALESCE(SUM(price), 0) AS revenue
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY calendar_name, service_name
        ORDER BY calendar_name, revenue DESC
        """,
        (start, end),
    ).fetchall()

    by_cal: dict[str, list[ProviderTreatmentItem]] = {}
    for r in rows:
        cal = r[0] or "Ukendt"
        svc = r[1] or "Ukendt"
        rev = round(float(r[3]), 2)
        by_cal.setdefault(cal, []).append(
            ProviderTreatmentItem(service_name=svc, count=r[2], revenue=rev)
        )

    cal_totals = conn.execute(
        """
        SELECT calendar_name,
               COUNT(*) AS cnt,
               COALESCE(SUM(price), 0) AS revenue
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY calendar_name
        """,
        (start, end),
    ).fetchall()
    totals = {(r[0] or "Ukendt"): (r[1], round(float(r[2]), 2)) for r in cal_totals}

    providers: list[ProviderBreakdown] = []
    for cal, treatments in by_cal.items():
        cnt, rev = totals.get(cal, (0, 0.0))
        providers.append(ProviderBreakdown(
            calendar_name=cal,
            total_revenue=rev,
            total_count=cnt,
            treatments=treatments,
        ))
    return ProviderBreakdownResponse(
        providers=sorted(providers, key=lambda x: x.total_revenue, reverse=True)
    )


def compute_revenue_by_service(conn: sqlite3.Connection, start: str, end: str) -> dict[str, float]:
    rows = conn.execute(
        """
        SELECT service_name, COALESCE(SUM(price), 0) AS rev
        FROM bookings
        WHERE booked_date >= ? AND booked_date <= ?
        GROUP BY service_name
        ORDER BY rev DESC
        """,
        (start, end),
    ).fetchall()
    return {(r[0] or "Ukendt"): round(float(r[1]), 2) for r in rows}
