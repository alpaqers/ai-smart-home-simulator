from asyncio import StreamWriter
from dataclasses import dataclass


@dataclass
class DeviceStateChangeEvent:
    device_id: int
    writer: StreamWriter


@dataclass
class DeviceResponseEvent:
    device_id: int
    writer: StreamWriter


@dataclass
class DeviceRegisterEvent:
    device_id: int
    writer: StreamWriter
