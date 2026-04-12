from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.server.events import DeviceStateChangeEvent
from smart_home.server.processors import StateChangeProcessor
from smart_home.server.registry import DeviceRegistry, RegisteredDevice


@pytest.mark.asyncio
async def test_state_update_device_not_registered_returns_false() -> None:
    registry = DeviceRegistry()

    success = await registry.update_state(
        device_id=1,
        parameters={"temperature": "21"},
        timestamp=100,
    )

    assert success is False
    assert await registry.get_by_device_id(1) is None


@pytest.mark.asyncio
async def test_registry_update_state_returns_true_and_updates_device_state() -> None:
    registry = DeviceRegistry()
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

    success = await registry.update_state(
        device_id=1,
        parameters={"temperature": "25"},
        timestamp=200,
    )

    assert success is True

    stored = await registry.get_by_device_id(1)

    assert stored is not None
    assert stored.device_state == {"temperature": "25"}
    assert stored.timestamp == 200


@pytest.mark.asyncio
async def test_state_change_processor_updates_device_state() -> None:
    registry = DeviceRegistry()
    processor = StateChangeProcessor(registry)
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
        device_type="thermostat",
        parameters={"temperature": "25"},
        timestamp=200,
    )

    await processor.handle(event)

    stored = await registry.get_by_device_id(1)

    assert stored is not None
    assert stored.device_state == {"temperature": "25"}
    assert stored.timestamp == 200