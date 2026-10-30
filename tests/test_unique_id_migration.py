"""Tests for the one-time unique ID migration from the mimbar_* suffixes."""
from __future__ import annotations

import pytest
from homeassistant.helpers import entity_registry as er

LEGACY_ENTITIES = (
    (
        "select",
        "mimbar_background",
        "skrin_solat_background",
        "waktu_solat_warna_latar_skrin_solat",
    ),
    (
        "select",
        "mimbar_background_visibility",
        "skrin_solat_background_visibility",
        "waktu_solat_paparan_latar_skrin_solat",
    ),
    (
        "select",
        "mimbar_time_format",
        "skrin_solat_time_format",
        "waktu_solat_format_masa_skrin_solat",
    ),
    (
        "number",
        "mimbar_background_opacity",
        "skrin_solat_background_opacity",
        "waktu_solat_kejelasan_latar_skrin_solat",
    ),
    (
        "text",
        "mimbar_background_image",
        "skrin_solat_background_image",
        "waktu_solat_imej_latar_skrin_solat",
    ),
)


async def _register_legacy_entities(hass, config_entry) -> dict[str, str]:
    """Register the old unique IDs as an install on 1.0.10 has them."""
    registry = er.async_get(hass)
    entity_ids = {}
    for domain, old_suffix, _new_suffix, object_id in LEGACY_ENTITIES:
        entry = registry.async_get_or_create(
            domain,
            "solat_my",
            f"{config_entry.entry_id}_{old_suffix}",
            config_entry=config_entry,
            suggested_object_id=object_id,
        )
        assert entry.entity_id == f"{domain}.{object_id}"
        entity_ids[old_suffix] = entry.entity_id
    return entity_ids


async def test_legacy_unique_ids_are_migrated_in_place(
    hass, config_entry, mock_api, freezer
) -> None:
    """Existing entities keep their entity IDs and gain the new unique IDs."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    entity_ids = await _register_legacy_entities(hass, config_entry)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    for domain, old_suffix, new_suffix, _object_id in LEGACY_ENTITIES:
        entity_id = registry.async_get_entity_id(
            domain, "solat_my", f"{config_entry.entry_id}_{new_suffix}"
        )
        assert entity_id == entity_ids[old_suffix]
        assert (
            registry.async_get_entity_id(
                domain, "solat_my", f"{config_entry.entry_id}_{old_suffix}"
            )
            is None
        )


async def test_migration_leaves_no_duplicate_entity_ids(
    hass, config_entry, mock_api, freezer
) -> None:
    """No entity ID ends in _2 and no entry keeps a mimbar unique ID."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await _register_legacy_entities(hass, config_entry)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    entries = er.async_entries_for_config_entry(
        er.async_get(hass), config_entry.entry_id
    )
    assert entries
    assert not [entry.entity_id for entry in entries if entry.entity_id.endswith("_2")]
    assert not [entry.unique_id for entry in entries if "mimbar" in entry.unique_id]


@pytest.mark.parametrize(("domain", "old_suffix", "new_suffix", "object_id"), LEGACY_ENTITIES)
async def test_new_install_uses_new_unique_ids_only(
    hass, config_entry, mock_api, freezer, domain, old_suffix, new_suffix, object_id
) -> None:
    """A fresh install registers the new unique ID and never the old one."""
    freezer.move_to("2026-10-30T10:00:00+08:00")

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    assert registry.async_get_entity_id(
        domain, "solat_my", f"{config_entry.entry_id}_{new_suffix}"
    )
    assert (
        registry.async_get_entity_id(
            domain, "solat_my", f"{config_entry.entry_id}_{old_suffix}"
        )
        is None
    )
