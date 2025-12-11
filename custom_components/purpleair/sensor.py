# custom_components/purpleair/sensor.py

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .api import PurpleAirResult


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up PurpleAir sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = [
        PurpleAirAQISensor(coordinator, entry),
        PurpleAirCategorySensor(coordinator, entry),
        PurpleAirConversionSensor(coordinator, entry),
        PurpleAirSitesSensor(coordinator, entry),
        PurpleAirHealthStatusSensor(coordinator, entry),
        PurpleAirHealthAdvisoryLongSensor(coordinator, entry),
        PurpleAirHealthAdvisoryShortSensor(coordinator, entry),
        PurpleAirAQIColorSensor(coordinator, entry),
        PurpleAirAQILevelSensor(coordinator, entry),
        PurpleAirAQIDeltaSensor(coordinator, entry),
    ]

    async_add_entities(entities, True)


# ════════════════════════════════════════════════════════════════════════
# COMMON MIXIN FOR DEVICE REGISTRATION
# ════════════════════════════════════════════════════════════════════════


class PurpleAirBase:
    """Mixin adding shared device_info."""

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "PurpleAir",
        }


# ════════════════════════════════════════════════════════════════════════
# CONSTANT MAPPINGS (EPA STYLE)
# ════════════════════════════════════════════════════════════════════════

CATEGORY_TO_LEVEL: dict[str, int] = {
    "Good": 1,
    "Moderate": 2,
    "Unhealthy for Sensitive Groups": 3,
    "Unhealthy": 4,
    "Very Unhealthy": 5,
    "Hazardous": 6,
}

# severity mapping for HA enum severity support
CATEGORY_TO_SEVERITY: dict[str, str] = {
    "Good": "info",
    "Moderate": "warning",
    "Unhealthy for Sensitive Groups": "warning",
    "Unhealthy": "critical",
    "Very Unhealthy": "critical",
    "Hazardous": "critical",
}

# color name + hex (EPA palette)
CATEGORY_TO_COLOR: dict[str, tuple[str, str]] = {
    "Good": ("green", "#00E400"),
    "Moderate": ("yellow", "#FFFF00"),
    "Unhealthy for Sensitive Groups": ("orange", "#FF7E00"),
    "Unhealthy": ("red", "#FF0000"),
    "Very Unhealthy": ("purple", "#8F3F97"),
    "Hazardous": ("maroon", "#7E0023"),
}

ADVISORIES_LONG: dict[str, str] = {
    "Good": "Air quality is good. Enjoy your day!",
    "Moderate": "Moderate air quality. Sensitive individuals should consider reducing prolonged outdoor exertion.",
    "Unhealthy for Sensitive Groups": "Limit prolonged outdoor exertion if you are sensitive.",
    "Unhealthy": "Air is unhealthy. Consider reducing outdoor activities.",
    "Very Unhealthy": "Health alert: everyone may experience more serious effects.",
    "Hazardous": "Emergency conditions: avoid outdoor activity.",
}

ADVISORIES_SHORT: dict[str, str] = {
    "Good": "Good",
    "Moderate": "Moderate",
    "Unhealthy for Sensitive Groups": "Unhealthy for sensitive groups",
    "Unhealthy": "Unhealthy",
    "Very Unhealthy": "Very unhealthy",
    "Hazardous": "Hazardous",
}


# ════════════════════════════════════════════════════════════════════════
# AQI SENSOR
# ════════════════════════════════════════════════════════════════════════


class PurpleAirAQISensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """PurpleAir AQI sensor."""

    _attr_has_entity_name = True
    _attr_name = "AQI"
    _attr_icon = "mdi:weather-hazy"
    _attr_native_unit_of_measurement = "AQI"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_aqi"
        self._update_interval = int(entry.data.get("update_interval", 10))

    @property
    def native_value(self) -> int | None:
        result: PurpleAirResult | None = self.coordinator.data
        return result.aqi if result else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None

        level = CATEGORY_TO_LEVEL.get(result.category)
        color_name, color_hex = CATEGORY_TO_COLOR.get(
            result.category, ("unknown", "#000000")
        )

        return {
            "category": result.category,
            "sites": result.sites,
            "conversion": result.conversion,
            "weighted": result.weighted,
            "fetch_time": datetime.now().isoformat(),
            "update_interval": self._update_interval,
            "aqi_level": level,
            "aqi_color_name": color_name,
            "aqi_color_hex": color_hex,
        }


# ════════════════════════════════════════════════════════════════════════
# CATEGORY SENSOR (ENUM + SEVERITY)
# ════════════════════════════════════════════════════════════════════════


class PurpleAirCategorySensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """AQI category sensor using HA enum/severity."""

    _attr_has_entity_name = True
    _attr_name = "Category"
    _attr_icon = "mdi:eye"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(CATEGORY_TO_LEVEL.keys())

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_category"

    @property
    def native_value(self) -> str | None:
        result: PurpleAirResult | None = self.coordinator.data
        return result.category if result else None

    @property
    def native_severity(self) -> str | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None
        return CATEGORY_TO_SEVERITY.get(result.category)


# ════════════════════════════════════════════════════════════════════════
# CONVERSION SENSOR
# ════════════════════════════════════════════════════════════════════════


class PurpleAirConversionSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Conversion method sensor."""

    _attr_has_entity_name = True
    _attr_name = "Conversion"
    _attr_icon = "mdi:flask-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_conversion"

    @property
    def native_value(self) -> str | None:
        result: PurpleAirResult | None = self.coordinator.data
        return result.conversion if result else None


# ════════════════════════════════════════════════════════════════════════
# SITES SENSOR
# ════════════════════════════════════════════════════════════════════════


class PurpleAirSitesSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Sites used in AQI calculation."""

    _attr_has_entity_name = True
    _attr_name = "Sites"
    _attr_icon = "mdi:map-marker-multiple-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_sites"

    @property
    def native_value(self) -> str | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result or not result.sites:
            return None
        return ", ".join(result.sites)


# ════════════════════════════════════════════════════════════════════════
# HEALTH STATUS SENSOR
# ════════════════════════════════════════════════════════════════════════


class PurpleAirHealthStatusSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Indicates if PurpleAir data is online or offline."""

    _attr_has_entity_name = True
    _attr_name = "Health Status"
    _attr_icon = "mdi:eye-check-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_health"

    @property
    def native_value(self) -> str:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return "offline"
        return "online"


# ════════════════════════════════════════════════════════════════════════
# HEALTH ADVISORY (LONG)
# ════════════════════════════════════════════════════════════════════════


class PurpleAirHealthAdvisoryLongSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Long-form health advisory based on AQI category."""

    _attr_has_entity_name = True
    _attr_name = "Health Advisory (Long)"
    _attr_icon = "mdi:head-question-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_advisory_long"

    @property
    def native_value(self) -> str:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return "No data available"
        return ADVISORIES_LONG.get(
            result.category, "Air quality information unavailable."
        )


# ════════════════════════════════════════════════════════════════════════
# HEALTH ADVISORY (SHORT)
# ════════════════════════════════════════════════════════════════════════


class PurpleAirHealthAdvisoryShortSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Short health advisory phrase based on AQI category."""

    _attr_has_entity_name = True
    _attr_name = "Health Advisory (Short)"
    _attr_icon = "mdi:head-alert-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_advisory_short"

    @property
    def native_value(self) -> str:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return "No data"
        return ADVISORIES_SHORT.get(result.category, "Unknown")


# ════════════════════════════════════════════════════════════════════════
# AQI COLOR SENSOR
# ════════════════════════════════════════════════════════════════════════


class PurpleAirAQIColorSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """AQI color (name) with hex in attributes."""

    _attr_has_entity_name = True
    _attr_name = "AQI Color"
    _attr_icon = "mdi:palette"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_aqi_color"

    @property
    def native_value(self) -> str | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None
        color_name, _ = CATEGORY_TO_COLOR.get(result.category, ("unknown", "#000000"))
        return color_name

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None
        color_name, color_hex = CATEGORY_TO_COLOR.get(
            result.category, ("unknown", "#000000")
        )
        return {
            "color_name": color_name,
            "color_hex": color_hex,
        }


# ════════════════════════════════════════════════════════════════════════
# AQI LEVEL SENSOR (1–6)
# ════════════════════════════════════════════════════════════════════════


class PurpleAirAQILevelSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """EPA AQI level 1–6."""

    _attr_has_entity_name = True
    _attr_name = "AQI Level"
    _attr_icon = "mdi:numeric"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_aqi_level"

    @property
    def native_value(self) -> int | None:
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None
        return CATEGORY_TO_LEVEL.get(result.category)


# ════════════════════════════════════════════════════════════════════════
# AQI DELTA SENSOR (CHANGE SINCE LAST UPDATE)
# ════════════════════════════════════════════════════════════════════════


class PurpleAirAQIDeltaSensor(PurpleAirBase, CoordinatorEntity, SensorEntity):
    """Change in AQI since last update."""

    _attr_has_entity_name = True
    _attr_name = "AQI Delta"
    _attr_icon = "mdi:triangle-wave"
    _attr_native_unit_of_measurement = "AQI"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_aqi_delta"
        self._last_aqi: int | None = None

    @property
    def native_value(self) -> int | None:
        """Return AQI delta since last coordinator update."""
        result: PurpleAirResult | None = self.coordinator.data
        if not result:
            return None

        current = result.aqi
        if self._last_aqi is None:
            delta = 0
        else:
            delta = current - self._last_aqi

        self._last_aqi = current
        return delta
