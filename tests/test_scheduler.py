import pytest

from smart_home.server.event_bus import EventBus
from smart_home.server.events import TickEvent, TaskDueEvent
from smart_home.server.scheduler import Scheduler
from smart_home.server.tasks import ScheduledTask, TaskDatabase


@pytest.mark.asyncio
async def test_scheduler_publishes_task_due_events_for_due_tasks() -> None:
    event_bus = EventBus()
    task_database = TaskDatabase()

    received_task_ids: list[int] = []

    async def handle_task_due(event: TaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(TaskDueEvent, handle_task_due)

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    scheduler = Scheduler(
        event_bus=event_bus,
        task_database=task_database,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(TickEvent(timestamp=100))

    assert received_task_ids == [1]


@pytest.mark.asyncio
async def test_scheduler_does_not_publish_future_tasks() -> None:
    event_bus = EventBus()
    task_database = TaskDatabase()

    received_task_ids: list[int] = []

    async def handle_task_due(event: TaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(TaskDueEvent, handle_task_due)

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    scheduler = Scheduler(
        event_bus=event_bus,
        task_database=task_database,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(TickEvent(timestamp=50))

    assert received_task_ids == []


@pytest.mark.asyncio
async def test_scheduler_does_not_publish_expired_tasks() -> None:
    event_bus = EventBus()
    task_database = TaskDatabase()

    received_task_ids: list[int] = []

    async def handle_task_due(event: TaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(TaskDueEvent, handle_task_due)

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )

    scheduler = Scheduler(
        event_bus=event_bus,
        task_database=task_database,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(TickEvent(timestamp=401))

    assert received_task_ids == []


@pytest.mark.asyncio
async def test_scheduler_publishes_multiple_task_due_events() -> None:
    event_bus = EventBus()
    task_database = TaskDatabase()

    received_task_ids: list[int] = []

    async def handle_task_due(event: TaskDueEvent) -> None:
        received_task_ids.append(event.task_id)

    await event_bus.subscribe(TaskDueEvent, handle_task_due)

    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=10,
            parameters={"power": "on"},
            time=100,
        )
    )
    await task_database.add_task(
        ScheduledTask(
            task_id=2,
            device_id=11,
            parameters={"temperature": "22"},
            time=120,
        )
    )

    scheduler = Scheduler(
        event_bus=event_bus,
        task_database=task_database,
        max_delay_seconds=300,
    )

    await scheduler.start()

    await event_bus.publish(TickEvent(timestamp=120))

    assert received_task_ids == [1, 2]