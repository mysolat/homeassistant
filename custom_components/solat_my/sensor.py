"""Sensor platform for Waktu Solat Malaysia."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
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
    coordinator: SolatMyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    for prayer in PRAYER_TIMES:
        entities.append(PrayerTimeSensor(coordinator, entry, prayer))

    entities.append(HijriDateSensor(coordinator, entry))
    entities.append(NextPrayerSensor(coordinator, entry))
    entities.append(CurrentPrayerSensor(coordinator, entry))

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
        dt_naive = self.coordinator.data["prayer_times"].get(self._prayer)
        if dt_naive is None:
            return None
        local_tz = dt_util.get_time_zone(self.hass.config.time_zone)
        return dt_naive.replace(tzinfo=local_tz) if local_tz else dt_naive

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

    def _get_next_prayer(self) -> tuple[str | None, datetime | None]:
        if self.coordinator.data is None:
            return None, None
        now = dt_util.now()
        local_tz = dt_util.get_time_zone(self.hass.config.time_zone)
        for prayer in [PRAYER_FAJR, PRAYER_SYURUK, PRAYER_DHUHA, PRAYER_DHUHR,
                       PRAYER_ASR, PRAYER_MAGHRIB, PRAYER_ISHA]:
            dt_naive = self.coordinator.data["prayer_times"].get(prayer)
            if dt_naive is None:
                continue
            dt_aware = dt_naive.replace(tzinfo=local_tz) if local_tz else dt_naive
            if dt_aware > now:
                return prayer, dt_aware
        return None, None

    @property
    def native_value(self) -> str | None:
        prayer, _ = self._get_next_prayer()
        return PRAYER_NAMES_MS.get(prayer, prayer.capitalize()) if prayer else "Selesai"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        prayer, dt_aware = self._get_next_prayer()
        if prayer is None or dt_aware is None:
            return {"prayer": None, "time_24h": None, "countdown": None}
        delta = dt_aware - dt_util.now()
        total_seconds = int(delta.total_seconds())
        hours, rem = divmod(total_seconds, 3600)
        raw = self.coordinator.data.get("raw", {}) if self.coordinator.data else {}
        time_str = raw.get(prayer, "")
        return {
            "prayer": prayer,
            "prayer_ms": PRAYER_NAMES_MS.get(prayer, prayer),
            "time_24h": time_str[:5] if time_str else None,
            "countdown": f"{hours:02d}:{rem // 60:02d}",
            "countdown_seconds": total_seconds,
        }


class CurrentPrayerSensor(CoordinatorEntity[SolatMyCoordinator], SensorEntity):
    """Sensor showing the current prayer period."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:mosque"

    def __init__(self, coordinator: SolatMyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_current_prayer"
        self._attr_name = "Waktu Solat Semasa"
        self._attr_device_info = _make_device_info(entry)

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        now = dt_util.now()
        local_tz = dt_util.get_time_zone(self.hass.config.time_zone)
        current = None
        for prayer in [PRAYER_IMSAK, PRAYER_FAJR, PRAYER_SYURUK, PRAYER_DHUHA,
                       PRAYER_DHUHR, PRAYER_ASR, PRAYER_MAGHRIB, PRAYER_ISHA]:
            dt_naive = self.coordinator.data["prayer_times"].get(prayer)
            if dt_naive is None:
                continue
            dt_aware = dt_naive.replace(tzinfo=local_tz) if local_tz else dt_naive
            if now >= dt_aware:
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
