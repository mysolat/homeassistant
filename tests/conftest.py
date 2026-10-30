"""Shared fixtures for the solat_my tests."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.solat_my.const import DOMAIN

FIXTURES = Path(__file__).parent / "fixtures"
MONTHLY_URL = "https://solat.my/api/monthly/{zone}/{month}?year={year}"


def load_fixture_json(name: str) -> dict:
    """Read a saved API response from tests/fixtures."""
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let Home Assistant load custom_components/solat_my."""
    yield


@pytest.fixture(autouse=True)
def skip_mimbar_frontend():
    """Skip serving the Mimbar card: the test instance has no HTTP server."""
    with patch(
        "custom_components.solat_my._async_register_mimbar_frontend", AsyncMock()
    ):
        yield


@pytest.fixture
def mock_api(aioclient_mock):
    """Serve saved October 2026 responses for SGR01 and SGR03."""
    for zone in ("SGR01", "SGR03"):
        aioclient_mock.get(
            MONTHLY_URL.format(zone=zone, month=10, year=2026),
            json=load_fixture_json(f"monthly_{zone}_2026_10.json"),
        )
    return aioclient_mock


@pytest.fixture
def config_entry(hass):
    """A Waktu Solat entry set up with zone SGR01."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Waktu Solat",
        data={"name": "Waktu Solat", "zone": "SGR01"},
        unique_id="waktu solat",
    )
    entry.add_to_hass(hass)
    return entry
