"""Text platform for iDotMatrix."""

from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .hub import IDotMatrixHub

from .const import (
    DOMAIN,
    DEFAULT_DEVICE_NAME,
    CONF_MAC,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iDotMatrix text."""
    hub: IDotMatrixHub = hass.data[DOMAIN][entry.entry_id]
    name: str = entry.title or DEFAULT_DEVICE_NAME
    address: str = entry.data[CONF_MAC]
    _LOGGER.debug("Setting up text entity for %s (%s)", name, address)
    async_add_entities([IDotMatrixText(hub, name=name, address=address)])


class IDotMatrixText(TextEntity):
    """A Text entity that writes to the iDotMatrix display over BLE."""

    _attr_has_entity_name = True
    _attr_name = "Text"
    _attr_native_min = 0
    _attr_native_max = 255  # Keep small to start (BLE packet limits vary)
    _attr_icon = "mdi:dot-matrix"

    def __init__(self, hub: IDotMatrixHub, name: str, address: str) -> None:
        self._hub = hub
        self.name = name
        self.address = address

        self._attr_unique_id = f"{address}_text"
        self._attr_native_value = ""

        self._attr_suggested_object_id = name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.address)},
            name=self.name,
            manufacturer="iDotMatrix",
            model="Bluetooth Pixel Display",
            connections={("bluetooth", self.address)},
        )

    async def async_set_value(self, value: str) -> None:
        """Set text and push it to the device."""
        # Update state first for responsiveness
        self._attr_native_value = value
        self.async_write_ha_state()

        try:
            await self._hub.async_send_text(value)
            _LOGGER.debug("Text updated on %s", self.address)
        except TimeoutError:
            _LOGGER.error("Timeout connecting/writing to %s", self.address)
        except Exception:
            _LOGGER.exception("Failed to write text to %s", self.address)
