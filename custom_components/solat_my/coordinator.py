"""DataUpdateCoordinator for Waktu Solat Malaysia."""
from __future__ import annotations

import html
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_BASE_URL, API_MONTHLY_ENDPOINT, DOMAIN, MALAYSIA_TZ

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)

# After an error, try again this soon instead of waiting for SCAN_INTERVAL.
RETRY_AFTER_ERROR = 300  # seconds

# About 30 minutes of failures at RETRY_AFTER_ERROR. Fewer would flag short blips.
FAILURES_BEFORE_REPAIR = 6

# The calendar keeps this many extra months, beyond the ones the update loop keeps.
CALENDAR_MONTHS_KEPT = 3

# JAKIM uses Malay month abbreviations (lang=ms_my) since 2026.
# Map them to English so strptime %b can parse them.
_MS_TO_EN = {
    "Jan": "Jan", "Feb": "Feb", "Mac": "Mar", "Apr": "Apr",
    "Mei": "May", "Jun": "Jun", "Jul": "Jul", "Ogos": "Aug",
    "Sep": "Sep", "Okt": "Oct", "Nov": "Nov", "Dis": "Dec",
}


def _normalise_ms_date(date_str: str) -> str:
    """Replace Malay month abbreviations with English equivalents."""
    parts = date_str.split("-")
    if len(parts) == 3:
        parts[1] = _MS_TO_EN.get(parts[1], parts[1])
    return "-".join(parts)


def _parse_date(date_str: str):
    """Parse a date string like '10-Mar-2026' or '10-Mei-2026' into a date object, or None on failure."""
    try:
        return datetime.strptime(_normalise_ms_date(date_str), "%d-%b-%Y").date()
    except ValueError:
        return None


class SolatMyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch prayer times from solat.my API."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, name: str, initial_zone: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{name}",
            update_interval=SCAN_INTERVAL,
        )
        self.zone = initial_zone
        # (zone, year, month) → API response. Holds this month and, on the
        # last day of the month, next month, so midnight needs no network.
        self._months: dict[tuple[str, int, int], dict[str, Any]] = {}
        # Months the calendar read outside the update loop's two months.
        # Kept apart so _async_update_data can prune _months freely.
        self._calendar_months: dict[tuple[str, int, int], dict[str, Any]] = {}
        # Failed updates in a row. At FAILURES_BEFORE_REPAIR the Repairs notice appears.
        self._consecutive_failures = 0
        self._issue_id = f"api_unreachable_{self.config_entry.entry_id}"
        self.config_entry.async_on_unload(
            lambda: ir.async_delete_issue(hass, DOMAIN, self._issue_id)
        )

    def async_track_midnight(self) -> Callable[[], None]:
        """Refresh at the start of each new day. Returns the function that stops it."""

        async def _midnight_refresh(_: datetime) -> None:
            _LOGGER.debug("Midnight triggered — refreshing prayer times for zone %s", self.zone)
            await self.async_refresh()

        return async_track_time_change(
            self.hass, _midnight_refresh, hour=0, minute=0, second=0
        )

    async def async_set_zone(self, zone: str) -> None:
        """Change the active zone and immediately refresh data."""
        self.zone = zone
        self._months.clear()
        self._calendar_months.clear()
        await self.async_refresh()

    def cached_month(self, year: int, month: int) -> dict[str, Any] | None:
        """Return one cached month for the current zone. Never fetches. None on a miss."""
        key = (self.zone, year, month)
        return self._months.get(key) or self._calendar_months.get(key)

    def cached_month_keys(self) -> list[tuple[str, int, int]]:
        """Return the sorted (zone, year, month) keys of every cached month."""
        return sorted({*self._months, *self._calendar_months})

    async def async_get_month(self, year: int, month: int) -> dict[str, Any] | None:
        """Return one month for the current zone, from cache or the API. None if unavailable."""
        if (cached := self.cached_month(year, month)) is not None:
            return cached
        key = (self.zone, year, month)
        try:
            data = await self._async_fetch_month(*key)
        except UpdateFailed as err:
            _LOGGER.debug("Could not fetch %s for the calendar: %s", key, err)
            return None
        self._calendar_months[key] = data
        while len(self._calendar_months) > CALENDAR_MONTHS_KEPT:
            del self._calendar_months[next(iter(self._calendar_months))]
        return data

    async def _async_fetch_month(self, zone: str, year: int, month: int) -> dict[str, Any]:
        """Fetch one month of prayer times for a zone from the solat.my API."""
        url = API_BASE_URL + API_MONTHLY_ENDPOINT.format(zone=zone, month=month, year=year)
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Error fetching prayer times: HTTP {response.status}",
                        retry_after=RETRY_AFTER_ERROR,
                    )
                data = await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(
                f"Error communicating with solat.my API: {err}",
                retry_after=RETRY_AFTER_ERROR,
            ) from err

        if not isinstance(data, dict):
            raise UpdateFailed(
                f"Unexpected API response: {type(data).__name__}",
                retry_after=RETRY_AFTER_ERROR,
            )
        if data.get("status") != "OK!":
            raise UpdateFailed(
                f"API returned error status: {data.get('status')}",
                retry_after=RETRY_AFTER_ERROR,
            )
        if not data.get("prayerTime"):
            raise UpdateFailed(
                "No prayer time data received from API", retry_after=RETRY_AFTER_ERROR
            )
        return data

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch today's data, and raise or clear the API repair issue."""
        try:
            data = await self._async_update_data_inner()
        except UpdateFailed as err:
            self._consecutive_failures += 1
            if self._consecutive_failures >= FAILURES_BEFORE_REPAIR:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    self._issue_id,
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="api_unreachable",
                    translation_placeholders={"zone": self.zone, "error": str(err)},
                )
            raise
        self._consecutive_failures = 0
        ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
        return data

    async def _async_update_data_inner(self) -> dict[str, Any]:
        """Return today's prayer times, fetching from API only when the zone or month changes."""
        today_date = dt_util.now(MALAYSIA_TZ).date()
        key = (self.zone, today_date.year, today_date.month)

        if key not in self._months:
            _LOGGER.debug("Fetching monthly prayer times for zone %s (%d-%02d)", *key)
            self._months[key] = await self._async_fetch_month(*key)
        else:
            _LOGGER.debug("Using cached monthly prayer times for zone %s", self.zone)
        data = self._months[key]

        prayer_times = data.get("prayerTime", [])
        today = next(
            (pt for pt in prayer_times if _parse_date(pt.get("date", "")) == today_date),
            None,
        )
        if today is None:
            self._months.pop(key, None)
            raise UpdateFailed(
                f"No prayer times for {today_date.isoformat()} in zone {self.zone}",
                retry_after=RETRY_AFTER_ERROR,
            )

        # On the last day of the month, also fetch next month. A failed
        # prefetch must never fail the update.
        tomorrow = today_date + timedelta(days=1)
        next_key = (self.zone, tomorrow.year, tomorrow.month)
        if next_key != key and next_key not in self._months:
            try:
                self._months[next_key] = await self._async_fetch_month(*next_key)
            except UpdateFailed as err:
                _LOGGER.debug("Could not prefetch %s: %s", next_key, err)
        self._months = {k: v for k, v in self._months.items() if k in (key, next_key)}

        date_str = today.get("date", "")
        parsed: dict[str, datetime | None] = {}

        for prayer in ["imsak", "fajr", "syuruk", "dhuha", "dhuhr", "asr", "maghrib", "isha"]:
            time_str = today.get(prayer, "")
            if time_str and date_str:
                try:
                    parsed[prayer] = datetime.strptime(
                        _normalise_ms_date(f"{date_str} {time_str}"), "%d-%b-%Y %H:%M:%S"
                    ).replace(tzinfo=MALAYSIA_TZ)
                except ValueError:
                    _LOGGER.warning(
                        "Could not parse %s time: %s %s", prayer, date_str, time_str
                    )
                    parsed[prayer] = None
            else:
                parsed[prayer] = None

        # Tomorrow's row comes from the cache only. The prefetch above already
        # ran, so a missing month or row leaves these two keys empty.
        tomorrow_row = next(
            (
                pt
                for pt in self._months.get(next_key, {}).get("prayerTime", [])
                if _parse_date(pt.get("date", "")) == tomorrow
            ),
            None,
        )
        tomorrow_fajr: datetime | None = None
        if tomorrow_row is not None:
            tomorrow_date_str = tomorrow_row.get("date", "")
            tomorrow_fajr_str = tomorrow_row.get("fajr", "")
            if tomorrow_fajr_str and tomorrow_date_str:
                try:
                    tomorrow_fajr = datetime.strptime(
                        _normalise_ms_date(f"{tomorrow_date_str} {tomorrow_fajr_str}"),
                        "%d-%b-%Y %H:%M:%S",
                    ).replace(tzinfo=MALAYSIA_TZ)
                except ValueError:
                    _LOGGER.warning(
                        "Could not parse fajr time: %s %s",
                        tomorrow_date_str,
                        tomorrow_fajr_str,
                    )

        return {
            "zone": data.get("zone", self.zone),
            "zone_desc": self._zone_desc(),
            "bearing": html.unescape(data.get("bearing", "")),
            "hijri": today.get("hijri", ""),
            "date": today.get("date", ""),
            "day": today.get("day", ""),
            "raw": today,
            "prayer_times": parsed,
            "locations": data.get("locations", []),
            "tomorrow_fajr": tomorrow_fajr,
            "tomorrow_raw": tomorrow_row or {},
        }

    def _zone_desc(self) -> str:
        """Return human-readable description for current zone."""
        from .const import ZONES
        return ZONES.get(self.zone, self.zone)
