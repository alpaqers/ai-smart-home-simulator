from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.events import DeviceStateChangeEvent
from smart_home.server.message_handler import decode_wire_message, parse_envelope
from smart_home.server.processors import StateChangeProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord
from smart_home.server.time_service import TimeService


def _time_service_at(timestamp: int) -> TimeService:
    time_service = TimeService()
    time_service.use_simulated_time(datetime.fromtimestamp(timestamp))
    return time_service


def _mock_writer() -> Mock:
    writer = Mock()
    writer.write = Mock()
    writer.drain = AsyncMock()
    return writer


@pytest.mark.asyncio
async def test_device_state_history_append_and_history_for() -> None:
    history = DeviceStateHistory()
    r1 = StateChangeRecord(
        device_id=1,
        timestamp=100,
        parameters={"temperature": "21"},
        device_type=2,
    )
    r2 = StateChangeRecord(
        device_id=1,
        timestamp=200,
        parameters={"temperature": "22"},
        device_type=2,
    )

    await history.append(r1)
    await history.append(r2)

    rows = await history.history_for(1)
    assert rows == [r1, r2]
    assert await history.history_for(99) == []


@pytest.mark.asyncio
async def test_state_change_processor_appends_record_when_device_registered() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    processor = StateChangeProcessor(registry, history, _time_service_at(200))
    writer = _mock_writer()

    await registry.register(
        RegisteredDevice(
            device_id=1,
            writer=writer,
            device_type="thermostat",
            capabilities={},
            device_state={"temperature": "21"},
            timestamp=100,
        )
    )

    event = DeviceStateChangeEvent(
        device_id=1,
        writer=writer,
        request_id="test-request-1",
        device_type=3,
        parameters={"temperature": "25"},
        timestamp=200,
    )

    await processor.handle(event)

    stored = await registry.get_by_device_id(1)
    assert stored is not None
    assert stored.device_state == {"temperature": "21"}
    assert stored.timestamp == 100

    rows = await history.history_for(1)
    assert len(rows) == 1
    rec = rows[0]
    assert rec.device_id == 1
    assert rec.timestamp == 200
    assert rec.device_type == 3
    assert rec.parameters == {"temperature": "25"}

    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()
    sent_request_id, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)
    assert sent_request_id == "test-request-1"
    assert sent_envelope.WhichOneof("payload") == "device_state_change_resp"
    resp = sent_envelope.device_state_change_resp
    assert resp.device_id == 1
    assert resp.success is True
    assert resp.timestamp == 200
    assert resp.message == "State change recorded: {'temperature': '25'}"


@pytest.mark.asyncio
async def test_state_change_processor_appends_multiple_events_in_order() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    processor = StateChangeProcessor(registry, history, _time_service_at(200))
    writer = _mock_writer()

    await registry.register(
        RegisteredDevice(
            device_id=7,
            writer=writer,
            device_type="sensor",
            capabilities={},
            device_state={},
            timestamp=1,
        )
    )

    await processor.handle(
        DeviceStateChangeEvent(
            device_id=7,
            writer=writer,
            request_id="test-request-2",
            device_type=1,
            parameters={"a": "1"},
            timestamp=10,
        )
    )
    await processor.handle(
        DeviceStateChangeEvent(
            device_id=7,
            writer=writer,
            request_id="test-request-3",
            device_type=1,
            parameters={"a": "2"},
            timestamp=20,
        )
    )

    rows = await history.history_for(7)
    assert [r.timestamp for r in rows] == [10, 20]
    assert [r.parameters for r in rows] == [{"a": "1"}, {"a": "2"}]


@pytest.mark.asyncio
async def test_state_change_processor_does_not_append_when_device_not_registered() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    processor = StateChangeProcessor(registry, history, _time_service_at(200))
    writer = _mock_writer()

    event = DeviceStateChangeEvent(
        device_id=99,
        writer=writer,
        request_id="test-request-4",
        device_type=1,
        parameters={"x": "y"},
        timestamp=50,
    )

    await processor.handle(event)

    assert await history.history_for(99) == []

    writer.write.assert_called_once()
    writer.drain.assert_awaited_once()
    sent_request_id, sent_proto_bytes = decode_wire_message(writer.write.call_args.args[0])
    sent_envelope = parse_envelope(sent_proto_bytes)
    assert sent_request_id == "test-request-4"
    assert sent_envelope.device_state_change_resp.success is False
    assert sent_envelope.device_state_change_resp.message == "Device 99 not registered"
