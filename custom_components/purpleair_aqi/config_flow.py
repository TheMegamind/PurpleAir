# custom_components/purpleair_aqi/config_flow.py

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE

from . import DOMAIN


CONVERSION_OPTIONS = [
    "US EPA",
    "Woodsmoke",
    "AQ&U",
    "LRAPA",
    "CF=1",
    "none",
]


class PurpleAirAQIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PurpleAirAQIOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="PurpleAir AQI", data=user_input)

        # Use HA location as default
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required("device_search", default=True): bool,
                vol.Optional(CONF_LATITUDE, default=lat): float,
                vol.Optional(CONF_LONGITUDE, default=lon): float,
                vol.Optional("search_range", default=1.5): float,
                vol.Optional("unit", default="miles"): vol.In(["miles", "kilometers"]),
                vol.Optional("weighted", default=True): bool,
                vol.Optional("sensor_index"): int,
                vol.Optional("read_key"): str,
                vol.Optional("conversion", default="US EPA"): vol.In(CONVERSION_OPTIONS),
                vol.Optional("update_interval", default=10): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)


class PurpleAirAQIOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            data = {**self._entry.data, **user_input}
            self.hass.config_entries.async_update_entry(self._entry, data=data, options={})
            return self.async_create_entry(title="", data={})

        data = self._entry.data

        schema = vol.Schema(
            {
                vol.Optional("conversion", default=data.get("conversion", "US EPA")): vol.In(
                    CONVERSION_OPTIONS
                ),
                vol.Optional("update_interval", default=data.get("update_interval", 10)): int,
                vol.Optional("weighted", default=data.get("weighted", True)): bool,
            }
        )

        return self.async_show_form(step_id="options", data_schema=schema)
