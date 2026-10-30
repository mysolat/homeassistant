"""Tests for the Waktu Solat Malaysia config flow."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, UnknownHandler
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.solat_my.const import DOMAIN

ZONE_URL = "https://solat.my/api/daily/SGR01"
DETECT_URL = "https://solat.my/api/detect"
USER_INPUT = {"name": "Rumah", "zone": "SGR01"}
KUALA_LUMPUR = {
    "zone": "WLY01",
    "name": "Kuala Lumpur",
    "state": "Kuala Lumpur",
    "distanceKm": 0.0,
}


async def _start_flow(hass: HomeAssistant) -> str:
    """Start the user flow and return its flow id."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return result["flow_id"]


def _default_zone(result) -> str:
    """Return the default value of the zone field in a form result."""
    for key in result["data_schema"].schema:
        if key == "zone":
            return key.default()
    raise AssertionError("zone field missing")


async def test_user_flow_creates_entry(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A valid zone creates an entry with the name and zone."""
    aioclient_mock.get(ZONE_URL, json={"status": "OK!"})
    aioclient_mock.get(
        DETECT_URL, status=422, json={"error": "Location is outside Malaysia"}
    )

    flow_id = await _start_flow(hass)
    with patch("custom_components.solat_my.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(flow_id, USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Rumah"
    assert result["data"] == {"name": "Rumah", "zone": "SGR01"}


async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A non-200 API response shows the cannot_connect error."""
    aioclient_mock.get(ZONE_URL, status=500)
    aioclient_mock.get(
        DETECT_URL, status=422, json={"error": "Location is outside Malaysia"}
    )

    flow_id = await _start_flow(hass)
    with patch("custom_components.solat_my.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(flow_id, USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_zone(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """An API status other than OK! shows the invalid_zone error."""
    aioclient_mock.get(ZONE_URL, json={"status": "NOT OK"})
    aioclient_mock.get(
        DETECT_URL, status=422, json={"error": "Location is outside Malaysia"}
    )

    flow_id = await _start_flow(hass)
    with patch("custom_components.solat_my.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(flow_id, USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_zone"}


async def test_no_options_flow(hass: HomeAssistant) -> None:
    """The integration has no options flow, so Configure cannot open one."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={"name": "Waktu Solat", "zone": "SGR01"}
    )
    entry.add_to_hass(hass)

    with pytest.raises(UnknownHandler):
        await hass.config_entries.options.async_init(entry.entry_id)


def _set_kuala_lumpur(hass: HomeAssistant) -> None:
    """Move Home Assistant's home location to Kuala Lumpur."""
    hass.config.latitude = 3.139
    hass.config.longitude = 101.686


async def test_zone_defaults_to_detected_zone(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """The form pre-selects the zone that solat.my detects for the home location."""
    _set_kuala_lumpur(hass)
    aioclient_mock.get(DETECT_URL, json=KUALA_LUMPUR)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert _default_zone(result) == "WLY01"
    assert aioclient_mock.call_count == 1
    url = aioclient_mock.mock_calls[0][1]
    assert url.query["latitude"] == "3.14"
    assert url.query["longitude"] == "101.69"


async def test_zone_defaults_to_sgr01_outside_malaysia(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A 422 from solat.my keeps the SGR01 default."""
    aioclient_mock.get(
        DETECT_URL, status=422, json={"error": "Location is outside Malaysia"}
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert _default_zone(result) == "SGR01"


async def test_zone_defaults_to_sgr01_when_detect_fails(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A timeout on the detect request keeps the SGR01 default."""
    _set_kuala_lumpur(hass)
    aioclient_mock.get(DETECT_URL, exc=TimeoutError())

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert _default_zone(result) == "SGR01"


async def test_unknown_detected_zone_is_ignored(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A zone code that is not in ZONES keeps the SGR01 default."""
    _set_kuala_lumpur(hass)
    aioclient_mock.get(DETECT_URL, json={"zone": "XXX99"})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert _default_zone(result) == "SGR01"


async def test_detect_runs_once_per_flow(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """An error re-render reuses the detected zone and sends no second request."""
    _set_kuala_lumpur(hass)
    aioclient_mock.get(DETECT_URL, json=KUALA_LUMPUR)
    aioclient_mock.get("https://solat.my/api/daily/WLY01", status=500)

    flow_id = await _start_flow(hass)
    with patch("custom_components.solat_my.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            flow_id, {"name": "Rumah", "zone": "WLY01"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert _default_zone(result) == "WLY01"
    detect_calls = [
        call
        for call in aioclient_mock.mock_calls
        if str(call[1]).startswith(DETECT_URL)
    ]
    assert len(detect_calls) == 1
