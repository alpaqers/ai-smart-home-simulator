import time
import uuid

from smart_home.proto.v1 import message_pb2
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.registry import DeviceRegistry


class StateUpdateSender:
    def __init__(self, registry: DeviceRegistry) -> None:
        self._registry = registry

    async def send(
        self,
        device_id: int,
        command_type: int,
        parameters: dict[str, str],
    ) -> bool:
        writer = await self._registry.get_writer(device_id)
        if writer is None:
            return False

        msg = message_pb2.DeviceStateUpdate()
        msg.device_id = device_id
        msg.command_type = command_type
        msg.timestamp = int(time.time())
        msg.parameters.update(parameters)

        proto_bytes = build_envelope(msg)
        request_id = str(uuid.uuid4())
        wire_data = encode_wire_message(request_id, proto_bytes)

        writer.write(wire_data)
        await writer.drain()
        return True
