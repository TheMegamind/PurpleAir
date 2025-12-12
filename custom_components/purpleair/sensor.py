from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
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
    "Good": "Good",
    "Moderate": "Moderate",
    "Unhealthy for Sensitive Groups": "Sensitive groups at risk",
    "Unhealthy": "Unhealthy",
    "Very Unhealthy": "Very unhealthy",
    "Hazardous": "Hazardous",
}

HEALTH_ADVISORY_LONG = {
    "Good": "Air quality is good. Enjoy your day!",
    "Moderate": "Air quality is acceptable; some pollutants may affect sensitive individuals.",
    "Unhealthy for Sensitive Groups": "Sensitive groups should reduce prolonged or heavy exertion outdoors.",
    "Unhealthy": "Everyone may experience health effects; limit outdoor activity.",
    "Very Unhealthy": "Health alert: increased risk for everyone.",
    "Hazardous": "Emergency conditions. Stay indoors.",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            PurpleAirAQISensor(coordinator, entry),
            PurpleAirAQIColorSensor(coordinator, entry),
            PurpleAirAQIDeltaSensor(coordinator, entry),
            PurpleAirAQILevelSensor(coordinator, entry),
            PurpleAirCategorySensor(coordinator, entry),
            PurpleAirConversionSensor(coordinator, entry),
            PurpleAirHealthAdvisoryShortSensor(coordinator, entry),
            PurpleAirHealthAdvisoryLongSensor(coordinator, entry),
            PurpleAirHealthStatusSensor(coordinator, entry),
            PurpleAirSitesSensor(coordinator, entry),
        ],
        True,
    )


# ─────────────────────────────────────────────────────────────
# Base sensor (CRITICAL FIX HERE)
# ─────────────────────────────────────────────────────────────
class PurpleAirBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def result(self) -> PurpleAirResult | None:
        return self.coordinator.data

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="PurpleAir",
        )


class PurpleAirAQISensor(PurpleAirBaseSensor):
    _attr_name = "AQI"
    _attr_icon = "mdi:weather-hazy"
    _attr_native_unit_of_measurement = "AQI"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_aqi"

    @property
    def native_value(self):
        return self.result.aqi if self.result else None


class PurpleAirAQIColorSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Color"
    _attr_icon = "mdi:palette"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_aqi_color"

    @property
    def native_value(self):
        return self.result.color if self.result else None


class PurpleAirAQIDeltaSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Delta"
    _attr_icon = "mdi:vector-difference"
    _attr_native_unit_of_measurement = "AQI"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._last = None

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_aqi_delta"

    @property
    def native_value(self):
        if not self.result:
            return None
        current = self.result.aqi
        delta = 0 if self._last is None else current - self._last
        self._last = current
        return delta


class PurpleAirAQILevelSensor(PurpleAirBaseSensor):
    _attr_name = "AQI Level"
    _attr_icon = "mdi:numeric"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_aqi_level"

    @property
    def native_value(self):
        if not self.result:
            return None
        level = CATEGORY_TO_LEVEL.get(self.result.category)
        return str(level) if level else None


class PurpleAirCategorySensor(PurpleAirBaseSensor):
    _attr_name = "Category"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(CATEGORY_TO_LEVEL.keys())

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_category"

    @property
    def native_value(self):
        return self.result.category if self.result else None


class PurpleAirConversionSensor(PurpleAirBaseSensor):
    _attr_name = "Conversion"
    _attr_icon = "mdi:flask"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_conversion"

    @property
    def native_value(self):
        return self.result.conversion if self.result else None


class PurpleAirHealthAdvisoryShortSensor(PurpleAirBaseSensor):
    _attr_name = "Health Advisory (Short)"
    _attr_icon = "mdi:lightbulb-question-outline"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_health_short"

    @property
    def native_value(self):
        return HEALTH_ADVISORY_SHORT.get(self.result.category) if self.result else None


class PurpleAirHealthAdvisoryLongSensor(PurpleAirBaseSensor):
    _attr_name = "Health Advisory"
    _attr_icon = "mdi:lightbulb-on-outline"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_health_long"

    @property
    def native_value(self):
        return HEALTH_ADVISORY_LONG.get(self.result.category) if self.result else None


class PurpleAirHealthStatusSensor(PurpleAirBaseSensor):
    _attr_name = "Health Status"
    _attr_icon = "mdi:eye"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_health_status"

    @property
    def native_value(self):
        return "online" if self.result else "offline"


class PurpleAirSitesSensor(PurpleAirBaseSensor):
    _attr_name = "Sites"
    _attr_icon = "mdi:map-marker"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_sites"

    @property
    def native_value(self):
        return ", ".join(self.result.sites) if self.result else None
