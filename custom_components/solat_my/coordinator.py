"""DataUpdateCoordinator for Waktu Solat Malaysia."""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import API_BASE_URL, API_MONTHLY_ENDPOINT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)


def _parse_date(date_str: str):
    """Parse a date string like '10-Mar-2026' into a date object, or None on failure."""
    try:
        return datetime.strptime(date_str, "%d-%b-%Y").date()
    except ValueError:
        return None


class SolatMyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch prayer times from solat.my API."""

    def __init__(self, hass: HomeAssistant, name: str, initial_zone: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name}",
            update_interval=SCAN_INTERVAL,
        )
        self.zone = initial_zone
        self._cancel_midnight: Callable | None = None
        self._monthly_cache: dict[str, Any] | None = None
        self._cache_ym: tuple[int, int] | None = None  # (year, month)

    def async_setup(self) -> None:
        """Register a midnight listener to refresh data at the start of each new day."""

        async def _midnight_refresh(_: datetime) -> None:
            _LOGGER.debug("Midnight triggered — refreshing prayer times for zone %s", self.zone)
            await self.async_refresh()

        self._cancel_midnight = async_track_time_change(
            self.hass, _midnight_refresh, hour=0, minute=0, second=0
        )

    def async_shutdown(self) -> None:
        """Cancel the midnight listener on unload."""
        if self._cancel_midnight:
            self._cancel_midnight()
            self._cancel_midnight = None

    async def async_set_zone(self, zone: str) -> None:
        """Change the active zone and immediately refresh data."""
        self.zone = zone
        self._monthly_cache = None
        self._cache_ym = None
        await self.async_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Return today's prayer times, fetching from API only when the month changes."""
        # Use Home Assistant timezone for date boundaries.
        today_date = dt_util.now().date()
        current_ym = (today_date.year, today_date.month)

        if self._monthly_cache is None or self._cache_ym != current_ym:
            _LOGGER.debug(
                "Fetching monthly prayer times for zone %s (%d-%02d)",
                self.zone, *current_ym,
            )
            url = API_BASE_URL + API_MONTHLY_ENDPOINT.format(zone=self.zone)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status != 200:
                            raise UpdateFailed(
                                f"Error fetching prayer times: HTTP {response.status}"
                            )
                        data = await response.json()
            except aiohttp.ClientError as err:
                raise UpdateFailed(f"Error communicating with solat.my API: {err}") from err

            if data.get("status") != "OK!":
                raise UpdateFailed(f"API returned error status: {data.get('status')}")

            if not data.get("prayerTime"):
                raise UpdateFailed("No prayer time data received from API")

            self._monthly_cache = data
            self._cache_ym = current_ym
        else:
            _LOGGER.debug("Using cached monthly prayer times for zone %s", self.zone)
            data = self._monthly_cache

        prayer_times = data.get("prayerTime", [])
        today = next(
            (
                pt for pt in prayer_times
                if _parse_date(pt.get("date", "")) == today_date
            ),
            prayer_times[0],
        )
        date_str = today.get("date", "")
        parsed: dict[str, datetime | None] = {}

        for prayer in ["imsak", "fajr", "syuruk", "dhuha", "dhuhr", "asr", "maghrib", "isha"]:
            time_str = today.get(prayer, "")
            if time_str and date_str:
                try:
                    parsed[prayer] = datetime.strptime(
                        f"{date_str} {time_str}", "%d-%b-%Y %H:%M:%S"
                    )
                except ValueError:
                    _LOGGER.warning(
                        "Could not parse %s time: %s %s", prayer, date_str, time_str
                    )
                    parsed[prayer] = None
            else:
                parsed[prayer] = None

        return {
            "zone": data.get("zone", self.zone),
            "zone_desc": self._zone_desc(),
            "bearing": data.get("bearing", ""),
            "hijri": today.get("hijri", ""),
            "date": today.get("date", ""),
            "day": today.get("day", ""),
            "raw": today,
            "prayer_times": parsed,
            "locations": data.get("locations", []),
        }

    def _zone_desc(self) -> str:
        """Return human-readable description for current zone."""
        from .const import ZONES
        return ZONES.get(self.zone, self.zone)
