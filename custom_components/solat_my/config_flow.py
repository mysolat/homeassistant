"""Config flow for Waktu Solat Malaysia integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    API_BASE_URL,
    CONF_NAME,
    CONF_ZONE,
    DEFAULT_NAME,
    DEFAULT_ZONE,
    DOMAIN,
    ZONES,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_zone(hass: HomeAssistant, zone: str) -> dict[str, str] | None:
    """Validate zone by calling the API. Returns None on success, error dict on failure."""
    url = f"{API_BASE_URL}/daily/{zone}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    return {"base": "cannot_connect"}
                data = await response.json()
                if data.get("status") != "OK!":
                    return {"base": "invalid_zone"}
    except aiohttp.ClientError:
        return {"base": "cannot_connect"}
    except Exception:  # pylint: disable=broad-except
        return {"base": "unknown"}
    return None


class SolatMyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Waktu Solat Malaysia."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            zone = user_input[CONF_ZONE]

            # Use lowercase name as unique_id to prevent duplicate device names
            await self.async_set_unique_id(name.lower())
            self._abort_if_unique_id_configured()

            error = await _validate_zone(self.hass, zone)
            if error:
                errors.update(error)
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_ZONE: zone,
                    },
                )

        zone_options = [
            SelectOptionDict(value=code, label=f"{code} — {desc}")
            for code, desc in sorted(ZONES.items())
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_ZONE, default=DEFAULT_ZONE): SelectSelector(
                    SelectSelectorConfig(
                        options=zone_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SolatMyOptionsFlow:
        """Get the options flow."""
        return SolatMyOptionsFlow(config_entry)


class SolatMyOptionsFlow(config_entries.OptionsFlow):
    """Handle options — zone is changed live via the Zon select entity."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show a note directing users to the Zon entity."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
            description_placeholders={
                "note": "Tukar zon waktu solat menggunakan entiti 'Zon' pada halaman peranti."
            },
        )
