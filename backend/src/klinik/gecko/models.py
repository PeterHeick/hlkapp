"""Pydantic-modeller for Gecko Booking API-svar."""
from __future__ import annotations

from pydantic import BaseModel, Field


class BookingInterval(BaseModel):
    from_: str = Field(alias="from")
    to: str

    def duration_minutes(self) -> int:
        fh, fm = map(int, self.from_.split(":"))
        th, tm = map(int, self.to.split(":"))
        return (th * 60 + tm) - (fh * 60 + fm)


class BookedTime(BaseModel):
    date: str
    interval: list[BookingInterval]


class GeckoService(BaseModel):
    serviceId: int | None = None
    serviceName: str | None = None


class GeckoCalendar(BaseModel):
    calendarId: int
    calendarName: str | None = None


class Booking(BaseModel):
    bookingId: int
    bookedTime: BookedTime
    service: GeckoService | None = None
    calendar: GeckoCalendar
    noShow: bool = False
    bookedOnline: bool = False
    createdDate: str | None = None
    createdTime: str | None = None
