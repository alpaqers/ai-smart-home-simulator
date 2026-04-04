from smart_home.proto.v1 import message_pb2
from smart_home.server.events import DeviceRegisterEvent
from smart_home.server.message_handler import build_envelope
from smart_home.server.registry import DeviceRegistry, RegisteredDevice


class RegisterProcessor:
    def __init__(self, registry: DeviceRegistry) -> None:
        self._registry = registry

    async def handle(self, event: DeviceRegisterEvent) -> None:
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
        response.timestamp = event.timestamp

        data = build_envelope(response)
        event.writer.write(data)
        await event.writer.drain()

        print(f"[RegisterProcessor] Device {event.device_id} registered")

class StateChangeProcessor:
    async def handle(self, event) -> None:
        print(f"[StateChangeProcessor] Received state change from device {event.device_id}")


class ResponseProcessor:
    async def handle(self, event) -> None:
        print(f"[ResponseProcessor] Received response from device {event.device_id}")