"""Waktu Solat Malaysia integration using solat.my API."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_NAME, CONF_ZONE, DEFAULT_NAME, DEFAULT_ZONE, DOMAIN
from .coordinator import SolatMyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.TEXT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Waktu Solat Malaysia from a config entry."""
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    zone = entry.data.get(CONF_ZONE, DEFAULT_ZONE)

    coordinator = SolatMyCoordinator(hass, name=name, initial_zone=zone)
    await coordinator.async_config_entry_first_refresh()
    coordinator.async_setup()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SolatMyCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.async_shutdown()
    return unload_ok
