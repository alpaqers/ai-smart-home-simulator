import pytest

from smart_home.server.event_bus import EventBus
from smart_home.server.events import ScheduledTaskDueEvent
from smart_home.server.scheduler import Scheduler


class FakeTickEvent:
    def __init__(self, timestamp: int) -> None:
        self.timestamp = timestamp


class FakeTaskStorage:
    def __init__(self) -> None:
        self.called_with_timestamp: int | None = None
        self.called_with_max_delay_seconds: int | None = None

    async def pop_due_task_ids(
        self,
        current_timestamp: int,
        max_delay_seconds: int | None = None,
    ) -> list[int]:
        self.called_with_timestamp = current_timestamp
        self.called_with_max_delay_seconds = max_delay_seconds

        if current_timestamp >= 100:
            return [10, 20, 30]

        return []


@pytest.mark.asyncio
async def test_scheduler_publishes_task_id_events_when_tasks_are_due() -> None:
    event_bus = EventBus()
    task_storage = FakeTaskStorage()

    received_task_ids: list[int] = []

    async def handle_scheduled_task(event: ScheduledTaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(ScheduledTaskDueEvent, handle_scheduled_task)

    scheduler = Scheduler(
        event_bus=event_bus,
        task_storage=task_storage,
        tick_event_type=FakeTickEvent,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(FakeTickEvent(timestamp=100))

    assert task_storage.called_with_timestamp == 100
    assert task_storage.called_with_max_delay_seconds == 300
    assert received_task_ids == [10, 20, 30]


@pytest.mark.asyncio
async def test_scheduler_does_not_publish_when_no_tasks_are_due() -> None:
    event_bus = EventBus()
    task_storage = FakeTaskStorage()

    received_task_ids: list[int] = []

    async def handle_scheduled_task(event: ScheduledTaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(ScheduledTaskDueEvent, handle_scheduled_task)

    scheduler = Scheduler(
        event_bus=event_bus,
        task_storage=task_storage,
        tick_event_type=FakeTickEvent,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(FakeTickEvent(timestamp=50))

    assert task_storage.called_with_timestamp == 50
    assert task_storage.called_with_max_delay_seconds == 300
    assert received_task_ids == []