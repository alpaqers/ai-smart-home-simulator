import asyncio
from dataclasses import dataclass


@dataclass
class StateChangeRecord:
    device_id: int
    timestamp: int
    parameters: dict[str, str]
    device_type: int


class DeviceStateHistory:
    def __init__(self) -> None:
        self._by_device: dict[int, list[StateChangeRecord]] = {}
        self._lock = asyncio.Lock()

    async def append(self, record: StateChangeRecord) -> None:
        async with self._lock:
            self._by_device.setdefault(record.device_id, []).append(record)

    async def history_for(self, device_id: int) -> list[StateChangeRecord]:
        async with self._lock:
            return list(self._by_device.get(device_id, []))