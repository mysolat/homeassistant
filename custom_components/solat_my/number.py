"""Number platform for Waktu Solat Malaysia — Azan volume control."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .sensor import _make_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    async_add_entities([AzanVolumeNumber(entry)])


class AzanVolumeNumber(RestoreEntity, NumberEntity):
    """Number entity for controlling azan playback volume."""

    _attr_has_entity_name = True
    _attr_name = "Kelantangan Azan"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.05
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = 0.6

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the volume number entity."""
        self._attr_unique_id = f"{entry.entry_id}_kelantangan_azan"
        self._attr_device_info = _make_device_info(entry)

    async def async_added_to_hass(self) -> None:
        """Restore last known volume on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = float(last_state.state)
            except (ValueError, TypeError):
                pass

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume value."""
        self._attr_native_value = round(value, 2)
        self.async_write_ha_state()
