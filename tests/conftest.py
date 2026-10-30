"""Shared fixtures for the solat_my tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


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
