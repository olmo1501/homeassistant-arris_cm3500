"""The Arris CM3500 integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    COORDINATOR,
    DATA_LISTENER,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .ArrisCM3500ModemData import ArrisCM3500ModemData
from .ArrisCM3500ModemDashboard import ArrisCM3500ModemDashboard
from .ArrisCM3500ModemEntities import ArrisCM3500ModemEntities

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up ArrisCM3500 from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    update_interval = timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

    coordinator = ArrisCM3500ModemCoordinator(hass, config_entry, update_interval)

    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)

        if DATA_LISTENER in entry_data:
            entry_data[DATA_LISTENER]()

        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ArrisCM3500ModemCoordinator(DataUpdateCoordinator):
    """Class to manage fetching mail data."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, update_interval: timedelta
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = config_entry
        self.modem = None
        self.modem_status_data = {}
        self.entities_list = None
        self.update_interval = update_interval
        self.modem_data = ArrisCM3500ModemData(
            config_entry.data.get(CONF_HOST),
            config_entry.data.get(CONF_USERNAME),
            config_entry.data.get(CONF_PASSWORD),
        )

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    async def _async_update_data(self):
        """Fetch data."""

        self.modem_status_data = await self.modem_data.get_modem_status()
        _LOGGER.debug("Fetching data...")
        if "login_failed" in self.modem_status_data:
            raise ConfigEntryAuthFailed("Credentials expired. Try to re-login.")
        _LOGGER.debug("New Data: %s", self.modem_status_data)
        return await self.update()

    async def update(self) -> ArrisCM3500ModemDashboard:
        """Update usage data from Arris CM3500."""

        self.modem = ArrisCM3500ModemDashboard(
            hass=self.hass,
            config_entry=self.config_entry,
            modem_data=self.modem_status_data,
        )
        if self.entities_list is None:
            self.entities_list = ArrisCM3500ModemEntities(self.modem).entities_list
        _LOGGER.debug(
            "Update is completed. Next update in %s",
            self.update_interval,
        )
        return None
