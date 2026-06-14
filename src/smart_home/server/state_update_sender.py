from __future__ import annotations

import uuid

from smart_home.proto.v1 import message_pb2
from smart_home.server.message_handler import build_envelope, encode_wire_message
from smart_home.server.registry import DeviceRegistry
from smart_home.server.time_service import TimeService


class StateUpdateSender:
    def __init__(
        self,
        registry: DeviceRegistry,
        time_service: TimeService,
    ) -> None:
        self._registry = registry
        self._time_service = time_service

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
        msg.timestamp = self._time_service.now_as_timestamp()
        msg.parameters.update(parameters)

        proto_bytes = build_envelope(msg)
        request_id = str(uuid.uuid4())
        wire_data = encode_wire_message(request_id, proto_bytes)

        writer.write(wire_data)
        await writer.drain()
        return True
