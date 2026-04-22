from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))


from smart_home.proto.v1 import message_pb2
from smart_home.client.controllers import message_coder
import base64
import time

TIMESTAMP = int(time.time())


def test_device_state_change_serialization():
    msg = message_pb2.DeviceStateChange()
    msg.device_id = 1
    msg.device_type = 2
    msg.timestamp = TIMESTAMP
    msg.parameters["temperature"] = "24.6"

    data = msg.SerializeToString()
    received = message_pb2.DeviceStateChange()
    received.ParseFromString(data)

    assert received.device_id == 1
    assert received.device_type == 2
    assert received.timestamp == TIMESTAMP
    assert received.parameters["temperature"] == "24.6"


def test_device_state_update_serialization():
    cmd = message_pb2.DeviceStateUpdate()
    cmd.device_id = 1
    cmd.command_type = 1
    cmd.timestamp = TIMESTAMP
    cmd.parameters["time"] = "16:00"

    data = cmd.SerializeToString()
    received = message_pb2.DeviceStateUpdate()
    received.ParseFromString(data)

    assert received.device_id == 1
    assert received.command_type == 1
    assert received.timestamp == TIMESTAMP
    assert received.parameters["time"] == "16:00"


def test_device_response_serialization():
    ack = message_pb2.DeviceResponse()
    ack.device_id = 1
    ack.timestamp = TIMESTAMP
    ack.success = True
    ack.message = "Swiatlo zapalone o 16:00"

    data = ack.SerializeToString()
    received = message_pb2.DeviceResponse()
    received.ParseFromString(data)

    assert received.device_id == 1
    assert received.success == True
    assert received.timestamp == TIMESTAMP
    assert received.message == "Swiatlo zapalone o 16:00"


def test_create_state_change_message_from_coder():
    msg = message_coder.create_state_change_message(
        device_id=7,
        parameters={"power": "ON", "brightness": "80"},
        device_type=1,
    )

    assert msg.device_id == 7
    assert msg.device_type == 1
    assert msg.parameters["power"] == "ON"
    assert msg.parameters["brightness"] == "80"
    assert msg.timestamp > 0


def test_encode_state_change_from_coder_roundtrip():
    payload_b64 = message_coder.encode_state_change(
        device_id=8,
        parameters={"temperature": "24.5"},
        device_type=2,
    )

    payload = base64.b64decode(payload_b64)
    decoded = message_pb2.DeviceStateChange.FromString(payload)

    assert decoded.device_id == 8
    assert decoded.device_type == 2
    assert decoded.parameters["temperature"] == "24.5"
    assert decoded.timestamp > 0
