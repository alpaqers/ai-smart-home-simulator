from smart_home.proto.v1 import message_pb2
from smart_home.server.events import DeviceRegisterEvent
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.time_service import TimeService


class RegisterProcessor:
    def __init__(self, registry: DeviceRegistry, time_service: TimeService) -> None:
        self._registry = registry
        self._time_service = time_service

    async def handle(self, event: DeviceRegisterEvent) -> None:
        server_timestamp = self._time_service.now_as_timestamp()
        try:
            device = RegisteredDevice(
                device_id=event.device_id,
                writer=event.writer,
                device_type=event.device_type,
                capabilities=event.capabilities,
                device_state=event.device_state,
                timestamp=event.timestamp,
            )

            await self._registry.register(device)

            response = message_pb2.DeviceRegisterResp()
            response.device_id = event.device_id
            response.success = True
            response.timestamp = server_timestamp

        except Exception as e:
            response = message_pb2.DeviceRegisterResp()
            response.device_id = event.device_id
            response.success = False
            response.timestamp = server_timestamp
            response.cause = str(e)

        try:
            data = encode_wire_message(event.request_id, build_envelope(response))
            event.writer.write(data)
            await event.writer.drain()
        except Exception:
            pass

        print(f"[RegisterProcessor] Device {event.device_id} registered")
