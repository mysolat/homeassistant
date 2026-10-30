"""Tests for the Malay date helpers in the solat_my coordinator."""
from __future__ import annotations

from datetime import date

import pytest

from custom_components.solat_my.coordinator import _normalise_ms_date, _parse_date


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("10-Mar-2026", date(2026, 3, 10)),
        ("10-Mac-2026", date(2026, 3, 10)),
        ("10-Mei-2026", date(2026, 5, 10)),
        ("05-Ogos-2026", date(2026, 8, 5)),
        ("01-Okt-2026", date(2026, 10, 1)),
        ("01-Nov-2026", date(2026, 11, 1)),
        ("31-Dis-2026", date(2026, 12, 31)),
        ("", None),
        ("not-a-date", None),
    ],
)
def test_parse_date(date_str: str, expected: date | None) -> None:
    """_parse_date maps Malay month names and returns None on bad input."""
    assert _parse_date(date_str) == expected


def test_normalise_ms_date_keeps_time_suffix() -> None:
    """_normalise_ms_date replaces the month and leaves the rest untouched."""
    assert _normalise_ms_date("30-Okt-2026 05:48:00") == "30-Oct-2026 05:48:00"
