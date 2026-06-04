import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduledTask:
    task_id: int
    device_id: int
    parameters: dict[str, str]
    time: int


class TaskDatabase:
    def __init__(self) -> None:
        self._tasks_by_id: dict[int, ScheduledTask] = {}
        self._lock = asyncio.Lock()

    async def add_task(self, task: ScheduledTask) -> bool:
        async with self._lock:
            if task.task_id in self._tasks_by_id:
                return False

            self._tasks_by_id[task.task_id] = _copy_task(task)
            return True

    async def get_by_task_id(self, task_id: int) -> ScheduledTask | None:
        async with self._lock:
            task = self._tasks_by_id.get(task_id)
            return _copy_task(task) if task is not None else None

    async def get_due_tasks(self, timestamp: int) -> list[ScheduledTask]:
        async with self._lock:
            return [
                _copy_task(task)
                for task in self._tasks_by_id.values()
                if task.time <= timestamp
            ]

    async def pop_due_tasks(self, timestamp: int) -> list[ScheduledTask]:
        async with self._lock:
            due_tasks = [
                task
                for task in self._tasks_by_id.values()
                if task.time <= timestamp
            ]

            for task in due_tasks:
                self._tasks_by_id.pop(task.task_id, None)

            return [_copy_task(task) for task in due_tasks]

    async def remove_task(self, task_id: int) -> bool:
        async with self._lock:
            return self._tasks_by_id.pop(task_id, None) is not None


def _copy_task(task: ScheduledTask) -> ScheduledTask:
    return ScheduledTask(
        task_id=task.task_id,
        device_id=task.device_id,
        parameters=dict(task.parameters),
        time=task.time,
    )