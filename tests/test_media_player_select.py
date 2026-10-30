"""Tests for the azan media player select: when its option list refreshes."""
from __future__ import annotations

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_report_event
from pytest_homeassistant_custom_component.common import async_capture_events

SELECT = "select.waktu_solat_pemain_media_azan"
NOW = "2026-10-30T10:00:00+08:00"


async def _setup(hass, config_entry, freezer) -> None:
    """Set up the entry with one media player, media_player.ruang_tamu, present."""
    freezer.move_to(NOW)
    hass.states.async_set("media_player.ruang_tamu", "idle")
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


def _options(hass) -> list[str]:
    """Return the select's current options."""
    return hass.states.get(SELECT).attributes["options"]


async def test_new_player_appears_in_options(
    hass, config_entry, mock_api, freezer
) -> None:
    """A media player added after setup shows up in the options."""
    await _setup(hass, config_entry, freezer)
    assert "media_player.dapur" not in _options(hass)

    hass.states.async_set("media_player.dapur", "idle")
    await hass.async_block_till_done()

    assert "media_player.dapur" in _options(hass)


async def test_removed_player_leaves_options(
    hass, config_entry, mock_api, freezer
) -> None:
    """A media player removed after setup leaves the options."""
    await _setup(hass, config_entry, freezer)
    hass.states.async_set("media_player.dapur", "idle")
    await hass.async_block_till_done()
    assert "media_player.dapur" in _options(hass)

    hass.states.async_remove("media_player.dapur")
    await hass.async_block_till_done()

    assert hass.states.get(SELECT).state == "media_player.ruang_tamu"
    assert "media_player.dapur" not in _options(hass)


async def test_player_state_change_does_not_rewrite_select(
    hass, config_entry, mock_api, freezer
) -> None:
    """A media player changing state does not write the select's state."""
    await _setup(hass, config_entry, freezer)

    changed = async_capture_events(hass, EVENT_STATE_CHANGED)
    reported = []

    @callback
    def _on_report(event) -> None:
        reported.append(event)

    async_track_state_report_event(hass, SELECT, _on_report)

    for state in ("playing", "idle", "playing"):
        hass.states.async_set("media_player.ruang_tamu", state)
        await hass.async_block_till_done()

    assert [e for e in changed if e.data["entity_id"] == SELECT] == []
    assert reported == []


async def test_selection_survives_player_removal(
    hass, config_entry, mock_api, freezer
) -> None:
    """Removing the selected player keeps it as the current option."""
    await _setup(hass, config_entry, freezer)
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": SELECT, "option": "media_player.ruang_tamu"},
        blocking=True,
    )

    hass.states.async_remove("media_player.ruang_tamu")
    await hass.async_block_till_done()

    assert hass.states.get(SELECT).state == "media_player.ruang_tamu"
