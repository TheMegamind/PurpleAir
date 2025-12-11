# custom_components/purpleair/sensor.py

from __future__ import annotations

from typing import Any
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .api import PurpleAirResult

CATEGORY_TO_LEVEL = {
    "Good": 1,
    "Moderate": 2,
    "Unhealthy for Sensitive Groups": 3,
    "Unhealthy": 4,
    "Very Unhealthy": 5,
    "Hazardous": 6,
}

HEALTH_ADVISORY_SHORT = {
    "Good": "Air quality is good.",
    "Moderate": "Acceptable; some pollutants may affect sensitive people.",
    "Unhealthy for Sensitive Groups": "Sensitive groups should limit exposure.",
    "Unhealthy": "Everyone may experience negative health effects.",
    "Very Unhealthy": "Health warnings of emergency conditions.",
    "Hazardous": "Serious health effects; avoid outdoor exposure.",
}

HEALTH_ADVISORY_LONG = {
    "Good": "Air quality is good. Enjoy your day!",
    "Moderate": "Air quality is acceptable, but some pollutants may affect sensitive individuals.",
    "Unhealthy for Sensitive Groups": "Sensitive groups should reduce prolonged or heavy exertion outdoors.",
    "Unhealthy": "Everyone may begin to experience health effects; limit outdoor activities.",
    "Very Unhealthy": "Health alert: increased risk for everyone. Avoid outdoor exertion.",
    "Hazardous": "Health warnings of emergency conditions. Stay indoors and minimize exposure.",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        PurpleAirAQISensor(coordinator, entry),
        PurpleAirCategorySensor(coordinator, entry),
        PurpleAirConversionSensor(coordinator, entry),
        PurpleAirSitesSensor(coordinator, entry),
        PurpleAirHealthStatusSensor(coordinator, entry),
        PurpleAirHealthAdvisoryShortSensor(coordinator, entry),
        PurpleAirHealthAdvisoryLongSensor(coordinator, entry),
        PurpleAirAQILevelSensor(coordinator, entry),
        PurpleAirAQIDeltaSensor(coordinator, entry),
        PurpleAirAQIColorSensor(coordinator, entry),
    ]

    async_add_entities(entities, True)


# ──────────────────────────────────────────────────────────────────────────────
# Base class
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for all PurpleAir sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._base_unique = entry.entry_id

    @property
    def result(self) -> PurpleAirResult | None:
        return self.coordinator.data

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="PurpleAir",
        )


# ──────────────────────────────────────────────────────────────────────────────
# AQI — numeric
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirAQISensor(PurpleAirBaseSensor):
    _attr_name = "AQI"
    _attr_icon = "mdi:weather-hazy"
    _attr_native_unit_of_measurement = "AQI"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_aqi"

    @property
    def native_value(self) -> int | None:
        return self.result.aqi if self.result else None


# ──────────────────────────────────────────────────────────────────────────────
# Category — ENUM
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirCategorySensor(PurpleAirBaseSensor):
    _attr_name = "Category"
    _attr_icon = "mdi:eye"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(CATEGORY_TO_LEVEL.keys())

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_category"

    @property
    def native_value(self) -> str | None:
        return self.result.category if self.result else None


# ──────────────────────────────────────────────────────────────────────────────
# Conversion
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirConversionSensor(PurpleAirBaseSensor):
    _attr_name = "Conversion"
    _attr_icon = "mdi:flask"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_conversion"

    @property
    def native_value(self) -> str | None:
        return self.result.conversion if self.result else None


# ──────────────────────────────────────────────────────────────────────────────
# Sites
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirSitesSensor(PurpleAirBaseSensor):
    _attr_name = "Sites"
    _attr_icon = "mdi:map-marker"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_sites"

    @property
    def native_value(self) -> str | None:
        if not self.result:
            return None
        return ", ".join(self.result.sites)


# ──────────────────────────────────────────────────────────────────────────────
# Health Status
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirHealthStatusSensor(PurpleAirBaseSensor):
    _attr_name = "Health Status"
    _attr_icon = "mdi:eye"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_health_status"

    @property
    def native_value(self) -> str | None:
        return "online" if self.result else "offline"


# ──────────────────────────────────────────────────────────────────────────────
# Health Advisory Short
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirHealthAdvisoryShortSensor(PurpleAirBaseSensor):
    _attr_name = "Health Advisory (Short)"
    _attr_icon = "mdi:lightbulb-question-outline"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_health_adv_short"

    @property
    def native_value(self) -> str | None:
        if not self.result:
            return None
        return HEALTH_ADVISORY_SHORT.get(self.result.category, "Unknown")


# ──────────────────────────────────────────────────────────────────────────────
# Health Advisory Long
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirHealthAdvisoryLongSensor(PurpleAirBaseSensor):
    _attr_name = "Health Advisory"
    _attr_icon = "mdi:lightbulb-on-outline"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_health_adv_long"

    @property
    def native_value(self) -> str | None:
        if not self.result:
            return None
        return HEALTH_ADVISORY_LONG.get(self.result.category, "Unknown")


# ──────────────────────────────────────────────────────────────────────────────
# AQI Level (1–6) — MUST be string to avoid becoming a control
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirAQILevelSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Level"
    _attr_icon = "mdi:numeric"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_aqi_level"

    @property
    def native_value(self) -> str | None:
        if not self.result:
            return None
        num = CATEGORY_TO_LEVEL.get(self.result.category)
        return str(num) if num is not None else None


# ──────────────────────────────────────────────────────────────────────────────
# AQI Delta — numeric
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirAQIDeltaSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Delta"
    _attr_icon = "mdi:vector-difference"
    _attr_native_unit_of_measurement = "AQI"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_aqi_delta"

    @property
    def native_value(self) -> int | None:
        if not self.result:
            return None
        return self.result.delta


# ──────────────────────────────────────────────────────────────────────────────
# AQI Color — text
# ──────────────────────────────────────────────────────────────────────────────
class PurpleAirAQIColorSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Color"
    _attr_icon = "mdi:palette"

    @property
    def unique_id(self) -> str:
        return f"{self._base_unique}_aqi_color"

    @property
    def native_value(self) -> str | None:
        return self.result.color if self.result else None
