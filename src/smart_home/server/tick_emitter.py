import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from smart_home.server.event_bus import EventBus
from smart_home.server.events import AITickEvent, TickEvent
from smart_home.server.time_service import TimeService


@dataclass
class _TickSchedule:
    interval_seconds: float
    event_factory: Callable[[int], Any]
    last_emitted_timestamp: int | None = None

    def is_due(self, timestamp: int) -> bool:
        return (
            self.last_emitted_timestamp is None
            or timestamp - self.last_emitted_timestamp >= self.interval_seconds
        )

    async def emit_if_due(self, bus: EventBus, timestamp: int) -> Any | None:
        if not self.is_due(timestamp):
            return None

        self.last_emitted_timestamp = timestamp
        event = self.event_factory(timestamp)
        await bus.publish(event)
        return event


class TickEmitter:
    def __init__(
        self,
        bus: EventBus,
        interval_seconds: float,
        ai_tick_interval_seconds: float | None = None,
        time_service: TimeService | None = None,
        time_provider: Callable[[], int] | None = None,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Tick interval must be greater than 0")
        if ai_tick_interval_seconds is not None and ai_tick_interval_seconds <= 0:
            raise ValueError("AI tick interval must be greater than 0")
        if time_service is not None and time_provider is not None:
            raise ValueError("Provide either time_service or time_provider, not both")

        self._bus = bus
        self._interval_seconds = interval_seconds
        self._time_service = time_service
        self._time_provider = time_provider or (lambda: int(time.time()))
        self._running = False
        self._task: asyncio.Task | None = None
        self._tick_schedule = _TickSchedule(
            interval_seconds=interval_seconds,
            event_factory=lambda timestamp: TickEvent(timestamp=timestamp),
        )
        self._extra_tick_schedules = self._build_extra_tick_schedules(
            ai_tick_interval_seconds
        )

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

    async def emit_once(self) -> TickEvent | None:
        if self._time_service is not None:
            timestamp = self._time_service.now_as_timestamp()
        else:
            timestamp = self._time_provider()

        event = await self._tick_schedule.emit_if_due(self._bus, timestamp)
        for schedule in self._extra_tick_schedules:
            await schedule.emit_if_due(self._bus, timestamp)

        if self._time_service is not None and self._time_service.is_simulated():
            self._time_service.advance_seconds(self._interval_seconds)

        return event

    def _build_extra_tick_schedules(
        self,
        ai_tick_interval_seconds: float | None,
    ) -> list[_TickSchedule]:
        schedules: list[_TickSchedule] = []
        if ai_tick_interval_seconds is not None:
            schedules.append(
                _TickSchedule(
                    interval_seconds=ai_tick_interval_seconds,
                    event_factory=lambda timestamp: AITickEvent(timestamp=timestamp),
                )
            )
        return schedules

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
