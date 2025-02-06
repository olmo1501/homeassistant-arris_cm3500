"""Arris CM3500 Modem Data."""

import logging
from bs4 import BeautifulSoup
import re

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class ArrisCM3500ModemData:
    """Main ArrisCM3500ModemData class to Arris CM3500 services."""

    def __init__(self, host: str, username: str, password: str) -> None:
        """Init ArrisCM3500ModemData class."""
        self.host = host
        self.username = username
        self.password = password
        self.cookies = None
        self.random_string = ""
        self.code = ""
        self.session = ClientSession()

    async def login(self) -> bool:
        """Start session."""
        _LOGGER.debug("Initiating new login")

        try:
            payload = {
                "username": self.username,
                "password": self.password,
            }
            url = "https://" + self.host + "/cgi-bin/login_cgi"

            async with self.session.post(
                url, data=payload, verify_ssl=False
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", self.session.headers)
                _LOGGER.debug("Response headers: %s", response.headers)
                if response.status == 200:
                    response_text = await response.text()
                    _LOGGER.debug("Response: %s", response_text)
                    if "url=status_cgi" in response_text:
                        self.cookies = response.cookies
                        return True
                else:
                    response_text = await response.text()
                    _LOGGER.error("Failed to login")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_text,
                    )
                return False
        except Exception as error:
            _LOGGER.error("Error during the login process, error %s", error)
            return False

    async def get_modem_status(self) -> dict:
        """Get modem status."""
        _LOGGER.debug("Getting modem status data")

        try:
            modem_raw_data = await self.get_raw_modem_status_data()
            if "login_failed" in modem_raw_data:
                return modem_raw_data
            modem_data = self.extract_data(modem_raw_data)
            return modem_data
        except Exception as error:
            _LOGGER.error(
                "Error during the modem status data retrieval process, error %s", error
            )
            return {"error_message": error}

    async def get_raw_modem_status_data(self) -> str:
        """Get raw modem status data."""
        _LOGGER.debug("Getting raw modem status data")

        try:
            if not await self.login():
                return "login_failed"

            url = "https://" + self.host + "/cgi-bin/status_cgi"

            async with self.session.get(
                url, cookies=self.cookies, verify_ssl=False
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", self.session.headers)
                _LOGGER.debug("Response headers: %s", response.headers)
                if response.status == 200:
                    response_text = await response.text()
                    _LOGGER.debug("Response: %s", response_text)
                    if "Touchstone Status" in response_text:
                        return response_text
                    else:
                        return "error"
                else:
                    response_text = await response.text()
                    _LOGGER.error("Failed to retrieve raw modem status data")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_text,
                    )
                return False
        except Exception as error:
            _LOGGER.error(
                "Error during the raw modem status data retrieval process, error %s",
                error,
            )
            return {"status_code": None, "error_message": error}

    def extract_data(self, raw_response: str) -> dict:
        """Extract data from HTML code."""
        _LOGGER.debug("Extracting data from HTML code")

        response = {
            "Downstream_QAM": [],
            "Downstream_OFDM": [],
            "Upstream_QAM": [],
            "Upstream_OFDM": [],
        }

        try:
            soup = BeautifulSoup(raw_response, "html.parser")
            tables = soup.find_all("table")

            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) == 9:
                        (
                            cell0,
                            cell1,
                            cell2,
                            cell3,
                            cell4,
                            cell5,
                            cell6,
                            cell7,
                            cell8,
                        ) = [c.text.strip() for c in cells]

                        if "QAM" in cell5:
                            response["Downstream_QAM"].append(
                                {
                                    "DCID": cell1,
                                    "Frequency": self.clean_value(cell2),
                                    "Power": self.clean_value(cell3),
                                    "SNR": self.clean_value(cell4),
                                    "Modulation": cell5,
                                    "Correcteds": self.clean_value(cell7),
                                    "Uncorrectables": self.clean_value(cell8),
                                }
                            )

                        if "4K" in cell1:
                            response["Downstream_OFDM"].append(
                                {
                                    "DCID_OFDM": self.clean_value(cell0),
                                    "FFT_Type": cell1,
                                    "Channel_Width": self.clean_value(cell2),
                                    "Active_Subcarriers": self.clean_value(cell3),
                                    "First_Subcarrier": self.clean_value(cell4),
                                    "Last_Subcarrier": self.clean_value(cell5),
                                    "RxMER_Pilot": self.clean_value(cell6),
                                    "RxMER_PLC": self.clean_value(cell7),
                                    "RxMER_Data": self.clean_value(cell8),
                                }
                            )

                        if "2K" in cell1:
                            response["Upstream_OFDM"].append(
                                {
                                    "UCID_OFDM": self.clean_value(cell0),
                                    "FFT_Type": cell1,
                                    "Channel_Width": self.clean_value(cell2),
                                    "Active_Subcarriers": self.clean_value(cell3),
                                    "First_Subcarrier": self.clean_value(cell4),
                                    "Last_Subcarrier": self.clean_value(cell5),
                                    "Tx_Power": self.clean_value(cell6),
                                }
                            )

                    if len(cells) == 7:
                        cell1, cell2, cell3, cell4, cell5, cell6 = [
                            c.text.strip() for c in cells[1:]
                        ]

                        if "ATDMA" in cell4:
                            response["Upstream_QAM"].append(
                                {
                                    "UCID": cell1,
                                    "Frequency": self.clean_value(cell2),
                                    "Power": self.clean_value(cell3),
                                    "Channel_Type": cell4,
                                    "Symbol_Rate": self.clean_value(cell5),
                                    "Modulation": cell6,
                                }
                            )

            # Add missing channels with default values
            for dcid in range(1, 33):
                if not any(
                    ch["DCID"] == str(dcid) for ch in response["Downstream_QAM"]
                ):
                    response["Downstream_QAM"].append(
                        {
                            "DCID": str(dcid),
                            "Frequency": 0,
                            "Power": 0,
                            "SNR": 0,
                            "Modulation": "N/A",
                            "Correcteds": 0,
                            "Uncorrectables": 0,
                        }
                    )

            for ucid in range(1, 9):
                if not any(ch["UCID"] == str(ucid) for ch in response["Upstream_QAM"]):
                    response["Upstream_QAM"].append(
                        {
                            "UCID": str(ucid),
                            "Frequency": 0,
                            "Power": 0,
                            "Channel_Type": "N/A",
                            "Symbol_Rate": 0,
                            "Modulation": "N/A",
                        }
                    )

            for dcid_ofdm in range(1, 3):
                if not any(
                    ch["DCID_OFDM"] == str(dcid_ofdm)
                    for ch in response["Downstream_OFDM"]
                ):
                    response["Downstream_OFDM"].append(
                        {
                            "DCID_OFDM": str(dcid_ofdm),
                            "FFT_Type": "N/A",
                            "Channel_Width": 0,
                            "Active_Subcarriers": 0,
                            "First_Subcarrier": 0,
                            "Last_Subcarrier": 0,
                            "RxMER_Pilot": 0,
                            "RxMER_PLC": 0,
                            "RxMER_Data": 0,
                        }
                    )

            for ucid_ofdm in range(0, 2):
                if not any(
                    ch["UCID_OFDM"] == str(ucid_ofdm)
                    for ch in response["Upstream_OFDM"]
                ):
                    response["Upstream_OFDM"].append(
                        {
                            "UCID_OFDM": str(ucid_ofdm),
                            "FFT_Type": "N/A",
                            "Channel_Width": 0,
                            "Active_Subcarriers": 0,
                            "First_Subcarrier": 0,
                            "Last_Subcarrier": 0,
                            "Tx_Power": 0,
                        }
                    )

            return response

        except Exception as error:
            _LOGGER.error("Error during the raw data conversion, error %s", error)
            return response

    def clean_value(self, value: str) -> float:
        cleaned_value = re.sub(r"[^\d.-]", "", value)
        return float(cleaned_value) if cleaned_value else 0
