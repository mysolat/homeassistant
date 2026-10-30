"""Tests for the Uji Azan and Henti Azan buttons."""
from __future__ import annotations

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import async_mock_service

NOW = "2026-10-30T10:00:00+08:00"
PLAYER = "media_player.ruang_tamu"
VOLUME_SET_FEATURE = 4


def _entity_id(hass, config_entry, domain: str, suffix: str) -> str:
    """Return the entity ID of an entity of this integration, by unique ID."""
    entity_id = er.async_get(hass).async_get_entity_id(
        domain, "solat_my", f"{config_entry.entry_id}_{suffix}"
    )
    assert entity_id is not None, f"no {domain} entity with unique ID suffix {suffix}"
    return entity_id


async def _setup(hass, config_entry, freezer, features: int = VOLUME_SET_FEATURE):
    """Set up the entry with one media player selected, and mock its actions."""
    freezer.move_to(NOW)
    hass.states.async_set(PLAYER, "idle", {"supported_features": features})
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        "select",
        "select_option",
        {
            "entity_id": _entity_id(hass, config_entry, "select", "pemain_media_azan"),
            "option": PLAYER,
        },
        blocking=True,
    )
    return (
        async_mock_service(hass, "media_player", "play_media"),
        async_mock_service(hass, "media_player", "volume_set"),
        async_mock_service(hass, "media_player", "media_stop"),
    )


async def _press(hass, config_entry, suffix: str) -> None:
    """Press one of the integration's buttons."""
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": _entity_id(hass, config_entry, "button", suffix)},
        blocking=True,
    )


async def test_uji_azan_plays_first_file_at_volume(
    hass, config_entry, mock_api, freezer
) -> None:
    """Uji Azan sets the volume, then plays the first azan file."""
    play_media, volume_set, _ = await _setup(hass, config_entry, freezer)
    await hass.services.async_call(
        "text",
        "set_value",
        {
            "entity_id": _entity_id(hass, config_entry, "text", "audio_azan"),
            "value": "azan1.mp3, azan2.mp3",
        },
        blocking=True,
    )
    await hass.services.async_call(
        "number",
        "set_value",
        {
            "entity_id": _entity_id(hass, config_entry, "number", "kelantangan_azan"),
            "value": 0.4,
        },
        blocking=True,
    )

    await _press(hass, config_entry, "uji_azan")

    assert len(volume_set) == 1
    assert volume_set[0].data["entity_id"] == PLAYER
    assert volume_set[0].data["volume_level"] == 0.4
    assert len(play_media) == 1
    assert play_media[0].data["entity_id"] == PLAYER
    assert (
        play_media[0].data["media_content_id"]
        == "media-source://media_source/local/azan/azan1.mp3"
    )
    assert play_media[0].data["media_content_type"] == "audio/mpeg"


async def test_uji_azan_skips_volume_when_unsupported(
    hass, config_entry, mock_api, freezer
) -> None:
    """A player without volume control still plays, and gets no volume_set."""
    play_media, volume_set, _ = await _setup(hass, config_entry, freezer, features=0)

    await _press(hass, config_entry, "uji_azan")

    assert volume_set == []
    assert len(play_media) == 1


async def test_uji_azan_without_player_raises(
    hass, config_entry, mock_api, freezer
) -> None:
    """With no player chosen, Uji Azan raises an error that names the setting."""
    play_media, volume_set, _ = await _setup(hass, config_entry, freezer)
    hass.states.async_set(
        _entity_id(hass, config_entry, "select", "pemain_media_azan"),
        "media_player.none",
    )

    with pytest.raises(HomeAssistantError, match="Pemain Media Azan"):
        await _press(hass, config_entry, "uji_azan")

    assert play_media == []
    assert volume_set == []


async def test_henti_azan_stops_player(hass, config_entry, mock_api, freezer) -> None:
    """Henti Azan stops the chosen player."""
    _, _, media_stop = await _setup(hass, config_entry, freezer)

    await _press(hass, config_entry, "henti_azan")

    assert len(media_stop) == 1
    assert media_stop[0].data["entity_id"] == PLAYER


async def test_buttons_have_stable_unique_ids(
    hass, config_entry, mock_api, freezer
) -> None:
    """Both buttons exist with the unique IDs the plan fixes."""
    await _setup(hass, config_entry, freezer)
    registry = er.async_get(hass)

    for suffix, name, object_id in (
        ("uji_azan", "Uji Main Azan", "uji_main_azan"),
        ("henti_azan", "Uji Henti Azan", "uji_henti_azan"),
    ):
        entity_id = registry.async_get_entity_id(
            "button", "solat_my", f"{config_entry.entry_id}_{suffix}"
        )
        assert entity_id == f"button.waktu_solat_{object_id}"
        assert hass.states.get(entity_id).attributes["friendly_name"] == (
            f"Waktu Solat {name}"
        )
