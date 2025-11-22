from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback

from . import DOMAIN

CONVERSION_OPTIONS = [
    "US EPA",
    "Woodsmoke",
    "AQ&U",
    "LRAPA",
    "CF=1",
    "none",
]


class PurpleAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for PurpleAir."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PurpleAirOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Initial setup."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="PurpleAir", data=user_input)

        # Defaults from HA location
        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        STEP_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required("device_search", default=True): bool,

                # Only used when device_search = True, but included in initial setup
                vol.Optional(CONF_LATITUDE, default=default_lat): vol.Coerce(float),
                vol.Optional(CONF_LONGITUDE, default=default_lon): vol.Coerce(float),

                vol.Optional(
                    "search_range", default=1.5
                ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=50)),

                vol.Optional("unit", default="miles"): vol.In(["miles", "kilometers"]),

                # Conversion & behavior
                vol.Optional("weighted", default=True): bool,
                vol.Optional("conversion", default="US EPA"): vol.In(CONVERSION_OPTIONS),
                vol.Optional("update_interval", default=10): vol.Coerce(int),

                # Optional for private sensors when device_search=False
                vol.Optional("sensor_index"): vol.Coerce(int),
                vol.Optional("read_key"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=STEP_SCHEMA)


class PurpleAirOptionsFlow(config_entries.OptionsFlow):
    """Options flow that allows editing limited parameters."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input: dict[str, Any] | None = None):
        """Edit options that should remain user-changeable."""
        entry = self._entry
        current = entry.data

        if user_input is not None:
            #
            # Merge updated option data back into entry.data
            # (We don't use entry.options because we want a single source of truth)
            #
            updated = {**current, **user_input}
            self.hass.config_entries.async_update_entry(
                entry,
                data=updated,
                options={}
            )
            return self.async_create_entry(title="", data={})

        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Optional(
                    "search_range",
                    default=current.get("search_range", 1.5),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=50)),

                vol.Optional(
                    "unit",
                    default=current.get("unit", "miles"),
                ): vol.In(["miles", "kilometers"]),

                vol.Optional(
                    "weighted",
                    default=current.get("weighted", True),
                ): bool,

                vol.Optional(
                    "conversion",
                    default=current.get("conversion", "US EPA"),
                ): vol.In(CONVERSION_OPTIONS),

                vol.Optional(
                    "update_interval",
                    default=current.get("update_interval", 10),
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="options", data_schema=OPTIONS_SCHEMA)
