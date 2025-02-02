"""Arris CM3500 Entities."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

from .ArrisCM3500ModemDashboard import ArrisCM3500ModemDashboard

_LOGGER = logging.getLogger(__name__)


class BaseEntity:
    """Base class for all components."""

    modem: ArrisCM3500ModemDashboard

    def __init__(
        self,
        component,
        attr: str,
        name: str,
        icon: str | None = None,
        entity_type: EntityCategory | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        display_precision: int | None = None,
    ) -> None:
        """Init."""
        self.attr = attr
        self.component = component
        self.name = name
        self.icon = icon
        self.entity_type = entity_type
        self.device_class = device_class
        self.state_class = state_class
        self.display_precision = display_precision

    def setup(self, modem: ArrisCM3500ModemDashboard) -> bool:
        """Set up entity if supported."""
        self.modem = modem
        if not self.is_supported:
            _LOGGER.debug("%s %s is not supported", type(self).__name__, self.attr)
            return False

        _LOGGER.debug("%s %s is supported", type(self).__name__, self.attr)
        return True

    @property
    def is_supported(self) -> bool:
        """Check entity is supported."""
        supported = "is_" + self.attr + "_supported"
        if hasattr(self.modem, supported):
            return getattr(self.modem, supported)
        return False


class Sensor(BaseEntity):
    """Base class for sensor type entities."""

    def __init__(
        self,
        attr: str,
        name: str,
        icon: str | None,
        unit: str | None,
        entity_type: EntityCategory | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        display_precision: int | None = None,
    ) -> None:
        """Init."""
        super().__init__(
            component="sensor",
            attr=attr,
            name=name,
            icon=icon,
            entity_type=entity_type,
            device_class=device_class,
            state_class=state_class,
            display_precision=display_precision,
        )
        self.unit = unit


# Function to create sensors
def create_sensors(modem):
    sensors = []
    #
    # Downstream_QAM
    #
    for channel in modem.modem_data.get("Downstream_QAM", []):
        dcid = channel.get("DCID")
        attributes = {
            "Frequency": {
                "icon": "mdi:sine-wave",
                "unit": "MHz",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Power": {
                "icon": "mdi:flash",
                "unit": "dBmV",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 2,
            },
            "SNR": {
                "icon": "mdi:signal",
                "unit": "dB",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 2,
            },
            "Modulation": {
                "icon": "mdi:chart-line",
                "unit": None,
                "device_class": None,
                "precision": None,
            },
            "Correcteds": {
                "icon": "mdi:check",
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Uncorrectables": {
                "icon": "mdi:alert-circle",
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
        }

        for key, details in attributes.items():
            sensors.append(
                Sensor(
                    attr=f"dcid_{dcid}_{key.lower()}",
                    name=f"DCID {dcid} {key}",
                    icon=details["icon"],
                    unit=details["unit"],
                    state_class=details["device_class"],
                    display_precision=details["precision"],
                )
            )

    #
    # Upstream_QAM
    #
    for channel in modem.modem_data.get("Upstream_QAM", []):
        ucid = channel.get("UCID")
        attributes = {
            "Frequency": {
                "icon": "mdi:sine-wave",
                "unit": "MHz",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Power": {
                "icon": "mdi:flash",
                "unit": "dBmV",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 2,
            },
            "Channel_Type": {
                "icon": "mdi:lan",
                "unit": None,
                "device_class": None,
                "precision": None,
            },
            "Symbol_Rate": {
                "icon": "mdi:swap-vertical",
                "unit": "kSym/s",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Modulation": {
                "icon": "mdi:chart-line",
                "unit": None,
                "device_class": None,
                "precision": None,
            },
        }

        for key, details in attributes.items():
            sensors.append(
                Sensor(
                    attr=f"ucid_{ucid}_{key.lower()}",
                    name=f"UCID {ucid} {key}",
                    icon=details["icon"],
                    unit=details["unit"],
                    state_class=details["device_class"],
                    display_precision=details["precision"],
                )
            )

    #
    # Downstream_OFDM
    #
    for channel in modem.modem_data.get("Downstream_OFDM", []):
        dcid_ofdm = channel.get("DCID_OFDM")
        attributes = {
            "FFT_Type": {
                "icon": "mdi:waveform",  # Represents frequency domain processing
                "unit": None,
                "device_class": None,
                "precision": None,
            },
            "Channel_Width": {
                "icon": "mdi:arrow-expand-horizontal",  # Shows width measurement
                "unit": "MHz",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Active_Subcarriers": {
                "icon": "mdi:radio-tower",  # Represents active frequency carriers
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "First_Subcarrier": {
                "icon": "mdi:skip-forward",  # Indicates the first subcarrier in sequence
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Last_Subcarrier": {
                "icon": "mdi:skip-backward",  # Indicates the last subcarrier in sequence
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "RxMER_Pilot": {
                "icon": "mdi:chart-bar",  # Represents measurement or pilot metrics
                "unit": "dB",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "RxMER_PLC": {
                "icon": "mdi:chart-scatter-plot",  # Shows error metrics (PLC-specific)
                "unit": "dB",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "RxMER_Data": {
                "icon": "mdi:database",  # Represents data-specific MER metrics
                "unit": "dB",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
        }

        for key, details in attributes.items():
            sensors.append(
                Sensor(
                    attr=f"dcid_ofdm_{dcid_ofdm}_{key.lower()}",
                    name=f"DCID OFDM {dcid_ofdm} {key}",
                    icon=details["icon"],
                    unit=details["unit"],
                    state_class=details["device_class"],
                    display_precision=details["precision"],
                )
            )

    #
    # Upstream_OFDM
    #
    for channel in modem.modem_data.get("Upstream_OFDM", []):
        ucid_ofdm = channel.get("UCID_OFDM")
        attributes = {
            "FFT_Type": {
                "icon": "mdi:waveform",  # Represents frequency domain processing
                "unit": None,
                "device_class": None,
                "precision": None,
            },
            "Channel_Width": {
                "icon": "mdi:arrow-expand-horizontal",  # Shows width measurement
                "unit": "MHz",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Active_Subcarriers": {
                "icon": "mdi:radio-tower",  # Represents active frequency carriers
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "First_Subcarrier": {
                "icon": "mdi:skip-forward",  # Indicates the first subcarrier in sequence
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Last_Subcarrier": {
                "icon": "mdi:skip-backward",  # Indicates the last subcarrier in sequence
                "unit": "#",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 0,
            },
            "Tx_Power": {
                "icon": "mdi:flash",  # Indicates transmission power
                "unit": "dBmV",
                "device_class": SensorStateClass.MEASUREMENT,
                "precision": 1,
            },
        }

        for key, details in attributes.items():
            sensors.append(
                Sensor(
                    attr=f"ucid_ofdm_{ucid_ofdm}_{key.lower()}",
                    name=f"UCID OFDM {ucid_ofdm} {key}",
                    icon=details["icon"],
                    unit=details["unit"],
                    state_class=details["device_class"],
                    display_precision=details["precision"],
                )
            )
    return sensors


class ArrisCM3500ModemEntities:
    """Class for accessing the entities."""

    def __init__(self, modem) -> None:
        """Initialize instruments."""
        self.entities_list = [
            entity for entity in create_sensors(modem) if entity.setup(modem)
        ]
