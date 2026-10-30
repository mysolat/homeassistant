"""Tests for the Skrin Solat entity names and their stable unique IDs."""
from __future__ import annotations

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

NAMES = (
    ("select", "skrin_solat_background", "Skrin Warna Latar", "warna_latar"),
    ("select", "skrin_solat_background_visibility", "Skrin Paparan Latar", "paparan_latar"),
    ("select", "skrin_solat_time_format", "Skrin Format Masa", "format_masa"),
    ("number", "skrin_solat_background_opacity", "Skrin Kejelasan Latar", "kejelasan_latar"),
    ("text", "skrin_solat_background_image", "Skrin Imej Latar", "imej_latar"),
)


async def _setup(hass, config_entry) -> None:
    """Set up the config entry and wait for all entities."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.parametrize(("domain", "suffix", "name", "id_stem"), NAMES)
async def test_entity_has_skrin_solat_name_and_unique_id(
    hass, config_entry, mock_api, freezer, domain, suffix, name, id_stem
) -> None:
    """A new install gets Skrin Solat names and unique IDs."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)

    entity_id = er.async_get(hass).async_get_entity_id(
        domain, "solat_my", f"{config_entry.entry_id}_{suffix}"
    )

    assert entity_id == f"{domain}.waktu_solat_skrin_{id_stem}"
    state = hass.states.get(entity_id)
    assert state.attributes["friendly_name"] == f"Waktu Solat {name}"


async def test_image_error_names_skrin_solat(
    hass, config_entry, mock_api, freezer
) -> None:
    """A remote image URL is refused with an error that names Skrin Solat."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _setup(hass, config_entry)
    entity_id = er.async_get(hass).async_get_entity_id(
        "text", "solat_my", f"{config_entry.entry_id}_skrin_solat_background_image"
    )

    with pytest.raises((ValueError, HomeAssistantError), match="Skrin Imej Latar"):
        await hass.services.async_call(
            "text",
            "set_value",
            {"entity_id": entity_id, "value": "https://x/a.png"},
            blocking=True,
        )
