"""Text platform for Waktu Solat Malaysia — audio filename configuration."""
from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .sensor import _make_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities for audio file configuration."""
    async_add_entities(
        [
            AudioFileText(entry, key="azan", default="azan1.mp3, azan2.mp3"),
            AudioFileText(entry, key="azan_subuh", default="azan_subuh.mp3"),
            AudioFileText(entry, key="doa", default="doa_selepas_azan.mp3"),
        ]
    )


_NAMES = {
    "azan": "Fail Audio Azan",
    "azan_subuh": "Fail Audio Azan Subuh",
    "doa": "Fail Doa Selepas Azan",
}

_ICONS = {
    "azan": "mdi:music",
    "azan_subuh": "mdi:weather-sunset-up",
    "doa": "mdi:hands-pray",
}


class AudioFileText(RestoreEntity, TextEntity):
    """Text entity for configuring comma-separated audio filenames.

    Files go in /config/www/azan/ and are referenced by filename only
    (e.g. "azan1.mp3, azan2.mp3").
    """

    _attr_has_entity_name = True
    _attr_mode = TextMode.TEXT
    _attr_native_min = 1
    _attr_native_max = 255

    def __init__(self, entry: ConfigEntry, key: str, default: str) -> None:
        """Initialize the audio file text entity."""
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_audio_{key}"
        self._attr_name = _NAMES[key]
        self._attr_icon = _ICONS[key]
        self._attr_native_value = default
        self._attr_device_info = _make_device_info(entry)

    async def async_added_to_hass(self) -> None:
        """Restore last configured value on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state not in ("unknown", "unavailable", ""):
                self._attr_native_value = last_state.state

    async def async_set_value(self, value: str) -> None:
        """Update the audio file list."""
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def filenames(self) -> list[str]:
        """Return the list of configured filenames (stripped)."""
        return [f.strip() for f in (self._attr_native_value or "").split(",") if f.strip()]
