"""Diagnostics for Waktu Solat Malaysia."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import MALAYSIA_TZ, PRAYER_NAMES_MS, PRAYER_TIMES


def _iso(value: datetime | None) -> str | None:
    """Return a time as an ISO string in Malaysian time, or None."""
    return None if value is None else value.astimezone(MALAYSIA_TZ).isoformat()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return what a maintainer needs for a bug report. The integration holds no secrets."""
    report: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
    }

    # runtime_data is unset when setup failed before the coordinator was stored.
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is None:
        report["coordinator"] = None
        return report

    data = coordinator.data or {}
    prayer_times = data.get("prayer_times", {})
    interval = coordinator.update_interval
    report["coordinator"] = {
        "zone": coordinator.zone,
        "last_update_success": coordinator.last_update_success,
        "last_exception": (
            None if coordinator.last_exception is None else str(coordinator.last_exception)
        ),
        "update_interval_seconds": None if interval is None else interval.total_seconds(),
        "source": data.get("source"),
    }
    report["today"] = {
        PRAYER_NAMES_MS[prayer].lower(): _iso(prayer_times.get(prayer))
        for prayer in PRAYER_TIMES
    }
    report["tomorrow_subuh"] = _iso(data.get("tomorrow_fajr"))
    report["hijri"] = data.get("hijri")
    report["date"] = data.get("date")
    report["zone_desc"] = data.get("zone_desc")
    report["cached_months"] = [
        f"{zone}-{year}-{month:02d}" for zone, year, month in coordinator.cached_month_keys()
    ]
    report["saved_years"] = sorted(f"{z}-{y}" for z, y in coordinator.saved_year_keys())
    return report
