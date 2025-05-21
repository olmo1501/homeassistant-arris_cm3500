import datetime
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ArrisCM3500ModemDashboard:
    """Init ArrisCM3500Modem coordinator class."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, modem_data: dict
    ) -> None:
        """Initialize ArrisCM3500Modem coordinator."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        self.modem_data = modem_data

        # Create lookup tables for faster access
        self.downstream_qam_lookup = {
            str(ch.get("DCID")): ch for ch in modem_data.get("Downstream_QAM", [])
        }
        self.upstream_qam_lookup = {
            str(ch.get("UCID")): ch for ch in modem_data.get("Upstream_QAM", [])
        }
        self.downstream_ofdm_lookup = {
            str(ch.get("DCID_OFDM")): ch for ch in modem_data.get("Downstream_OFDM", [])
        }
        self.upstream_ofdm_lookup = {
            str(ch.get("UCID_OFDM")): ch for ch in modem_data.get("Upstream_OFDM", [])
        }

    def get_value(self, lookup, channel_id, key):
        """Generic method to get the value for modem data."""
        return lookup.get(str(channel_id), {}).get(key)


# Helper function to dynamically create properties
def create_properties(cls, prefix, id_range, keys, getter_func):
    for channel_id in id_range:
        for key in keys:
            attr_name = f"{prefix}_{channel_id}_{key.lower()}"
            last_update_attr = f"{attr_name}_last_update"
            supported_attr = f"is_{attr_name}_supported"

            # Property to get the value
            def getter(self, channel_id=channel_id, key=key):
                return getter_func(self, channel_id, key)

            # Property to get the last update timestamp
            def last_update(self):
                return datetime.datetime.now(datetime.UTC)

            # Property to check if supported
            def is_supported(self):
                return True

            setattr(cls, attr_name, property(getter))
            setattr(cls, last_update_attr, property(last_update))
            setattr(cls, supported_attr, property(is_supported))


# Apply properties to the class
create_properties(
    ArrisCM3500ModemDashboard,
    "dcid",
    range(1, 33),
    ["Frequency", "Power", "SNR", "Modulation", "Correcteds", "Uncorrectables"],
    lambda self, dcid, key: self.get_value(self.downstream_qam_lookup, dcid, key),
)

create_properties(
    ArrisCM3500ModemDashboard,
    "ucid",
    range(1, 13),
    ["Frequency", "Power", "Channel_Type", "Symbol_Rate", "Modulation"],
    lambda self, ucid, key: self.get_value(self.upstream_qam_lookup, ucid, key),
)

create_properties(
    ArrisCM3500ModemDashboard,
    "dcid_ofdm",
    range(1, 3),
    [
        "FFT_Type",
        "Channel_Width",
        "Active_Subcarriers",
        "First_Subcarrier",
        "Last_Subcarrier",
        "RxMER_Pilot",
        "RxMER_PLC",
        "RxMER_Data",
    ],
    lambda self, dcid_ofdm, key: self.get_value(
        self.downstream_ofdm_lookup, dcid_ofdm, key
    ),
)

create_properties(
    ArrisCM3500ModemDashboard,
    "ucid_ofdm",
    range(0, 2),
    [
        "FFT_Type",
        "Channel_Width",
        "Active_Subcarriers",
        "First_Subcarrier",
        "Last_Subcarrier",
        "Lower_Frequency",
        "Upper_Frequency",
        "Tx_Power",
    ],
    lambda self, ucid_ofdm, key: self.get_value(
        self.upstream_ofdm_lookup, ucid_ofdm, key
    ),
)
