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
        due_task_ids = await self._task_database.claim_due_task_ids(
            timestamp=event.timestamp,
            max_delay_seconds=self._max_delay_seconds,
        )

        for task_id in due_task_ids:
            await self._event_bus.publish(TaskDueEvent(task_id=task_id))