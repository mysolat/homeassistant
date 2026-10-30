"""Tests for the Kalendar Solat calendar entity."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import MONTHLY_URL, load_fixture_json

NOW = "2026-10-30T10:00:00+08:00"
NOVEMBER_URL = MONTHLY_URL.format(zone="SGR01", month=11, year=2026)
FIVE_PRAYERS = ["Subuh", "Zohor", "Asar", "Maghrib", "Isyak"]


def _register_november(mock_api, **kwargs) -> None:
    """Serve November for SGR01: the saved reply, or the reply given in kwargs."""
    if not kwargs:
        kwargs = {"json": load_fixture_json("monthly_SGR01_2026_11.json")}
    mock_api.get(NOVEMBER_URL, **kwargs)


async def _setup(hass, config_entry, freezer, now: str = NOW) -> str:
    """Set up the entry at the given time and return the calendar's entity ID."""
    freezer.move_to(now)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = er.async_get(hass).async_get_entity_id(
        "calendar", "solat_my", f"{config_entry.entry_id}_calendar"
    )
    assert entity_id is not None, "no calendar entity with unique ID suffix calendar"
    return entity_id


async def _get_events(hass, entity_id: str, start: str, end: str) -> list[dict]:
    """Call calendar.get_events and return the events of the entity."""
    response = await hass.services.async_call(
        "calendar",
        "get_events",
        {"entity_id": entity_id, "start_date_time": start, "end_date_time": end},
        blocking=True,
        return_response=True,
    )
    return response[entity_id]["events"]


async def test_events_for_a_day(hass, config_entry, mock_api, freezer) -> None:
    """One day has the five prayers, each starting when JAKIM says and lasting 10 minutes."""
    entity_id = await _setup(hass, config_entry, freezer)

    events = await _get_events(
        hass, entity_id, "2026-10-30T00:00:00+08:00", "2026-10-31T00:00:00+08:00"
    )

    assert [event["summary"] for event in events] == FIVE_PRAYERS
    assert [event["start"] for event in events] == [
        "2026-10-30T05:48:00+08:00",
        "2026-10-30T13:00:00+08:00",
        "2026-10-30T16:19:00+08:00",
        "2026-10-30T18:59:00+08:00",
        "2026-10-30T20:09:00+08:00",
    ]
    assert events[0]["end"] == "2026-10-30T05:58:00+08:00"
    # The length is a display convention. It never comes from the next prayer.
    for event in events:
        length = datetime.fromisoformat(event["end"]) - datetime.fromisoformat(
            event["start"]
        )
        assert length == timedelta(minutes=10)
    assert events[0]["description"] == "Zon SGR01"


async def test_events_span_months(hass, config_entry, mock_api, freezer) -> None:
    """A range over two months reads the second month from the API, once."""
    _register_november(mock_api)
    entity_id = await _setup(hass, config_entry, freezer)

    events = await _get_events(
        hass, entity_id, "2026-10-31T00:00:00+08:00", "2026-11-02T00:00:00+08:00"
    )

    assert len(events) == 10
    assert [event["summary"] for event in events] == FIVE_PRAYERS * 2
    assert events[5]["start"] == "2026-11-01T05:48:00+08:00"
    assert events[-1]["start"] == "2026-11-01T20:09:00+08:00"

    calls = mock_api.call_count
    again = await _get_events(
        hass, entity_id, "2026-10-31T00:00:00+08:00", "2026-11-02T00:00:00+08:00"
    )
    assert again == events
    assert mock_api.call_count == calls


async def test_current_event_state(hass, config_entry, mock_api, freezer) -> None:
    """The calendar is on only while an event is in progress, and names it."""
    entity_id = await _setup(hass, config_entry, freezer)

    state = hass.states.get(entity_id)
    assert state.state == "off"
    assert state.attributes["message"] == "Zohor"

    freezer.move_to("2026-10-30T13:05:00+08:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.state == "on"
    assert state.attributes["message"] == "Zohor"

    freezer.move_to("2026-10-30T13:11:00+08:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.state == "off"
    assert state.attributes["message"] == "Asar"


async def test_zone_change_clears_calendar_cache(
    hass, config_entry, mock_api, freezer
) -> None:
    """After a zone change the calendar shows the new zone's times."""
    _register_november(mock_api)
    entity_id = await _setup(hass, config_entry, freezer)
    coordinator = config_entry.runtime_data
    day = ("2026-10-30T00:00:00+08:00", "2026-10-31T00:00:00+08:00")

    events = await _get_events(hass, entity_id, *day)
    assert events[3]["start"] == "2026-10-30T18:59:00+08:00"

    # Read November so the calendar cache holds a month for SGR01.
    await _get_events(
        hass, entity_id, "2026-11-01T00:00:00+08:00", "2026-11-02T00:00:00+08:00"
    )
    assert coordinator._calendar_months

    await hass.services.async_call(
        "select",
        "select_option",
        {
            "entity_id": er.async_get(hass).async_get_entity_id(
                "select", "solat_my", f"{config_entry.entry_id}_zon"
            ),
            "option": "SGR03",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    assert not coordinator._calendar_months
    events = await _get_events(hass, entity_id, *day)
    assert [event["summary"] for event in events] == FIVE_PRAYERS
    assert events[3]["start"] == "2026-10-30T19:00:00+08:00"
    assert events[0]["description"] == "Zon SGR03"


async def test_month_fetch_failure_returns_known_days(
    hass, config_entry, mock_api, freezer
) -> None:
    """If the next month cannot be fetched, the days already known still show."""
    _register_november(mock_api, status=500)
    entity_id = await _setup(hass, config_entry, freezer)

    events = await _get_events(
        hass, entity_id, "2026-10-31T00:00:00+08:00", "2026-11-02T00:00:00+08:00"
    )

    assert [event["summary"] for event in events] == FIVE_PRAYERS
    assert all(event["start"].startswith("2026-10-31T") for event in events)
