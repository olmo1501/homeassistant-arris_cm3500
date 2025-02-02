"""Sensor platform for Arris CM3500 integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ArrisCM3500ModemCoordinator
from .const import COORDINATOR, DOMAIN
from .ArrisCM3500ModemEntity import ArrisCM3500ModemEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Arris CM3500 config entry."""
    coordinator: ArrisCM3500ModemCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR
    ]

    if coordinator.modem:
        async_add_entities(
            ArrisCM3500ModemSensor(
                hass=hass,
                config_entry=config_entry,
                coordinator=coordinator,
                attr=entity.attr,
                name=entity.name,
                icon=entity.icon,
                unit=entity.unit,
                device_class=entity.device_class,
                value=getattr(coordinator.modem, entity.attr),
                state_class=entity.state_class,
                display_precision=entity.display_precision,
            )
            for entity in (
                entity
                for entity in coordinator.entities_list
                if entity.component == "sensor"
            )
        )


class ArrisCM3500ModemSensor(ArrisCM3500ModemEntity, SensorEntity):
    """ArrisCM3500Modem Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        coordinator: str,
        attr: str,
        name: str,
        icon: str,
        unit: str,
        device_class: str,
        value: str,
        state_class: str,
        display_precision: int,
    ) -> None:
        """Initialize ArrisCM3500Modem Sensor."""
        super().__init__(
            config_entry=config_entry,
            coordinator=coordinator,
            attr=attr,
        )
        self.hass = hass
        self.config_entry = config_entry
        self.coordinator = coordinator
        self.attr = attr
        self._attr_name = name
        self._attr_unique_id = f"arris_cm3500_{attr}"
        self._attr_has_entity_name = True
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_available = True
        self._attr_native_value = value
        self._attr_should_poll = False
        self._attr_suggested_display_precision = display_precision
        self.entity_id = f"sensor.arris_cm3500_{attr}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self.coordinator.modem, self.attr)
        self.async_write_ha_state()
