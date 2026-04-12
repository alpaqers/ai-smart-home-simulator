from asyncio import StreamWriter
from dataclasses import dataclass
from smart_home.proto.v1 import message_pb2

@dataclass
class DeviceStateChangeEvent:
    device_id: str
    writer: StreamWriter
    request_id: str
    timestamp: int
    device_type: int
    parameters: dict[str, str]


@dataclass
class DeviceResponseEvent:
    device_id: str
    writer: StreamWriter
    request_id: str
    timestamp: int
    success: bool
    message: str


@dataclass
class DeviceRegisterEvent:
    device_id: str
    writer: StreamWriter
    request_id: str
    device_type: str
    capabilities: dict[str, str]
    device_state: dict[str, str]
    timestamp: int
