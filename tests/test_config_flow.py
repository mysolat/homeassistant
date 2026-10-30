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
USER_INPUT = {"name": "Rumah", "zone": "SGR01"}


async def _start_flow(hass: HomeAssistant) -> str:
    """Start the user flow and return its flow id."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return result["flow_id"]


async def test_user_flow_creates_entry(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A valid zone creates an entry with the name and zone."""
    aioclient_mock.get(ZONE_URL, json={"status": "OK!"})

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
