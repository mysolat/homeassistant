"""Sensor platform for Waktu Solat Malaysia."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    PRAYER_ASR,
    PRAYER_DHUHA,
    PRAYER_DHUHR,
    PRAYER_FAJR,
    PRAYER_ICONS,
    PRAYER_ISHA,
    PRAYER_IMSAK,
    PRAYER_MAGHRIB,
    PRAYER_NAMES_MS,
    PRAYER_SYURUK,
    PRAYER_TIMES,
)
from .coordinator import SolatMyCoordinator

_LOGGER = logging.getLogger(__name__)
LOCAL_STATE_UPDATE_INTERVAL = timedelta(minutes=1)
_BEARING_RE = re.compile(r"(\d+)\s*°(?:\s*(\d+)\s*′)?(?:\s*(\d+(?:\.\d+)?)\s*″)?")


def _parse_bearing(text: str) -> float | None:
    """Return a bearing like ``291° 7′ 23″`` in decimal degrees, or None."""
    match = _BEARING_RE.search(text or "")
    if match is None:
        return None
    deg, minutes, seconds = match.groups()
    value = int(deg) + int(minutes or 0) / 60 + float(seconds or 0) / 3600
    return round(value, 2)


def _make_device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return device info keyed by entry_id, named by user-provided name."""
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="JAKIM / solat.my",
        entry_type="service",
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Waktu Solat sensors from config entry."""
    coordinator: SolatMyCoordinator = entry.runtime_data

    entities: list[SensorEntity] = []
    for prayer in PRAYER_TIMES:
        entities.append(PrayerTimeSensor(coordinator, entry, prayer))

    entities.append(HijriDateSensor(coordinator, entry))
    entities.append(NextPrayerSensor(coordinator, entry))
    entities.append(CurrentPrayerSensor(coordinator, entry))
    entities.append(QiblaSensor(coordinator, entry))

    async_add_entities(entities)


class PrayerTimeSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor for a single prayer time."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SolatMyCoordinator, entry: ConfigEntry, prayer: str
    ) -> None:
        super().__init__(coordinator)
        self._prayer = prayer
        # unique_id uses entry_id so it's stable even when zone changes
        self._attr_unique_id = f"{entry.entry_id}_{prayer}"
        self._attr_name = PRAYER_NAMES_MS.get(prayer, prayer.capitalize())
        self._attr_icon = PRAYER_ICONS.get(prayer, "mdi:clock")
        self._attr_device_info = _make_device_info(entry)

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["prayer_times"].get(self._prayer)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        raw = self.coordinator.data.get("raw", {})
        time_str = raw.get(self._prayer, "")
        return {
            "time_24h": time_str[:5] if time_str else None,
            "zone": self.coordinator.data.get("zone"),
            "zone_desc": self.coordinator.data.get("zone_desc"),
            "hijri": self.coordinator.data.get("hijri"),
            "date": self.coordinator.data.get("date"),
        }


class HijriDateSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor for the Hijri date."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_hijri_date"
        self._attr_name = "Tarikh Hijri"
        self._attr_device_info = _make_device_info(entry)

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        hijri = self.coordinator.data.get("hijri", "")
        if not hijri:
            return None
        months_ms = [
            "Muharram", "Safar", "Rabi'ul Awwal", "Rabi'ul Akhir",
            "Jamadil Awwal", "Jamadil Akhir", "Rejab", "Sya'ban",
            "Ramadan", "Syawal", "Zulkaedah", "Zulhijjah",
        ]
        try:
            year, month, day = hijri.split("-")
            return f"{int(day)} {months_ms[int(month) - 1]} {year}H"
        except (ValueError, IndexError):
            return hijri

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        hijri = self.coordinator.data.get("hijri", "")
        try:
            year, month, day = hijri.split("-")
            return {
                "year": year,
                "month": month,
                "day": day,
                "iso": hijri,
                "gregorian": self.coordinator.data.get("date"),
            }
        except (ValueError, AttributeError):
            return {"iso": hijri}


class NextPrayerSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor showing the next upcoming prayer and countdown."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:clock-alert"

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_prayer"
        self._attr_name = "Waktu Solat Seterusnya"
        self._attr_device_info = _make_device_info(entry)
        self._cancel_interval: Any = None

    async def async_added_to_hass(self) -> None:
        """Set up periodic local updates for countdown and next prayer transitions."""
        await super().async_added_to_hass()

        @callback
        def _handle_interval(_: datetime) -> None:
            self.async_write_ha_state()

        self._cancel_interval = async_track_time_interval(
            self.hass, _handle_interval, LOCAL_STATE_UPDATE_INTERVAL
        )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up periodic update listener."""
        if self._cancel_interval is not None:
            self._cancel_interval()
            self._cancel_interval = None
        await super().async_will_remove_from_hass()

    def _get_next_prayer(self) -> tuple[str | None, datetime | None, bool]:
        """Return (prayer, time, is_tomorrow). After Isyak this is tomorrow's Subuh."""
        if self.coordinator.data is None:
            return None, None, False
        now = dt_util.now()
        for prayer in [PRAYER_FAJR, PRAYER_SYURUK, PRAYER_DHUHA, PRAYER_DHUHR,
                       PRAYER_ASR, PRAYER_MAGHRIB, PRAYER_ISHA]:
            prayer_at = self.coordinator.data["prayer_times"].get(prayer)
            if prayer_at is None:
                continue
            if prayer_at > now:
                return prayer, prayer_at, False
        return PRAYER_FAJR, self.coordinator.data.get("tomorrow_fajr"), True

    @property
    def native_value(self) -> str | None:
        prayer, _, _ = self._get_next_prayer()
        return PRAYER_NAMES_MS[prayer] if prayer else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        prayer, dt_aware, tomorrow = self._get_next_prayer()
        if prayer is None:
            return {
                "prayer": None,
                "time_24h": None,
                "countdown": None,
                "tomorrow": False,
            }
        data = self.coordinator.data or {}
        raw = data.get("tomorrow_raw", {}) if tomorrow else data.get("raw", {})
        time_str = raw.get(prayer, "")
        attributes: dict[str, Any] = {
            "prayer": prayer,
            "prayer_ms": PRAYER_NAMES_MS.get(prayer, prayer),
            "time_24h": time_str[:5] if time_str else None,
            "tomorrow": tomorrow,
        }
        if dt_aware is None:
            attributes["countdown"] = None
            attributes["countdown_seconds"] = None
            return attributes
        total_seconds = max(0, int((dt_aware - dt_util.now()).total_seconds()))
        hours, rem = divmod(total_seconds, 3600)
        attributes["countdown"] = f"{hours:02d}:{rem // 60:02d}"
        attributes["countdown_seconds"] = total_seconds
        return attributes


class CurrentPrayerSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor showing the current prayer period."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:mosque"

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_prayer"
        self._attr_name = "Waktu Solat Semasa"
        self._attr_device_info = _make_device_info(entry)
        self._cancel_interval: Any = None

    async def async_added_to_hass(self) -> None:
        """Set up periodic local updates for prayer-period transitions."""
        await super().async_added_to_hass()

        @callback
        def _handle_interval(_: datetime) -> None:
            self.async_write_ha_state()

        self._cancel_interval = async_track_time_interval(
            self.hass, _handle_interval, LOCAL_STATE_UPDATE_INTERVAL
        )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up periodic update listener."""
        if self._cancel_interval is not None:
            self._cancel_interval()
            self._cancel_interval = None
        await super().async_will_remove_from_hass()

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        now = dt_util.now()
        current = None
        for prayer in [PRAYER_IMSAK, PRAYER_FAJR, PRAYER_SYURUK, PRAYER_DHUHA,
                       PRAYER_DHUHR, PRAYER_ASR, PRAYER_MAGHRIB, PRAYER_ISHA]:
            prayer_at = self.coordinator.data["prayer_times"].get(prayer)
            if prayer_at is None:
                continue
            if now >= prayer_at:
                current = prayer
        return PRAYER_NAMES_MS.get(current, current.capitalize()) if current else "Sebelum Imsak"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        return {
            "zone": self.coordinator.data.get("zone"),
            "zone_desc": self.coordinator.data.get("zone_desc"),
            "bearing": self.coordinator.data.get("bearing"),
            "hijri": self.coordinator.data.get("hijri"),
            "date": self.coordinator.data.get("date"),
            "day": self.coordinator.data.get("day"),
        }


class QiblaSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor for the qibla direction, in degrees from true north."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = DEGREE
    _attr_icon = "mdi:compass-outline"
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_qibla"
        self._attr_name = "Arah Kiblat"
        self._attr_device_info = _make_device_info(entry)

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return _parse_bearing(self.coordinator.data.get("bearing", ""))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        return {
            "dms": self.coordinator.data.get("bearing"),
            "rujukan": "utara benar",
        }
