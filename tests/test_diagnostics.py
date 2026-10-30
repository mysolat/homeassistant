"""Tests for the diagnostics download."""
from __future__ import annotations

import json

from custom_components.solat_my.diagnostics import async_get_config_entry_diagnostics

from .conftest import MONTHLY_URL


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_diagnostics_report_the_entry_and_today(
    hass, config_entry, mock_api, freezer
) -> None:
    """Diagnostics hold the entry, the last update result and today's times."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)

    result = await async_get_config_entry_diagnostics(hass, config_entry)

    assert result["entry"]["data"] == {"name": "Waktu Solat", "zone": "SGR01"}
    assert result["coordinator"]["zone"] == "SGR01"
    assert result["coordinator"]["last_update_success"] is True
    assert result["coordinator"]["last_exception"] is None
    assert result["today"]["subuh"] == "2026-10-30T05:48:00+08:00"
    assert "SGR01-2026-10" in result["cached_months"]
    json.dumps(result)


async def test_diagnostics_after_a_failed_setup(
    hass, config_entry, aioclient_mock, freezer
) -> None:
    """A failed setup still gives a report, and shows the error when the coordinator exists."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(MONTHLY_URL.format(zone="SGR01", month=10, year=2026), status=500)
    await _setup(hass, config_entry)

    result = await async_get_config_entry_diagnostics(hass, config_entry)

    if hasattr(config_entry, "runtime_data"):
        assert result["coordinator"]["last_update_success"] is False
        assert result["coordinator"]["last_exception"]
    else:
        assert result == {"entry": result["entry"], "coordinator": None}
    assert result["entry"]["data"] == {"name": "Waktu Solat", "zone": "SGR01"}
    json.dumps(result)
