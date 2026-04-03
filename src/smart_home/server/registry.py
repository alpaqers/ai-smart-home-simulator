from asyncio import StreamWriter

#Simple device reegistry file which will require more work in a future (registers only device)
# We could add unregistering devices or checking their status (?) idk xd
class DeviceRegistry:
    def __init__(self) -> None:
        self._devices: dict[int, StreamWriter] = {}

    def register(self, device_id: int, writer: StreamWriter) -> None:
        self._devices[device_id] = writer
        print(f"[Registry] Registered device_id={device_id}")