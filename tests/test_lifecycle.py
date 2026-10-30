"""Tests for the coordinator's lifecycle: unload, reload and where it is stored."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import async_fire_time_changed


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_unload_stops_midnight_refresh(
    hass, config_entry, mock_api, freezer
) -> None:
    """After unload the midnight listener is gone and makes no API call."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    calls = mock_api.call_count

    freezer.move_to("2026-10-31T00:00:01+08:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_api.call_count == calls


async def test_reload_works(hass, config_entry, mock_api, freezer) -> None:
    """Reloading the entry sets it up again with the same times."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)

    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    assert (
        hass.states.get("sensor.waktu_solat_subuh").state
        == "2026-10-29T21:48:00+00:00"
    )


async def test_coordinator_is_runtime_data(
    hass, config_entry, mock_api, freezer
) -> None:
    """The coordinator lives on the entry and knows which entry owns it."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)

    assert config_entry.runtime_data.config_entry is config_entry
