import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_home.client.controllers.message_coder import (
    encode_register_request,
    decode_register_response,
    encode_state_change,
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
    payload_b64 = encode_state_change(1, {"power": "ON"}, "lamp")
    data = base64.b64decode(payload_b64)
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    assert envelope.WhichOneof("payload") == "device_state_change"
    assert envelope.device_state_change.device_id == 1
    assert envelope.device_state_change.parameters["power"] == "ON"
