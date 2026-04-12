from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from smart_home.proto.v1 import message_pb2
from smart_home.server.message_handler import handle_message, parse_envelope, build_envelope


def test_handle_message_recognizes_state_change():
    envelope = message_pb2.Envelope()
    envelope.device_state_change.device_id = "1"

    assert handle_message(envelope) == "device_state_change"


def test_handle_message_recognizes_device_response():
    envelope = message_pb2.Envelope()
    envelope.device_response.device_id = "2"

    assert handle_message(envelope) == "device_response"


def test_full_flow_device_state_change():
    msg = message_pb2.DeviceStateChange()
    msg.device_id = "1"
    msg.parameters["temperature"] = "24.6"

    data = build_envelope(msg)
    envelope = parse_envelope(data)
    result = handle_message(envelope)

    assert result == "device_state_change"


def test_full_flow_device_response():
    msg = message_pb2.DeviceResponse()
    msg.device_id = "2"
    msg.success = True
    msg.message = "Light turned on"

    data = build_envelope(msg)
    envelope = parse_envelope(data)
    result = handle_message(envelope)

    assert result == "device_response"
