from __future__ import annotations
from datetime import datetime
import uuid
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    message: str
    level: LogLevel = LogLevel.INFO
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[{self.timestamp.isoformat(timespec='seconds')}] [{self.level}] {self.message}"


@dataclass
class LogSession:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    started_at: datetime = field(default_factory=datetime.now)
    device_type: str = ""
    entries: list[LogEntry] = field(default_factory=list)