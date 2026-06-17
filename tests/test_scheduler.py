from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.event_bus import EventBus
from smart_home.server.events import TickEvent, TaskDueEvent
from smart_home.server.processors.state_update import StateUpdateProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.scheduler import Scheduler
from smart_home.server.state_update_sender import StateUpdateSender
from smart_home.server.tasks import ScheduledTask, TaskDatabase
from smart_home.server.time_service import TimeService
from smart_home.server.message_handler import decode_wire_message, parse_envelope


@pytest.mark.asyncio
async def test_publishes_due_task() -> None:
    # Checks that scheduler publishes TaskDueEvent
    # and keeps the task available in the database.

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

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.task_id == 1
    assert task.dispatched is True


@pytest.mark.asyncio
async def test_skips_future_task() -> None:
    # Checks that scheduler does not publish a task
    # scheduled after the current tick.

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

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.dispatched is False


@pytest.mark.asyncio
async def test_skips_expired_task() -> None:
    # Checks that scheduler does not publish a task
    # older than max_delay_seconds.

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

    task = await task_database.get_by_task_id(1)

    assert task is not None
    assert task.dispatched is False


@pytest.mark.asyncio
async def test_publishes_many_tasks() -> None:
    # Checks that scheduler publishes one TaskDueEvent
    # for each due task.

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

    task_1 = await task_database.get_by_task_id(1)
    task_2 = await task_database.get_by_task_id(2)

    assert task_1 is not None
    assert task_2 is not None
    assert task_1.dispatched is True
    assert task_2.dispatched is True


@pytest.mark.asyncio
async def test_does_not_publish_twice() -> None:
    # Checks that the same task is not published again
    # on the next tick.

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
    await event_bus.publish(TickEvent(timestamp=101))

    assert received_task_ids == [1]


@pytest.mark.asyncio
async def test_due_task_is_sent_to_device_as_state_update() -> None:
    event_bus = EventBus()
    task_database = TaskDatabase()
    registry = DeviceRegistry()
    time_service = TimeService()
    time_service.use_simulated_epoch(100)

    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()

    await registry.register(
        RegisteredDevice(
            device_id=10,
            writer=writer,
            device_type="lamp",
            capabilities={"power": "on/off"},
            device_state={"power": "off"},
            timestamp=1,
        )
    )

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
    sender = StateUpdateSender(registry, time_service)
    processor = StateUpdateProcessor(sender, task_database)

    await scheduler.start()
    await event_bus.subscribe(TaskDueEvent, processor.handle)
    await event_bus.publish(TickEvent(timestamp=100))

    writer.write.assert_called_once()

    _, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)

    assert sent_envelope.WhichOneof("payload") == "device_state_update"
    update = sent_envelope.device_state_update
    assert update.device_id == 10
    assert dict(update.parameters) == {"power": "on"}
