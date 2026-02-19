from .connection_manager import ConnectionManager
from .modules.text import TextModule
from .screensize import ScreenSize

class IDotMatrixClient:
    """
    Client for interacting with the iDotMatrix device.
    """

    def __init__(
        self,
        screen_size: ScreenSize,
        mac_address: str,
    ):
        """
        Initializes the IDotMatrix client with the specified screen size and optional MAC address.

        Args:
            screen_size (ScreenSize): The size of the screen, e.g., ScreenSize.SIZE_64x64.
            mac_address (str): The Bluetooth MAC address of the iDotMatrix device.
        """
        self._connection_manager = ConnectionManager(
            address=mac_address,
        )
        self._connection_manager.address = mac_address
        self.screen_size = screen_size
        self.mac_address = mac_address

    @property
    def text(self) -> TextModule:
        return TextModule(
            connection_manager=self._connection_manager,
        )

    async def connect(self):
        """
        Connect to the IDotMatrix device.
        """
        await self._connection_manager.connect_by_address(self.mac_address)

    async def disconnect(self):
        """
        Disconnect from the IDotMatrix device.
        """
        await self._connection_manager.disconnect()
