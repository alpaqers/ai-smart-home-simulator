from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from smart_home.proto.v1 import message_pb2
from smart_home.server.events import TickEvent, TimeShiftEvent
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.time_service import TimeService

if TYPE_CHECKING:
    from smart_home.server.event_bus import EventBus


class TimeShiftProcessor:
    def __init__(
        self,
        time_service: TimeService,
        *,
        event_bus: EventBus | None = None,
    ) -> None:
        self._time_service = time_service
        self._event_bus = event_bus

    async def handle(self, event: TimeShiftEvent) -> None:
        """Receives TimeShiftRequest and sets server time to new datetime."""
        response = message_pb2.TimeShiftResp()

        try:
            new_time = datetime(
                year=event.year,
                month=event.month,
                day=event.day,
                hour=event.hour,
                minute=event.minute,
                second=event.second,
            )
            self._time_service.use_simulated_time(new_time)
            response.success = True
            response.timestamp = self._time_service.now_as_timestamp()
            print(f"[TimeShiftProcessor] Server time set to: {new_time}")
        except Exception as e:
            response.success = False
            response.timestamp = self._time_service.now_as_timestamp()
            response.cause = str(e)
            print(f"[TimeShiftProcessor] Failed to set time: {e}")

        try:
            data = encode_wire_message(event.request_id, build_envelope(response))
            event.writer.write(data)
            await event.writer.drain()
        except Exception:
            pass

        if (
            response.success
            and self._event_bus is not None
            and self._time_service.is_simulated()
        ):
            await self._event_bus.publish(
                TickEvent(timestamp=self._time_service.now_as_timestamp())
            )
