from asyncio import StreamWriter
from dataclasses import dataclass
from smart_home.proto.v1 import message_pb2


@dataclass
class TickEvent:
    timestamp: int


@dataclass
class AITickEvent:
    timestamp: int


@dataclass
class TaskDueEvent:
    task_id: int


@dataclass
class DeviceStateChangeEvent:
    device_id: int
    writer: StreamWriter
    request_id: str
    timestamp: int
    device_type: str
    parameters: dict[str, str]


@dataclass
class DeviceStateChangeRespEvent:
    device_id: int
    writer: StreamWriter
    request_id: str
    timestamp: int
    success: bool
    message: str


@dataclass
class DeviceRegisterEvent:
    device_id: int
    writer: StreamWriter
    request_id: str
    device_type: str
    capabilities: dict[str, str]
    device_state: dict[str, str]
    timestamp: int


@dataclass
class TimeShiftEvent:
    request_id: str
    writer: StreamWriter
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


@dataclass
class TaskListRequestEvent:
    request_id: str
    writer: StreamWriter
    include_dispatched: bool


@dataclass
class AITickRequestEvent:
    request_id: str
    writer: StreamWriter
