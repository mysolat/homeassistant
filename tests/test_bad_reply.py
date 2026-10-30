"""Tests for API replies that are not a JSON object."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState

from .conftest import MONTHLY_URL

OCTOBER_URL = MONTHLY_URL.format(zone="SGR01", month=10, year=2026)
NOVEMBER_URL = MONTHLY_URL.format(zone="SGR01", month=11, year=2026)
BAD_BODY = "<html>Bad gateway</html>"
JSON_HEADERS = {"Content-Type": "application/json"}


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_non_json_reply_retries_setup(
    hass, config_entry, aioclient_mock, freezer, caplog
) -> None:
    """A 200 reply with a broken JSON body is an API error, not an unexpected one."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, text=BAD_BODY, headers=JSON_HEADERS)

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert "Unexpected error" not in caplog.text


async def test_non_object_reply_retries_setup(
    hass, config_entry, aioclient_mock, freezer, caplog
) -> None:
    """A 200 reply with valid JSON that is not an object is an API error."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, json=[])

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert "Unexpected error" not in caplog.text


async def test_bad_prefetch_reply_keeps_today(
    hass, config_entry, mock_api, freezer
) -> None:
    """A bad reply for next month does not fail the update for today."""
    freezer.move_to("2026-10-31T21:00:00+08:00")
    mock_api.get(NOVEMBER_URL, text=BAD_BODY, headers=JSON_HEADERS)

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert (
        hass.states.get("sensor.waktu_solat_subuh").state
        == "2026-10-30T21:48:00+00:00"
    )
