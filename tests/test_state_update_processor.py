from unittest.mock import AsyncMock

import pytest

from smart_home.server.events import TaskDueEvent
from smart_home.server.processors.state_update import StateUpdateProcessor
from smart_home.server.tasks import ScheduledTask, TaskDatabase


@pytest.mark.asyncio
async def test_state_update_processor_sends_task_parameters() -> None:
    task_database = TaskDatabase()
    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=7,
            parameters={"power": "on"},
            time=100,
        )
    )

    sender = AsyncMock()
    sender.send = AsyncMock(return_value=True)
    processor = StateUpdateProcessor(sender, task_database)

    await processor.handle(TaskDueEvent(task_id=1))

    sender.send.assert_awaited_once_with(
        device_id=7,
        command_type=0,
        parameters={"power": "on"},
    )


@pytest.mark.asyncio
async def test_state_update_processor_ignores_missing_task() -> None:
    task_database = TaskDatabase()
    sender = AsyncMock()
    sender.send = AsyncMock(return_value=True)
    processor = StateUpdateProcessor(sender, task_database)

    await processor.handle(TaskDueEvent(task_id=99))

    sender.send.assert_not_awaited()
