from unittest.mock import AsyncMock, Mock

import pytest

from smart_home.client.controllers.device_service import send_state_change
from smart_home.client.controllers.message_coder import build_envelope
from smart_home.client.models.connection_storage import ConnectionStorage
from smart_home.client.models.device import Device
from smart_home.proto.v1 import message_pb2
import base64


def _mock_logger() -> Mock:
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    return logger


@pytest.mark.asyncio
async def test_send_state_change_logs_success() -> None:
    resp = message_pb2.DeviceStateChangeResp()
    resp.device_id = 1
    resp.success = True
    resp.message = "State change recorded: {'is_on': 'false'}"
    response_b64 = base64.b64encode(build_envelope(resp)).decode("utf-8")

    handler = Mock()
    handler.send_and_wait = AsyncMock(return_value=response_b64)

    storage = ConnectionStorage()
    storage.connections[1] = handler

    device = Device(device_id=1, device_type="lamp", device_state={"is_on": "false"})
    logger = _mock_logger()

    ok, msg = await send_state_change(storage, device, {"is_on": "false"}, logger)

    assert ok is True
    assert msg == "State change sent: device=1 state={'is_on': 'false'}"
    logger.info.assert_called_once_with(msg)
    logger.error.assert_not_called()


@pytest.mark.asyncio
async def test_send_state_change_logs_missing_connection() -> None:
    device = Device(device_id=9, device_type="lamp")
    logger = _mock_logger()

    ok, msg = await send_state_change(ConnectionStorage(), device, {"is_on": "true"}, logger)

    assert ok is False
    assert msg == "No active connection for device 9."
    logger.error.assert_called_once_with(msg)
    logger.info.assert_not_called()
