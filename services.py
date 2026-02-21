"""Services for the iDotMatrix integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .hub import IDotMatrixHub

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_UPLOAD_GIF = "upload_gif"
SERVICE_SCREEN_ON = "screen_on"
SERVICE_SCREEN_OFF = "screen_off"

MEDIA_SOURCE_PREFIX = "media-source://media_source/local/"

UPLOAD_GIF_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
        vol.Required("media_file"): cv.string,
    }
)

SCREEN_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
    }
)

def _get_hub_for_entity(hass: HomeAssistant, entity_id: str) -> IDotMatrixHub | None:
    """Get the hub for the given entity_id."""
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)
    if not entity_entry or not entity_entry.config_entry_id:
        return None
    return hass.data.get(DOMAIN, {}).get(entity_entry.config_entry_id)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the iDotMatrix integration."""
    if hass.services.has_service(DOMAIN, SERVICE_UPLOAD_GIF):
        return

    async def handle_screen_on(call: ServiceCall) -> None:
        """Handle screen_on service call."""
        for entity_id in call.data["entity_id"]:
            hub = _get_hub_for_entity(hass, entity_id)
            if hub is None:
                _LOGGER.warning("Could not find iDotMatrix device for entity %s", entity_id)
                continue
            try:
                await hub.async_screen_on()
                _LOGGER.info("Screen turned on for %s", entity_id)
            except TimeoutError:
                _LOGGER.error("Timeout turning screen on for %s", entity_id)
            except Exception:
                _LOGGER.exception("Failed to turn screen on for %s", entity_id)

    async def handle_screen_off(call: ServiceCall) -> None:
        """Handle screen_off service call."""
        for entity_id in call.data["entity_id"]:
            hub = _get_hub_for_entity(hass, entity_id)
            if hub is None:
                _LOGGER.warning("Could not find iDotMatrix device for entity %s", entity_id)
                continue
            try:
                await hub.async_screen_off()
                _LOGGER.info("Screen turned off for %s", entity_id)
            except TimeoutError:
                _LOGGER.error("Timeout turning screen off for %s", entity_id)
            except Exception:
                _LOGGER.exception("Failed to turn screen off for %s", entity_id)

    async def handle_upload_gif(call: ServiceCall) -> None:
        """Handle upload_gif service call."""
        entity_ids = call.data["entity_id"]
        media_file = call.data["media_file"].strip().lstrip("/")
        media_content_id = f"{MEDIA_SOURCE_PREFIX}{media_file}"

        from homeassistant.components.media_source import async_resolve_media

        try:
            resolved = await async_resolve_media(
                hass,
                media_content_id,
                entity_ids[0] if entity_ids else None,
            )
            if resolved.path is None:
                _LOGGER.error(
                    "Media could not be resolved to a file path (e.g. not from local storage)"
                )
                return
            file_path = str(resolved.path)
        except Exception as err:
            _LOGGER.exception("Failed to resolve media: %s", err)
            return

        for entity_id in entity_ids:
            hub = _get_hub_for_entity(hass, entity_id)
            if hub is None:
                _LOGGER.warning("Could not find iDotMatrix device for entity %s", entity_id)
                continue
            try:
                await hub.async_upload_gif(file_path)
                _LOGGER.info("GIF uploaded to %s", entity_id)
            except TimeoutError:
                _LOGGER.error("Timeout uploading GIF to %s", entity_id)
            except Exception:
                _LOGGER.exception("Failed to upload GIF to %s", entity_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPLOAD_GIF,
        handle_upload_gif,
        schema=UPLOAD_GIF_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCREEN_ON,
        handle_screen_on,
        schema=SCREEN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCREEN_OFF,
        handle_screen_off,
        schema=SCREEN_SCHEMA,
    )
