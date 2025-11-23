from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PurpleAirClient, PurpleAirConfig

DOMAIN = "purpleair"
PLATFORMS = ["sensor", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration (YAML config not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PurpleAir from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    conf = entry.data

    device_search = conf.get("device_search", True)
    sensor_index = conf.get("sensor_index")
    read_key = conf.get("read_key")

    coords = None
    if device_search:
        lat = float(conf.get("latitude"))
        lon = float(conf.get("longitude"))
        coords = (lat, lon)

    cfg = PurpleAirConfig(
        api_key=conf["api_key"],
        device_search=device_search,
        search_coords=coords,
        search_range=float(conf.get("search_range", 1.5)),
        unit=conf.get("unit", "miles"),
        weighted=conf.get("weighted", True),
        sensor_index=int(sensor_index) if sensor_index is not None else None,
        read_key=read_key,
        conversion=conf.get("conversion", "US EPA"),
        update_interval=int(conf.get("update_interval", 10)),
    )

    client = PurpleAirClient(session, cfg)

    async def async_update():
        try:
            return await client.fetch()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="PurpleAir",
        update_method=async_update,
        update_interval=timedelta(minutes=cfg.update_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store references properly
    hass.data[DOMAIN][entry.entry_id] = {
        "session": session,
        "coordinator": coordinator,
        "config": cfg,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload PurpleAir."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return unload_ok
