from __future__ import annotations

import base64

from time import time
from ...proto.v1 import message_pb2

def build_envelope(message) -> bytes:
    envelope = message_pb2.Envelope()
    if isinstance(message, message_pb2.DeviceStateChange):
        envelope.device_state_change.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceStateUpdate):
        envelope.device_state_update.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceResponse):
        envelope.device_response.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterReq):
        envelope.device_register_req.CopyFrom(message)
    elif isinstance(message, message_pb2.DeviceRegisterResp):
        envelope.device_register_resp.CopyFrom(message)
    else:
        raise ValueError(f"Unsupported message type: {type(message).__name__}")

    return envelope.SerializeToString()

def parse_envelope(data: bytes) -> message_pb2.Envelope:
    envelope = message_pb2.Envelope()
    envelope.ParseFromString(data)
    return envelope

def encode_register_request(
    device_type:  str,
    capabilities: dict[str, str],
    device_state: dict[str, str],
) -> tuple[str, message_pb2.DeviceRegisterReq]:
    req = message_pb2.DeviceRegisterReq()
    req.device_type = device_type
    req.timestamp   = int(time())
    req.capabilities.update(capabilities)
    req.device_state.update(device_state)

    envelope_bytes = build_envelope(req)
    payload_b64 = base64.b64encode(envelope_bytes).decode("utf-8")
    return payload_b64, req


def decode_register_response(response_b64: str) -> message_pb2.DeviceRegisterResp:
    envelope_bytes = base64.b64decode(response_b64)
    envelope = parse_envelope(envelope_bytes)
    return envelope.device_register_resp


def encode_state_change(device_id: int, parameters: dict[str, str], device_type: str) -> str:
    msg = message_pb2.DeviceStateChange()
    msg.device_id = device_id
    msg.timestamp = int(time())
    msg.device_type = device_type
    if parameters:
        msg.parameters.update(parameters)

    envelope_bytes = build_envelope(msg)
    return base64.b64encode(envelope_bytes).decode("utf-8")


def decode_state_update_message(response_b64: str) -> message_pb2.DeviceStateUpdate | None:
    try:
        envelope_bytes = base64.b64decode(response_b64, validate=True)
        envelope = parse_envelope(envelope_bytes)
        msg = envelope.device_state_update
    except Exception:
        return None

    has_content = bool(msg.parameters) or msg.command_type != 0 or msg.timestamp != 0
    if msg.device_id <= 0 or not has_content:
        return None

    return msg
