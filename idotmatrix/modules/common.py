import logging
from datetime import datetime
from typing import Optional

from . import IDotMatrixModule


class CommonModule(IDotMatrixModule):
    """
    This class contains generic Bluetooth functions for the iDotMatrix.
    Based on the BleProtocolN.java file of the iDotMatrix Android App.
    """

    logging = logging.getLogger(__name__)

    async def turn_off(self):
        """
        Turns the screen off.

        Returns:
            bytearray: Command to be sent to the device.
        """
        data = bytearray(
            [
                5,
                0,
                7,
                1,
                0,
            ]
        )
        await self._send_bytes(data=data, response=True)

    async def turn_on(self):
        """
        Turns the screen on.

        Returns:
            bytearray: Command to be sent to the device.
        """
        data = bytearray(
            [
                5,
                0,
                7,
                1,
                1,
            ]
        )
        await self._send_bytes(data=data)
        """
        Rotates the screen 180 degrees.

        Args:
            flip (bool): False = normal, True = rotated. Defaults to True.
        """
        data = bytearray(
            [
                5,
                0,
                6,
                128,
                1 if flip else 0,
            ]
        )
        await self._send_bytes(data=data, response=True)
        """
        Sends a command that resets the device and its internals.
        Can fix issues that appear over time.

        Note:
            Credits to 8none1 for finding this method:
            https://github.com/8none1/idotmatrix/commit/1a08e1e9b82d78427ab1c896c24c2a7fb45bc2f0
        """
        reset_packets = [
            [
                bytes(bytearray.fromhex("04 00 03 80"))
            ]
        ]
        await self._send_packets(packets=reset_packets, response=True)