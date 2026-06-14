from __future__ import annotations

from smart_home.proto.v1 import message_pb2
from smart_home.server.event_bus import EventBus
from smart_home.server.events import AITickEvent, AITickRequestEvent
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.tasks import TaskDatabase
from smart_home.server.time_service import TimeService


class AITickTriggerProcessor:
    def __init__(
        self,
        bus: EventBus,
        task_database: TaskDatabase,
        time_service: TimeService,
        *,
        ai_enabled: bool,
    ) -> None:
        self._bus = bus
        self._task_database = task_database
        self._time_service = time_service
        self._ai_enabled = ai_enabled

    async def handle(self, event: AITickRequestEvent) -> None:
        response = message_pb2.AITickResp()
        response.timestamp = self._time_service.now_as_timestamp()

        if not self._ai_enabled:
            response.success = False
            response.cause = "AI processor is not configured on the server"
            await self._send_response(event, response)
            return

        tasks_before = await self._task_database.list_tasks()
        try:
            await self._bus.publish(AITickEvent(timestamp=response.timestamp))
            tasks_after = await self._task_database.list_tasks()
            response.success = True
            response.tasks_added = len(tasks_after) - len(tasks_before)
            print(
                "[AITickTriggerProcessor] Manual AI tick completed; "
                f"tasks_added={response.tasks_added}"
            )
        except Exception as exc:
            response.success = False
            response.cause = str(exc)
            print(f"[AITickTriggerProcessor] Manual AI tick failed: {exc}")

        await self._send_response(event, response)

    async def _send_response(
        self,
        event: AITickRequestEvent,
        response: message_pb2.AITickResp,
    ) -> None:
        data = encode_wire_message(event.request_id, build_envelope(response))
        event.writer.write(data)
        await event.writer.drain()
