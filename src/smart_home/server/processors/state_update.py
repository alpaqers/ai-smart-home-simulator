from __future__ import annotations

from typing import TYPE_CHECKING

from smart_home.server.events import TaskDueEvent
from smart_home.server.state_update_sender import StateUpdateSender

if TYPE_CHECKING:
    from smart_home.server.tasks import TaskDatabase


class StateUpdateProcessor:
    def __init__(
        self,
        sender: StateUpdateSender,
        task_database: "TaskDatabase",
    ) -> None:
        self._sender = sender
        self._task_database = task_database

    async def handle(self, event: TaskDueEvent) -> None:
        task = await self._task_database.get_by_task_id(event.task_id)
        if task is None:
            print(f"[StateUpdateProcessor] Task {event.task_id} not found")
            return

        ok = await self._sender.send(
            device_id=task.device_id,
            command_type=0,
            parameters=task.parameters,
        )
        if ok:
            await self._task_database.remove_task(task.task_id)
        else:
            print(
                f"[StateUpdateProcessor] Device {task.device_id} unreachable, "
                f"task {task.task_id} stays in DB for retry"
            )
