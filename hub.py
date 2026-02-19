"""Runtime hub coordinating BLE communication and device operations."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from .idotmatrix.client import IDotMatrixClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class IDotMatrixHub:
    client: IDotMatrixClient

    def __post_init__(self) -> None:
        self._lock = asyncio.Lock()

    async def async_send_text(self, text: str) -> None:
        async with self._lock:
            _LOGGER.debug("Sending text to %s", self.client.mac_address)
            await self.client.connect()
            try:
                await self.client.text.show_text(text)
                _LOGGER.debug("Text sent successfully to %s", self.client.mac_address)
            finally:
                await self.client.disconnect()
