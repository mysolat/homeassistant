"""Tests for the change of month: explicit months, prefetch and quick retry."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import MONTHLY_URL, load_fixture_json

OCTOBER_URL = MONTHLY_URL.format(zone="SGR01", month=10, year=2026)
NOVEMBER_URL = MONTHLY_URL.format(zone="SGR01", month=11, year=2026)


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_last_day_prefetches_next_month(
    hass, config_entry, mock_api, freezer
) -> None:
    """On the last day of the month the coordinator also downloads next month."""
    mock_api.get(NOVEMBER_URL, json=load_fixture_json("monthly_SGR01_2026_11.json"))
    freezer.move_to("2026-10-31T21:00:00+08:00")

    await _setup(hass, config_entry)

    assert mock_api.call_count == 2


async def test_midnight_uses_prefetched_month_when_api_is_down(
    hass, config_entry, mock_api, freezer
) -> None:
    """After midnight the prefetched month serves the new day without network."""
    mock_api.get(NOVEMBER_URL, json=load_fixture_json("monthly_SGR01_2026_11.json"))
    freezer.move_to("2026-10-31T21:00:00+08:00")
    await _setup(hass, config_entry)
    coordinator = hass.data["solat_my"][config_entry.entry_id]

    mock_api.clear_requests()
    mock_api.get(NOVEMBER_URL, status=500)
    freezer.move_to("2026-11-01T00:00:05+08:00")
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success is True
    assert (
        hass.states.get("sensor.waktu_solat_subuh").state
        == "2026-10-31T21:48:00+00:00"
    )


async def test_missing_today_is_an_error(
    hass, config_entry, mock_api, freezer, caplog
) -> None:
    """A reply without today's date makes setup retry and the log names the date."""
    freezer.move_to("2026-10-15T10:00:00+08:00")

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert "2026-10-15" in caplog.text


async def test_error_retries_after_five_minutes(
    hass, config_entry, mock_api, freezer
) -> None:
    """After an API error the coordinator retries in five minutes, not 12 hours."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)
    coordinator = hass.data["solat_my"][config_entry.entry_id]

    mock_api.clear_requests()
    mock_api.get(OCTOBER_URL, status=500)
    await coordinator.async_set_zone("SGR01")
    assert coordinator.last_update_success is False

    mock_api.clear_requests()
    mock_api.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))
    freezer.tick(timedelta(seconds=301))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert coordinator.last_update_success is True
