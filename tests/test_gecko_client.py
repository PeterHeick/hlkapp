"""Unit tests for BookingInterval.duration_minutes() — ingen httpx-mock."""
from klinik.gecko.models import BookingInterval


def test_duration_full_hour() -> None:
    interval = BookingInterval(**{"from": "09:00", "to": "10:00"})
    assert interval.duration_minutes() == 60


def test_duration_half_hour() -> None:
    interval = BookingInterval(**{"from": "10:30", "to": "11:00"})
    assert interval.duration_minutes() == 30


def test_duration_crosses_hour() -> None:
    interval = BookingInterval(**{"from": "09:45", "to": "10:15"})
    assert interval.duration_minutes() == 30


def test_duration_zero() -> None:
    interval = BookingInterval(**{"from": "09:00", "to": "09:00"})
    assert interval.duration_minutes() == 0


def test_duration_90_minutes() -> None:
    interval = BookingInterval(**{"from": "08:00", "to": "09:30"})
    assert interval.duration_minutes() == 90
