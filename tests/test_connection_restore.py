import sys
from unittest.mock import AsyncMock, Mock, patch

mock_models = Mock()
mock_events = Mock()
mock_models.events = mock_events
sys.modules["models"] = mock_models
sys.modules["models.events"] = mock_events

mock_protobuf = Mock()
sys.modules["google"] = mock_protobuf
sys.modules["google.protobuf"] = mock_protobuf
sys.modules["google.protobuf.descriptor"] = mock_protobuf
sys.modules["google.protobuf.internal"] = mock_protobuf

mock_pb2 = Mock()
sys.modules["smart_home.proto.v1"] = mock_pb2
sys.modules["smart_home.proto.v1.message_pb2"] = mock_pb2

import pytest

from smart_home.client.controllers.connection_restore import restore_connections
from smart_home.client.models.connection_storage import ConnectionStorage
from smart_home.client.models.device import Device
from smart_home.client.models.device_storage import DeviceStorage


@pytest.mark.asyncio
async def test_restore_connections_adds_handler_on_success():
    storage = DeviceStorage()
    storage.lamps[1] = Device(device_id=1, device_type="lamp", device_state={"is_on": "true"})

    conn_storage = ConnectionStorage()
    bus = Mock()
    logger = Mock()

    handler = Mock()
    handler.start = AsyncMock()
    handler.stop = AsyncMock()

    with patch(
        "smart_home.client.controllers.connection_restore.reconnect_device",
        new=AsyncMock(return_value=(handler, "ok")),
    ):
        await restore_connections(storage, conn_storage, bus, logger)

    assert conn_storage.connections[1] is handler
    logger.info.assert_called()