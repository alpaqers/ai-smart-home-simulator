from __future__ import annotations

from ..controllers.logger_controller import LoggerController
from ..models.logger import LogEntry, LogSession, LogLevel


class LoggerService:
    def __init__(self, controller: LoggerController) -> None:
        self._ctrl = controller

    def create_session(self, device_type: str = "") -> LogSession:
        return self._ctrl.create_session(device_type)

    def get_entries(self, session_id: str | None = None) -> list[LogEntry]:
        return self._ctrl.entries(session_id)

    def get_entries_by_level(self, level: LogLevel, session_id: str | None = None) -> list[LogEntry]:
        return [entry for entry in self.get_entries(session_id) if entry.level == level]

    def all_sessions(self) -> list[LogSession]:
        return self._ctrl.all_sessions()

    def info(self, msg: str) -> None: self._ctrl.info(msg)

    def warning(self, msg: str) -> None: self._ctrl.warning(msg)

    def error(self, msg: str) -> None: self._ctrl.error(msg)

_LEVEL_MAP = {
    "1": None,
    "2": LogLevel.INFO,
    "3": LogLevel.WARNING,
    "4": LogLevel.ERROR,
}

_LOG_MENU = """
  Filter by:
    1) All
    2) Info
    3) Warning
    4) Error"""

def _show_logs(logger: LoggerService) -> None:
    choice = input(_LOG_MENU + "\n  › ").strip()

    if choice not in _LEVEL_MAP:
        print("Invalid choice.")
        return

    level = _LEVEL_MAP[choice]
    entries = (
        logger.get_entries()
        if level is None
        else logger.get_entries_by_level(level)
    )

    if not entries:
        print("No log entries found.")
        return

    print()
    for entry in entries:
        print(f"  {entry}")