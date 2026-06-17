import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_home.client.controllers.message_coder import (
    build_envelope,
    decode_register_response,
    decode_state_change_response,
    decode_task_list_response,
    encode_register_request,
    encode_state_change,
    encode_task_list_request,
    decode_state_update_message,
)
from smart_home.proto.v1 import message_pb2
import base64


def test_encode_register_request():
    payload_b64, req = encode_register_request("lamp")
  
    data = base64.b64decode(payload_b64)
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    assert envelope.WhichOneof("payload") == "device_register_req"
    assert envelope.device_register_req.device_type == "lamp"


def test_encode_state_change():
    payload_b64 = encode_state_change(1, {"power": "ON"}, 1)
    data = base64.b64decode(payload_b64)
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    assert envelope.WhichOneof("payload") == "device_state_change"
    assert envelope.device_state_change.device_id == 1
    assert envelope.device_state_change.device_type == 1
    assert envelope.device_state_change.parameters["power"] == "ON"


def test_decode_state_change_response_roundtrip():
    resp = message_pb2.DeviceStateChangeResp()
    resp.device_id = 3
    resp.timestamp = 1700000000
    resp.success = True
    resp.message = "State change recorded: {'is_on': 'false'}"

    payload_b64 = base64.b64encode(build_envelope(resp)).decode("utf-8")
    decoded = decode_state_change_response(payload_b64)

    assert decoded is not None
    assert decoded.device_id == 3
    assert decoded.success is True
    assert decoded.message == "State change recorded: {'is_on': 'false'}"


def test_encode_task_list_request():
    payload_b64 = encode_task_list_request(include_dispatched=False)

    data = base64.b64decode(payload_b64)
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)

    assert envelope.WhichOneof("payload") == "task_list_request"
    assert envelope.task_list_request.include_dispatched is False


def test_decode_task_list_response_roundtrip():
    resp = message_pb2.TaskListResp()
    resp.success = True
    resp.timestamp = 1700000000

    task = resp.tasks.add()
    task.task_id = 1
    task.device_id = 7
    task.parameters["power"] = "on"
    task.time = 1700000300

    payload_b64 = base64.b64encode(build_envelope(resp)).decode("utf-8")
    decoded = decode_task_list_response(payload_b64)

    assert decoded is not None
    assert decoded.success is True
    assert len(decoded.tasks) == 1
    assert decoded.tasks[0].device_id == 7
    assert dict(decoded.tasks[0].parameters) == {"power": "on"}
