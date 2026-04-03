from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.proto.v1 import message_pb2
from smart_home.server.events import DeviceRegisterEvent
from smart_home.server.message_handler import msg_to_event, parse_envelope
from smart_home.server.processors import RegisterProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice


def test_msg_to_event_maps_device_register_req() -> None:
    writer = Mock()

    envelope = message_pb2.Envelope()
    req = envelope.device_register_req
    req.device_id = 1
    req.device_type = "thermostat"
    req.capabilities["mode"] = "heat"
    req.capabilities["fan"] = "auto"
    req.device_state["temperature"] = "21"
    req.device_state["humidity"] = "45"
    req.timestamp = 123456789

    event = msg_to_event(envelope, writer)

    assert isinstance(event, DeviceRegisterEvent)
    assert event.device_id == 1
    assert event.writer is writer
    assert event.device_type == "thermostat"
    assert event.capabilities == {"mode": "heat", "fan": "auto"}
    assert event.device_state == {"temperature": "21", "humidity": "45"}
    assert event.timestamp == 123456789


@pytest.mark.asyncio
async def test_registry_register_and_unregister_by_writer() -> None:
    registry = DeviceRegistry()
    writer = Mock()

    device = RegisteredDevice(
        device_id=10,
        writer=writer,
        device_type="thermostat",
        capabilities={"mode": "heat"},
        device_state={"temperature": "22"},
        timestamp=111,
    )

    await registry.register(device)

    stored = await registry.get_by_device_id(10)
    assert stored is not None
    assert stored.device_id == 10
    assert stored.writer is writer
    assert stored.device_type == "thermostat"
    assert stored.capabilities == {"mode": "heat"}
    assert stored.device_state == {"temperature": "22"}
    assert stored.timestamp == 111

    stored_writer = await registry.get_writer(10)
    assert stored_writer is writer

    is_registered = await registry.is_registered(10)
    assert is_registered is True

    await registry.unregister_by_writer(writer)

    stored_after = await registry.get_by_device_id(10)
    assert stored_after is None

    stored_writer_after = await registry.get_writer(10)
    assert stored_writer_after is None

    is_registered_after = await registry.is_registered(10)
    assert is_registered_after is False


@pytest.mark.asyncio
async def test_register_processor_registers_device_and_sends_response() -> None:
    registry = DeviceRegistry()
    processor = RegisterProcessor(registry)

    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()

    event = DeviceRegisterEvent(
        device_id=7,
        writer=writer,
        device_type="thermostat",
        capabilities={"mode": "cool"},
        device_state={"temperature": "19"},
        timestamp=999,
    )

    await processor.handle(event)

    stored = await registry.get_by_device_id(7)
    assert stored is not None
    assert stored.device_id == 7
    assert stored.writer is writer
    assert stored.device_type == "thermostat"
    assert stored.capabilities == {"mode": "cool"}
    assert stored.device_state == {"temperature": "19"}
    assert stored.timestamp == 999

    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()

    sent_data = writer.write.call_args.args[0]
    sent_envelope = parse_envelope(sent_data)

    assert sent_envelope.WhichOneof("payload") == "device_register_resp"
    assert sent_envelope.device_register_resp.device_id == 7
    assert sent_envelope.device_register_resp.success is True
    assert sent_envelope.device_register_resp.timestamp == 999