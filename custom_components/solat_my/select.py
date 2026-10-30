"""Select platform for Waktu Solat Malaysia — zone and media player selectors."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_added_domain,
    async_track_state_removed_domain,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_ZONE,
    DEFAULT_SKRIN_SOLAT_BACKGROUND,
    DEFAULT_SKRIN_SOLAT_BACKGROUND_VISIBILITY,
    DEFAULT_SKRIN_SOLAT_TIME_FORMAT,
    SKRIN_SOLAT_BACKGROUND_OPTIONS,
    SKRIN_SOLAT_BACKGROUND_VISIBILITY_OPTIONS,
    SKRIN_SOLAT_TIME_FORMAT_OPTIONS,
    ZONES,
)
from .coordinator import SolatMyCoordinator
from .sensor import _make_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator: SolatMyCoordinator = entry.runtime_data
    async_add_entities(
        [
            ZoneSelect(coordinator, entry),
            MediaPlayerSelect(hass, entry),
            AnnouncementModeSelect(entry),
            SkrinSolatBackgroundSelect(entry),
            SkrinSolatBackgroundVisibilitySelect(entry),
            SkrinSolatTimeFormatSelect(entry),
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
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_zon"
        self._attr_current_option = coordinator.zone
        self._attr_device_info = _make_device_info(entry)

    @property
    def extra_state_attributes(self) -> dict:
        """Show the human-readable description of the current zone."""
        return {
            "description": ZONES.get(self._attr_current_option or "", ""),
        }

    async def async_added_to_hass(self) -> None:
        """Move a zone kept only in restore state (before 1.0.6) into the config entry."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if (
            last_state is not None
            and last_state.state in ZONES
            and last_state.state != self._coordinator.zone
        ):
            await self._async_apply_zone(last_state.state)

    async def async_select_option(self, option: str) -> None:
        """Handle zone change — persist it, then refresh all sensors."""
        await self._async_apply_zone(option)

    async def _async_apply_zone(self, zone: str) -> None:
        """Save the zone in the config entry and refresh the coordinator."""
        self._attr_current_option = zone
        if self._entry.data.get(CONF_ZONE) != zone:
            self.hass.config_entries.async_update_entry(
                self._entry, data={**self._entry.data, CONF_ZONE: zone}
            )
        self.async_write_ha_state()
        await self._coordinator.async_set_zone(zone)


class MediaPlayerSelect(RestoreEntity, SelectEntity):
    """Select entity for choosing which media player plays the azan."""

    _attr_has_entity_name = True
    _attr_name = "Pemain Media Azan"
    _attr_icon = "mdi:speaker"
    _OPTION_MEDIA_PLAYER = "azan_media_player"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the media player select entity."""
        self._hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_pemain_media_azan"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = entry.options.get(self._OPTION_MEDIA_PLAYER)
        self._attr_options = self._get_media_players()

    def _get_media_players(self) -> list[str]:
        """Return all known media player entity IDs regardless of availability."""
        players = [
            state.entity_id
            for state in self._hass.states.async_all("media_player")
        ]
        # Keep persisted/current selection in options even if entity is not yet loaded.
        # This prevents startup ordering from overwriting user's preferred player.
        if self._attr_current_option and self._attr_current_option not in players:
            players.append(self._attr_current_option)
        return sorted(players) if players else ["media_player.none"]

    def _persist_selected_player(self) -> None:
        """Persist selected media player in config entry options."""
        if not self._attr_current_option:
            return
        if self._entry.options.get(self._OPTION_MEDIA_PLAYER) == self._attr_current_option:
            return

        new_options = dict(self._entry.options)
        new_options[self._OPTION_MEDIA_PLAYER] = self._attr_current_option
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)

    async def async_added_to_hass(self) -> None:
        """Restore last selection and track availability changes."""
        await super().async_added_to_hass()

        last_state_value = None
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state not in ("unknown", "unavailable", ""):
                last_state_value = last_state.state

        if not self._attr_current_option and last_state_value:
            self._attr_current_option = last_state_value

        self._attr_options = self._get_media_players()
        if not self._attr_current_option:
            self._attr_current_option = self._attr_options[0] if self._attr_options else None

        self._persist_selected_player()

        @callback
        def _on_media_players_changed(event) -> None:
            """Refresh the option list when a media player is added or removed."""
            self._attr_options = self._get_media_players()
            # Do not auto-switch current option when entities appear/disappear.
            # User selection is persisted and should remain sticky.
            self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_added_domain(
                self.hass, "media_player", _on_media_players_changed
            )
        )
        self.async_on_remove(
            async_track_state_removed_domain(
                self.hass, "media_player", _on_media_players_changed
            )
        )
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Handle media player selection."""
        self._attr_current_option = option
        self._persist_selected_player()
        self.async_write_ha_state()


class AnnouncementModeSelect(RestoreEntity, SelectEntity):
    """Select entity for announcement mode played before azan.

    Options:
      ``tts``   — use Google Translate TTS (original behaviour, default)
      ``audio`` — play a pre-recorded MP3 from media/tts/ instead
    """

    _attr_has_entity_name = True
    _attr_name = "Mod Pengumuman Azan"
    _attr_icon = "mdi:bullhorn"
    _attr_options = ["tts", "audio"]

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the announcement mode select entity."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_mod_pengumuman"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = "tts"

    async def async_added_to_hass(self) -> None:
        """Restore last selection on startup."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in self._attr_options:
                self._attr_current_option = last_state.state
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Handle mode selection."""
        self._attr_current_option = option
        self.async_write_ha_state()


class SkrinSolatBackgroundSelect(RestoreEntity, SelectEntity):
    """Select the shared Skrin Solat display colour for this device."""

    _attr_has_entity_name = True
    _attr_name = "Warna Latar Skrin Solat"
    _attr_icon = "mdi:palette"
    _attr_options = SKRIN_SOLAT_BACKGROUND_OPTIONS

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the Skrin Solat background colour selector."""
        self._attr_unique_id = f"{entry.entry_id}_skrin_solat_background"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = DEFAULT_SKRIN_SOLAT_BACKGROUND

    async def async_added_to_hass(self) -> None:
        """Restore the last selected background colour."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in self._attr_options:
                self._attr_current_option = last_state.state
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Update the shared Skrin Solat background colour."""
        self._attr_current_option = option
        self.async_write_ha_state()


class SkrinSolatBackgroundVisibilitySelect(RestoreEntity, SelectEntity):
    """Toggle the shared Skrin Solat image background for this device."""

    _attr_has_entity_name = True
    _attr_name = "Paparan Latar Skrin Solat"
    _attr_icon = "mdi:image-outline"
    _attr_options = SKRIN_SOLAT_BACKGROUND_VISIBILITY_OPTIONS

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the Skrin Solat background visibility selector."""
        self._attr_unique_id = f"{entry.entry_id}_skrin_solat_background_visibility"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = DEFAULT_SKRIN_SOLAT_BACKGROUND_VISIBILITY

    async def async_added_to_hass(self) -> None:
        """Restore the last selected background visibility."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in self._attr_options:
                self._attr_current_option = last_state.state
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Update the shared Skrin Solat background visibility."""
        self._attr_current_option = option
        self.async_write_ha_state()


class SkrinSolatTimeFormatSelect(RestoreEntity, SelectEntity):
    """Select the shared Skrin Solat clock format for this device."""

    _attr_has_entity_name = True
    _attr_name = "Format Masa Skrin Solat"
    _attr_icon = "mdi:clock-outline"
    _attr_options = SKRIN_SOLAT_TIME_FORMAT_OPTIONS

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the Skrin Solat time-format selector."""
        self._attr_unique_id = f"{entry.entry_id}_skrin_solat_time_format"
        self._attr_device_info = _make_device_info(entry)
        self._attr_current_option = DEFAULT_SKRIN_SOLAT_TIME_FORMAT

    async def async_added_to_hass(self) -> None:
        """Restore the last selected time format."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in self._attr_options:
                self._attr_current_option = last_state.state
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Update the shared Skrin Solat time format."""
        self._attr_current_option = option
        self.async_write_ha_state()
