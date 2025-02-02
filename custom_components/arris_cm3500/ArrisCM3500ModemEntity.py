"""Arris CM3500 Entity."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ArrisCM3500ModemEntity(CoordinatorEntity, Entity):
    """Base class for all ArrisCM3500 entities."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: str,
        attr: str,
    ) -> None:
        """Initialize ArrisCM3500 base entity."""

        super().__init__(coordinator)

        self.config_entry = config_entry
        self.coordinator = coordinator
        self.attr = attr
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "Arris CM3500")},
            "name": "Arris CM3500",
            "model": "Arris CM3500",
            "manufacturer": "Arris",
        }

    @property
    def available(self) -> bool:
        """Return true if entity is supported."""
        return getattr(self.coordinator.modem, "is_" + self.attr + "_supported")
