"""Tests for the saved year of prayer times that covers a solat.my outage."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import issue_registry as ir

from custom_components.solat_my.const import DOMAIN

from .conftest import MONTHLY_URL, YEARLY_URL, load_fixture_json

OCTOBER_URL = MONTHLY_URL.format(zone="SGR01", month=10, year=2026)
NOVEMBER_URL = MONTHLY_URL.format(zone="SGR01", month=11, year=2026)
YEAR_URL = YEARLY_URL.format(zone="SGR01", year=2026)
NEXT_PRAYER = "sensor.waktu_solat_waktu_solat_seterusnya"


def _year_payload() -> dict:
    """Build a yearly reply from the October and November fixtures."""
    payload = load_fixture_json("monthly_SGR01_2026_10.json")
    payload["periodType"] = "year"
    payload["prayerTime"] += load_fixture_json("monthly_SGR01_2026_11.json")["prayerTime"]
    return payload


def _store_key(config_entry) -> str:
    """Return the storage key of the entry's saved years."""
    return f"{DOMAIN}.{config_entry.entry_id}"


def _prefill_storage(hass_storage, config_entry) -> None:
    """Put the SGR01 2026 year in storage before setup."""
    key = _store_key(config_entry)
    hass_storage[key] = {
        "version": 1,
        "minor_version": 1,
        "key": key,
        "data": {"years": {"SGR01-2026": _year_payload()}},
    }


def _yearly_calls(aioclient_mock, url: str = YEAR_URL) -> int:
    """Count requests made to a yearly URL."""
    return sum(1 for call in aioclient_mock.mock_calls if str(call[1]) == url)


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


async def test_year_saved_after_first_update(
    hass, config_entry, aioclient_mock, hass_storage, freezer
) -> None:
    """A good update also saves the whole year on disk."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))
    aioclient_mock.get(YEAR_URL, json=_year_payload())

    await _setup(hass, config_entry)

    assert _yearly_calls(aioclient_mock) == 1
    assert "SGR01-2026" in hass_storage[_store_key(config_entry)]["data"]["years"]
    assert config_entry.runtime_data.data["source"] == "api"


async def test_month_from_saved_year_when_api_down(
    hass, config_entry, aioclient_mock, hass_storage, freezer
) -> None:
    """With solat.my down, the saved year serves today and no Repairs notice appears."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    _prefill_storage(hass_storage, config_entry)
    aioclient_mock.get(OCTOBER_URL, status=500)
    aioclient_mock.get(YEAR_URL, status=500)

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert hass.states.get("sensor.waktu_solat_subuh").state != "unavailable"
    assert config_entry.runtime_data.data["source"] == "saved"
    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, f"api_unreachable_{config_entry.entry_id}"
        )
        is None
    )


async def test_no_saved_year_still_fails(
    hass, config_entry, aioclient_mock, freezer
) -> None:
    """With no saved year, an outage fails setup as before."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, status=500)
    aioclient_mock.get(YEAR_URL, status=500)

    await _setup(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_yearly_tried_once_a_day(
    hass, config_entry, aioclient_mock, freezer
) -> None:
    """A failed yearly fetch is not tried again the same day."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))
    aioclient_mock.get(YEAR_URL, status=500)
    await _setup(hass, config_entry)
    coordinator = config_entry.runtime_data

    for _ in range(3):
        await coordinator.async_refresh()

    assert coordinator.last_update_success is True
    assert _yearly_calls(aioclient_mock) == 1


async def test_month_boundary_uses_saved_year(
    hass, config_entry, aioclient_mock, hass_storage, freezer
) -> None:
    """When next month cannot be fetched, tomorrow's Subuh comes from the saved year."""
    freezer.move_to("2026-10-31T21:00:00+08:00")
    _prefill_storage(hass_storage, config_entry)
    aioclient_mock.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))
    aioclient_mock.get(NOVEMBER_URL, status=500)
    aioclient_mock.get(YEAR_URL, status=404)

    await _setup(hass, config_entry)

    state = hass.states.get(NEXT_PRAYER)
    assert state.attributes["tomorrow"] is True
    assert state.attributes["time_24h"] == "05:48"


async def test_store_removed_with_entry(
    hass, config_entry, aioclient_mock, hass_storage, freezer
) -> None:
    """Removing the entry removes its saved years."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    aioclient_mock.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))
    aioclient_mock.get(YEAR_URL, json=_year_payload())
    await _setup(hass, config_entry)
    assert _store_key(config_entry) in hass_storage

    await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    assert _store_key(config_entry) not in hass_storage


async def test_zone_change_drops_saved_year(
    hass, config_entry, aioclient_mock, freezer
) -> None:
    """A new zone drops the old zone's saved year."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    for zone in ("SGR01", "SGR03"):
        aioclient_mock.get(
            MONTHLY_URL.format(zone=zone, month=10, year=2026),
            json=load_fixture_json(f"monthly_{zone}_2026_10.json"),
        )
    aioclient_mock.get(YEAR_URL, json=_year_payload())
    aioclient_mock.get(YEARLY_URL.format(zone="SGR03", year=2026), status=404)
    await _setup(hass, config_entry)
    coordinator = config_entry.runtime_data
    assert coordinator.saved_year_keys() == [("SGR01", 2026)]

    await coordinator.async_set_zone("SGR03")

    assert coordinator.saved_year_keys() == []
