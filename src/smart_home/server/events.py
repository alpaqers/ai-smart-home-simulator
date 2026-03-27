from asyncio import StreamWriter
from dataclasses import dataclass


@dataclass
class DeviceStateChangeEvent:
    device_id: int
    writer: StreamWriter
    timestamp: int
    device_type: int
    parameters: dict[str, str]
    envelope: message_pb2.Envelope


@dataclass
class DeviceResponseEvent:
    device_id: int
    writer: StreamWriter
    timestamp: int
    success: bool
    message: str
    envelope: message_pb2.Envelope


@dataclass
class DeviceRegisterEvent:
    device_id: int
    writer: StreamWriter
    device_type: str
    capabilities: dict[str, str]
    device_state: dict[str, str]
    timestamp: int
    envelope: message_pb2.Envelope
