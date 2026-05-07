from __future__ import annotations

from ..controllers.logger_controller import LoggerController
from ..models.logger import LogEntry, LogSession


class LoggerService:
    def __init__(self, controller: LoggerController) -> None:
        self._ctrl = controller

    def create_session(self, device_type: str = "") -> LogSession:
        return self._ctrl.create_session(device_type)

    def get_entries(self, session_id: str | None = None) -> list[LogEntry]:
        return self._ctrl.entries(session_id)

    def all_sessions(self) -> list[LogSession]:
        return self._ctrl.all_sessions()

    def info(self, msg: str) -> None: self._ctrl.info(msg)

    def warning(self, msg: str) -> None: self._ctrl.warning(msg)

    def error(self, msg: str) -> None: self._ctrl.error(msg)