"""Unit tests for statistik-service-funktioner."""
import pytest

from klinik.gecko.models import BookedTime, Booking, BookingInterval, GeckoCalendar, GeckoService
from klinik.statistics.service import aggregate_volume, compute_by_treatment, compute_providers


def make_booking(
    booking_id: int = 1,
    date: str = "2024-01-15",
    interval: tuple[str, str] = ("09:00", "10:00"),
    calendar_id: int = 1,
    calendar_name: str = "Behandler 1",
    service_name: str | None = "Laser",
    no_show: bool = False,
) -> Booking:
    return Booking(
        bookingId=booking_id,
        bookedTime=BookedTime(
            date=date,
            interval=[BookingInterval(**{"from": interval[0], "to": interval[1]})],
        ),
        service=GeckoService(serviceId=1, serviceName=service_name) if service_name else None,
        calendar=GeckoCalendar(calendarId=calendar_id, calendarName=calendar_name),
        noShow=no_show,
    )


def test_aggregate_volume_totals() -> None:
    bookings = [
        make_booking(1, "2024-01-15"),
        make_booking(2, "2024-01-15", no_show=True),
        make_booking(3, "2024-01-16"),
    ]
    result = aggregate_volume(bookings)
    assert result.total == 3
    assert result.no_show_total == 1
    assert len(result.bookings) == 2
    day1 = result.bookings[0]
    assert day1.date == "2024-01-15"
    assert day1.count == 2
    assert day1.no_show_count == 1


def test_aggregate_volume_sorted() -> None:
    bookings = [make_booking(1, "2024-01-16"), make_booking(2, "2024-01-14")]
    result = aggregate_volume(bookings)
    assert result.bookings[0].date == "2024-01-14"


def test_compute_by_treatment_revenue(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("klinik.statistics.service.load_prices", lambda: {"Laser": 1200.0})
    bookings = [
        make_booking(1, service_name="Laser"),
        make_booking(2, service_name="Laser"),
        make_booking(3, service_name="IPL"),
    ]
    result = compute_by_treatment(bookings)
    laser = next(i for i in result.items if i.service_name == "Laser")
    assert laser.booking_count == 2
    assert laser.unit_price == 1200.0
    assert laser.total_revenue == 2400.0


def test_compute_by_treatment_no_price(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("klinik.statistics.service.load_prices", lambda: {})
    bookings = [make_booking(1, service_name="Laser")]
    result = compute_by_treatment(bookings)
    assert result.items[0].unit_price == 0.0
    assert result.items[0].total_revenue == 0.0


def test_compute_providers_revenue(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("klinik.statistics.service.load_prices", lambda: {"Laser": 500.0})
    bookings = [
        make_booking(1, calendar_id=1, calendar_name="Ana", service_name="Laser", no_show=False),
        make_booking(2, calendar_id=1, calendar_name="Ana", service_name="Laser", no_show=True),
        make_booking(3, calendar_id=2, calendar_name="Bo", service_name="Laser", no_show=False),
    ]
    result = compute_providers(bookings)
    assert len(result.providers) == 2
    ana = next(p for p in result.providers if p.calendar_name == "Ana")
    assert ana.booking_count == 2
    assert ana.no_show_count == 1
    assert ana.revenue == 1000.0


def test_compute_providers_sorted_by_revenue(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("klinik.statistics.service.load_prices", lambda: {"Laser": 500.0})
    bookings = [
        make_booking(1, calendar_id=2, calendar_name="Bo"),
        make_booking(2, calendar_id=1, calendar_name="Ana"),
        make_booking(3, calendar_id=1, calendar_name="Ana"),
    ]
    result = compute_providers(bookings)
    assert result.providers[0].calendar_name == "Ana"
