"""The iDotMatrix integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .idotmatrix.client import IDotMatrixClient
from .idotmatrix.screensize import ScreenSize
from .hub import IDotMatrixHub

from .const import (
    DOMAIN,
    CONF_MAC,
)

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.TEXT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iDotMatrix from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = IDotMatrixClient(
        screen_size=ScreenSize.SIZE_64x64,
        mac_address=entry.data[CONF_MAC],
    )

    hass.data[DOMAIN][entry.entry_id] = IDotMatrixHub(client=client)
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    _LOGGER.info("Setup complete for %s", entry.data[CONF_MAC])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if unload_ok:
        hub: IDotMatrixHub | None = hass.data[DOMAIN].pop(entry.entry_id, None)
        if hub:
            try:
                await hub.client.disconnect()
            except Exception as err:
                _LOGGER.warning("Error disconnecting from %s: %s", entry.data[CONF_MAC], err)
    return unload_ok