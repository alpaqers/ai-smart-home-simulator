from unittest.mock import Mock

import pytest

from smart_home.server.events import DeviceStateChangeEvent
from smart_home.server.processors import StateChangeProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice
from smart_home.server.state_history import DeviceStateHistory, StateChangeRecord


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
    processor = StateChangeProcessor(registry, history)
    writer = Mock()

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


@pytest.mark.asyncio
async def test_state_change_processor_appends_multiple_events_in_order() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    processor = StateChangeProcessor(registry, history)
    writer = Mock()

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
            device_type=1,
            parameters={"a": "1"},
            timestamp=10,
        )
    )
    await processor.handle(
        DeviceStateChangeEvent(
            device_id=7,
            writer=writer,
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
    processor = StateChangeProcessor(registry, history)
    writer = Mock()

    event = DeviceStateChangeEvent(
        device_id=99,
        writer=writer,
        device_type=1,
        parameters={"x": "y"},
        timestamp=50,
    )

    await processor.handle(event)

    assert await history.history_for(99) == []