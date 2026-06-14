from __future__ import annotations

from smart_home.proto.v1 import message_pb2
from smart_home.server.events import TaskListRequestEvent
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.tasks import ScheduledTask, TaskDatabase
from smart_home.server.time_service import TimeService


class TaskListProcessor:
    def __init__(
        self,
        task_database: TaskDatabase,
        time_service: TimeService,
    ) -> None:
        self._task_database = task_database
        self._time_service = time_service

    async def handle(self, event: TaskListRequestEvent) -> None:
        response = message_pb2.TaskListResp()
        response.timestamp = self._time_service.now_as_timestamp()

        try:
            tasks = await self._task_database.list_tasks(
                include_dispatched=event.include_dispatched,
            )
            response.success = True
            response.tasks.extend(_task_to_proto(task) for task in tasks)
        except Exception as exc:
            response.success = False
            response.cause = str(exc)

        data = encode_wire_message(event.request_id, build_envelope(response))
        event.writer.write(data)
        await event.writer.drain()


def _task_to_proto(task: ScheduledTask) -> message_pb2.ScheduledTaskInfo:
    task_info = message_pb2.ScheduledTaskInfo()
    task_info.task_id = task.task_id
    task_info.device_id = task.device_id
    task_info.parameters.update(task.parameters)
    task_info.time = task.time
    task_info.dispatched = task.dispatched
    return task_info
