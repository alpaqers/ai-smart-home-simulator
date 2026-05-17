from unittest.mock import Mock
import pytest

from smart_home.server.registry import DeviceRegistry, RegisteredDevice

@pytest.mark.asyncio
async def test_registration_duplicates() -> None:
    registry = DeviceRegistry()

    writer_1 = Mock()
    writer_2 = Mock()

    device_1 = RegisteredDevice(
        device_id=10,
        writer=writer_1,
        device_type="thermostat",
        capabilities={"mode": "heat"},
        device_state={"temperature": "22"},
        timestamp=111,
    )

    device_2 = RegisteredDevice(
        device_id=10,
        writer=writer_2,
        device_type="thermostat",
        capabilities={"mode": "cool"},
        device_state={"temperature": "19"},
        timestamp=222,
    )

    await registry.register(device_1)

    with pytest.raises(ValueError):
        await registry.register(device_2)

    stored = await registry.get_by_device_id(10)
    assert stored is not None
    assert stored.device_id == 10
    assert stored.writer is writer_1
    assert stored.capabilities == {"mode": "heat"}
    assert stored.device_state == {"temperature": "22"}
    assert stored.timestamp == 111