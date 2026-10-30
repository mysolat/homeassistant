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
from homeassistant.helpers import entity_registry as er

from .const import CONF_NAME, CONF_ZONE, DEFAULT_NAME, DEFAULT_ZONE, DOMAIN
from .coordinator import SolatMyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.TEXT,
    Platform.BUTTON,
    Platform.CALENDAR,
]

SKRIN_SOLAT_FRONTEND_URL = f"/api/{DOMAIN}/skrin-solat"
SKRIN_SOLAT_FRONTEND_PATH = Path(__file__).parent / "frontend"
SKRIN_SOLAT_FRONTEND_REGISTERED = f"{DOMAIN}_skrin_solat_frontend_registered"
SKRIN_SOLAT_FRONTEND_LOCK = f"{DOMAIN}_skrin_solat_frontend_lock"
SKRIN_SOLAT_CARD_URL = f"{SKRIN_SOLAT_FRONTEND_URL}/solat-my-skrin-solat-card.js"

# One-time migration from 1.0.10 and earlier. Safe to remove once no install runs 1.0.10.
_LEGACY_UNIQUE_ID_SUFFIXES = {
    "mimbar_background": "skrin_solat_background",
    "mimbar_background_visibility": "skrin_solat_background_visibility",
    "mimbar_time_format": "skrin_solat_time_format",
    "mimbar_background_opacity": "skrin_solat_background_opacity",
    "mimbar_background_image": "skrin_solat_background_image",
}


def _migrate_legacy_unique_id(
    entry: ConfigEntry, entity_entry: er.RegistryEntry
) -> dict[str, str] | None:
    """Return the new unique ID for a legacy settings entity, else None."""
    prefix = f"{entry.entry_id}_"
    if not entity_entry.unique_id.startswith(prefix):
        return None
    new_suffix = _LEGACY_UNIQUE_ID_SUFFIXES.get(entity_entry.unique_id[len(prefix) :])
    if new_suffix is None:
        return None
    return {"new_unique_id": f"{prefix}{new_suffix}"}


def _skrin_solat_frontend_version() -> str:
    """Hash the card modules so any file change produces a new cache-busting URL."""
    digest = hashlib.sha256()
    for path in sorted(SKRIN_SOLAT_FRONTEND_PATH.iterdir()):
        if path.suffix in (".js", ".mjs"):
            digest.update(path.name.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


async def _async_register_skrin_solat_frontend(hass: HomeAssistant) -> None:
    """Serve the Skrin Solat card and load it on every dashboard, once per process."""
    lock = hass.data.setdefault(SKRIN_SOLAT_FRONTEND_LOCK, asyncio.Lock())
    async with lock:
        if hass.data.get(SKRIN_SOLAT_FRONTEND_REGISTERED):
            return

        await hass.http.async_register_static_paths(
            [StaticPathConfig(SKRIN_SOLAT_FRONTEND_URL, str(SKRIN_SOLAT_FRONTEND_PATH), False)]
        )
        if "frontend" in hass.config.components:
            version = await hass.async_add_executor_job(_skrin_solat_frontend_version)
            frontend.add_extra_js_url(hass, f"{SKRIN_SOLAT_CARD_URL}?v={version}")
        hass.data[SKRIN_SOLAT_FRONTEND_REGISTERED] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Waktu Solat Malaysia from a config entry."""
    await _async_register_skrin_solat_frontend(hass)

    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    zone = entry.data.get(CONF_ZONE, DEFAULT_ZONE)

    coordinator = SolatMyCoordinator(hass, entry, name=name, initial_zone=zone)
    await coordinator.async_config_entry_first_refresh()
    entry.async_on_unload(coordinator.async_track_midnight())
    entry.runtime_data = coordinator

    await er.async_migrate_entries(
        hass, entry.entry_id, lambda entity_entry: _migrate_legacy_unique_id(entry, entity_entry)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
