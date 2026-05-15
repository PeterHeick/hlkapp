"""Pydantic-modeller for Gecko Booking API-svar."""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class _Stripped(BaseModel):
    """Base der stripper leading/trailing whitespace fra alle string-felter ved parse."""

    @model_validator(mode="before")
    @classmethod
    def _strip_strings(cls, data: object) -> object:
        if isinstance(data, dict):
            return {
                k: v.strip() if isinstance(v, str) else v
                for k, v in data.items()
            }
        return data


class BookingInterval(_Stripped):
    from_: str = Field(alias="from")
    to: str

    def duration_minutes(self) -> int:
        fh, fm = map(int, self.from_.split(":"))
        th, tm = map(int, self.to.split(":"))
        return (th * 60 + tm) - (fh * 60 + fm)


class BookedTime(_Stripped):
    date: str
    interval: list[BookingInterval]


class GeckoService(_Stripped):
    serviceId: int | None = None
    serviceName: str | None = None


class GeckoCalendar(_Stripped):
    calendarId: int
    calendarName: str | None = None


class Booking(_Stripped):
    bookingId: int
    bookedTime: BookedTime
    service: GeckoService | None = None
    calendar: GeckoCalendar
    noShow: bool = False
    bookedOnline: bool = False
    createdDate: str | None = None
    createdTime: str | None = None
