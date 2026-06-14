from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.message_handler import decode_wire_message, parse_envelope
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_update_sender import StateUpdateSender
from smart_home.server.time_service import TimeService


@pytest.mark.asyncio
async def test_state_update_sender_writes_device_state_update() -> None:
    registry = DeviceRegistry()
    time_service = TimeService()
    time_service.use_simulated_epoch(1700000000)

    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()

    await registry.register(
        RegisteredDevice(
            device_id=7,
            writer=writer,
            device_type="lamp",
            capabilities={"power": "on/off"},
            device_state={"power": "off"},
            timestamp=1,
        )
    )

    sender = StateUpdateSender(registry, time_service)

    ok = await sender.send(
        device_id=7,
        command_type=0,
        parameters={"power": "on"},
    )

    assert ok is True
    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()

    _, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)

    assert sent_envelope.WhichOneof("payload") == "device_state_update"
    update = sent_envelope.device_state_update
    assert update.device_id == 7
    assert update.timestamp == 1700000000
    assert dict(update.parameters) == {"power": "on"}


@pytest.mark.asyncio
async def test_state_update_sender_returns_false_for_missing_device() -> None:
    registry = DeviceRegistry()
    time_service = TimeService()
    sender = StateUpdateSender(registry, time_service)

    ok = await sender.send(
        device_id=99,
        command_type=0,
        parameters={"power": "on"},
    )

    assert ok is False
