"""Tests for zone persistence, Malaysian time and API response handling."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import State
from pytest_homeassistant_custom_component.common import mock_restore_cache

from .conftest import MONTHLY_URL

# 10:00 in Malaysia on 30 October 2026.
NOW = "2026-10-30T02:00:00+00:00"
SUBUH_UTC = "2026-10-29T21:48:00+00:00"
MAGHRIB_SGR03_UTC = "2026-10-30T11:00:00+00:00"


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_times_are_malaysian_time_when_ha_uses_utc(
    hass, config_entry, mock_api, freezer
) -> None:
    """Prayer times are Malaysian time even when Home Assistant uses UTC."""
    await hass.config.async_set_time_zone("UTC")
    freezer.move_to(NOW)

    await _setup(hass, config_entry)

    assert hass.states.get("sensor.waktu_solat_subuh").state == SUBUH_UTC
    assert hass.states.get("sensor.waktu_solat_waktu_solat_semasa").state == "Dhuha"
    assert hass.states.get("sensor.waktu_solat_waktu_solat_seterusnya").state == "Zohor"


async def test_times_are_malaysian_time_with_test_default_zone(
    hass, config_entry, mock_api, freezer
) -> None:
    """Prayer times are Malaysian time under the test default time zone (US/Pacific)."""
    freezer.move_to(NOW)

    await _setup(hass, config_entry)

    assert hass.states.get("sensor.waktu_solat_subuh").state == SUBUH_UTC


async def test_restored_zone_is_used_after_restart(
    hass, config_entry, mock_api, freezer
) -> None:
    """A zone kept only in restore state moves into the config entry and the sensors."""
    mock_restore_cache(hass, [State("select.waktu_solat_zon", "SGR03")])
    freezer.move_to(NOW)

    await _setup(hass, config_entry)

    maghrib = hass.states.get("sensor.waktu_solat_maghrib")
    assert maghrib.state == MAGHRIB_SGR03_UTC
    assert maghrib.attributes["zone"] == "SGR03"
    assert config_entry.data["zone"] == "SGR03"


async def test_selecting_zone_persists_it(
    hass, config_entry, mock_api, freezer
) -> None:
    """Selecting a zone saves it in the config entry and refreshes the sensors."""
    freezer.move_to(NOW)
    await _setup(hass, config_entry)

    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": "select.waktu_solat_zon", "option": "SGR03"},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert config_entry.data["zone"] == "SGR03"
    assert hass.states.get("sensor.waktu_solat_maghrib").state == MAGHRIB_SGR03_UTC


async def test_bearing_is_unescaped(hass, config_entry, mock_api, freezer) -> None:
    """The bearing attribute shows degrees, minutes and seconds, not HTML entities."""
    freezer.move_to(NOW)

    await _setup(hass, config_entry)

    current = hass.states.get("sensor.waktu_solat_waktu_solat_semasa")
    assert current.attributes["bearing"] == "291° 7′ 23″"


async def test_timeout_retries_setup(
    hass, config_entry, aioclient_mock, freezer
) -> None:
    """An API timeout makes setup retry instead of raising an unexpected error."""
    aioclient_mock.get(MONTHLY_URL.format(zone="SGR01", month=10, year=2026), exc=TimeoutError())
    freezer.move_to(NOW)

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
