"""Calendar platform for Waktu Solat Malaysia — the five prayer times as events."""
from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    MALAYSIA_TZ,
    PRAYER_ASR,
    PRAYER_DHUHR,
    PRAYER_FAJR,
    PRAYER_ISHA,
    PRAYER_MAGHRIB,
    PRAYER_NAMES_MS,
)
from .coordinator import SolatMyCoordinator, _normalise_ms_date, _parse_date
from .sensor import _make_device_info

# The five fardu prayers only. Imsak, Syuruk and Dhuha are left out of the calendar.
CALENDAR_PRAYERS = (PRAYER_FAJR, PRAYER_DHUHR, PRAYER_ASR, PRAYER_MAGHRIB, PRAYER_ISHA)

# EVENT_LENGTH: display length only. An event marks when a prayer time begins, as
# JAKIM publishes it; it says nothing about when the time ends.
EVENT_LENGTH = timedelta(minutes=10)

# One request reads at most this many months. The coordinator caches the same number.
MAX_MONTHS_PER_REQUEST = 3


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the prayer calendar."""
    coordinator: SolatMyCoordinator = entry.runtime_data
    async_add_entities([PrayerCalendar(coordinator, entry)])


def _months_in_range(start: datetime, end: datetime) -> list[tuple[int, int]]:
    """List the (year, month) pairs in Malaysian time that [start, end) touches.

    Stops after MAX_MONTHS_PER_REQUEST months. An empty or reversed range has none.
    """
    first = start.astimezone(MALAYSIA_TZ)
    last = (end - timedelta(microseconds=1)).astimezone(MALAYSIA_TZ)
    months: list[tuple[int, int]] = []
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month) and len(months) < MAX_MONTHS_PER_REQUEST:
        months.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def _events_for_month(
    data: dict[str, Any], start: datetime, end: datetime
) -> list[CalendarEvent]:
    """Build the events of one API month that overlap [start, end).

    Skips any row or time that does not parse. Never raises on bad data.
    """
    # A margin of one day on the early side keeps an event that crosses midnight.
    first_day = start.astimezone(MALAYSIA_TZ).date() - timedelta(days=1)
    last_day = end.astimezone(MALAYSIA_TZ).date()
    zone = data.get("zone")
    description = f"Zon {zone}" if zone else None

    events: list[CalendarEvent] = []
    for row in data.get("prayerTime") or []:
        if not isinstance(row, dict):
            continue
        date_str = row.get("date")
        if not isinstance(date_str, str):
            continue
        row_date = _parse_date(date_str)
        if row_date is None or not first_day <= row_date <= last_day:
            continue
        for key in CALENDAR_PRAYERS:
            time_str = row.get(key)
            if not time_str:
                continue
            try:
                begins = datetime.strptime(
                    _normalise_ms_date(f"{date_str} {time_str}"), "%d-%b-%Y %H:%M:%S"
                ).replace(tzinfo=MALAYSIA_TZ)
            except ValueError:
                continue
            finishes = begins + EVENT_LENGTH
            if begins < end and finishes > start:
                events.append(
                    CalendarEvent(
                        start=begins,
                        end=finishes,
                        summary=PRAYER_NAMES_MS[key],
                        description=description,
                    )
                )
    return events


class PrayerCalendar(CoordinatorEntity[SolatMyCoordinator], CalendarEntity):
    """The five daily prayers as calendar events.

    Each event starts when the prayer time begins, as JAKIM publishes it. The
    event length is a fixed display length and never a ruling on when the time ends.
    """

    _attr_has_entity_name = True
    _attr_name = "Kalendar Solat"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the prayer calendar."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_device_info = _make_device_info(entry)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the event in progress now, or else the next one.

        Reads only months the coordinator already holds. Returns None if there are none.
        """
        now = dt_util.now(MALAYSIA_TZ)
        # Look through the end of tomorrow, so the next event exists after Isyak.
        horizon = datetime.combine(
            now.date() + timedelta(days=2), time.min, tzinfo=MALAYSIA_TZ
        )
        events: list[CalendarEvent] = []
        for year, month in _months_in_range(now, horizon):
            data = self.coordinator.cached_month(year, month)
            if data is not None:
                events.extend(_events_for_month(data, now, horizon))
        return min(events, key=lambda event: event.start_datetime_local, default=None)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return the events that overlap [start_date, end_date).

        A month the API cannot give is left out. The other months still show.
        """
        events: list[CalendarEvent] = []
        for year, month in _months_in_range(start_date, end_date):
            data = await self.coordinator.async_get_month(year, month)
            if data is not None:
                events.extend(_events_for_month(data, start_date, end_date))
        return sorted(events, key=lambda event: event.start_datetime_local)
