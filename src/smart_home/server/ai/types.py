from dataclasses import dataclass, field

from smart_home.server.registry import RegisteredDevice
from smart_home.server.state_history import StateChangeRecord


@dataclass
class AIPrompt:
    messages: list[dict[str, str]]
    parameters: dict[str, object] = field(default_factory=dict)


@dataclass
class AIResponse:
    text: str
    raw: dict[str, object]


@dataclass
class AIContext:
    devices: list[RegisteredDevice]
    history: dict[int, list[StateChangeRecord]]
