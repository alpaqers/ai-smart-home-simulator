from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.events import TaskListRequestEvent
from smart_home.server.message_handler import decode_wire_message, parse_envelope
from smart_home.server.processors.task_list import TaskListProcessor
from smart_home.server.tasks import ScheduledTask, TaskDatabase
from smart_home.server.time_service import TimeService


@pytest.mark.asyncio
async def test_task_list_processor_sends_scheduler_tasks() -> None:
    task_database = TaskDatabase()
    await task_database.add_task(
        ScheduledTask(
            task_id=1,
            device_id=7,
            parameters={"power": "on"},
            time=1700000300,
        )
    )

    time_service = TimeService()
    time_service.use_simulated_epoch(1700000000)
    processor = TaskListProcessor(task_database, time_service)

    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()

    await processor.handle(
        TaskListRequestEvent(
            request_id="req-tasks",
            writer=writer,
            include_dispatched=True,
        )
    )

    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()

    sent_request_id, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)

    assert sent_request_id == "req-tasks"
    assert sent_envelope.WhichOneof("payload") == "task_list_resp"
    assert sent_envelope.task_list_resp.success is True
    assert sent_envelope.task_list_resp.timestamp == 1700000000
    assert len(sent_envelope.task_list_resp.tasks) == 1
    task = sent_envelope.task_list_resp.tasks[0]
    assert task.task_id == 1
    assert task.device_id == 7
    assert dict(task.parameters) == {"power": "on"}
    assert task.time == 1700000300
