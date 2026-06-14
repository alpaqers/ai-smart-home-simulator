import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduledTask:
    task_id: int
    device_id: int
    parameters: dict[str, str]
    time: int
    dispatched: bool = False

class TaskDatabase:
    def __init__(self) -> None:
        """Create an empty in-memory task store."""
        self._tasks_by_id: dict[int, ScheduledTask] = {}
        self._lock = asyncio.Lock()

    async def add_task(self, task: ScheduledTask) -> bool:
        """Add a task if its ID is not already stored."""
        async with self._lock:
            if task.task_id in self._tasks_by_id:
                return False

            self._tasks_by_id[task.task_id] = _copy_task(task)
            return True

    async def get_by_task_id(self, task_id: int) -> ScheduledTask | None:
        """Return a task by ID, or None when it does not exist."""
        async with self._lock:
            task = self._tasks_by_id.get(task_id)
            return _copy_task(task) if task is not None else None

    async def list_tasks(self, include_dispatched: bool = True) -> list[ScheduledTask]:
        """Return stored tasks sorted by scheduled time."""
        async with self._lock:
            tasks = [
                task
                for task in self._tasks_by_id.values()
                if include_dispatched or not task.dispatched
            ]
            tasks.sort(key=lambda task: (task.time, task.device_id, task.task_id))
            return [_copy_task(task) for task in tasks]

    async def get_due_tasks(self, timestamp: int) -> list[ScheduledTask]:
        """Return tasks scheduled at or before the given timestamp."""
        async with self._lock:
            return [
                _copy_task(task)
                for task in self._tasks_by_id.values()
                if task.time <= timestamp and not task.dispatched
            ]

    async def claim_due_task_ids(
        self,
        timestamp: int,
        max_delay_seconds: int | None = None,
    ) -> list[int]:
        """Return due task IDs and mark them as dispatched without removing them."""
        async with self._lock:
            claimed_task_ids: list[int] = []

            for task_id, task in self._tasks_by_id.items():
                if task.dispatched:
                    continue

                if task.time > timestamp:
                    continue

                if max_delay_seconds is not None:
                    if timestamp - task.time > max_delay_seconds:
                        continue

                self._tasks_by_id[task_id] = ScheduledTask(
                    task_id=task.task_id,
                    device_id=task.device_id,
                    parameters=dict(task.parameters),
                    time=task.time,
                    dispatched=True,
                )

                claimed_task_ids.append(task_id)

            return claimed_task_ids

    async def pop_due_tasks(self, timestamp: int) -> list[ScheduledTask]:
        """Return and remove tasks scheduled at or before the timestamp."""
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
        """Remove a task by ID and report whether it existed."""
        async with self._lock:
            return self._tasks_by_id.pop(task_id, None) is not None

    async def reset_dispatched_flags(self) -> int:
        """Mark dispatched tasks as pending again and return the updated count."""
        async with self._lock:
            count = 0
            for task_id, task in list(self._tasks_by_id.items()):
                if not task.dispatched:
                    continue

                self._tasks_by_id[task_id] = ScheduledTask(
                    task_id=task.task_id,
                    device_id=task.device_id,
                    parameters=dict(task.parameters),
                    time=task.time,
                    dispatched=False,
                )
                count += 1

            return count


def _copy_task(task: ScheduledTask) -> ScheduledTask:
    return ScheduledTask(
        task_id=task.task_id,
        device_id=task.device_id,
        parameters=dict(task.parameters),
        time=task.time,
        dispatched=task.dispatched
    )
