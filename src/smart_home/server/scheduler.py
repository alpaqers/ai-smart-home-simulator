from __future__ import annotations

from smart_home.server.event_bus import EventBus
from smart_home.server.events import TickEvent, TaskDueEvent
from smart_home.server.tasks import TaskDatabase


class Scheduler:
    def __init__(
        self,
        event_bus: EventBus,
        task_database: TaskDatabase,
        max_delay_seconds: int | None = 300,
    ) -> None:
        self._event_bus = event_bus
        self._task_database = task_database
        self._max_delay_seconds = max_delay_seconds

    async def start(self) -> None:
        await self._event_bus.subscribe(TickEvent, self.handle_tick)

    async def handle_tick(self, event: TickEvent) -> None:
        due_tasks = await self._task_database.pop_due_tasks(event.timestamp)

        for task in due_tasks:
            if self._is_expired(task.time, event.timestamp):
                continue

            await self._event_bus.publish(
                TaskDueEvent(task_id=task.task_id)
            )

    def _is_expired(self, task_time: int, current_timestamp: int) -> bool:
        if self._max_delay_seconds is None:
            return False

        return current_timestamp - task_time > self._max_delay_seconds