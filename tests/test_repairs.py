"""Tests for the Repairs notice that appears when solat.my keeps failing."""
from __future__ import annotations

from homeassistant.helpers import issue_registry as ir

from custom_components.solat_my.const import DOMAIN

from .conftest import MONTHLY_URL, load_fixture_json

OCTOBER_URL = MONTHLY_URL.format(zone="SGR01", month=10, year=2026)


async def _set_up(hass, config_entry, freezer):
    """Set up the entry on a day in the middle of October and return its coordinator."""
    freezer.move_to("2026-10-30T10:00:00+08:00")
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry.runtime_data


def _serve_error(mock_api) -> None:
    """Make every request for October fail with HTTP 500."""
    mock_api.clear_requests()
    mock_api.get(OCTOBER_URL, status=500)


def _serve_october(mock_api) -> None:
    """Make October load normally again."""
    mock_api.clear_requests()
    mock_api.get(OCTOBER_URL, json=load_fixture_json("monthly_SGR01_2026_10.json"))


async def _refresh(coordinator, times: int) -> None:
    """Refresh `times` times, and clear the cache first so each one fetches."""
    for _ in range(times):
        coordinator._months.clear()
        await coordinator.async_refresh()


def _issue(hass, config_entry):
    """Return the API repair issue for the entry, or None."""
    return ir.async_get(hass).async_get_issue(
        DOMAIN, f"api_unreachable_{config_entry.entry_id}"
    )


async def test_no_issue_after_few_failures(
    hass, config_entry, mock_api, freezer
) -> None:
    """Five failed refreshes in a row are a blip, so there is no notice."""
    coordinator = await _set_up(hass, config_entry, freezer)

    _serve_error(mock_api)
    await _refresh(coordinator, 5)

    assert coordinator.last_update_success is False
    assert _issue(hass, config_entry) is None


async def test_issue_after_six_failures(hass, config_entry, mock_api, freezer) -> None:
    """Six failed refreshes in a row raise a warning that the user cannot fix in the UI."""
    coordinator = await _set_up(hass, config_entry, freezer)

    _serve_error(mock_api)
    await _refresh(coordinator, 6)

    issue = _issue(hass, config_entry)
    assert issue is not None
    assert issue.severity == ir.IssueSeverity.WARNING
    assert issue.is_fixable is False
    assert issue.translation_key == "api_unreachable"
    assert issue.translation_placeholders["zone"] == "SGR01"
    assert "HTTP 500" in issue.translation_placeholders["error"]


async def test_issue_cleared_on_recovery(hass, config_entry, mock_api, freezer) -> None:
    """The first good refresh after the notice removes it."""
    coordinator = await _set_up(hass, config_entry, freezer)
    _serve_error(mock_api)
    await _refresh(coordinator, 6)
    assert _issue(hass, config_entry) is not None

    _serve_october(mock_api)
    await _refresh(coordinator, 1)

    assert coordinator.last_update_success is True
    assert _issue(hass, config_entry) is None


async def test_counter_resets_on_success(hass, config_entry, mock_api, freezer) -> None:
    """A good refresh restarts the count, so 5 + success + 5 failures raise nothing."""
    coordinator = await _set_up(hass, config_entry, freezer)

    _serve_error(mock_api)
    await _refresh(coordinator, 5)
    _serve_october(mock_api)
    await _refresh(coordinator, 1)
    assert coordinator.last_update_success is True
    _serve_error(mock_api)
    await _refresh(coordinator, 5)

    assert coordinator.last_update_success is False
    assert _issue(hass, config_entry) is None


async def test_issue_removed_on_unload(hass, config_entry, mock_api, freezer) -> None:
    """Removing the integration removes its notice."""
    coordinator = await _set_up(hass, config_entry, freezer)
    _serve_error(mock_api)
    await _refresh(coordinator, 6)
    assert _issue(hass, config_entry) is not None

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert _issue(hass, config_entry) is None
