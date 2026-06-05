import asyncio
import time
from collections.abc import Callable

from smart_home.server.event_bus import EventBus
from smart_home.server.events import TickEvent


class TickEmitter:
    def __init__(
        self,
        bus: EventBus,
        interval_seconds: float,
        time_provider: Callable[[], int] | None = None,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Tick interval must be greater than 0")

        self._bus = bus
        self._interval_seconds = interval_seconds
        self._time_provider = time_provider or (lambda: int(time.time()))
        self._running = False
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        self._running = True
        self._task = asyncio.create_task(self._run(), name="TickEmitter")

    async def stop(self) -> None:
        self._running = False
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def emit_once(self) -> TickEvent:
        event = TickEvent(timestamp=self._time_provider())
        await self._bus.publish(event)
        return event

    async def _run(self) -> None:
        try:
            while self._running:
                await asyncio.sleep(self._interval_seconds)
                await self.emit_once()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[TickEmitter] Error: {e}")
            self._running = False
