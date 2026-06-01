from __future__ import annotations

from datetime import datetime
from typing import Any

from smart_home.server.event_bus import EventBus
from smart_home.server.events import ScheduledTaskDueEvent


class Scheduler:
    def __init__(
        self,
        event_bus: EventBus,
        task_storage: Any,
        tick_event_type: type,
        max_delay_seconds: int | None = 300,
    ) -> None:
        self._event_bus = event_bus
        self._task_storage = task_storage
        self._tick_event_type = tick_event_type
        self._max_delay_seconds = max_delay_seconds
        
    async def start(self) -> None:
        await self._event_bus.subscribe(self._tick_event_type, self.handle_tick)

    async def handle_tick(self, event: Any) -> None:
        current_timestamp = self._extract_timestamp(event)

        due_task_ids = await self._task_storage.pop_due_task_ids(
            current_timestamp=current_timestamp,
            max_delay_seconds=self._max_delay_seconds,
        )

        for task_id in due_task_ids:
            await self._event_bus.publish(
                ScheduledTaskDueEvent(task_id=task_id)
            )

    def _extract_timestamp(self, event: Any) -> int:
        # TODO: replace with real TickEvent field when TickEvent is implemented.
        if hasattr(event, "timestamp"):
            return self._normalize_timestamp(event.timestamp)

        if hasattr(event, "current_time"):
            return self._normalize_timestamp(event.current_time)

        if hasattr(event, "time"):
            return self._normalize_timestamp(event.time)

        raise ValueError(
            "TickEvent does not contain timestamp, current_time or time field"
        )

    def _normalize_timestamp(self, value: Any) -> int:
        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, datetime):
            return int(value.replace(microsecond=0).timestamp())

        raise TypeError(
            "TickEvent time value must be int, float or datetime, "
            f"got {type(value).__name__}"
        )