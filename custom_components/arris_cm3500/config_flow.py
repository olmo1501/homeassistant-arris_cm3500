"""Config flow for Arris CM3500 integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DEFAULT_HOST,
)

from .const import DOMAIN
from .ArrisCM3500ModemData import ArrisCM3500ModemData

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("host", default=DEFAULT_HOST): str,
        vol.Required("username"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
        ),
        vol.Required("password"): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
    }
)


class ArrisCM3500ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle user step."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    reauth_entry: ConfigEntry | None = None

    def __init__(self) -> None:
        """Initialize."""
        self.data = None
        self.host = None
        self.username = None
        self.password = None

    async def async_step_user(self, user_input=None):
        """Handle login step."""
        errors = {}

        if user_input is not None:
            try:
                # Store the username and password in the user_input to pass it to the next step
                self.host = user_input[CONF_HOST]
                self.username = user_input[CONF_USERNAME]
                self.password = user_input[CONF_PASSWORD]

                # Perform login using the provided credentials
                self.data = ArrisCM3500ModemData(
                    self.host, self.username, self.password
                )
                response = await self.data.login()

                if response:
                    # Create the config entry with the collected data
                    return self.async_create_entry(
                        title=self.host,
                        data={
                            "host": self.host,
                            "username": self.username,
                            "password": self.password,
                        },
                    )
                else:
                    errors["base"] = "login_failed"

            except Exception as e:
                _LOGGER.error("Error during login: %s", str(e))
                errors["base"] = "login_failed"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input=None) -> dict:
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> dict:
        """Dialog that informs the user that reauth is required."""
        errors = {}

        if user_input is not None:
            try:
                # Store the username and password in the user_input to pass it to the next step
                self.host = user_input[CONF_HOST]
                self.username = user_input[CONF_USERNAME]
                self.password = user_input[CONF_PASSWORD]

                # Perform login using the provided credentials
                self.data = ArrisCM3500ModemData(
                    self.host, self.username, self.password
                )
                response = await self.data.login()

                if response:
                    data = self.reauth_entry.data.copy()
                    self.hass.config_entries.async_update_entry(
                        self.reauth_entry,
                        data={
                            **data,
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )
                    self.hass.async_create_task(
                        self.hass.config_entries.async_reload(
                            self.reauth_entry.entry_id
                        )
                    )

                    return self.async_abort(reason="reauth_successful")
                errors["base"] = "login_failed"

            except Exception as e:
                _LOGGER.error("Error during login: %s", str(e))
                errors["base"] = "login_failed"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=self.reauth_entry.data[DEFAULT_HOST]
                    ): str,
                    vol.Required(
                        CONF_USERNAME, default=self.reauth_entry.data[CONF_USERNAME]
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
