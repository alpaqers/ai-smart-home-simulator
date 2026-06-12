import asyncio
import time
from collections.abc import Callable

from smart_home.server.event_bus import EventBus
from smart_home.server.events import TickEvent
from smart_home.server.time_service import TimeService


class TickEmitter:
    def __init__(
        self,
        bus: EventBus,
        interval_seconds: float,
        time_service: TimeService | None = None,
        time_provider: Callable[[], int] | None = None,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Tick interval must be greater than 0")
        if time_service is not None and time_provider is not None:
            raise ValueError("Provide either time_service or time_provider, not both")

        self._bus = bus
        self._interval_seconds = interval_seconds
        self._time_service = time_service
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
        if self._time_service is not None:
            timestamp = self._time_service.now_as_timestamp()
        else:
            timestamp = self._time_provider()

        event = TickEvent(timestamp=timestamp)
        await self._bus.publish(event)

        if self._time_service is not None and self._time_service.is_simulated():
            self._time_service.advance_seconds(self._interval_seconds)

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
