"""Select platform for Waktu Solat Malaysia — zone and media player selectors."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_ZONE, DOMAIN, ZONES
from .coordinator import SolatMyCoordinator
from .sensor import _make_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator: SolatMyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ZoneSelect(coordinator, entry),
            MediaPlayerSelect(hass, entry),
        ]
    )


class ZoneSelect(RestoreEntity, SelectEntity):
    """Select entity for switching the active prayer time zone.

    Changing this entity immediately triggers a coordinator refresh
    so all prayer time sensors update to the new zone.
    """

    _attr_has_entity_name = True
    _attr_name = "Zon"
    _attr_icon = "mdi:map-marker"
    # All 59 JAKIM zone codes as selectable options
    _attr_options = sorted(ZONES.keys())

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the zone select entity."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_zon"
        self._attr_current_option = entry.data.get(CONF_ZONE)
        self._attr_device_info = _make_device_info(entry)

    @property
    def extra_state_attributes(self) -> dict:
        """Show the human-readable description of the current zone."""
        return {
            "description": ZONES.get(self._attr_current_option or "", ""),
        }

    async def async_added_to_hass(self) -> None:
        """Restore last zone on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in ZONES:
                self._attr_current_option = last_state.state
                # Sync coordinator in case it differs from restored state
                if self._coordinator.zone != last_state.state:
                    self._coordinator.zone = last_state.state

    async def async_select_option(self, option: str) -> None:
        """Handle zone change — update coordinator and refresh all sensors."""
        self._attr_current_option = option
        self.async_write_ha_state()
        await self._coordinator.async_set_zone(option)


class MediaPlayerSelect(RestoreEntity, SelectEntity):
    """Select entity for choosing which media player plays the azan."""

    _attr_has_entity_name = True
    _attr_name = "Pemain Media Azan"
    _attr_icon = "mdi:speaker"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the media player select entity."""
        self._hass = hass
        self._attr_unique_id = f"{entry.entry_id}_pemain_media_azan"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = None
        self._attr_options = self._get_media_players()

    def _get_media_players(self) -> list[str]:
        """Return all known media player entity IDs regardless of availability."""
        players = [
            state.entity_id
            for state in self._hass.states.async_all("media_player")
        ]
        return players or ["media_player.none"]

    async def async_added_to_hass(self) -> None:
        """Restore last selection and track availability changes."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is not None:
            self._attr_current_option = last_state.state

        @callback
        def _on_media_player_change(event) -> None:
            self._attr_options = self._get_media_players()
            # Preserve the current selection — a player going offline is temporary.
            # Only fall back if the entity_id is completely gone from HA state.
            if self._attr_current_option not in self._attr_options:
                self._attr_current_option = self._attr_options[0] if self._attr_options else None
            self.async_write_ha_state()

        # Track ALL media_player domain state changes (covers new players added later)
        self.async_on_remove(
            self.hass.bus.async_listen(
                "state_changed",
                lambda event: (
                    _on_media_player_change(event)
                    if event.data.get("entity_id", "").startswith("media_player.")
                    else None
                ),
            )
        )

        if self._attr_current_option not in self._attr_options:
            self._attr_current_option = self._attr_options[0] if self._attr_options else None

    async def async_select_option(self, option: str) -> None:
        """Handle media player selection."""
        self._attr_current_option = option
        self.async_write_ha_state()
