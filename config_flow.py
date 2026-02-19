"""Config flow for the iDotMatrix integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, FlowResult
from homeassistant.const import CONF_NAME
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)

from .const import (
    DOMAIN,
    DEFAULT_DEVICE_NAME,
    CONF_MAC,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iDotMatrix."""

    VERSION = 1

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle Bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.discovery_info = discovery_info
        
        # Good UX: show the device name in the confirmation dialog
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            # Store whatever you need to connect later.
            # Address is usually enough for BLE.
            name = self.discovery_info.name or DEFAULT_DEVICE_NAME
            return self.async_create_entry(
                title=name,
                data={
                    CONF_NAME: name,
                    CONF_MAC: self.discovery_info.address,
                },
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self.discovery_info.name},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                address = user_input[CONF_MAC]
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_DEVICE_NAME),
                    data={CONF_MAC: address, CONF_NAME: user_input.get(CONF_NAME, DEFAULT_DEVICE_NAME)},
                )
            except Exception as e:
                _LOGGER.exception("Unexpected exception in config flow")
                errors["base"] = "unknown"

        from homeassistant.components import bluetooth

        # Look for devices
        options = {}
        for service_info in bluetooth.async_discovered_service_info(self.hass):
             if service_info.name and str(service_info.name).startswith("IDM-"):
                 options[service_info.address] = f"{service_info.name} ({service_info.address})"

        if not options:
            # Fallback to manual entry
            schema = vol.Schema({
                vol.Required(CONF_MAC): str,
                vol.Optional(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
            })
        else:
            # Show list
            schema = vol.Schema({
                vol.Required(CONF_MAC): vol.In(list(options.keys())),
                vol.Optional(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
            })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )