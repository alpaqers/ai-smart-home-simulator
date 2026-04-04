from asyncio import StreamWriter
from dataclasses import dataclass
from smart_home.proto.v1 import message_pb2

@dataclass
class DeviceStateChangeEvent:
    device_id: int
    writer: StreamWriter
    timestamp: int
    device_type: int
    parameters: dict[str, str]


@dataclass
class DeviceResponseEvent:
    device_id: int
    writer: StreamWriter
    timestamp: int
    success: bool
    message: str


@dataclass
class DeviceRegisterEvent:
    device_id: int
    writer: StreamWriter
    device_type: str
    capabilities: dict[str, str]
    device_state: dict[str, str]
    timestamp: int
