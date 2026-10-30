"""Button platform for Waktu Solat Malaysia — test and stop the azan."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensor import _make_device_info

AZAN_MEDIA_SOURCE = "media-source://media_source/local/azan/{file}"
AZAN_CONTENT_TYPE = "audio/mpeg"
NO_PLAYER_STATES = (STATE_UNKNOWN, STATE_UNAVAILABLE, "media_player.none")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the azan test and stop buttons."""
    async_add_entities([TestAzanButton(entry), StopAzanButton(entry)])


def _setting_state(
    hass: HomeAssistant, entry: ConfigEntry, domain: str, suffix: str
) -> State | None:
    """Return the state of a settings entity, found by unique ID.

    The unique ID is stable. The entity ID is not, because users can rename it.
    """
    entity_id = er.async_get(hass).async_get_entity_id(
        domain, DOMAIN, f"{entry.entry_id}_{suffix}"
    )
    return hass.states.get(entity_id) if entity_id else None


def _selected_player(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Return the entity ID of the chosen azan media player, or raise."""
    state = _setting_state(hass, entry, "select", "pemain_media_azan")
    player = state.state if state else None
    if (
        player is None
        or player in NO_PLAYER_STATES
        or not player.startswith("media_player.")
    ):
        raise HomeAssistantError(
            "Pilih pemain media dalam tetapan Pemain Media Azan dahulu."
        )
    return player


class TestAzanButton(ButtonEntity):
    """Play the first azan file now, with the configured player and volume."""

    _attr_has_entity_name = True
    _attr_name = "Uji Main Azan"
    _attr_icon = "mdi:play-circle-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the test azan button."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_uji_azan"
        self._attr_device_info = _make_device_info(entry)

    async def async_press(self) -> None:
        """Set the volume when the player supports it, then play the azan."""
        player = _selected_player(self.hass, self._entry)

        files_state = _setting_state(self.hass, self._entry, "text", "audio_azan")
        files = [
            name.strip()
            for name in (files_state.state if files_state else "").split(",")
            if name.strip()
        ]
        if not files:
            raise HomeAssistantError("Tetapkan nama fail dalam Fail Audio Azan dahulu.")

        player_state = self.hass.states.get(player)
        features = (
            int(player_state.attributes.get("supported_features") or 0)
            if player_state
            else 0
        )
        volume_state = _setting_state(
            self.hass, self._entry, "number", "kelantangan_azan"
        )
        volume = None
        if volume_state is not None:
            try:
                volume = float(volume_state.state)
            except ValueError:
                volume = None

        if features & MediaPlayerEntityFeature.VOLUME_SET and volume is not None:
            await self.hass.services.async_call(
                "media_player",
                "volume_set",
                {"entity_id": player, "volume_level": volume},
                blocking=True,
            )
        await self.hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": player,
                "media_content_id": AZAN_MEDIA_SOURCE.format(file=files[0]),
                "media_content_type": AZAN_CONTENT_TYPE,
            },
            blocking=True,
        )


class StopAzanButton(ButtonEntity):
    """Stop the azan media player."""

    _attr_has_entity_name = True
    _attr_name = "Uji Henti Azan"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the stop azan button."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_henti_azan"
        self._attr_device_info = _make_device_info(entry)

    async def async_press(self) -> None:
        """Stop the chosen azan media player."""
        await self.hass.services.async_call(
            "media_player",
            "media_stop",
            {"entity_id": _selected_player(self.hass, self._entry)},
            blocking=True,
        )
