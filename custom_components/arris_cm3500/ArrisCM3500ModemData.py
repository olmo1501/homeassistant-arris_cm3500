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
            _LOGGER.error("Error during the login proccess, error %s", error)
            return False

    async def get_modem_status(self) -> dict:
        """Get modem status."""
        _LOGGER.debug("Getting modem status data")

        try:
            modem_raw_data = await self.get_raw_modem_status_data()
            modem_data = self.extract_data(modem_raw_data)
            return modem_data
        except Exception as error:
            _LOGGER.error(
                "Error during the modem status data retrieval proccess, error %s",
                error,
            )
            return {
                "error_message": error,
            }

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
                "Error during the raw modem status data retrieval proccess, error %s",
                error,
            )
            return {
                "status_code": None,
                "error_message": error,
            }

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

            # Find Downstream & Upstream tables
            tables = soup.find_all("table")  # Identify the table containing DCID values

            for table in tables:
                rows = table.find_all("tr")

                for row in rows:
                    cells = row.find_all("td")

                    if len(cells) == 9:  # Ensure enough columns exist
                        cell0 = cells[0].text.strip()
                        cell1 = cells[1].text.strip()
                        cell2 = cells[2].text.strip()
                        cell3 = cells[3].text.strip()
                        cell4 = cells[4].text.strip()
                        cell5 = cells[5].text.strip()
                        cell6 = cells[6].text.strip()
                        cell7 = cells[7].text.strip()
                        cell8 = cells[8].text.strip()

                        # Downstream_QAM
                        if "QAM" in cell5:
                            entry = {
                                "DCID": cell1,
                                "Frequency": self.clean_value(cell2),
                                "Power": self.clean_value(cell3),
                                "SNR": self.clean_value(cell4),
                                "Modulation": cell5,
                                "Correcteds": cell7,
                                "Uncorrectables": cell8,
                            }
                            response["Downstream_QAM"].append(entry)

                        # Downstream_OFDM
                        if "4K" in cell1:
                            entry = {
                                "DCID_OFDM": self.clean_value(cell0),
                                "FFT_Type": cell1,
                                "Channel_Width": cell2,
                                "Active_Subcarriers": cell3,
                                "First_Subcarrier": cell4,
                                "Last_Subcarrier": cell5,
                                "RxMER_Pilot": cell6,
                                "RxMER_PLC": cell7,
                                "RxMER_Data": cell8,
                            }
                            response["Downstream_OFDM"].append(entry)

                        # Upstream_OFDM
                        if "2K" in cell1:
                            entry = {
                                "UCID_OFDM": self.clean_value(cell0),
                                "FFT_Type": cell1,
                                "Channel_Width": cell2,
                                "Active_Subcarriers": cell3,
                                "First_Subcarrier": cell4,
                                "Last_Subcarrier": cell5,
                                "Tx_Power": cell6,
                            }
                            response["Upstream_OFDM"].append(entry)

                    if len(cells) == 7:  # Ensure enough columns exist
                        cell1 = cells[1].text.strip()
                        cell2 = cells[2].text.strip()
                        cell3 = cells[3].text.strip()
                        cell4 = cells[4].text.strip()
                        cell5 = cells[5].text.strip()
                        cell6 = cells[6].text.strip()

                        # Upstream_QAM
                        if "ATDMA" in cell4:
                            entry = {
                                "UCID": cell1,
                                "Frequency": self.clean_value(cell2),
                                "Power": self.clean_value(cell3),
                                "Channel_Type": cell4,
                                "Symbol_Rate": self.clean_value(cell5),
                                "Modulation": cell6,
                            }
                            response["Upstream_QAM"].append(entry)
            return response

        except Exception as error:
            _LOGGER.error(
                "Error during the raw data convertion, error %s",
                error,
            )
            return response

    def clean_value(self, value: str) -> float:
        # Use regex to remove anything that is not a number, period, or minus sign
        cleaned_value = re.sub(r"[^\d.-]", "", value)
        return cleaned_value
