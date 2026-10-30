"""Tests for the next-prayer sensor, including the roll-over to tomorrow's Subuh."""
from __future__ import annotations

from .conftest import MONTHLY_URL, load_fixture_json

NEXT_PRAYER = "sensor.waktu_solat_waktu_solat_seterusnya"
NOVEMBER_URL = MONTHLY_URL.format(zone="SGR01", month=11, year=2026)


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_daytime_unchanged(hass, config_entry, mock_api, freezer) -> None:
    """During the day the sensor shows today's next prayer and tomorrow is False."""
    freezer.move_to("2026-10-30T10:00:00+08:00")

    await _setup(hass, config_entry)

    state = hass.states.get(NEXT_PRAYER)
    assert state.state == "Zohor"
    assert state.attributes["tomorrow"] is False


async def test_after_isyak_shows_tomorrow_subuh(
    hass, config_entry, mock_api, freezer
) -> None:
    """After Isyak the sensor shows tomorrow's Subuh with its time and countdown."""
    freezer.move_to("2026-10-30T21:00:00+08:00")

    await _setup(hass, config_entry)

    state = hass.states.get(NEXT_PRAYER)
    assert state.state == "Subuh"
    assert state.attributes["prayer"] == "fajr"
    assert state.attributes["time_24h"] == "05:48"
    assert state.attributes["countdown_seconds"] == 31680
    assert state.attributes["countdown"] == "08:48"
    assert state.attributes["tomorrow"] is True


async def test_after_isyak_on_last_day_uses_next_month(
    hass, config_entry, mock_api, freezer
) -> None:
    """On the last day of the month, tomorrow's Subuh comes from next month's data."""
    mock_api.get(NOVEMBER_URL, json=load_fixture_json("monthly_SGR01_2026_11.json"))
    freezer.move_to("2026-10-31T21:00:00+08:00")

    await _setup(hass, config_entry)

    state = hass.states.get(NEXT_PRAYER)
    assert state.state == "Subuh"
    assert state.attributes["time_24h"] == "05:48"
    assert state.attributes["tomorrow"] is True
    assert state.attributes["countdown_seconds"] == 31680


async def test_after_isyak_without_tomorrow_data(
    hass, config_entry, mock_api, freezer
) -> None:
    """If next month is unavailable, the sensor still says Subuh but has no time."""
    mock_api.get(NOVEMBER_URL, status=500)
    freezer.move_to("2026-10-31T21:00:00+08:00")

    await _setup(hass, config_entry)

    state = hass.states.get(NEXT_PRAYER)
    assert state.state == "Subuh"
    assert state.attributes["tomorrow"] is True
    assert state.attributes["time_24h"] is None
    assert state.attributes["countdown"] is None


async def test_never_selesai(hass, config_entry, mock_api, freezer) -> None:
    """Just before midnight the sensor never reports Selesai."""
    freezer.move_to("2026-10-30T23:59:00+08:00")

    await _setup(hass, config_entry)

    assert hass.states.get(NEXT_PRAYER).state != "Selesai"
