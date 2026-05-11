from __future__ import annotations

import asyncio

from ..models.logger import LogEntry, LogLevel, LogSession


class LoggerController:
    def __init__(self) -> None:
        self._sessions: dict[str, LogSession] = {}
        self._active: LogSession | None = None
        self.queue: asyncio.Queue[LogEntry] = asyncio.Queue()
        self._task: asyncio.Task = None

    async def start(self) -> None:
        self._task = self._task = asyncio.create_task(self._consumer(), name="logger-consumer")

    async def stop(self) -> None:
        await self.queue.join()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def create_session(self, device_type: str = "") -> LogSession:
        session = LogSession(device_type=device_type)
        self._sessions[session.session_id] = session
        self._active = session
        return session

    def switch_session(self, session_id: str) -> LogSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"No session with id '{session_id}'")
        self._active = session
        return session

    @property
    def active_session(self) -> LogSession:
        if self._active is None:
            raise RuntimeError("No active logger session. Call create_session() first.")
        return self._active

    def all_sessions(self) -> list[LogSession]:
        return list(self._sessions.values())

    def log(self, message: str, level: LogLevel = LogLevel.INFO) -> LogEntry:
        entry = LogEntry(message=message, level=level)
        self.active_session.entries.append(entry)
        return entry

    def info(self, message: str) -> LogEntry: return self.log(message, LogLevel.INFO)
    def warning(self, message: str) -> LogEntry: return self.log(message, LogLevel.WARNING)
    def error(self, message: str) -> LogEntry: return self.log(message, LogLevel.ERROR)

    def entries(self, session_id: str | None = None) -> list[LogEntry]:
        session = self._sessions[session_id] if session_id else self.active_session
        return list(session.entries)

    async def _handle(self, entry: LogEntry) -> None:
        #placeholder
        print(str(entry))

    async def _consumer(self) -> None:
        while True:
            entry = await self.queue.get()
            try:
                await self._handle(entry)
            finally:
                self.queue.task_done()


