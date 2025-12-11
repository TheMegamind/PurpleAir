from __future__ import annotations

from datetime import timedelta   # <-- REQUIRED

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([PurpleAirUpdateIntervalNumber(coordinator, entry)])


class PurpleAirUpdateIntervalNumber(CoordinatorEntity, NumberEntity):
    """Number entity that controls the polling interval."""

    _attr_has_entity_name = True
    _attr_name = "Update Interval"
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 1
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"
    _attr_mode = "slider"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_update_interval"

    @property
    def native_value(self):
        """Return current interval as reported by config entry."""
        return int(self.entry.data.get("update_interval", 10))

    async def async_set_native_value(self, value):
        """User moved the slider — update entry & coordinator."""
        # Update config entry
        new = {**self.entry.data, "update_interval": int(value)}
        self.hass.config_entries.async_update_entry(self.entry, data=new)

        # Apply new polling interval instantly
        self.coordinator.update_interval = timedelta(minutes=int(value))

        await self.coordinator.async_request_refresh()
