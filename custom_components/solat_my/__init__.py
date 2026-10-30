"""Waktu Solat Malaysia integration using solat.my API."""
from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
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

MIMBAR_FRONTEND_URL = f"/api/{DOMAIN}/mimbar"
MIMBAR_FRONTEND_PATH = Path(__file__).parent / "frontend"
MIMBAR_FRONTEND_REGISTERED = f"{DOMAIN}_mimbar_frontend_registered"
MIMBAR_FRONTEND_LOCK = f"{DOMAIN}_mimbar_frontend_lock"
MIMBAR_CARD_URL = f"{MIMBAR_FRONTEND_URL}/solat-my-mimbar-card.js"


def _mimbar_frontend_version() -> str:
    """Hash the card modules so any file change produces a new cache-busting URL."""
    digest = hashlib.sha256()
    for path in sorted(MIMBAR_FRONTEND_PATH.iterdir()):
        if path.suffix in (".js", ".mjs"):
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


async def _async_register_mimbar_frontend(hass: HomeAssistant) -> None:
    """Serve the Mimbar card and load it on every dashboard, once per process."""
    lock = hass.data.setdefault(MIMBAR_FRONTEND_LOCK, asyncio.Lock())
    async with lock:
        if hass.data.get(MIMBAR_FRONTEND_REGISTERED):
            return

        await hass.http.async_register_static_paths(
            [StaticPathConfig(MIMBAR_FRONTEND_URL, str(MIMBAR_FRONTEND_PATH), False)]
        )
        if "frontend" in hass.config.components:
            version = await hass.async_add_executor_job(_mimbar_frontend_version)
            frontend.add_extra_js_url(hass, f"{MIMBAR_CARD_URL}?v={version}")
        hass.data[MIMBAR_FRONTEND_REGISTERED] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Waktu Solat Malaysia from a config entry."""
    await _async_register_mimbar_frontend(hass)

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
