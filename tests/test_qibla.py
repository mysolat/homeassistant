"""Tests for the qibla direction sensor."""
from __future__ import annotations

from custom_components.solat_my.sensor import _parse_bearing


def test_parse_bearing() -> None:
    """Degrees, minutes and seconds become decimal degrees."""
    assert _parse_bearing("291° 7′ 23″") == 291.12
    assert _parse_bearing("291°") == 291.0
    assert _parse_bearing("") is None
    assert _parse_bearing("abc") is None


async def test_qibla_sensor(hass, config_entry, mock_api, freezer) -> None:
    """The sensor shows the zone's qibla direction in decimal degrees."""
    freezer.move_to("2026-10-30T10:00:00+08:00")

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.waktu_solat_arah_kiblat")
    assert state is not None
    assert state.state == "291.12"
    assert state.attributes["unit_of_measurement"] == "°"
    assert state.attributes["dms"] == "291° 7′ 23″"
    assert state.attributes["rujukan"] == "utara benar"
