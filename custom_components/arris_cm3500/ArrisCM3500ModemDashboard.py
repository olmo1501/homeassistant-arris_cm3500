"""Arris CM3500 Dashboard."""

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ArrisCM3500ModemDashboard:
    """Init ArrisCM3500Modem coordinator class."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        modem_data: dict,
    ) -> None:
        """Initialize ArrisCM3500Modem coordinator."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        self.modem_data = modem_data

    def get_download_qam_value(self, dcid, key):
        """Return value for the usage data."""
        for channel in self.modem_data.get("Downstream_QAM", []):
            if str(channel.get("DCID")) == str(dcid):
                return channel.get(key)
        return None

    def get_upstream_qam_value(self, dcid, key):
        """Return value for the usage data."""
        for channel in self.modem_data.get("Upstream_QAM", []):
            if str(channel.get("UCID")) == str(dcid):
                return channel.get(key)
        return None

    def get_download_ofdm_value(self, dcid_ofdm, key):
        """Return value for the usage data."""
        for channel in self.modem_data.get("Downstream_OFDM", []):
            if str(channel.get("DCID_OFDM")) == str(dcid_ofdm):
                return channel.get(key)
        return None

    def get_upload_ofdm_value(self, ucid_ofdm, key):
        """Return value for the usage data."""
        for channel in self.modem_data.get("Upstream_OFDM", []):
            if str(channel.get("UCID_OFDM")) == str(ucid_ofdm):
                return channel.get(key)
        return None


#
# Downstream_QAM
#
for dcid in range(1, 33):
    for key in [
        "Frequency",
        "Power",
        "SNR",
        "Modulation",
        "Correcteds",
        "Uncorrectables",
    ]:
        attr_name = f"dcid_{dcid}_{key.lower()}"
        last_update_attr = f"dcid_{dcid}_{key.lower()}_last_update"
        supported_attr = f"is_dcid_{dcid}_{key.lower()}_supported"

        # Property to get the value
        def getter(self, dcid=dcid, key=key):
            return self.get_download_qam_value(str(dcid), key)

        # Property to get the last update timestamp
        def last_update(self):
            return datetime.datetime.now(datetime.UTC)

        # Property to check if supported
        def is_supported(self, dcid=dcid, key=key):
            return self.get_download_qam_value(str(dcid), key) is not None

        setattr(ArrisCM3500ModemDashboard, attr_name, property(getter))
        setattr(ArrisCM3500ModemDashboard, last_update_attr, property(last_update))
        setattr(ArrisCM3500ModemDashboard, supported_attr, property(is_supported))

#
# Upstream_QAM
#
for ucid in range(1, 9):
    for key in ["Frequency", "Power", "Channel_Type", "Symbol_Rate", "Modulation"]:
        attr_name = f"ucid_{ucid}_{key.lower()}"
        last_update_attr = f"ucid_{ucid}_{key.lower()}_last_update"
        supported_attr = f"is_ucid_{ucid}_{key.lower()}_supported"

        # Property to get the value
        def getter(self, ucid=ucid, key=key):
            return self.get_upstream_qam_value(str(ucid), key)

        # Property to get the last update timestamp
        def last_update(self):
            return datetime.datetime.now(datetime.UTC)

        # Property to check if supported
        def is_supported(self, ucid=ucid, key=key):
            return self.get_upstream_qam_value(str(ucid), key) is not None

        setattr(ArrisCM3500ModemDashboard, attr_name, property(getter))
        setattr(ArrisCM3500ModemDashboard, last_update_attr, property(last_update))
        setattr(ArrisCM3500ModemDashboard, supported_attr, property(is_supported))

#
# Downstream_OFDM
#
for dcid_ofdm in range(1, 3):
    for key in [
        "FFT_Type",
        "Channel_Width",
        "Active_Subcarriers",
        "First_Subcarrier",
        "Last_Subcarrier",
        "RxMER_Pilot",
        "RxMER_PLC",
        "RxMER_Data",
    ]:
        attr_name = f"dcid_ofdm_{dcid_ofdm}_{key.lower()}"
        last_update_attr = f"dcid_ofdm_{dcid_ofdm}_{key.lower()}_last_update"
        supported_attr = f"is_dcid_ofdm_{dcid_ofdm}_{key.lower()}_supported"

        # Property to get the value
        def getter(self, dcid_ofdm=dcid_ofdm, key=key):
            return self.get_download_ofdm_value(str(dcid_ofdm), key)

        # Property to get the last update timestamp
        def last_update(self):
            return datetime.datetime.now(datetime.UTC)

        # Property to check if supported
        def is_supported(self, dcid_ofdm=dcid_ofdm, key=key):
            return self.get_download_ofdm_value(str(dcid_ofdm), key) is not None

        setattr(ArrisCM3500ModemDashboard, attr_name, property(getter))
        setattr(ArrisCM3500ModemDashboard, last_update_attr, property(last_update))
        setattr(ArrisCM3500ModemDashboard, supported_attr, property(is_supported))

#
# Upstream_OFDM
#
for ucid_ofdm in range(0, 2):
    for key in [
        "FFT_Type",
        "Channel_Width",
        "Active_Subcarriers",
        "First_Subcarrier",
        "Last_Subcarrier",
        "Tx_Power",
    ]:
        attr_name = f"ucid_ofdm_{ucid_ofdm}_{key.lower()}"
        last_update_attr = f"ucid_ofdm_{ucid_ofdm}_{key.lower()}_last_update"
        supported_attr = f"is_ucid_ofdm_{ucid_ofdm}_{key.lower()}_supported"

        # Property to get the value
        def getter(self, ucid_ofdm=ucid_ofdm, key=key):
            return self.get_upload_ofdm_value(str(ucid_ofdm), key)

        # Property to get the last update timestamp
        def last_update(self):
            return datetime.datetime.now(datetime.UTC)

        # Property to check if supported
        def is_supported(self, ucid_ofdm=ucid_ofdm, key=key):
            return self.get_upload_ofdm_value(str(ucid_ofdm), key) is not None

        setattr(ArrisCM3500ModemDashboard, attr_name, property(getter))
        setattr(ArrisCM3500ModemDashboard, last_update_attr, property(last_update))
        setattr(ArrisCM3500ModemDashboard, supported_attr, property(is_supported))
