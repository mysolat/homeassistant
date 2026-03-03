"""DataUpdateCoordinator for Waktu Solat Malaysia."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_BASE_URL, API_DAILY_ENDPOINT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)


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

    async def async_set_zone(self, zone: str) -> None:
        """Change the active zone and immediately refresh data."""
        self.zone = zone
        await self.async_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from solat.my API."""
        url = API_BASE_URL + API_DAILY_ENDPOINT.format(zone=self.zone)

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

        prayer_times = data.get("prayerTime", [])
        if not prayer_times:
            raise UpdateFailed("No prayer time data received from API")

        today = prayer_times[0]
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
