from smart_home.proto.v1 import message_pb2
from smart_home.server.registry import DeviceRegistry
from smart_home.server.events import DeviceStateChangeEvent
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord
from smart_home.server.time_service import TimeService


class StateChangeProcessor:
    def __init__(
        self,
        registry: DeviceRegistry,
        history: DeviceStateHistory,
        time_service: TimeService,
    ) -> None:
        self._registry = registry
        self._history = history
        self._time_service = time_service

    async def handle(self, event: DeviceStateChangeEvent) -> None:
        server_timestamp = self._time_service.now_as_timestamp()
        response = message_pb2.DeviceStateChangeResp()
        response.device_id = event.device_id
        response.timestamp = server_timestamp

        if not await self._registry.is_registered(event.device_id):
            print(f"[StateChangeProcessor] Device {event.device_id} not registered")
            response.success = False
            response.message = f"Device {event.device_id} not registered"
        else:
            record = StateChangeRecord(
                device_id=event.device_id,
                timestamp=event.timestamp,
                parameters=dict(event.parameters),
                device_type=event.device_type,
            )
            await self._history.append(record)
            print(
                f"[StateChangeProcessor] Recorded state change for device "
                f"{event.device_id}: {event.parameters!r}"
            )
            response.success = True
            response.message = f"State change recorded: {dict(event.parameters)}"

        try:
            data = encode_wire_message(event.request_id, build_envelope(response))
            event.writer.write(data)
            await event.writer.drain()
        except Exception:
            pass
