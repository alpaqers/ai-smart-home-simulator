import asyncio
from asyncio import StreamWriter
from dataclasses import dataclass


@dataclass
class RegisteredDevice:
    device_id: int
    writer: StreamWriter
    device_type: int | str
    capabilities: dict[str, str]
    device_state: dict[str, str]
    timestamp: int


class DeviceRegistry:
    def __init__(self) -> None:
        self._devices_by_id: dict[int, RegisteredDevice] = {}
        self._device_id_by_writer: dict[int, int] = {}
        self._lock = asyncio.Lock()

    async def register(
        self,
        device_id: int,
        writer: StreamWriter,
        device_type: int | str,
        capabilities: dict[str, str],
        device_state: dict[str, str],
        timestamp: int,
    ) -> None:
        async with self._lock:
            entry = RegisteredDevice(
                device_id=device_id,
                writer=writer,
                device_type=device_type,
                capabilities=capabilities,
                device_state=device_state,
                timestamp=timestamp,
            )

            self._devices_by_id[device_id] = entry
            self._device_id_by_writer[id(writer)] = device_id

            print(f"[DeviceRegistry] Registered device {device_id}")

    async def get_by_device_id(self, device_id: int) -> RegisteredDevice | None:
        async with self._lock:
            return self._devices_by_id.get(device_id)

    async def get_writer(self, device_id: int) -> StreamWriter | None:
        async with self._lock:
            entry = self._devices_by_id.get(device_id)
            return entry.writer if entry else None

    async def unregister_by_writer(self, writer: StreamWriter) -> None:
        async with self._lock:
            writer_key = id(writer)
            device_id = self._device_id_by_writer.pop(writer_key, None)

            if device_id is None:
                return

            self._devices_by_id.pop(device_id, None)
            print(f"[DeviceRegistry] Unregistered device {device_id}")

    async def is_registered(self, device_id: int) -> bool:
        async with self._lock:
            return device_id in self._devices_by_id